from typing import TYPE_CHECKING

from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.annotations import ELNAnnotation, SectionProperties
from nomad.datamodel.metainfo.plot import PlotSection
from nomad.metainfo import Package, Quantity, Section, SubSection

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger


m_package = Package(
    name='hyperspectral_image_plugin',
    description='Schema for hyperspectral image datasets.',
)


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
                ],
            ),
        ),
    )

    interleave = Quantity(
        type=str,
        description='Interleave format of the hyperspectral cube.',
        a_eln={'choices': ['bil', 'bsq', 'bip', 'BIL', 'BSQ', 'BIP']},
    )
    data_type = Quantity(
        type=str,
        description='ENVI data type code stored in the header.',
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
        description='Shutter value from the acquisition header.',
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
        description='Sensor temperature during acquisition.',
        a_eln={'component': 'NumberEditQuantity'},
    )
    imager_serial_number = Quantity(
        type=str,
        description='Serial number of the imager.',
        a_eln={'component': 'StringEditQuantity'},
    )
    rotation = Quantity(
        type=str,
        description='Rotation metadata from the header.',
        a_eln={'component': 'StringEditQuantity'},
    )
    pixel_size = Quantity(
        type=float,
        description='Pixel size of the hyperspectral image.',
        a_eln={'component': 'NumberEditQuantity'},
    )
    byte_order = Quantity(
        type=str,
        description='Byte order value from the ENVI header.',
        a_eln={'component': 'StringEditQuantity'},
    )
    header_offset = Quantity(
        type=int,
        description='Offset in bytes to the start of the binary data.',
        a_eln={'component': 'NumberEditQuantity'},
    )
    flip_radiometric_calibration = Quantity(
        type=bool,
        description='Whether radiometric calibration should be flipped.',
        a_eln={'component': 'BoolEditQuantity'},
    )
    reflection_scale_factor = Quantity(
        type=float,
        description='Scale factor for reflectance data.',
        a_eln={'component': 'NumberEditQuantity'},
    )
    wavelength_unit = Quantity(
        type=str,
        description='Unit of the wavelength axis.',
        a_eln={'component': 'StringEditQuantity'},
    )
    label = Quantity(
        type=str,
        description='Label from the acquisition header.',
        a_eln={'component': 'StringEditQuantity'},
    )
    history = Quantity(
        type=str,
        description='History from the acquisition header.',
        a_eln={'component': 'StringEditQuantity'},
    )


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
                ],
            ),
        ),
    )

    lines = Quantity(
        type=int,
        description='Number of spatial scan lines.',
        a_eln={'component': 'NumberEditQuantity'},
    )
    samples = Quantity(
        type=int,
        description='Number of spatial samples per line.',
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
        description='Interleave format of the hyperspectral cube.',
        a_eln={'choices': ['bil', 'bsq', 'bip', 'BIL', 'BSQ', 'BIP']},
    )
    data_type = Quantity(
        type=str,
        description='ENVI data type code stored in the header.',
        a_eln={'component': 'StringEditQuantity'},
    )


class HyperspectralRawData(ArchiveSection):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'hdr_file',
                    'bil_file',
                    'cube_npy',
                    'rgb_preview',
                ],
            ),
        ),
    )

    hdr_file = Quantity(
        type=str,
        description='Relative path to the ENVI header file.',
        a_eln={'component': 'FileEditQuantity'},
    )
    bil_file = Quantity(
        type=str,
        description='Relative path to the BIL binary cube file.',
        a_eln={'component': 'FileEditQuantity'},
    )
    cube_npy = Quantity(
        type=str,
        description='Relative path to the generated NumPy cube.',
        a_eln={'component': 'FileEditQuantity'},
    )
    rgb_preview = Quantity(
        type=str,
        description='Relative path to the generated RGB preview image.',
        a_eln={'component': 'FileEditQuantity'},
    )


class HyperspectralVisualization(PlotSection, ArchiveSection):
    pass


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
                ],
            ),
        ),
    )

    acquisition_metadata = SubSection(
        section_def=AcquisitionMetadata,
        description='Acquisition metadata parsed from the ENVI header.',
    )
    cube_metadata = SubSection(
        section_def=CubeMetadata,
        description='Cube dimensions and spectral axis metadata.',
    )
    raw_data = SubSection(
        section_def=HyperspectralRawData,
        description='Raw and derived data files for this hyperspectral measurement.',
    )
    visualization = SubSection(
        section_def=HyperspectralVisualization,
        description='Plotly visualizations for the hyperspectral measurement.',
    )
    label = Quantity(
        type=str,
        description='Label for the hyperspectral measurement.',
        a_eln={'component': 'StringEditQuantity'},
    )
    history = Quantity(
        type=str,
        description='History for the hyperspectral measurement.',
        a_eln={'component': 'StringEditQuantity'},
    )


class HyperspectralDataset(EntryData):
    m_def = Section(
        a_eln=ELNAnnotation(
            properties=SectionProperties(
                order=[
                    'name',
                    'measurements',
                ],
            ),
        ),
    )

    name = Quantity(
        type=str,
        description='A descriptive name for the hyperspectral dataset.',
        a_eln={'component': 'StringEditQuantity'},
    )
    measurements = SubSection(
        section_def=HyperspectralMeasurement,
        description='Collection of hyperspectral cube measurements.',
        repeats=True,
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        super().normalize(archive, logger)


m_package.__init_metainfo__()
