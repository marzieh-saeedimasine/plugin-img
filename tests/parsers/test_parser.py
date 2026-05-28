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
            
            # Verify image data with dimensions and ROI
            if measurement.image:
                assert measurement.image is not None
                
                # Check dimensions
                if measurement.image.dimensions:
                    assert measurement.image.dimensions.height > 0
                    assert measurement.image.dimensions.width > 0
                    assert measurement.image.dimensions.channels > 0
                    assert measurement.image.dimensions.bit_depth > 0
                
                # Check region of interest
                if measurement.image.roi:
                    assert measurement.image.roi.center_x_px is not None
                    assert measurement.image.roi.center_y_px is not None
                    assert measurement.image.roi.radius_px > 0
                    
                    # Check bounding box
                    if measurement.image.roi.bounding_box:
                        bbox = measurement.image.roi.bounding_box
                        assert bbox.x_min >= 0
                        assert bbox.y_min >= 0
                        assert bbox.width > 0
                        assert bbox.height > 0
                
                # Check image file reference
                if measurement.image.image_array:
                    assert 'image_raw.npy' in measurement.image.image_array
                    assert 'npy' in measurement.image.image_array
                
                    # Check visualization subsection with PNG preview
                    if measurement.image.visualization:
                        assert measurement.image.visualization.image_file is not None
                        assert 'png' in measurement.image.visualization.image_file
                        # visualization stores relative path (with forward slashes), image_preview stores absolute path
                        # Convert to forward slash format for comparison
                        vis_file_normalized = measurement.image.visualization.image_file.replace('\\', '/')
                        preview_normalized = measurement.image.image_preview.replace('\\', '/')
                        assert vis_file_normalized in preview_normalized