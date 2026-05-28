import logging
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive

from nomad.parsing.parser import MatchingParser
import numpy as np
from PIL import Image

from plugin_img.schema_packages.image_analysis import (
    ImageDataset,
    ImageExperimentRun,
    ImageMetadata,
    ManifestData,
    ImageData,
    ImageDimensions,
    RegionOfInterest,
    BoundingBox,
    ImageVisualization,
)

logger_module = logging.getLogger(__name__)


class DataRootParser(MatchingParser):
    """Parser for image data - processes manifest.csv files from timestamped folders."""

    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger=None,
        child_archives=None,
    ) -> None:
        """Parse all experiments from parent directory."""
        log = logger or logger_module
        mainfile_path = Path(mainfile)
        
        # Skip if already processed
        if archive.data is not None:
            log.debug('Archive already has data, skipping parse')
            return
        
        # Get parent directory (contains all timestamp folders)
        parent_path = mainfile_path.parent
        log.info('Parsing experiments from parent directory: %s', parent_path)
        
        try:
            # Find all timestamp-named folders
            timestamp_pattern = re.compile(r'^\d{8}_\d{6}$')
            experiment_folders = sorted([
                d for d in parent_path.iterdir()
                if d.is_dir() and timestamp_pattern.match(d.name)
            ])
            
            if not experiment_folders:
                log.warning('No timestamp-named folders found in %s', parent_path)
                return
            
            log.info('Found %d experiment folders', len(experiment_folders))
            
            # Parse all experiments
            experiments = []
            for exp_folder in experiment_folders:
                log.info('Processing experiment: %s', exp_folder.name)
                experiment = ImageExperimentRun()
                experiment.timestamp = exp_folder.name
                experiment.name = f'Experiment {exp_folder.name}'
                
                # Parse manifest.csv
                manifest_path = exp_folder / 'manifest.csv'
                if manifest_path.exists():
                    manifest = self._parse_manifest(str(manifest_path), log)
                    if manifest:
                        experiment.manifest_data = manifest
                        log.info('Manifest parsed for: %s', exp_folder.name)
                else:
                    log.debug('manifest.csv not found in %s', exp_folder.name)
                
                # Parse metadata.json
                metadata_path = exp_folder / 'metadata.json'
                if metadata_path.exists():
                    metadata, image_data = self._parse_metadata(metadata_path, log)
                    if metadata:
                        experiment.metadata = metadata
                        log.info('Metadata parsed for: %s', exp_folder.name)
                    if image_data:
                        experiment.image = image_data
                        log.info('Image data parsed for: %s', exp_folder.name)
                else:
                    log.debug('metadata.json not found in %s', exp_folder.name)
                
                # Load and parse image_raw.npy
                image_path = exp_folder / 'image_raw.npy'
                if image_path.exists() and experiment.image:
                    # Store the path to the image file
                    experiment.image.image_array = str(image_path)
                    
                    # Convert NPY to PNG for visualization
                    png_path = self._convert_npy_to_png(image_path, log)
                    if png_path:
                        # Store both absolute and relative paths
                        experiment.image.image_preview = png_path
                        
                        # Create visualization subsection with PNG file reference
                        visualization = ImageVisualization()
                        # Store as relative path from the data root for NOMAD to access
                        try:
                            rel_png_path = Path(png_path).relative_to(parent_path)
                            # Use forward slashes for web URL compatibility
                            visualization.image_file = str(rel_png_path).replace('\\', '/')
                        except ValueError:
                            # If relative path fails, use absolute path
                            visualization.image_file = png_path
                        
                        experiment.image.visualization = visualization
                        
                        log.info('PNG preview created: %s (stored as: %s)', 
                                png_path, visualization.image_file)
                    
                    log.info('Image file referenced for: %s (%s)', exp_folder.name, image_path.name)
                else:
                    if not image_path.exists():
                        log.debug('image_raw.npy not found in %s', exp_folder.name)
                
                experiments.append(experiment)
            
            # Create single dataset with all experiments
            dataset = ImageDataset()
            dataset.name = f'Image Dataset from {parent_path.name}'
            dataset.measurements = experiments
            archive.data = dataset
            
            log.info('Successfully created dataset with %d experiments', len(experiments))
            
        except Exception as exc:
            log.error('Error parsing experiments: %s', str(exc), exc_info=True)

    def _parse_manifest(self, csv_path: Path, log) -> ManifestData:
        """Parse manifest.csv file."""
        try:
            import pandas as pd
            
            df = pd.read_csv(str(csv_path))
            if df.empty:
                log.debug('Manifest CSV is empty')
                return None

            row = df.iloc[0]
            manifest = ManifestData()

            field_mapping = {
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

            for csv_col, field_name in field_mapping.items():
                if csv_col in row.index:
                    value = row[csv_col]
                    if pd.notna(value):
                        try:
                            if field_name == 'Date':
                                setattr(manifest, field_name, str(value))
                            else:
                                setattr(manifest, field_name, float(value))
                        except (ValueError, TypeError):
                            log.warning('Could not convert %s=%s', field_name, value)

            log.info('Parsed manifest successfully')
            return manifest

        except Exception as exc:
            log.error('Error parsing manifest: %s', str(exc))
            return None

    def _parse_metadata(self, json_path: Path, log) -> tuple:
        """Parse metadata.json file and extract metadata and image data.
        
        Returns:
            tuple: (ImageMetadata, ImageData) or (None, None) if parsing fails
        """
        try:
            with open(str(json_path)) as f:
                data = json.load(f)

            metadata = ImageMetadata()

            # Basic metadata fields
            metadata.timestamp = data.get('timestamp', '')
            metadata.exposure_ms = float(data.get('exposure_ms', 0.0))
            metadata.gain = float(data.get('gain', 0))
            metadata.bit_depth = int(data.get('bit_depth', 8))
            metadata.shape = data.get('shape', [])
            metadata.is_color = bool(data.get('is_color', False))
            metadata.min = float(data.get('min', 0))
            metadata.max = float(data.get('max', 255))

            log.info('Parsed metadata successfully')
            
            # Parse image data from metadata
            image_data = self._extract_image_data(data, log)
            
            return metadata, image_data

        except Exception as exc:
            log.error('Error parsing metadata: %s', str(exc))
            return None, None
    
    def _extract_image_data(self, metadata_dict: dict, log) -> ImageData:
        """Extract image data from metadata dictionary.
        
        Extracts dimensions and region of interest information.
        """
        try:
            image_data = ImageData()
            
            # Extract image dimensions
            shape = metadata_dict.get('shape', [])
            if shape and len(shape) >= 2:
                dimensions = ImageDimensions()
                # shape is [height, width, channels] or [height, width]
                dimensions.height = int(shape[0])
                dimensions.width = int(shape[1])
                dimensions.channels = int(shape[2]) if len(shape) > 2 else 1
                dimensions.bit_depth = int(metadata_dict.get('bit_depth', 8))
                dimensions.is_color = bool(metadata_dict.get('is_color', False))
                dimensions.min = float(metadata_dict.get('min', 0))
                dimensions.max = float(metadata_dict.get('max', 255))
                image_data.dimensions = dimensions
                log.info('Image dimensions extracted: %d x %d x %d channels', 
                        dimensions.height, dimensions.width, dimensions.channels)
            
            # Extract region of interest
            circular_roi = metadata_dict.get('circular_roi', {})
            if circular_roi:
                roi = RegionOfInterest()
                roi.center_x_px = float(circular_roi.get('center_x_px', 0))
                roi.center_y_px = float(circular_roi.get('center_y_px', 0))
                roi.radius_px = float(circular_roi.get('radius_px', 0))
                roi.square_crop_size_px = int(circular_roi.get('square_crop_size_px', 0))
                
                # Extract bounding box
                bbox_data = circular_roi.get('bounding_box', {})
                if bbox_data:
                    bbox = BoundingBox()
                    bbox.x_min = int(bbox_data.get('x_min', 0))
                    bbox.y_min = int(bbox_data.get('y_min', 0))
                    bbox.x_max = int(bbox_data.get('x_max', 0))
                    bbox.y_max = int(bbox_data.get('y_max', 0))
                    bbox.width = int(bbox_data.get('width', 0))
                    bbox.height = int(bbox_data.get('height', 0))
                    roi.bounding_box = bbox
                    log.info('Bounding box extracted: (%d,%d) to (%d,%d)', 
                            bbox.x_min, bbox.y_min, bbox.x_max, bbox.y_max)
                
                image_data.roi = roi
                log.info('ROI extracted: center=(%f, %f), radius=%f', 
                        roi.center_x_px, roi.center_y_px, roi.radius_px)
            
            return image_data
            
        except Exception as exc:
            log.error('Error extracting image data: %s', str(exc))
            return None
    
    def _convert_npy_to_png(self, npy_path: Path, log) -> str:
        """Convert NPY image to PNG for visualization.
        
        Args:
            npy_path: Path to the .npy file
            log: Logger instance
            
        Returns:
            str: Path to the generated PNG file, or None if conversion fails
        """
        try:
            # Load the NPY file
            image_array = np.load(str(npy_path))
            log.info('Loaded NPY array with shape: %s', image_array.shape)
            
            # Normalize image to 0-255 range for display
            if image_array.size == 0:
                log.warning('Image array is empty')
                return None
            
            # Handle different image shapes
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                # RGB image
                img_normalized = self._normalize_array(image_array)
                img = Image.fromarray(img_normalized.astype(np.uint8), mode='RGB')
            elif len(image_array.shape) == 3 and image_array.shape[2] == 1:
                # Grayscale with channel dimension
                img_normalized = self._normalize_array(image_array[:, :, 0])
                img = Image.fromarray(img_normalized.astype(np.uint8), mode='L')
            elif len(image_array.shape) == 2:
                # Grayscale without channel dimension
                img_normalized = self._normalize_array(image_array)
                img = Image.fromarray(img_normalized.astype(np.uint8), mode='L')
            else:
                log.warning('Unsupported image shape: %s', image_array.shape)
                return None
            
            # Save as PNG
            png_path = npy_path.parent / 'image_preview.png'
            img.save(str(png_path))
            log.info('Saved PNG preview to: %s', png_path)
            
            return str(png_path)
            
        except Exception as exc:
            log.error('Error converting NPY to PNG: %s', str(exc))
            return None
    
    def _normalize_array(self, array: np.ndarray) -> np.ndarray:
        """Normalize array values to 0-255 range.
        
        Args:
            array: Input numpy array
            
        Returns:
            np.ndarray: Normalized array
        """
        arr_min = array.min()
        arr_max = array.max()
        
        if arr_max == arr_min:
            # Constant array
            return np.full_like(array, 128, dtype=np.uint16)
        
        # Scale to 0-255
        normalized = ((array - arr_min) / (arr_max - arr_min) * 255)
        return normalized