from nomad.config.models.plugins import ParserEntryPoint


class ImageDataRootParserEntryPoint(ParserEntryPoint):
    def load(self):
        from plugin_img.parsers.root_parser import DataRootParser

        return DataRootParser(**self.dict())


parser_entry_point = ImageDataRootParserEntryPoint(
    name='ImageDataRootParser',
    description='Parser for image analysis data directories with manifest and metadata files.',
    mainfile_name_re=r'.*synth_con\.json$',
)
