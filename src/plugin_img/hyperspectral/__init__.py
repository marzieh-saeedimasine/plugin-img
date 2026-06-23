from nomad.config.models.plugins import ParserEntryPoint, SchemaPackageEntryPoint


class Hyperspectral(SchemaPackageEntryPoint):
    def load(self):
        from plugin_img.hyperspectral.hyperspectral_shcema import (
            m_package as hyperspectral_schema,
        )
        #from plugin_img.images.image_shcema import m_package as image_schema

        # Combine the image schema and hyperspectral schema into a single package
        #combined_package = image_schema.copy()
        #combined_package.update(hyperspectral_schema)
        return hyperspectral_schema


schema_package_entry_point = Hyperspectral(
    name='HyperspectralSchema',
    description='Combined schema package for hyperspectral image analysis.',
)


class HyperspectralRootParserEntryPoint(ParserEntryPoint):
    def load(self):
        from plugin_img.hyperspectral.hyperspectral_parser import (
            HyperspectralRootParser,
        )

        return HyperspectralRootParser(**self.dict())


parser_entry_point = HyperspectralRootParserEntryPoint(
    name='HyperspectralRootParser',
    description='Parser for hyperspectral ENVI datasets with .hdr/.bil cube files.',
    mainfile_name_re=r'.*(\.hdr)$',
)