import logging
import os
from pathlib import Path

from nomad.datamodel import EntryArchive

from plugin_img.parsers.root_parser import DataRootParser


def test_parse_image_data():
    """Test parsing image data directory with all experiments."""
    parser = DataRootParser()
    archive = EntryArchive()
    
    # Get the absolute path to test data - use nomad_collect.txt marker file
    test_dir = Path(__file__).parent.parent / 'data' / 'data-img'
    mainfile = test_dir / 'nomad_collect.txt'
    
    # Create marker file if it doesn't exist
    if not mainfile.exists():
        mainfile.touch()
    
    if mainfile.exists():
        parser.parse(str(mainfile), archive, logging.getLogger())
        
        # Verify dataset was created
        assert archive.data is not None
        assert archive.data.name is not None
        
        # Verify multiple experiments were found and parsed
        assert hasattr(archive.data, 'measurements')
        assert archive.data.measurements is not None
        assert len(archive.data.measurements) >= 2  # Should have at least 2 experiments
        
        # Check each measurement/experiment
        for measurement in archive.data.measurements:
            assert measurement.timestamp is not None
            assert measurement.name is not None
            
            # Verify manifest data
            if measurement.manifest_data:
                assert measurement.manifest_data.Date is not None
                
            # Verify metadata
            if measurement.metadata:
                assert measurement.metadata.timestamp is not None
                assert measurement.metadata.shape is not None
                assert len(measurement.metadata.shape) > 0
