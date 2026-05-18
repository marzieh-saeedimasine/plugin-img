import logging
from pathlib import Path

import pandas as pd

from plugin_img.schema_packages.image_analysis import ManifestData

logger_module = logging.getLogger(__name__)


class ManifestParser:
    """Parse manifest.csv files containing experiment parameters."""

    def parse_csv(self, csv_path: Path, log) -> ManifestData:
        """Parse manifest data from CSV file."""
        try:
            df = pd.read_csv(csv_path)
            if df.empty:
                log.debug('Manifest CSV is empty')
                return None

            row = df.iloc[0]
            manifest = ManifestData()

            field_mapping = {
                'Date': 'Date',
                'Cu_source_power': 'Cu_source_power',
                'Sn_source_power': 'Sn_source_power',
                'Zn_source_power': 'Zn_source_power',
                'Pressure': 'Pressure',
                'Source_temperature': 'Source_temperature',
                'Process_temperature': 'Process_temperature',
                'Chamber_pressure': 'Chamber_pressure',
                'Process_time': 'Process_time',
                'Cooling_time': 'Cooling_time',
                'Cooling_rate': 'Cooling_rate',
            }

            for csv_col, field_name in field_mapping.items():
                if csv_col in row.index:
                    value = row[csv_col]
                    if pd.notna(value):
                        try:
                            if field_name == 'Date':
                                setattr(manifest, field_name, str(value))
                            else:
                                setattr(manifest, field_name, float(value))
                        except (ValueError, TypeError):
                            log.warning('Could not convert %s=%s', field_name, value)

            log.info('Parsed manifest from CSV: %s', csv_path.name)
            return manifest

        except Exception as exc:
            log.error('Error parsing manifest CSV %s: %s', csv_path, str(exc))
            return None