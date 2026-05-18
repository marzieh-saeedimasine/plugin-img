import logging
import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive

from nomad.parsing.parser import MatchingParser

from plugin_img.schema_packages.image_analysis import (
    ImageDataset,
    ImageExperimentRun,
    ImageMetadata,
    ManifestData,
)

logger_module = logging.getLogger(__name__)


class DataRootParser(MatchingParser):
    """Parser for image data - processes manifest.csv files from timestamped folders."""

    def parse(
        self,
        mainfile: str,
        archive: 'EntryArchive',
        logger=None,
        child_archives=None,
    ) -> None:
        """Parse all experiments from parent directory."""
        log = logger or logger_module
        mainfile_path = Path(mainfile)
        
        # Skip if already processed
        if archive.data is not None:
            log.debug('Archive already has data, skipping parse')
            return
        
        # Get parent directory (contains all timestamp folders)
        parent_path = mainfile_path.parent
        log.info('Parsing experiments from parent directory: %s', parent_path)
        
        try:
            # Find all timestamp-named folders
            timestamp_pattern = re.compile(r'^\d{8}_\d{6}$')
            experiment_folders = sorted([
                d for d in parent_path.iterdir()
                if d.is_dir() and timestamp_pattern.match(d.name)
            ])
            
            if not experiment_folders:
                log.warning('No timestamp-named folders found in %s', parent_path)
                return
            
            log.info('Found %d experiment folders', len(experiment_folders))
            
            # Parse all experiments
            experiments = []
            for exp_folder in experiment_folders:
                log.info('Processing experiment: %s', exp_folder.name)
                experiment = ImageExperimentRun()
                experiment.timestamp = exp_folder.name
                experiment.name = f'Experiment {exp_folder.name}'
                
                # Parse manifest.csv
                manifest_path = exp_folder / 'manifest.csv'
                if manifest_path.exists():
                    manifest = self._parse_manifest(str(manifest_path), log)
                    if manifest:
                        experiment.manifest_data = manifest
                        log.info('Manifest parsed for: %s', exp_folder.name)
                else:
                    log.debug('manifest.csv not found in %s', exp_folder.name)
                
                # Parse metadata.json
                metadata_path = exp_folder / 'metadata.json'
                if metadata_path.exists():
                    metadata = self._parse_metadata(metadata_path, log)
                    if metadata:
                        experiment.metadata = metadata
                        log.info('Metadata parsed for: %s', exp_folder.name)
                else:
                    log.debug('metadata.json not found in %s', exp_folder.name)
                
                experiments.append(experiment)
            
            # Create single dataset with all experiments
            dataset = ImageDataset()
            dataset.name = f'Image Dataset from {parent_path.name}'
            dataset.measurements = experiments
            archive.data = dataset
            
            log.info('Successfully created dataset with %d experiments', len(experiments))
            
        except Exception as exc:
            log.error('Error parsing experiments: %s', str(exc), exc_info=True)

    def _parse_manifest(self, csv_path: Path, log) -> ManifestData:
        """Parse manifest.csv file."""
        try:
            import pandas as pd
            
            df = pd.read_csv(str(csv_path))
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

            log.info('Parsed manifest successfully')
            return manifest

        except Exception as exc:
            log.error('Error parsing manifest: %s', str(exc))
            return None

    def _parse_metadata(self, json_path: Path, log) -> ImageMetadata:
        """Parse metadata.json file."""
        try:
            with open(str(json_path)) as f:
                data = json.load(f)

            metadata = ImageMetadata()

            # Basic fields
            metadata.timestamp = data.get('timestamp', '')
            metadata.exposure_ms = float(data.get('exposure_ms', 0.0))
            metadata.gain = float(data.get('gain', 0))
            metadata.bit_depth = int(data.get('bit_depth', 8))
            metadata.shape = data.get('shape', [])
            metadata.is_color = bool(data.get('is_color', False))
            metadata.min = float(data.get('min', 0))
            metadata.max = float(data.get('max', 255))

            log.info('Parsed metadata successfully')
            return metadata

        except Exception as exc:
            log.error('Error parsing metadata: %s', str(exc))
            return None