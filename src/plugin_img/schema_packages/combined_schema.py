"""Combined dataset metainfo for plugin-img.

This package defines a NOMAD metainfo `CombinedDataset` that holds the
image dataset, hyperspectral dataset, synthesis conditions and aggregated
figures for the overview section.
"""

from typing import TYPE_CHECKING

from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.plot import PlotSection
from nomad.metainfo import Package, Quantity, Section, SubSection

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive

from plugin_img.hyperspectral.hyperspectral_shcema import HyperspectralDataset
from plugin_img.images.image_shcema import ImageDataset, ManifestData

m_package = Package(
    name='plugin_img_combined',
    description='Combined image + hyperspectral dataset for overview',
)


class CombinedDataset(PlotSection, EntryData):
    """Combined dataset containing image and hyperspectral results."""

    m_def = Section(
        a_eln=None,
        description='Combined dataset for images and hyperspectral measurements',
    )

    name = Quantity(
        type=str,
        description='Descriptive name for the combined dataset',
    )

    synthesis_conditions = SubSection(
        section_def=ManifestData,
        description='Sample-level synthesis/condition data',
    )

    image_dataset = SubSection(
        section_def=ImageDataset,
        description='Parsed image dataset (if present)',
    )

    hyperspectral_dataset = SubSection(
        section_def=HyperspectralDataset,
        description='Parsed hyperspectral dataset (if present)',
    )

    def normalize(self, archive: 'EntryArchive', logger=None) -> None:
        super().normalize(archive, logger)


m_package.__init_metainfo__()
