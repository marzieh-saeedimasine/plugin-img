from typing import TYPE_CHECKING

from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.annotations import ELNAnnotation, SectionProperties
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.metainfo import Package, Quantity, Section, SubSection

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

import plugin_img.hyperspectral.plotting_utils as plu 

m_package = Package(
    name='hyperspectral_image_plugin',
    description='Schema for hyperspectral image datasets.',
)


# ============================================================
# Acquisition Metadata
# ============================================================


class AcquisitionMetadata(ArchiveSection):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'interleave',
                    'data_type',
                    'sample_binning',
                    'spectral_binning',
                    'line_binning',
                    'shutter',
                    'gain',
                    'framerate',
                    'temperature',
                    'imager_serial_number',
                    'rotation',
                    'pixel_size',
                    'byte_order',
                    'header_offset',
                    'flip_radiometric_calibration',
                    'reflection_scale_factor',
                    'wavelength_unit',
                    'label',
                    'history',
                ]
            )
        )
    )

    interleave = Quantity(
        type=str,
        description='BIL, BSQ or BIP',
        a_eln={'choices': ['bil', 'bsq', 'bip', 'BIL', 'BSQ', 'BIP']},
    )

    data_type = Quantity(
        type=str,
        description='Data type stored in cube',
        a_eln={'component': 'StringEditQuantity'},
    )

    sample_binning = Quantity(
        type=int,
        description='Binning factor in the sample dimension.',
        a_eln={'component': 'NumberEditQuantity'},
    )
    spectral_binning = Quantity(
        type=int,
        description='Binning factor in the spectral dimension.',
        a_eln={'component': 'NumberEditQuantity'},
    )
    line_binning = Quantity(
        type=int,
        description='Binning factor in the line dimension.',
        a_eln={'component': 'NumberEditQuantity'},
    )

    shutter = Quantity(
        type=float,
        description='Shutter value used during acquisition.',
        a_eln={'component': 'NumberEditQuantity'},
    )

    gain = Quantity(
        type=float,
        description='Gain setting used during acquisition.',
        a_eln={'component': 'NumberEditQuantity'},
    )

    framerate = Quantity(
        type=float,
        description='Frame rate of the hyperspectral image.',
        a_eln={'component': 'NumberEditQuantity'},
    )

    temperature = Quantity(
        type=float,
        description='Temperature during acquisition.',
        a_eln={'component': 'NumberEditQuantity'},
    )
    imager_serial_number = Quantity(
        type=str,
        description='Serial number of the imager.',
        a_eln={'component': 'StringEditQuantity'},
    )

    rotation = Quantity(
        type=str,
        description='Rotation metadata of the hyperspectral image.',
        a_eln={'component': 'StringEditQuantity'},
    )

    pixel_size = Quantity(
        type=float,
        description='Size of each pixel in the hyperspectral image.',
        a_eln={'component': 'NumberEditQuantity'},
    )
    byte_order = Quantity(
        type=str,
        description='Byte order of the data.',
        a_eln={'component': 'StringEditQuantity'},
    )

    header_offset = Quantity(
        type=int,
        description='Offset of the header in the data file.',
        a_eln={'component': 'NumberEditQuantity'},
    )

    flip_radiometric_calibration = Quantity(
        type=bool,
        description='Whether to flip the radiometric calibration data.',
        a_eln={'component': 'BoolEditQuantity'},
    )

    reflection_scale_factor = Quantity(
        type=float,
        description='Scale factor for reflection data.',
        a_eln={'component': 'NumberEditQuantity'},
    )
    wavelength_unit = Quantity(
        type=str,
        description='Unit for the wavelength values.',
        a_eln={'component': 'StringEditQuantity'},
    )
    label = Quantity(
        type=str,
        description='Label for the hyperspectral image.',
        a_eln={'component': 'StringEditQuantity'},
    )
    history = Quantity(
        type=str,
        description='History of the hyperspectral image.',
        a_eln={'component': 'StringEditQuantity'},
    )


# ============================================================
# Cube Metadata
# ============================================================


class CubeMetadata(ArchiveSection):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'lines',
                    'samples',
                    'bands',
                    'wavelength',
                    'wavelength_min_nm',
                    'wavelength_max_nm',
                    'interleave',
                    'data_type',
                ]
            )
        )
    )

    lines = Quantity(
        type=int,
        description='Number of spatial scan lines.',
        a_eln={'component': 'NumberEditQuantity'},
    )

    samples = Quantity(
        type=int,
        description='Number of spatial samples.',
        a_eln={'component': 'NumberEditQuantity'},
    )

    bands = Quantity(
        type=int,
        description='Number of spectral bands.',
        a_eln={'component': 'NumberEditQuantity'},
    )

    wavelength = Quantity(
        type=float,
        shape=['*'],
        unit='nanometer',
        description='Wavelength values corresponding to each spectral band.',
    )

    wavelength_min_nm = Quantity(
        type=float,
        unit='nanometer',
        description='Minimum wavelength.',
        a_eln={'component': 'NumberEditQuantity'},
    )

    wavelength_max_nm = Quantity(
        type=float,
        unit='nanometer',
        description='Maximum wavelength.',
        a_eln={'component': 'NumberEditQuantity'},
    )

    interleave = Quantity(
        type=str,
        description='BIL, BSQ or BIP.',
        a_eln={'choices': ['bil', 'bsq', 'bip', 'BIL', 'BSQ', 'BIP']},
    )

    data_type = Quantity(
        type=str,
        description='Underlying storage datatype.',
        a_eln={'component': 'StringEditQuantity'},
    )


# ============================================================
# Raw Data Files
# ============================================================


class HyperspectralRawData(ArchiveSection):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'hdr_file',
                    'bil_file',
                    'cube_npy',
                    'rgb_preview',
                ]
            )
        )
    )

    hdr_file = Quantity(
        type=str,
        a_eln={'component': 'FileEditQuantity'},
    )

    bil_file = Quantity(
        type=str,
        a_eln={'component': 'FileEditQuantity'},
    )

    cube_npy = Quantity(
        type=str,
        a_eln={'component': 'FileEditQuantity'},
    )

    rgb_preview = Quantity(
        type=str,
        a_eln={'component': 'FileEditQuantity'},
    )


# ============================================================
# Visualization Section
# ============================================================
class HyperspectralAnalysis(
    PlotSection,
    ArchiveSection,
):
   
    def normalize(self, archive: "EntryArchive", logger: "BoundLogger") -> None:

        super().normalize(archive, logger)
        try:
            measurement = self.m_parent

            if measurement is None or measurement.raw_data is None:
                return

            cube_path = archive.m_context.raw_file(str(measurement.raw_data.cube_npy))

            wavelength_path = archive.m_context.raw_file(
                str(measurement.raw_data.hdr_file)
            )

            self.create_analysis_figures(
                cube_path,
                wavelength_path,
                logger,
            )
        
        except Exception as exc:
            logger.warning(
                'Failed to generate hyperspectral figures: %s',
                exc,
            )

    def create_analysis_figures(
        self,
        cube_path,
        hdr_path,
        logger=None,
    ):
        analysis_figures = []
    
        peak_fig = plu.create_peak_wavelength_map(
            cube_path,
            hdr_path,
            logger,
        )
        if peak_fig:
            analysis_figures.append(peak_fig)
    
        pca_rgb_fig = plu.create_pca_rgb_plot(
            cube_path,
            logger,
        )

        if pca_rgb_fig:
            analysis_figures.append(pca_rgb_fig)

        pc_figs = plu.create_pca_component_maps(
            cube_path,
            logger,
        )

        if pc_figs:
            analysis_figures.extend(pc_figs)

        loading_fig = plu.create_pca_loading_plot(
            cube_path,
            hdr_path,
            logger,
        )

        if loading_fig:
            analysis_figures.append(loading_fig)

        variance_fig = plu.create_spectral_variance_map(
            cube_path,
            logger,
        )

        if variance_fig:
            analysis_figures.append(variance_fig)

        

        peak_surface_fig = plu.create_3d_peak_wavelength_surface(
            cube_path,
            hdr_path,
            logger,
        )
        if peak_surface_fig:
            analysis_figures.append(peak_surface_fig)

        # Set overview figures (shown in dataset overview)
        self.figures = analysis_figures
        
                
    


class HyperspectralVisualization(
    PlotSection,
    ArchiveSection,
):
    def normalize(self, archive, logger):

        super().normalize(archive, logger)

        try:
            measurement = self.m_parent

            if measurement is None or measurement.raw_data is None:
                return

            cube_path = archive.m_context.raw_file(str(measurement.raw_data.cube_npy))

            wavelength_path = archive.m_context.raw_file(
                str(measurement.raw_data.hdr_file)
            )

            self.create_plots(
                cube_path,
                wavelength_path,
                logger,
            )

            # Immediately attach analysis figures into the parent dataset so
            # they are visible even if the dataset-level normalizer is not
            # executed (some workflows may skip it). Merge with existing
            # figures rather than overwriting.
            #try:
            #    analysis_figs = getattr(self, '_analysis_figures', None)
            #    if analysis_figs:
            #        dataset = getattr(measurement, 'm_parent', None)
            #        if dataset is not None:
            #            if dataset.hyperspectral_analysis is None:
            #                dataset.hyperspectral_analysis = HyperspectralAnalysis()
#
            #            existing = getattr(dataset.hyperspectral_analysis, 'figures', None)
            #            if existing:
            #                merged = []
            #                merged.extend(existing if isinstance(existing, list) else [existing])
            #                merged.extend(analysis_figs if isinstance(analysis_figs, list) else [analysis_figs])
            #                dataset.hyperspectral_analysis.figures = merged
            #            else:
            #                dataset.hyperspectral_analysis.figures = analysis_figs
            #except Exception:
            #    logger.debug('Failed to attach analysis figures from visualization to dataset.')

        except Exception as exc:
            logger.warning(
                'Failed to generate hyperspectral figures: %s',
                exc,
            )

    # ============================================================
    # Utility functions for visualization
    # ============================================================
    def create_plots(
        self,
        cube_path,
        hdr_path,
        logger=None,
    ):

        figures = []

        overview_figues = []

        analysis_figures = []

        mean_fig = self.create_mean_spectrum_plot(
            cube_path,
            hdr_path,
            logger,
        )

        if mean_fig:
            analysis_figures.append(mean_fig)

        intensity_fig = self.create_integrated_intensity_plot(
            cube_path,
            logger,
        )

        if intensity_fig:
            overview_figues.append(intensity_fig)

        peak_fig = self.create_peak_wavelength_map(
            cube_path,
            hdr_path,
            logger,
        )

        if peak_fig:
            analysis_figures.append(peak_fig)

        quadrant_fig = self.create_quadrant_spectra_plot(
            cube_path,
            hdr_path,
            logger,
        )

        if quadrant_fig:
            overview_figues.append(quadrant_fig)
        
        pca_rgb_fig = self.create_pca_rgb_plot(
            cube_path,
            logger,
        )

        if pca_rgb_fig:
            analysis_figures.append(pca_rgb_fig)

        pc_figs = self.create_pca_component_maps(
            cube_path,
            logger,
        )

        if pc_figs:
            analysis_figures.extend(pc_figs)

        loading_fig = self.create_pca_loading_plot(
            cube_path,
            hdr_path,
            logger,
        )

        if loading_fig:
            analysis_figures.append(loading_fig)

        variance_fig = self.create_spectral_variance_map(
            cube_path,
            logger,
        )

        if variance_fig:
            analysis_figures.append(variance_fig)

        # slider_fig = self.create_wavelength_slider_plot(
        #    cube_path,
        #    hdr_path,
        #    logger,
        # )

        # if slider_fig:
        #    figures.append(
        #    slider_fig
        # )
        surface_fig = self.create_3d_integrated_surface(
            cube_path,
            logger,
        )

        if surface_fig:
            overview_figues.append(surface_fig)

        peak_surface_fig = self.create_3d_peak_wavelength_surface(
            cube_path,
            hdr_path,
            logger,
        )
        if peak_surface_fig:
            analysis_figures.append(peak_surface_fig)

        # Set overview figures (shown in dataset overview)
        self.figures = overview_figues
        self._analysis_figures = analysis_figures  # store as private attribute to avoid clashing with public `figures` property

        # Preserve analysis figures on the visualization object so the
        # dataset-level normalizer can attach them into the
        # `hyperspectral_analysis` subsection.
        # store as a private attribute to avoid clashing with the public
        # `figures` property used for overview.
        setattr(self, "_analysis_figures", analysis_figures)

        # Log counts and attempt an immediate attach into the parent
        # dataset so the GUI sees analysis figures even if dataset
        # normalization isn't executed later.
        try:
            if logger:
                logger.debug(
                    'HyperspectralVisualization created %d overview and %d analysis figures',
                    len(overview_figues),
                    len(analysis_figures),
                )

            # Attach to parent dataset (measurement -> dataset) defensively
            measurement = getattr(self, 'm_parent', None)
            if measurement is not None:
                dataset = getattr(measurement, 'm_parent', None)
                if dataset is not None and analysis_figures:
                    if getattr(dataset, 'hyperspectral_analysis', None) is None:
                        dataset.hyperspectral_analysis = HyperspectralAnalysis()

                    existing = getattr(dataset.hyperspectral_analysis, 'figures', None)
                    if existing:
                        merged = []
                        merged.extend(existing if isinstance(existing, list) else [existing])
                        merged.extend(analysis_figures if isinstance(analysis_figures, list) else [analysis_figures])
                        dataset.hyperspectral_analysis.figures = merged
                    else:
                        dataset.hyperspectral_analysis.figures = analysis_figures
        except Exception:
            if logger:
                logger.debug('Failed to attach analysis figures from create_plots to dataset.')

        

    def create_mean_spectrum_plot(
        self,
        cube_path,
        hdr_path,
        logger=None,
    ):

        try:
            import numpy as np
            import plotly.graph_objects as go

            from plugin_img.hyperspectral.hyperspectral_cube import (
                read_envi_hdr,
            )

            cube = np.load(
                str(cube_path),
                mmap_mode='r',
            )

            hdr = read_envi_hdr(str(hdr_path))

            # Be tolerant to different header formats: some readers
            # provide a list, others a string like "{400.0,401.0,...}".
            raw_wl = hdr.get('wavelength', None)
            if isinstance(raw_wl, (list, tuple)):
                wavelengths = np.array(raw_wl, dtype=float)
            elif isinstance(raw_wl, str):
                wavelengths = np.array(
                    [float(v) for v in raw_wl.strip('{} \n').split(',')]
                )
            else:
                # fallback: use band indices if no wavelength info
                wavelengths = np.arange(int(hdr.get('bands', 0)), dtype=float)

            mean_spectrum = cube.mean(axis=(0, 1))

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=wavelengths,
                    y=mean_spectrum,
                    mode='lines',
                    name='Mean Spectrum',
                )
            )

            fig.update_layout(
                title='Mean Spectrum',
                template='plotly_white',
                xaxis_title='Wavelength (nm)',
                yaxis_title='Intensity',
                width=850,
                height=650,
            )

            return PlotlyFigure(
                label='Mean Spectrum',
                figure=fig.to_plotly_json(),
            )

        except Exception as exc:
            if logger:
                logger.warning(
                    'Could not create mean spectrum: %s',
                    exc,
                )

            return None

    def create_integrated_intensity_plot(
        self,
        cube_path,
        logger=None,
    ):

        try:
            import numpy as np
            import plotly.graph_objects as go

            cube = np.load(
                str(cube_path),
                mmap_mode='r',
            )

            integrated = cube.sum(axis=2)

            max_display_size = 1000

            scale = max(
                1,
                int(np.ceil(integrated.shape[0] / max_display_size)),
                int(np.ceil(integrated.shape[1] / max_display_size)),
            )

            integrated = integrated[
                ::scale,
                ::scale,
            ]

            fig = go.Figure()

            fig.add_trace(
                go.Heatmap(
                    z=integrated,
                    colorbar=dict(title='Intensity'),
                )
            )

            fig.update_layout(
                title='Integrated Intensity Map',
                template='plotly_white',
                width=850,
                height=750,
                xaxis_title='Pixel X',
                yaxis_title='Pixel Y',
            )

            return PlotlyFigure(
                label='Integrated Intensity',
                figure=fig.to_plotly_json(),
            )

        except Exception as exc:
            if logger:
                logger.warning(
                    'Could not create intensity map: %s',
                    exc,
                )

            return None

    def create_peak_wavelength_map(
        self,
        cube_path,
        hdr_path,
        logger=None,
    ):

        try:
            import numpy as np
            import plotly.graph_objects as go

            from plugin_img.hyperspectral.hyperspectral_cube import (
                read_envi_hdr,
            )

            cube = np.load(
                str(cube_path),
                mmap_mode='r',
            )

            hdr = read_envi_hdr(str(hdr_path))

            raw_wl = hdr.get('wavelength', None)

            if isinstance(raw_wl, (list, tuple)):
                wavelengths = np.array(
                    raw_wl,
                    dtype=float,
                )

            elif isinstance(raw_wl, str):
                wavelengths = np.array(
                    [float(v) for v in raw_wl.strip('{} \n').split(',')]
                )

            else:
                wavelengths = np.arange(
                    int(hdr.get('bands', cube.shape[2])),
                    dtype=float,
                )

            # -----------------------------------
            # Peak wavelength calculation
            # -----------------------------------

            peak_idx = np.argmax(
                cube,
                axis=2,
            )

            peak_wavelength = wavelengths[peak_idx]

            # -----------------------------------
            # Downsample for display
            # -----------------------------------

            max_display_size = 1000

            scale = max(
                1,
                int(np.ceil(peak_wavelength.shape[0] / max_display_size)),
                int(np.ceil(peak_wavelength.shape[1] / max_display_size)),
            )

            peak_wavelength = peak_wavelength[
                ::scale,
                ::scale,
            ]

            # -----------------------------------
            # Plot
            # -----------------------------------

            fig = go.Figure()

            fig.add_trace(
                go.Heatmap(
                    z=peak_wavelength,
                    colorscale='Turbo',
                    colorbar=dict(title='Peak λ (nm)'),
                )
            )

            fig.update_layout(
                title='Peak Wavelength Map',
                template='plotly_white',
                width=850,
                height=750,
                xaxis_title='Pixel X',
                yaxis_title='Pixel Y',
            )

            return PlotlyFigure(
                label='Peak Wavelength Map',
                figure=fig.to_plotly_json(),
            )

        except Exception as exc:
            if logger:
                logger.warning(
                    'Could not create peak wavelength map: %s',
                    exc,
                )

            return None

    def create_quadrant_spectra_plot(
        self,
        cube_path,
        hdr_path,
        logger=None,
    ):

        try:
            import numpy as np
            import plotly.graph_objects as go

            from plugin_img.hyperspectral.hyperspectral_cube import (
                read_envi_hdr,
            )

            cube = np.load(
                str(cube_path),
                mmap_mode='r',
            )

            hdr = read_envi_hdr(str(hdr_path))

            raw_wl = hdr.get(
                'wavelength',
                None,
            )

            if isinstance(
                raw_wl,
                (list, tuple),
            ):
                wavelengths = np.array(
                    raw_wl,
                    dtype=float,
                )

            elif isinstance(
                raw_wl,
                str,
            ):
                wavelengths = np.array(
                    [float(v) for v in raw_wl.strip('{} \n').split(',')]
                )

            else:
                wavelengths = np.arange(
                    cube.shape[2],
                    dtype=float,
                )

            # -----------------------------------
            # Split cube into quadrants
            # -----------------------------------

            ny, nx, _ = cube.shape

            ymid = ny // 2
            xmid = nx // 2

            q1 = cube[:ymid, :xmid, :]

            q2 = cube[:ymid, xmid:, :]

            q3 = cube[ymid:, :xmid, :]

            q4 = cube[ymid:, xmid:, :]

            # -----------------------------------
            # Mean spectra
            # -----------------------------------

            q1_spec = q1.mean(axis=(0, 1))

            q2_spec = q2.mean(axis=(0, 1))

            q3_spec = q3.mean(axis=(0, 1))

            q4_spec = q4.mean(axis=(0, 1))

            # -----------------------------------
            # Plot
            # -----------------------------------

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=wavelengths,
                    y=q1_spec,
                    mode='lines',
                    name='Q1',
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=wavelengths,
                    y=q2_spec,
                    mode='lines',
                    name='Q2',
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=wavelengths,
                    y=q3_spec,
                    mode='lines',
                    name='Q3',
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=wavelengths,
                    y=q4_spec,
                    mode='lines',
                    name='Q4',
                )
            )

            fig.update_layout(
                title='Regional Mean Spectra',
                template='plotly_white',
                width=900,
                height=650,
                xaxis_title='Wavelength (nm)',
                yaxis_title='Intensity',
                legend_title='Region',
            )

            return PlotlyFigure(
                label='2×2 Regional Spectra',
                figure=fig.to_plotly_json(),
            )

        except Exception as exc:
            if logger:
                logger.warning(
                    'Could not create quadrant spectra: %s',
                    exc,
                )

            return None

    def create_pca_rgb_plot(
        self,
        cube_path,
        logger=None,
    ):

        try:
            import numpy as np
            import plotly.graph_objects as go
            from sklearn.decomposition import PCA

            cube = np.load(
                str(cube_path),
                mmap_mode='r',
            )

            # ----------------------------------
            # Downsample
            # ----------------------------------

            cube_small = cube[::4, ::4, :]

            ny, nx, nbands = cube_small.shape

            # ----------------------------------
            # Reshape for PCA
            # ----------------------------------

            pixels = cube_small.reshape(
                -1,
                nbands,
            )

            # ----------------------------------
            # PCA
            # ----------------------------------

            pca = PCA(
                n_components=3,
                random_state=0,
            )

            scores = pca.fit_transform(pixels)

            # ----------------------------------
            # Normalize
            # ----------------------------------

            rgb = np.zeros(
                (
                    scores.shape[0],
                    3,
                ),
                dtype=float,
            )

            for i in range(3):
                component = scores[:, i]

                component = (component - component.min()) / (
                    component.max() - component.min() + 1e-12
                )

                rgb[:, i] = component

            rgb = rgb.reshape(
                ny,
                nx,
                3,
            )

            rgb = (rgb * 255).astype(np.uint8)

            # ----------------------------------
            # Plot
            # ----------------------------------

            fig = go.Figure()

            fig.add_trace(go.Image(z=rgb))

            explained = pca.explained_variance_ratio_ * 100

            fig.update_layout(
                title=(
                    'PCA RGB Map '
                    f'(PC1={explained[0]:.1f}% '
                    f'PC2={explained[1]:.1f}% '
                    f'PC3={explained[2]:.1f}%)'
                ),
                template='plotly_white',
                width=900,
                height=750,
            )

            return PlotlyFigure(
                label='PCA RGB Map',
                figure=fig.to_plotly_json(),
            )

        except Exception as exc:
            if logger:
                logger.warning(
                    'Could not create PCA RGB map: %s',
                    exc,
                )

        return None

    def create_pca_component_maps(
        self,
        cube_path,
        logger=None,
    ):

        try:
            import numpy as np
            import plotly.graph_objects as go
            from sklearn.decomposition import PCA

            cube = np.load(
                str(cube_path),
                mmap_mode='r',
            )

            cube_small = cube[::4, ::4, :]

            ny, nx, nbands = cube_small.shape

            pixels = cube_small.reshape(
                -1,
                nbands,
            )

            pca = PCA(
                n_components=3,
                random_state=0,
            )

            scores = pca.fit_transform(pixels)

            explained = pca.explained_variance_ratio_ * 100

            figures = []

            for pc in range(3):
                image = scores[:, pc].reshape(
                    ny,
                    nx,
                )

                fig = go.Figure()

                fig.add_trace(
                    go.Heatmap(
                        z=image,
                        colorscale='RdBu',
                        colorbar=dict(title=f'PC{pc + 1}'),
                    )
                )

                fig.update_layout(
                    title=(
                        f'Principal Component {pc + 1} ({explained[pc]:.1f}% variance)'
                    ),
                    template='plotly_white',
                    width=850,
                    height=750,
                    xaxis_title='Pixel X',
                    yaxis_title='Pixel Y',
                )

                figures.append(
                    PlotlyFigure(
                        label=f'PC{pc + 1} Map',
                        figure=fig.to_plotly_json(),
                    )
                )

            return figures

        except Exception as exc:
            if logger:
                logger.warning(
                    'Could not create PCA maps: %s',
                    exc,
                )

            return []

    def create_pca_loading_plot(
        self,
        cube_path,
        hdr_path,
        logger=None,
    ):

        try:
            import numpy as np
            import plotly.graph_objects as go
            from sklearn.decomposition import PCA

            from plugin_img.hyperspectral.hyperspectral_cube import (
                read_envi_hdr,
            )

            cube = np.load(
                str(cube_path),
                mmap_mode='r',
            )

            hdr = read_envi_hdr(str(hdr_path))

            raw_wl = hdr.get(
                'wavelength',
                None,
            )

            if isinstance(
                raw_wl,
                (list, tuple),
            ):
                wavelengths = np.array(
                    raw_wl,
                    dtype=float,
                )

            elif isinstance(
                raw_wl,
                str,
            ):
                wavelengths = np.array(
                    [float(v) for v in raw_wl.strip('{} \n').split(',')]
                )

            else:
                wavelengths = np.arange(
                    cube.shape[2],
                    dtype=float,
                )

            # ----------------------------------
            # Downsample spatially
            # ----------------------------------

            cube_small = cube[::4, ::4, :]

            ny, nx, nbands = cube_small.shape

            pixels = cube_small.reshape(
                -1,
                nbands,
            )

            pca = PCA(
                n_components=3,
                random_state=0,
            )

            pca.fit(pixels)

            explained = pca.explained_variance_ratio_ * 100

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=wavelengths,
                    y=pca.components_[0],
                    mode='lines',
                    name=f'PC1 ({explained[0]:.1f}%)',
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=wavelengths,
                    y=pca.components_[1],
                    mode='lines',
                    name=f'PC2 ({explained[1]:.1f}%)',
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=wavelengths,
                    y=pca.components_[2],
                    mode='lines',
                    name=f'PC3 ({explained[2]:.1f}%)',
                )
            )

            fig.update_layout(
                title='PCA Loading Spectra',
                template='plotly_white',
                width=900,
                height=650,
                xaxis_title='Wavelength (nm)',
                yaxis_title='Loading Weight',
                legend_title='Component',
            )

            return PlotlyFigure(
                label='PCA Loading Spectra',
                figure=fig.to_plotly_json(),
            )

        except Exception as exc:
            if logger:
                logger.warning(
                    'Could not create PCA loading spectra: %s',
                    exc,
                )

            return None

    def create_wavelength_slider_plot(
        self,
        cube_path,
        hdr_path,
        logger=None,
    ):

        try:
            import numpy as np
            import plotly.graph_objects as go
            from nomad.datamodel.metainfo.plot import PlotlyFigure

            from plugin_img.hyperspectral.hyperspectral_cube import (
                read_envi_hdr,
            )

            cube = np.load(
                str(cube_path),
                mmap_mode='r',
            )

            hdr = read_envi_hdr(str(hdr_path))

            raw_wl = hdr.get('wavelength', None)
            if isinstance(raw_wl, (list, tuple)):
                wavelengths = np.array(raw_wl, dtype=float)
            elif isinstance(raw_wl, str):
                wavelengths = np.array(
                    [float(v) for v in raw_wl.strip('{} \n').split(',')]
                )
            else:
                wavelengths = np.arange(int(hdr.get('bands', 0)), dtype=float)

            # ----------------------------------
            # Spatial downsampling
            # ----------------------------------

            cube = cube[::4, ::4, :]

            # ----------------------------------
            # Spectral downsampling
            # ----------------------------------

            wavelength_step = max(
                1,
                len(wavelengths) // 100,
            )

            cube = cube[
                :,
                :,
                ::wavelength_step,
            ]

            wavelengths = wavelengths[::wavelength_step]

            # ----------------------------------
            # Normalize first image
            # ----------------------------------

            image0 = cube[:, :, 0]

            image0 = (image0 - image0.min()) / (image0.max() - image0.min() + 1e-12)

            fig = go.Figure(
                data=[
                    go.Heatmap(
                        z=image0,
                        colorscale='Viridis',
                        showscale=True,
                    )
                ]
            )

            # ----------------------------------
            # Frames
            # ----------------------------------

            frames = []

            for i in range(len(wavelengths)):
                image = cube[:, :, i]

                image = (image - image.min()) / (image.max() - image.min() + 1e-12)

                frames.append(
                    go.Frame(
                        data=[
                            go.Heatmap(
                                z=image,
                                colorscale='Viridis',
                                showscale=True,
                            )
                        ],
                        name=f'{wavelengths[i]:.1f}',
                    )
                )

            fig.frames = frames

            # ----------------------------------
            # Slider
            # ----------------------------------

            slider_steps = []

            for i, wl in enumerate(wavelengths):
                slider_steps.append(
                    {
                        'args': [
                            [f'{wl:.1f}'],
                            {
                                'frame': {
                                    'duration': 0,
                                    'redraw': True,
                                },
                                'mode': 'immediate',
                            },
                        ],
                        'label': f'{wl:.0f}',
                        'method': 'animate',
                    }
                )

            fig.update_layout(
                title='Hyperspectral Wavelength Explorer',
                width=850,
                height=750,
                template='plotly_white',
                xaxis_title='Pixel X',
                yaxis_title='Pixel Y',
                sliders=[
                    {
                        'active': 0,
                        'currentvalue': {'prefix': 'Wavelength (nm): '},
                        'steps': slider_steps,
                    }
                ],
            )

            return PlotlyFigure(
                label='Wavelength Explorer',
                figure=fig.to_plotly_json(),
            )

        except Exception as exc:
            if logger:
                logger.warning(
                    'Could not create wavelength slider: %s',
                    exc,
                )

            return None

    def create_spectral_variance_map(
        self,
        cube_path,
        logger=None,
    ):

        try:
            import numpy as np
            import plotly.graph_objects as go

            cube = np.load(
                str(cube_path),
                mmap_mode='r',
            )

            # ----------------------------------
            # Spectral variance
            # ----------------------------------

            variance_map = np.std(
                cube,
                axis=2,
            )

            # ----------------------------------
            # Downsample
            # ----------------------------------

            max_display_size = 1000

            scale = max(
                1,
                int(np.ceil(variance_map.shape[0] / max_display_size)),
                int(np.ceil(variance_map.shape[1] / max_display_size)),
            )

            variance_map = variance_map[
                ::scale,
                ::scale,
            ]

            # ----------------------------------
            # Plot
            # ----------------------------------

            fig = go.Figure()

            fig.add_trace(
                go.Heatmap(
                    z=variance_map,
                    colorscale='Inferno',
                    colorbar=dict(title='σ'),
                )
            )

            fig.update_layout(
                title='Spectral Variance Map',
                template='plotly_white',
                width=850,
                height=750,
                xaxis_title='Pixel X',
                yaxis_title='Pixel Y',
            )

            return PlotlyFigure(
                label='Spectral Variance Map',
                figure=fig.to_plotly_json(),
            )

        except Exception as exc:
            if logger:
                logger.warning(
                    'Could not create variance map: %s',
                    exc,
                )

            return None

    def create_3d_integrated_surface(
        self,
        cube_path,
        logger=None,
    ):

        try:
            import numpy as np
            import plotly.graph_objects as go

            cube = np.load(
                str(cube_path),
                mmap_mode='r',
            )

            # ----------------------------------
            # Integrated intensity
            # ----------------------------------

            integrated = np.sum(
                cube,
                axis=2,
            )

            # ----------------------------------
            # Aggressive downsampling
            # ----------------------------------

            max_size = 50

            scale = max(
                1,
                int(np.ceil(integrated.shape[0] / max_size)),
                int(np.ceil(integrated.shape[1] / max_size)),
            )

            integrated = integrated[
                ::scale,
                ::scale,
            ]

            ny, nx = integrated.shape

            x = np.arange(nx)
            y = np.arange(ny)

            # ----------------------------------
            # Robust normalization
            # ----------------------------------

            p1 = np.percentile(
                integrated,
                1,
            )

            p99 = np.percentile(
                integrated,
                99,
            )

            z = np.clip(
                integrated,
                p1,
                p99,
            )

            z = (z - z.min()) / (z.max() - z.min() + 1e-12)

            # ----------------------------------
            # Surface
            # ----------------------------------

            fig = go.Figure()

            fig.add_trace(
                go.Surface(
                    z=z,
                    x=x,
                    y=y,
                    colorscale='Viridis',
                    showscale=True,
                    #smoothing='best',
                    colorbar=dict(title='Normalized Intensity'),
                )
            )

            fig.update_layout(
                title='3D Integrated Intensity Surface',
                template='plotly_white',
                width=1000,
                height=850,
                scene=dict(
                    xaxis_title='Pixel X',
                    yaxis_title='Pixel Y',
                    zaxis_title='Normalized Intensity',
                    camera=dict(
                        eye=dict(
                            x=1.8,
                            y=1.8,
                            z=1.2,
                        )
                    ),
                ),
            )

            return PlotlyFigure(
                label='3D Integrated Surface',
                figure=fig.to_plotly_json(),
            )

        except Exception as exc:
            if logger:
                logger.warning(
                    'Could not create 3D integrated surface: %s',
                    exc,
                )

            return None

    def create_3d_peak_wavelength_surface(
        self,
        cube_path,
        hdr_path,
        logger=None,
    ):

        try:
            import numpy as np
            import plotly.graph_objects as go

            from plugin_img.hyperspectral.hyperspectral_cube import (
                read_envi_hdr,
            )

            cube = np.load(
                str(cube_path),
                mmap_mode='r',
            )

            hdr = read_envi_hdr(str(hdr_path))

            raw_wl = hdr.get(
                'wavelength',
                None,
            )

            if isinstance(
                raw_wl,
                (list, tuple),
            ):
                wavelengths = np.array(
                    raw_wl,
                    dtype=float,
                )

            elif isinstance(
                raw_wl,
                str,
            ):
                wavelengths = np.array(
                    [float(v) for v in raw_wl.strip('{} \n').split(',')]
                )

            else:
                wavelengths = np.arange(
                    cube.shape[2],
                    dtype=float,
                )

            # ----------------------------------
            # Peak wavelength map
            # ----------------------------------

            peak_idx = np.argmax(
                cube,
                axis=2,
            )

            peak_wavelength = wavelengths[peak_idx]

            # ----------------------------------
            # Downsample
            # ----------------------------------

            max_size = 150

            scale = max(
                1,
                int(np.ceil(peak_wavelength.shape[0] / max_size)),
                int(np.ceil(peak_wavelength.shape[1] / max_size)),
            )

            peak_wavelength = peak_wavelength[
                ::scale,
                ::scale,
            ]

            ny, nx = peak_wavelength.shape

            x = np.arange(nx)
            y = np.arange(ny)

            # ----------------------------------
            # Surface
            # ----------------------------------

            fig = go.Figure()

            fig.add_trace(
                go.Surface(
                    z=peak_wavelength,
                    x=x,
                    y=y,
                    colorscale='Turbo',
                    showscale=True,
                    colorbar=dict(title='λ (nm)'),
                )
            )

            fig.update_layout(
                title='3D Peak Wavelength Surface',
                template='plotly_white',
                width=1000,
                height=850,
                scene=dict(
                    xaxis_title='Pixel X',
                    yaxis_title='Pixel Y',
                    zaxis_title='Peak Wavelength (nm)',
                    camera=dict(
                        eye=dict(
                            x=1.8,
                            y=1.8,
                            z=1.2,
                        )
                    ),
                ),
            )

            return PlotlyFigure(
                label='3D Peak Wavelength Surface',
                figure=fig.to_plotly_json(),
            )

        except Exception as exc:
            if logger:
                logger.warning(
                    'Could not create 3D peak wavelength surface: %s',
                    exc,
                )

            return None


# ============================================================
# Measurement
# ============================================================


class HyperspectralMeasurement(ArchiveSection):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'acquisition_metadata',
                    'cube_metadata',
                    'raw_data',
                    'visualization',
                    'label',
                    'history',
                ]
            )
        )
    )

    acquisition_metadata = SubSection(
        section_def=AcquisitionMetadata,
    )

    cube_metadata = SubSection(
        section_def=CubeMetadata,
    )

    raw_data = SubSection(
        section_def=HyperspectralRawData,
    )

    visualization = SubSection(
        section_def=HyperspectralAnalysis,
    )

    label = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )

    history = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )

    def normalize(
        self,
        archive,
        logger,
    ):

        super().normalize(
            archive,
            logger,
        )

        if not self.visualization:
            return

        visualization = self.visualization


# ============================================================
# Dataset
# ============================================================

class HyperspectralDataset(PlotSection, EntryData):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'measurements',
                ]
            )
        )
    )

    name = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )

    measurements = SubSection(
        section_def=HyperspectralMeasurement,
        repeats=True,
    )

    def normalize(
        self,
        archive,
        logger,
    ):

        super().normalize(
            archive,
            logger,
        )

        if not self.measurements:
            return

        measurement = self.measurements[0]

        if not measurement.visualization:
            return

        vis = measurement.visualization

        #if hasattr(
        #    vis,
        #    "_analysis_figures",
        #):
#
        #    if self.hyperspectral_analysis is None:
        #        self.hyperspectral_analysis = (
        #            HyperspectralAnalysis()
        #        )
#
        #    self.hyperspectral_analysis.figures = (
        #        vis._analysis_figures
        #    )
        
            #except Exception:
            #
            #    logger.debug('Failed to attach analysis figures to hyperspectral_analysis.')
            #    logger.debug(
            #    'Hyperspectral dataset has %d measurements.',
            #    len(self.measurements),
            #    )


m_package.__init_metainfo__()
