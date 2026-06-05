import json
import logging
from pathlib import Path

from plugin_img.schema_packages.image_analysis import (
    BoundingBox,
    ImageMetadata,
    RegionOfInterest,
)

logger_module = logging.getLogger(__name__)


class MetadataParser:
    """Parse metadata.json files containing image acquisition settings."""

    def parse_json(self, json_path: Path, log) -> ImageMetadata:
        """
        Parse metadata.json file.
        
        Expects JSON with fields: timestamp, exposure_ms, gain, bit_depth, 
        is_color, shape, min, max, and optionally circular_roi.
        """
        try:
            with open(json_path) as f:
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

            log.info('Parsed metadata from JSON: %s', json_path.name)
            return metadata

        except Exception as exc:
            log.error('Error parsing metadata JSON %s: %s', json_path, str(exc))
            return None

    def parse_roi(self, metadata_dict: dict, log) -> RegionOfInterest:
        """Parse circular ROI and bounding box from metadata."""
        try:
            roi_data = metadata_dict.get('circular_roi', {})
            if not roi_data:
                return None

            roi = RegionOfInterest()
            roi.center_x_px = float(roi_data.get('center_x_px', 0))
            roi.center_y_px = float(roi_data.get('center_y_px', 0))
            roi.radius_px = float(roi_data.get('radius_px', 0))
            roi.square_crop_size_px = int(roi_data.get('square_crop_size_px', 0))

            # Parse bounding box
            bbox_data = roi_data.get('bounding_box', {})
            if bbox_data:
                bbox = BoundingBox()
                bbox.x_min = int(bbox_data.get('x_min', 0))
                bbox.y_min = int(bbox_data.get('y_min', 0))
                bbox.x_max = int(bbox_data.get('x_max', 0))
                bbox.y_max = int(bbox_data.get('y_max', 0))
                bbox.width = int(bbox_data.get('width', 0))
                bbox.height = int(bbox_data.get('height', 0))
                roi.bounding_box = bbox

            log.debug('Parsed ROI from metadata')
            return roi

        except Exception as exc:
            log.error('Error parsing ROI: %s', str(exc))
            return None