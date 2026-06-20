from nomad.config.models.plugins import ParserEntryPoint


class HyperspectralRootParserEntryPoint(ParserEntryPoint):
    def load(self):
        from plugin_img.parsers.hyperspectral_root_parser import HyperspectralRootParser

        return HyperspectralRootParser(**self.dict())


parser_entry_point = HyperspectralRootParserEntryPoint(
    name='HyperspectralRootParser',
    description='Parser for hyperspectral ENVI datasets with .hdr/.bil cube files.',
    mainfile_name_re=r'.*(synth_con\.json|\.hdr)$',
)
