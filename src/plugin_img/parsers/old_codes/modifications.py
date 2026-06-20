
import numpy as np


class HyperspectralCube:
    """
    Container and analysis tools for hyperspectral datacubes.

    Coordinate conventions
    ----------------------
    data[line, sample, band]

    - line    → spatial Y (scan direction, reconstructed by Spectronon)
    - sample  → spatial X (across-track, sensor dimension)
    - band    → spectral dimension (wavelength)
    """

    def __init__(
        self,
        data,
        wavelengths,
        metadata=None,
        pixel_size_x_mm=None,
        pixel_size_y_mm=None,
    ):
        """
        Parameters
        ----------
        data : ndarray
            Hyperspectral data, shape (lines, samples, bands)
        wavelengths : ndarray
            Wavelengths in nm, shape (bands,)
        metadata : dict, optional
            ENVI header metadata
        pixel_size_x_mm : float, optional
            Physical size of one pixel in X (mm / sample)
        pixel_size_y_mm : float, optional
            Physical size of one pixel in Y (mm / line)
        """
        self.data = data
        self.wavelengths = wavelengths
        self.metadata = metadata or {}

        # Explicit spatial calibration (None = unknown / not set)
        self.pixel_size_x_mm = pixel_size_x_mm
        self.pixel_size_y_mm = pixel_size_y_mm

    # ------------------
    # Basic accessors
    # ------------------

    @property
    def shape(self):
        return self.data.shape

    @property
    def lines(self):
        return self.data.shape[0]

    @property
    def samples(self):
        return self.data.shape[1]

    @property
    def bands(self):
        return self.data.shape[2]

    def band_index(self, wavelength_nm):
        """Return band index closest to a wavelength."""
        return int(np.abs(self.wavelengths - wavelength_nm).argmin())

    def band(self, wavelength_nm):
        """Return spatial image at a given wavelength."""
        idx = self.band_index(wavelength_nm)
        return self.data[:, :, idx]

    def spectrum(self, line, sample):
        """Return spectrum at a single pixel."""
        return self.data[line, sample, :]

    def mean_spectrum(self, roi=None):
        """
        Compute mean spectrum.

        Parameters
        ----------
        roi : tuple or None
            (line_start, line_end, sample_start, sample_end)
        """
        if roi is None:
            return self.data.mean(axis=(0, 1))

        l1, l2, s1, s2 = roi
        return self.data[l1:l2, s1:s2, :].mean(axis=(0, 1))

    # ------------------
    # Spatial calibration
    # ------------------

    def has_spatial_calibration(self):
        """Return True if both pixel sizes are known."""
        return (
            self.pixel_size_x_mm is not None
            and self.pixel_size_y_mm is not None
        )

    def physical_coordinates(self):
        """
        Return physical coordinate arrays (x_mm, y_mm).

        Returns
        -------
        x_mm : ndarray, shape (samples,)
        y_mm : ndarray, shape (lines,)

        Raises
        ------
        ValueError if spatial calibration is not set.
        """
        if not self.has_spatial_calibration():
            raise ValueError(
                "Spatial calibration not set. "
                "Set pixel_size_x_mm and pixel_size_y_mm first."
            )

        x_mm = np.arange(self.samples) * self.pixel_size_x_mm
        y_mm = np.arange(self.lines) * self.pixel_size_y_mm

        return x_mm, y_mm

    def set_spatial_calibration(self, pixel_size_x_mm, pixel_size_y_mm):
        """
        Set spatial calibration explicitly.

        Parameters
        ----------
        pixel_size_x_mm : float
            mm per sample (sensor direction)
        pixel_size_y_mm : float
            mm per line (scan direction)
        """
        self.pixel_size_x_mm = float(pixel_size_x_mm)
        self.pixel_size_y_mm = float(pixel_size_y_mm)
