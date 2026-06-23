import logging
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING

from nomad.config.models.plugins import ParserEntryPoint
from nomad.datamodel.metainfo.plot import PlotlyFigure

from plugin_img.hyperspectral.hyperspectral_parser import HyperspectralRootParser
from plugin_img.hyperspectral.hyperspectral_shcema import HyperspectralDataset
from plugin_img.images.image_parser import DataRootParser
from plugin_img.images.image_shcema import ImageDataset
from plugin_img.schema_packages.combined_schema import CombinedDataset

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# CombinedDataset is defined in `plugin_img.schema_packages.combined_schema`
# and imported above. It provides the structured metainfo used for the
# combined overview.


class SynthesisCompositeParser:
    """Lightweight helper that runs both image and hyperspectral parsers
    into temporary archives and aggregates their outputs into a
    combined dataset attached to the provided `archive`.
    """

    def __init__(self):
        self.image_parser = DataRootParser()
        self.hyperspec_parser = HyperspectralRootParser()

    def parse(self, mainfile: str, archive, logger=None, child_archives=None):
        log = logger or logger

        tmp_img = SimpleNamespace()
        tmp_img.data = None

        tmp_hs = SimpleNamespace()
        tmp_hs.data = None

        # Run sub-parsers into temporary archives so they don't stomp on
        # the shared `archive.data` field.
        try:
            self.image_parser.parse(mainfile, tmp_img, logger=log)
        except Exception as e:
            log and log.error('Image parser failed: %s', e)

        try:
            self.hyperspec_parser.parse(mainfile, tmp_hs, logger=log)
        except Exception as e:
            log and log.error('Hyperspectral parser failed: %s', e)

        # Build a combined dataset instance
        combined = CombinedDataset()
        combined.name = f'Combined dataset - {Path(mainfile).parent.name}'

        # Attach image dataset if available
        img_count = 0
        hs_count = 0
        if getattr(tmp_img, 'data', None) is not None and isinstance(
            tmp_img.data, ImageDataset
        ):
            img_data = tmp_img.data
            combined.image_dataset = img_data
            img_count = len(getattr(img_data, 'measurements', []) or [])
            # carry synthesis conditions if present
            if hasattr(img_data, 'synthesis_conditions'):
                combined.synthesis_conditions = img_data.synthesis_conditions

            # collect image figures
            figs = []
            for meas in getattr(img_data, 'measurements', []) or []:
                image_section = getattr(meas, 'image', None)
                if image_section is None:
                    continue
                if getattr(image_section, 'figures', None):
                    figs.extend(image_section.figures)
                vis = getattr(image_section, 'visualization', None)
                if vis is not None and getattr(vis, 'image_file', None):
                    figs.append(
                        PlotlyFigure(
                            label=f'Image preview: {getattr(meas, "name", meas)}',
                            figure={'image_file': vis.image_file},
                        )
                    )
            if figs:
                combined.figures = figs

        # Attach hyperspectral dataset if available
        if getattr(tmp_hs, 'data', None) is not None and isinstance(
            tmp_hs.data, HyperspectralDataset
        ):
            hs_data = tmp_hs.data
            combined.hyperspectral_dataset = hs_data
            hs_count = len(getattr(hs_data, 'measurements', []) or [])
            # append hyperspectral figures
            if getattr(hs_data, 'figures', None):
                combined.figures = list(getattr(combined, 'figures', []) or []) + list(
                    hs_data.figures
                )

            # Transfer any analysis figures stored on measurement.visualization
            # directly into the hyperspectral_analysis subsection so the
            # GUI will display them even if normalization isn't run later.
            try:
                # Ensure hyperspectral_analysis subsection exists
                if combined.hyperspectral_dataset.hyperspectral_analysis is None:
                    combined.hyperspectral_dataset.hyperspectral_analysis = None
                analysis_figs = []
                for meas in getattr(hs_data, 'measurements', []) or []:
                    vis = getattr(meas, 'visualization', None)
                    if vis is None:
                        continue
                    if getattr(vis, '_analysis_figures', None):
                        analysis_figs.extend(vis._analysis_figures)

                if analysis_figs:
                    # create the subsection object if needed
                    try:
                        if combined.hyperspectral_dataset.hyperspectral_analysis is None:
                            from plugin_img.hyperspectral.hyperspectral_shcema import HyperspectralAnalysis

                            combined.hyperspectral_dataset.hyperspectral_analysis = HyperspectralAnalysis()
                        combined.hyperspectral_dataset.hyperspectral_analysis.figures = analysis_figs
                    except Exception:
                        # best-effort: ignore failures to avoid breaking parsing
                        pass
            except Exception:
                pass

        archive.data = combined
        log and log.info(
            'Composite parse created combined dataset with %d image measurements and %d hyperspectral measurements',
            img_count,
            hs_count,
        )


class SynthesisCompositeParserEntryPoint(ParserEntryPoint):
    def load(self):
        # Return a callable/instance that the NOMAD parsing machinery
        # will call. We provide an instance with a `parse()` method.
        return SynthesisCompositeParser()


#parser_entry_point = SynthesisCompositeParserEntryPoint(
#    name='SynthesisCompositeParser',
#    description='Composite parser that parses synthesis-condition folders and aggregates image and hyperspectral data into an overview.',
#    mainfile_name_re=r'.*(synth_con\.json)$',
#)
