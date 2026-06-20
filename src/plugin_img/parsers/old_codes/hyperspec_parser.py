import json
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from matplotlib import lines
from nomad.parsing.parser import MatchingParser

from plugin_img.schema_packages.hyperspectral_image_plugin import (
    Acquisition_metadata,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive

logger_module = logging.getLogger(__name__)

class HyperspecParser(MatchingParser):
    def __init__(self):
        super().__init__(
            name='HyperspecParser',
            code_name='hyperspec_parser',
            domain='data',
            mainfile_must_exist=False,
            match_path_patterns=[
                re.compile(r'.*synthesis\.json$'),
                re.compile(r'.*hyperspectral_image\.hdr$'),
            ]
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger: logging.Logger) -> None:
        mainfile_path = Path(mainfile)
        if mainfile_path.name == 'synthesis.json':
            self._parse_synthesis_json(mainfile_path, archive, logger)
        elif mainfile_path.name == 'hyperspectral_image.hdr':
            self._parse_hyperspectral_image(mainfile_path, archive, logger)

    def _parse_synthesis_json(self, json_file: Path, archive: EntryArchive, logger: logging.Logger) -> None:
        with json_file.open() as f:
            data = json.load(f)
        
        synthesis_conditions = archive.data.synthesis_conditions
        if synthesis_conditions is None:
            synthesis_conditions = archive.data.synthesis_conditions = Acquisition_metadata()
        
        for key, value in data.items():
            setattr(synthesis_conditions, key.replace('_', '-'), value)

    def _parse_hyperspectral_image(self, hdr_file: Path, archive: EntryArchive, logger: logging.Logger) -> None:
        # Placeholder for actual hyperspectral image parsing logic
        # This would involve reading the .hdr file to get metadata and then reading the corresponding .img file for the data
        """
        Read a BIL hyperspectral file into a NumPy array.


        Returns array of shape:
        (lines, samples, bands)
        """
        data = np.fromfile(path, dtype=np.dtype)


        expected = lines * samples * bands
        if data.size != expected:
            raise ValueError(f"Size mismatch: expected {expected}, got {data.size}")


        # BIL order: (lines, bands, samples)
        data = data.reshape(lines, bands, samples)


        # Reorder to (lines, samples, bands)
        data = np.transpose(data, (0, 2, 1))


        return data
    

## Need to add parsers for .hdr ans .bil files, and then create a new entry for the hyperspectral image data, and add the parsed data to that entry.