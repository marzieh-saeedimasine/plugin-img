from nomad.config.models.plugins import ParserEntryPoint, SchemaPackageEntryPoint


class ImageAnalysisSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from plugin_img.images.image_shcema import m_package

        return m_package


schema_package_entry_point = ImageAnalysisSchemaPackageEntryPoint(
    name='ImageAnalysisSchema',
    description='Schema package for image analysis with metadata, ROI, and dimensions.',
)


class image_analysis_parser_entry_point(ParserEntryPoint):
    def load(self):
        from plugin_img.images.image_parser import DataRootParser

        return DataRootParser(**self.dict())


parser_entry_point = image_analysis_parser_entry_point(
    name='ImageAnalysisParser',
    description='Parser for image datasets with metadata, ROI, and dimensions.',
    # Only match explicit per-sample metadata files (not arbitrary JSON)
    mainfile_name_re=r'.*(synthesis\.json)$',
)
