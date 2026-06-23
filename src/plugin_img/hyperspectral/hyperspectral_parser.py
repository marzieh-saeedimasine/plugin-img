import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from nomad.datamodel.metainfo.plot import PlotlyFigure
from nomad.parsing.parser import MatchingParser
from PIL import Image

from plugin_img.hyperspectral.hyperspectral_cube import (
    ENVI_DTYPE_MAP,
    read_bil,
    read_envi_hdr,
)
from plugin_img.hyperspectral.hyperspectral_shcema import (
    AcquisitionMetadata,
    CubeMetadata,
    HyperspectralDataset,
    HyperspectralMeasurement,
    HyperspectralRawData,
    HyperspectralVisualization,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive

logger_module = logging.getLogger(__name__)


class HyperspectralRootParser(MatchingParser):
    """
    Parser for hyperspectral datasets.

    Expected structure:

    sample/
    ├── synth_con.json
    │
    ├── image_data/
    │   ...
    │
    └── hyperspectral_data/
        ├── cube.hdr
        ├── cube.bil
        └── optional_preview.png
    """

    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger=None,
        child_archives=None,
    ) -> None:

        log = logger or logger_module

        if archive.data is not None:
            return

        root = Path(mainfile).parent

        dataset = HyperspectralDataset()
        dataset.name = f'Hyperspectral Dataset - {root.name}'

        measurements = []

        for folder in self._find_hyperspectral_folders(root):
            measurement = self._parse_hyperspectral_folder(
                folder,
                root,
                log,
            )

            if measurement:
                measurements.append(measurement)

        dataset.measurements = measurements
        dataset.figures = self._collect_dataset_figures(measurements)

        archive.data = dataset

        log.info(
            'Parsed %d hyperspectral measurements',
            len(measurements),
        )

    def _collect_dataset_figures(
        self,
        measurements: list[HyperspectralMeasurement],
    ):

        figures = []

        for measurement in measurements:
            visualization = measurement.visualization
            if visualization is None or not visualization.figures:
                continue

            for figure in visualization.figures:
                label = figure.label
                if len(measurements) > 1 and measurement.label:
                    label = f'{measurement.label} - {label}'

                figures.append(
                    PlotlyFigure(
                        label=label,
                        index=figure.index,
                        open=figure.open,
                        figure=figure.figure,
                    )
                )

        return figures

    # ==========================================================
    # Folder Discovery
    # ==========================================================

    def _find_hyperspectral_folders(
        self,
        root: Path,
    ) -> list[Path]:

        folders = []

        if self._find_hdr_file(root) and self._find_bil_file(root):
            folders.append(root)

        for folder in sorted(root.iterdir()):
            if not folder.is_dir():
                continue

            hdr_files = list(folder.glob('*.hdr'))

            if hdr_files:
                folders.append(folder)

        return folders

    # ==========================================================
    # Parse One Folder
    # ==========================================================

    def _parse_hyperspectral_folder(
        self,
        folder: Path,
        root: Path,
        log,
    ) -> HyperspectralMeasurement | None:

        hdr_file = self._find_hdr_file(folder)
        bil_file = self._find_bil_file(folder, hdr_file)

        if hdr_file is None:
            return None

        if bil_file is None:
            return None

        try:
            hdr = read_envi_hdr(str(hdr_file))

            wavelengths = self._extract_wavelengths(hdr)

            dtype = ENVI_DTYPE_MAP[str(hdr['data type'])]

            cube = read_bil(
                str(bil_file),
                lines=int(hdr['lines']),
                samples=int(hdr['samples']),
                bands=int(hdr['bands']),
                dtype=dtype,
            )

            npy_file = self._create_npy(
                folder,
                cube,
            )

            preview_file = self._create_rgb_preview(
                folder,
                cube,
                wavelengths,
                log,
            )

            measurement = HyperspectralMeasurement()

            measurement.acquisition_metadata = self._build_acquisition_metadata(hdr)

            measurement.cube_metadata = self._build_cube_metadata(
                hdr,
                wavelengths,
            )

            raw_data = HyperspectralRawData()

            raw_data.hdr_file = self._relative_upload_path(hdr_file, root)
            raw_data.bil_file = self._relative_upload_path(bil_file, root)
            raw_data.cube_npy = self._relative_upload_path(npy_file, root)

            if preview_file:
                raw_data.rgb_preview = self._relative_upload_path(preview_file, root)

            measurement.raw_data = raw_data

            measurement.visualization = HyperspectralVisualization()
            measurement.visualization.create_plots(
                npy_file,
                hdr_file,
                log,
            )

            measurement.label = folder.name

            return measurement

        except Exception as exc:
            log.error(
                'Error parsing hyperspectral folder %s : %s',
                folder,
                exc,
            )

            return None

    # ==========================================================
    # File Discovery
    # ==========================================================

    def _find_hdr_file(
        self,
        folder: Path,
    ) -> Path | None:

        files = list(folder.glob('*.hdr'))

        return files[0] if files else None

    def _find_bil_file(
        self,
        folder: Path,
        hdr_file: Path | None = None,
    ) -> Path | None:

        if hdr_file is not None and hdr_file.name.endswith('.bil.hdr'):
            matching_bil = folder / hdr_file.name.removesuffix('.hdr')
            if matching_bil.exists():
                return matching_bil

        files = list(folder.glob('*.bil'))

        return files[0] if files else None

    # ==========================================================
    # Metadata Construction
    # ==========================================================

    def _build_cube_metadata(
        self,
        hdr,
        wavelengths,
    ) -> CubeMetadata:

        metadata = CubeMetadata()

        metadata.lines = int(hdr['lines'])
        metadata.samples = int(hdr['samples'])
        metadata.bands = int(hdr['bands'])
        metadata.wavelength = wavelengths.tolist()

        metadata.interleave = hdr.get(
            'interleave',
            '',
        )

        metadata.data_type = hdr.get(
            'data type',
            '',
        )

        metadata.wavelength_min_nm = float(wavelengths.min())

        metadata.wavelength_max_nm = float(wavelengths.max())

        return metadata

    def _build_acquisition_metadata(
        self,
        hdr,
    ) -> AcquisitionMetadata:

        metadata = AcquisitionMetadata()

        metadata.interleave = hdr.get('interleave')

        metadata.data_type = hdr.get('data type')

        metadata.sample_binning = self._safe_int(hdr.get('sample binning'))

        metadata.spectral_binning = self._safe_int(hdr.get('spectral binning'))

        metadata.line_binning = self._safe_int(hdr.get('line binning'))

        metadata.shutter = self._safe_float(hdr.get('shutter'))

        metadata.gain = self._safe_float(hdr.get('gain'))

        metadata.framerate = self._safe_float(hdr.get('framerate'))

        metadata.temperature = self._safe_float(hdr.get('temperature'))

        metadata.imager_serial_number = hdr.get('imager serial number')

        metadata.rotation = hdr.get('rotation')

        metadata.pixel_size = self._safe_float(hdr.get('pixel size'))

        metadata.byte_order = hdr.get('byte order')

        metadata.header_offset = self._safe_int(
            hdr.get(
                'header offset',
                0,
            )
        )

        metadata.flip_radiometric_calibration = self._safe_bool(
            hdr.get('flip radiometric calibration')
        )

        metadata.wavelength_unit = hdr.get('wavelength units')

        metadata.label = hdr.get('label')

        return metadata

    # ==========================================================
    # Cube Creation
    # ==========================================================

    def _create_npy(
        self,
        folder: Path,
        cube: np.ndarray,
    ) -> Path:

        npy_path = folder / 'cube.npy'

        np.save(
            npy_path,
            cube.astype(np.float32),
        )

        return npy_path

    # ==========================================================
    # RGB Preview
    # ==========================================================

    def _create_rgb_preview(
        self,
        folder: Path,
        cube: np.ndarray,
        wavelengths: np.ndarray,
        log,
    ) -> Path | None:

        try:
            r = self._nearest_band(
                wavelengths,
                650,
            )

            g = self._nearest_band(
                wavelengths,
                550,
            )

            b = self._nearest_band(
                wavelengths,
                450,
            )

            rgb = np.stack(
                [
                    cube[:, :, r],
                    cube[:, :, g],
                    cube[:, :, b],
                ],
                axis=-1,
            ).astype(np.float32)

            rgb /= rgb.max() + 1e-9

            rgb = (rgb * 255).astype(np.uint8)

            preview_path = folder / 'rgb_preview.png'

            Image.fromarray(rgb).save(preview_path)

            return preview_path

        except Exception as exc:
            log.warning(
                'Could not create RGB preview: %s',
                exc,
            )

            return None

    # ==========================================================
    # Utilities
    # ==========================================================

    def _extract_wavelengths(
        self,
        hdr,
    ) -> np.ndarray:

        values = hdr['wavelength']

        values = values.strip('{}')

        return np.array([float(v) for v in values.split(',')])

    def _nearest_band(
        self,
        wavelengths,
        wavelength,
    ):

        return int(np.abs(wavelengths - wavelength).argmin())

    def _safe_float(
        self,
        value,
    ):

        try:
            return float(value)
        except Exception:
            return None

    def _safe_int(
        self,
        value,
    ):

        try:
            return int(float(value))
        except Exception:
            return None

    def _safe_bool(
        self,
        value,
    ):

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            value = value.strip().lower()
            if value in {'true', '1', 'yes'}:
                return True
            if value in {'false', '0', 'no'}:
                return False

        return None

    def _relative_upload_path(
        self,
        path: Path,
        root: Path,
    ) -> str:

        try:
            upload_path = path.relative_to(root)
        except ValueError:
            upload_path = path

        return str(upload_path).replace('\\', '/')
