from nomad.config.models.plugins import SchemaPackageEntryPoint


class ImageAnalysisSchemaPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from plugin_img.schema_packages.image_analysis import m_package

        return m_package


schema_package_entry_point = ImageAnalysisSchemaPackageEntryPoint(
    name='ImageAnalysisSchema',
    description='Schema package for image analysis with metadata, ROI, and dimensions.',
)
