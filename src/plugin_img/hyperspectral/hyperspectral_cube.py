import math

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ENVI_DTYPE_MAP = {
    '12': np.uint16,
    '4': np.float32,
    '5': np.float64,
    '2': np.int16,
}


def read_envi_hdr(path):
    """
    Read an ENVI .hdr file into a dictionary.

    Parameters
    ----------
    path : str
        Path to the .hdr file

    Returns
    -------
    dict
        Header metadata (keys are lowercase)
    """
    metadata = {}

    with open(path) as f:
        lines = f.readlines()

    key = None
    collecting = False
    buffer = []

    for line in lines:
        line = line.strip()

        if not line or line.upper() == 'ENVI':
            continue

        if collecting:
            buffer.append(line)
            if '}' in line:
                metadata[key] = ' '.join(buffer)
                collecting = False
                buffer = []
            continue

        if '=' in line:
            k, v = map(str.strip, line.split('=', 1))
            k = k.lower()

            if v.startswith('{') and not v.endswith('}'):
                key = k
                collecting = True
                buffer.append(v)
            else:
                metadata[k] = v

    return metadata


def read_bil(path, lines, samples, bands, dtype):
    """
    Read a BIL (Band Interleaved by Line) file.

    Parameters
    ----------
    path : str
        Path to .bil file
    lines, samples, bands : int
        Cube dimensions
    dtype : numpy dtype
        Data type from ENVI header

    Returns
    -------
    ndarray
        Data array with shape (lines, samples, bands)
    """
    data = np.fromfile(path, dtype=dtype)

    expected = lines * samples * bands
    if data.size != expected:
        raise ValueError(f'Size mismatch: expected {expected}, got {data.size}')

    # BIL order → (lines, bands, samples)
    data = data.reshape(lines, bands, samples)

    # Reorder → (lines, samples, bands)
    return np.transpose(data, (0, 2, 1))


class HyperspectralCube:
    """
    Container and analysis tools for hyperspectral datacubes.
    """

    def __init__(self, data, wavelengths, metadata=None):
        """
        Parameters
        ----------
        data : ndarray
            Shape (lines, samples, bands)
        wavelengths : ndarray
            Shape (bands,)
        metadata : dict, optional
            ENVI header metadata
        """
        self.data = data
        self.wavelengths = wavelengths
        self.metadata = metadata or {}

    # ------------------
    # Basic accessors
    # ------------------

    def band_index(self, wavelength_nm):
        """Return band index closest to a wavelength."""
        return int(np.abs(self.wavelengths - wavelength_nm).argmin())

    def band(self, wavelength_nm):
        """Return spatial image at given wavelength."""
        idx = self.band_index(wavelength_nm)
        return self.data[:, :, idx]

    def lines(self):
        """Number of scan lines (spatial Y)."""
        return self.data.shape[0]

    def spectrum(self, line, sample):
        """Return spectrum at a single pixel."""
        return self.data[line, sample, :]

    def mean_spectrum(self, roi=None):
        """
        Compute mean spectrum.

        roi : tuple or None
            (line_start, line_end, sample_start, sample_end)
        """
        if roi is None:
            return self.data.mean(axis=(0, 1))

        l1, l2, s1, s2 = roi
        return self.data[l1:l2, s1:s2, :].mean(axis=(0, 1))

    def plot_rgb(self, r_nm, g_nm, b_nm, title=None):
        """
        Interactive RGB composite with channel toggle buttons.
        """
        r = self.band_index(r_nm)
        g = self.band_index(g_nm)
        b = self.band_index(b_nm)

        rgb = np.stack(
            [
                self.data[:, :, r],
                self.data[:, :, g],
                self.data[:, :, b],
            ],
            axis=-1,
        ).astype(float)

        rgb /= rgb.max() + 1e-9
        rgb_uint8 = (255 * rgb).astype(np.uint8)

        fig = go.Figure()

        # RGB image
        fig.add_trace(go.Image(z=rgb_uint8, name='RGB'))

        # Individual channels (for toggling)
        fig.add_trace(go.Image(z=rgb_uint8[:, :, [0]], name='R', visible=False))
        fig.add_trace(go.Image(z=rgb_uint8[:, :, [1]], name='G', visible=False))
        fig.add_trace(go.Image(z=rgb_uint8[:, :, [2]], name='B', visible=False))

        fig.update_layout(
            title=title or f'RGB ({r_nm}/{g_nm}/{b_nm} nm)',
            xaxis_title='Samples',
            yaxis_title='Lines',
            yaxis_autorange='reversed',
            updatemenus=[
                dict(
                    type='buttons',
                    direction='right',
                    buttons=[
                        dict(
                            label='RGB',
                            method='update',
                            args=[{'visible': [True, False, False, False]}],
                        ),
                        dict(
                            label='R',
                            method='update',
                            args=[{'visible': [False, True, False, False]}],
                        ),
                        dict(
                            label='G',
                            method='update',
                            args=[{'visible': [False, False, True, False]}],
                        ),
                        dict(
                            label='B',
                            method='update',
                            args=[{'visible': [False, False, False, True]}],
                        ),
                    ],
                    pad={'r': 10, 't': 10},
                    showactive=True,
                )
            ],
        )

        return fig

    def _add_grid_lines(self, fig, n_rows, n_cols, lines, samples):
        row_edges = np.linspace(0, lines, n_rows + 1)
        col_edges = np.linspace(0, samples, n_cols + 1)

        for r in row_edges:
            fig.add_shape(
                type='line',
                x0=0,
                x1=samples,
                y0=r,
                y1=r,
                line=dict(color='cyan', width=1),
            )

        for c in col_edges:
            fig.add_shape(
                type='line',
                x0=c,
                x1=c,
                y0=0,
                y1=lines,
                line=dict(color='cyan', width=1),
            )

    def plot_wavelength_images(
        self, wavelength_list, max_cols=3, normalize=True, title='Wavelength images'
    ):
        """
        Interactive grid of single-band images.
        """
        n = len(wavelength_list)
        cols = min(max_cols, n)
        rows = math.ceil(n / cols)

        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=[f'{wl:.1f} nm' for wl in wavelength_list],
        )

        for i, wl in enumerate(wavelength_list):
            r = i // cols + 1
            c = i % cols + 1

            img = self.band(wl).astype(float)
            if normalize:
                img /= img.max() + 1e-9

            fig.add_trace(
                go.Heatmap(z=img, colorscale='Gray', showscale=False), row=r, col=c
            )

        fig.update_layout(title=title, height=300 * rows, width=350 * cols)

        fig.update_yaxes(autorange='reversed')

        return fig

    def plot_grid_mean_spectra(
        self,
        n_rows,
        n_cols,
        image_band_nm=None,
        normalize=True,
        title='Grid mean spectra',
    ):
        """
        Interactive spatial grid + mean spectra per grid cell.
        """
        lines, samples, _ = self.data.shape

        # Background image
        if image_band_nm is None:
            image = self.data.mean(axis=2)
            img_title = 'Mean intensity'
        else:
            image = self.band(image_band_nm)
            img_title = f'{image_band_nm:.1f} nm'

        fig = make_subplots(
            rows=1,
            cols=2,
            column_widths=[0.45, 0.55],
            subplot_titles=(img_title, 'Mean spectra'),
        )

        # Image
        fig.add_trace(
            go.Heatmap(z=image, colorscale='Gray', showscale=False), row=1, col=1
        )

        row_edges = np.linspace(0, lines, n_rows + 1)
        col_edges = np.linspace(0, samples, n_cols + 1)

        cell = 1
        for i in range(n_rows):
            for j in range(n_cols):
                rs = slice(int(row_edges[i]), int(row_edges[i + 1]))
                cs = slice(int(col_edges[j]), int(col_edges[j + 1]))

                spectrum = self.data[rs, cs, :].mean(axis=(0, 1))
                if normalize:
                    spectrum /= spectrum.max() + 1e-9

                fig.add_trace(
                    go.Scatter(
                        x=self.wavelengths,
                        y=spectrum,
                        mode='lines',
                        name=f'Cell {cell}',
                    ),
                    row=1,
                    col=2,
                )

                # Grid cell label
                fig.add_annotation(
                    x=0.5 * (col_edges[j] + col_edges[j + 1]),
                    y=0.5 * (row_edges[i] + row_edges[i + 1]),
                    text=str(cell),
                    showarrow=False,
                    font=dict(color='yellow'),
                    bgcolor='black',
                    opacity=0.6,
                    row=1,
                    col=1,
                )

                cell += 1

        fig.update_yaxes(autorange='reversed', row=1, col=1)

        self._add_grid_lines(fig, n_rows, n_cols, lines, samples)
        fig.update_layout(
            title=title,
            xaxis2_title='Wavelength (nm)',
            yaxis2_title='Normalized intensity' if normalize else 'Intensity',
        )

        return fig

    def plot_3d_spectral_slice(
        self, line_index=None, normalize=False, title='3D Spectral Slice'
    ):
        """
        3D plot: spatial X × wavelength × intensity for one scan line.
        """
        if line_index is None:
            line_index = self.lines // 2

        slice_data = self.data[line_index, :, :]

        if normalize:
            slice_data = slice_data / (slice_data.max() + 1e-9)

        fig = go.Figure(
            data=[
                go.Surface(
                    z=slice_data.T,
                    x=np.arange(self.samples),
                    y=self.wavelengths,
                    colorscale='Viridis',
                )
            ]
        )

        fig.update_layout(
            title=title + f' (line {line_index})',
            scene=dict(
                xaxis_title='Spatial X (samples)',
                yaxis_title='Wavelength (nm)',
                zaxis_title='Normalized intensity',
            ),
            height=600,
        )

        return fig


if __name__ == '__main__':
    hdr = read_envi_hdr('cube1.bil.hdr')

    dtype = ENVI_DTYPE_MAP[hdr['data type']]

    wavelengths = np.array([float(w) for w in hdr['wavelength'].strip('{}').split(',')])

    cube_data = read_bil(
        'cube1.bil',
        lines=int(hdr['lines']),
        samples=int(hdr['samples']),
        bands=int(hdr['bands']),
        dtype=dtype,
    )

    cube = HyperspectralCube(cube_data, wavelengths, hdr)

    fig = cube.plot_rgb(650, 550, 450)
    fig.show()
    fig = cube.plot_wavelength_images(
        [350, 450, 550, 650, 750, 850, 950, 1050], max_cols=3
    )
    fig.show()
    fig = cube.plot_grid_mean_spectra(3, 3, normalize=False)
    fig.show()
    fig = cube.plot_grid_mean_spectra(6, 6, normalize=False)
    fig.show()
    fig = cube.plot_grid_mean_spectra(9, 9, normalize=False)
    fig.show()
    fig = cube.plot_3d_spectral_slice()
    fig.show()
