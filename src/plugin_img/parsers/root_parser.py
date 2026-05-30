import json
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from nomad.parsing.parser import MatchingParser
from PIL import Image

from plugin_img.schema_packages.image_analysis import (
    BoundingBox,
    ImageData,
    ImageDataset,
    ImageDimensions,
    ImageExperimentRun,
    ImageMetadata,
    ImageVisualization,
    ManifestData,
    RegionOfInterest,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive

logger_module = logging.getLogger(__name__)


class DataRootParser(MatchingParser):
    """Parser for sample folders with synthesis conditions and image data."""

    METADATA_NAMES = ('metadata.json',)
    NPY_NAMES = ('image_raw.npy', 'raw_image.npy')
    PNG_NAMES = ('image_preview.png', 'preview.png', 'image.png')
    IMAGE_FOLDER_HINTS = ('image data', 'image_data', 'images', 'image')
    TIMESTAMP_PATTERN = re.compile(r'^\d{8}_\d{6}$')

    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger=None,
        child_archives=None,
    ) -> None:
        """Parse a complete sample folder into one image dataset entry."""
        log = logger or logger_module

        if archive.data is not None:
            log.debug('Archive already has data, skipping parse')
            return

        data_root = Path(mainfile).parent
        log.info('Parsing image sample folder: %s', data_root)

        try:
            dataset = ImageDataset()
            dataset.name = f'Image Dataset from {data_root.name}'

            synthesis_json = self._find_synthesis_json(data_root)
            if synthesis_json:
                dataset.synthesis_conditions = self._parse_synthesis_json(
                    synthesis_json, log
                )
                log.info('Parsed synthesis conditions from %s', synthesis_json.name)

            experiments = []
            for image_folder in self._find_image_folders(data_root):
                experiment = self._parse_image_folder(image_folder, data_root, log)
                if experiment:
                    experiments.append(experiment)

            if not experiments:
                log.warning('No image data folders found in %s', data_root)
                archive.data = dataset
                return

            dataset.measurements = experiments
            archive.data = dataset

            log.info('Successfully created dataset with %d image measurements', len(experiments))

        except Exception as exc:
            log.error('Error parsing image sample folder: %s', str(exc), exc_info=True)

    def _find_synthesis_json(self, data_root: Path) -> Path | None:
        """Find the sample-level synthesis/condition JSON file."""
        json_files = [
            path
            for path in data_root.glob('*.json')
            if path.name.lower() not in self.METADATA_NAMES
        ]
        if not json_files:
            return None

        preferred_terms = ('synth', 'synthesis', 'condition', 'conditions')
        for path in sorted(json_files):
            if any(term in path.stem.lower() for term in preferred_terms):
                return path

        return sorted(json_files)[0]

    def _find_image_folders(self, data_root: Path) -> list[Path]:
        """Find direct child folders that contain image metadata or image arrays."""
        folders: list[Path] = []

        # Old layout: timestamp folders. New layout: Image data folder. This also
        # accepts any experiment folder that directly contains a metadata JSON or NPY.
        for folder in sorted(path for path in data_root.iterdir() if path.is_dir()):
            if folder.name.startswith('.'):
                continue

            has_image_files = (
                self._find_metadata_file(folder) is not None
                or self._find_npy_file(folder) is not None
                or self._find_png_file(folder) is not None
            )
            has_layout_hint = folder.name.lower() in self.IMAGE_FOLDER_HINTS
            has_timestamp_name = self.TIMESTAMP_PATTERN.match(folder.name) is not None

            if has_image_files or has_layout_hint or has_timestamp_name:
                folders.append(folder)

        return folders

    def _parse_image_folder(
        self, image_folder: Path, data_root: Path, log
    ) -> ImageExperimentRun | None:
        """Parse one image-bearing folder into an experiment run."""
        metadata_path = self._find_metadata_file(image_folder)
        manifest_path = image_folder / 'manifest.csv'
        npy_path = self._find_npy_file(image_folder)
        png_path = self._find_png_file(image_folder)

        if not any((metadata_path, manifest_path.exists(), npy_path, png_path)):
            log.debug('Skipping folder without parseable image data: %s', image_folder)
            return None

        experiment = ImageExperimentRun()
        experiment.timestamp = image_folder.name
        experiment.name = self._experiment_name(image_folder)

        if manifest_path.exists():
            manifest = self._parse_manifest(manifest_path, log)
            if manifest:
                experiment.manifest_data = manifest

        metadata_dict = {}
        if metadata_path:
            metadata, image_data, metadata_dict = self._parse_metadata(metadata_path, log)
            if metadata:
                experiment.metadata = metadata
            if image_data:
                experiment.image = image_data

        if npy_path or png_path:
            if experiment.image is None:
                experiment.image = ImageData()

            if npy_path:
                experiment.image.image_array = self._relative_upload_path(npy_path, data_root)
                if experiment.image.dimensions is None:
                    experiment.image.dimensions = self._dimensions_from_npy(
                        npy_path, metadata_dict, log
                    )
                experiment.image.create_image_plot(npy_path, log)

            preview_path = png_path
            if preview_path is None and npy_path:
                preview_path = self._convert_npy_to_png(npy_path, log)

            if preview_path:
                preview_ref = self._relative_upload_path(preview_path, data_root)
                experiment.image.image_preview = preview_ref
                experiment.image.visualization = ImageVisualization()
                experiment.image.visualization.image_file = preview_ref
                log.info('Image preview available for %s: %s', image_folder.name, preview_ref)

        return experiment

    def _experiment_name(self, image_folder: Path) -> str:
        if image_folder.name.lower() in self.IMAGE_FOLDER_HINTS:
            return 'Image data'
        return f'Experiment {image_folder.name}'

    def _find_metadata_file(self, folder: Path) -> Path | None:
        for name in self.METADATA_NAMES:
            path = folder / name
            if path.exists():
                return path
        candidates = sorted(folder.glob('*metadata*.json'))
        return candidates[0] if candidates else None

    def _find_npy_file(self, folder: Path) -> Path | None:
        for name in self.NPY_NAMES:
            path = folder / name
            if path.exists():
                return path
        candidates = sorted(folder.glob('*.npy'))
        return candidates[0] if candidates else None

    def _find_png_file(self, folder: Path) -> Path | None:
        for name in self.PNG_NAMES:
            path = folder / name
            if path.exists():
                return path
        candidates = sorted(folder.glob('*.png'))
        return candidates[0] if candidates else None

    def _relative_upload_path(self, path: Path, data_root: Path) -> str:
        try:
            return str(path.relative_to(data_root)).replace('\\', '/')
        except ValueError:
            return str(path).replace('\\', '/')

    def _parse_manifest(self, csv_path: Path, log) -> ManifestData | None:
        """Parse legacy per-experiment manifest.csv files."""
        try:
            df = pd.read_csv(csv_path)
            if df.empty:
                log.debug('Manifest CSV is empty: %s', csv_path)
                return None

            row = df.iloc[0]
            manifest = ManifestData()
            mapping = {
                'Date': 'Date',
                'Cu_source_power': 'Cu_source_power',
                'Sn_source_power': 'Sn_source_power',
                'Zn_source_power': 'Zn_source_power',
                'Pressure': 'Pressure',
                'Source_temperature': 'Source_temperature',
                'Process_temperature': 'Process_temperature',
                'Chamber_pressure': 'Chamber_pressure',
                'Process_time': 'Process_time',
                'Cooling_time': 'Cooling_time',
                'Cooling_rate': 'Cooling_rate',
            }

            for csv_col, field_name in mapping.items():
                if csv_col in row.index and pd.notna(row[csv_col]):
                    self._set_manifest_value(manifest, field_name, row[csv_col], log)

            return manifest

        except Exception as exc:
            log.error('Error parsing manifest %s: %s', csv_path, str(exc))
            return None

    def _parse_synthesis_json(self, json_path: Path, log) -> ManifestData | None:
        """Parse sample-level synthesis condition JSON into ManifestData."""
        try:
            with open(json_path) as file:
                data = json.load(file)

            manifest = ManifestData()
            mapping = {
                'date': 'Date',
                'Date': 'Date',
                'cu_source_power': 'Cu_source_power',
                'Cu_source_power': 'Cu_source_power',
                'sn_source_power': 'Sn_source_power',
                'Sn_source_power': 'Sn_source_power',
                'zn_source_power': 'Zn_source_power',
                'Zn_source_power': 'Zn_source_power',
                'pressure_mtorr': 'Pressure',
                'Pressure': 'Pressure',
                'source_temperature_degc': 'Source_temperature',
                'Source_temperature': 'Source_temperature',
                'process_temperature_degc': 'Process_temperature',
                'Process_temperature': 'Process_temperature',
                'chamber_pressure_mbar': 'Chamber_pressure',
                'Chamber_pressure': 'Chamber_pressure',
                'process_time_min': 'Process_time',
                'Process_time': 'Process_time',
                'cooling_time_min': 'Cooling_time',
                'Cooling_time': 'Cooling_time',
                'cooling_rate_degc_min': 'Cooling_rate',
                'Cooling_rate': 'Cooling_rate',
            }

            for json_key, field_name in mapping.items():
                if json_key in data:
                    self._set_manifest_value(manifest, field_name, data[json_key], log)

            return manifest

        except Exception as exc:
            log.error('Error parsing synthesis JSON %s: %s', json_path, str(exc))
            return None

    def _set_manifest_value(self, manifest: ManifestData, field_name: str, value, log):
        if value in (None, '', '-'):
            return
        try:
            if field_name == 'Date':
                setattr(manifest, field_name, str(value))
            else:
                setattr(manifest, field_name, self._to_float(value))
        except (ValueError, TypeError):
            log.warning('Could not convert manifest field %s=%s', field_name, value)

    def _to_float(self, value) -> float:
        if isinstance(value, str):
            value = value.strip().replace(',', '.')
        return float(value)

    def _parse_metadata(
        self, json_path: Path, log
    ) -> tuple[ImageMetadata | None, ImageData | None, dict]:
        """Parse metadata.json and derive image dimensions/ROI information."""
        try:
            with open(json_path) as file:
                data = json.load(file)

            metadata = ImageMetadata()
            metadata.timestamp = str(data.get('timestamp', ''))
            metadata.exposure_ms = self._to_float(data.get('exposure_ms', 0.0))
            metadata.gain = self._to_float(data.get('gain', 0))
            metadata.bit_depth = int(self._to_float(data.get('bit_depth', 8)))
            metadata.shape = data.get('shape', [])
            metadata.is_color = bool(data.get('is_color', False))
            metadata.min = self._to_float(data.get('min', 0))
            metadata.max = self._to_float(data.get('max', 255))

            image_data = self._extract_image_data(data, log)
            return metadata, image_data, data

        except Exception as exc:
            log.error('Error parsing metadata %s: %s', json_path, str(exc))
            return None, None, {}

    def _extract_image_data(self, metadata_dict: dict, log) -> ImageData:
        """Extract image dimensions and circular ROI from metadata."""
        image_data = ImageData()

        shape = metadata_dict.get('shape', [])
        if isinstance(shape, list) and len(shape) >= 2:
            dimensions = ImageDimensions()
            dimensions.height = int(shape[0])
            dimensions.width = int(shape[1])
            dimensions.channels = int(shape[2]) if len(shape) > 2 else 1
            dimensions.bit_depth = int(self._to_float(metadata_dict.get('bit_depth', 8)))
            dimensions.is_color = bool(metadata_dict.get('is_color', False))
            dimensions.pixel_value_min = int(self._to_float(metadata_dict.get('min', 0)))
            dimensions.pixel_value_max = int(self._to_float(metadata_dict.get('max', 255)))
            image_data.dimensions = dimensions

        circular_roi = metadata_dict.get('circular_roi', {})
        if circular_roi:
            roi = RegionOfInterest()
            roi.center_x_px = self._to_float(circular_roi.get('center_x_px', 0))
            roi.center_y_px = self._to_float(circular_roi.get('center_y_px', 0))
            roi.radius_px = self._to_float(circular_roi.get('radius_px', 0))
            roi.square_crop_size_px = int(
                self._to_float(circular_roi.get('square_crop_size_px', 0))
            )

            bbox_data = circular_roi.get('bounding_box', {})
            if bbox_data:
                bbox = BoundingBox()
                bbox.x_min = int(self._to_float(bbox_data.get('x_min', 0)))
                bbox.y_min = int(self._to_float(bbox_data.get('y_min', 0)))
                bbox.x_max = int(self._to_float(bbox_data.get('x_max', 0)))
                bbox.y_max = int(self._to_float(bbox_data.get('y_max', 0)))
                bbox.width = int(self._to_float(bbox_data.get('width', 0)))
                bbox.height = int(self._to_float(bbox_data.get('height', 0)))
                roi.bounding_box = bbox

            image_data.roi = roi

        return image_data

    def _dimensions_from_npy(
        self, npy_path: Path, metadata_dict: dict, log
    ) -> ImageDimensions | None:
        try:
            image_array = np.load(str(npy_path), mmap_mode='r')
            if len(image_array.shape) < 2:
                return None

            dimensions = ImageDimensions()
            dimensions.height = int(image_array.shape[0])
            dimensions.width = int(image_array.shape[1])
            dimensions.channels = int(image_array.shape[2]) if len(image_array.shape) > 2 else 1
            dimensions.bit_depth = int(self._to_float(metadata_dict.get('bit_depth', 8)))
            dimensions.is_color = dimensions.channels > 1
            dimensions.pixel_value_min = int(np.min(image_array))
            dimensions.pixel_value_max = int(np.max(image_array))
            return dimensions
        except Exception as exc:
            log.warning('Could not derive dimensions from %s: %s', npy_path, str(exc))
            return None

    def _convert_npy_to_png(self, npy_path: Path, log) -> Path | None:
        """Convert an NPY image to a PNG preview for visualization."""
        try:
            image_array = np.load(str(npy_path))
            if image_array.size == 0:
                log.warning('Image array is empty: %s', npy_path)
                return None

            if len(image_array.shape) == 3 and image_array.shape[2] >= 3:
                img_normalized = self._normalize_array(image_array[:, :, :3])
                img = Image.fromarray(img_normalized.astype(np.uint8), mode='RGB')
            elif len(image_array.shape) == 3 and image_array.shape[2] == 1:
                img_normalized = self._normalize_array(image_array[:, :, 0])
                img = Image.fromarray(img_normalized.astype(np.uint8), mode='L')
            elif len(image_array.shape) == 2:
                img_normalized = self._normalize_array(image_array)
                img = Image.fromarray(img_normalized.astype(np.uint8), mode='L')
            else:
                log.warning('Unsupported image shape: %s', image_array.shape)
                return None

            png_path = npy_path.parent / 'image_preview.png'
            img.save(str(png_path))
            return png_path

        except Exception as exc:
            log.error('Error converting NPY to PNG %s: %s', npy_path, str(exc))
            return None

    def _normalize_array(self, array: np.ndarray) -> np.ndarray:
        arr_min = array.min()
        arr_max = array.max()

        if arr_max == arr_min:
            return np.full_like(array, 128, dtype=np.float32)

        return (array - arr_min) / (arr_max - arr_min) * 255
