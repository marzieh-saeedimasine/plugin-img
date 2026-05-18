import json
import logging
from pathlib import Path

import numpy as np

from plugin_img.schema_packages.image_analysis import (
    BoundingBox,
    ImageData,
    ImageDimensions,
    RegionOfInterest,
)

logger_module = logging.getLogger(__name__)

# Constants for image shape dimensions
GRAYSCALE_SHAPE_DIM = 2
COLOR_SHAPE_DIM = 3
MIN_COLOR_CHANNELS = 3


class NPYParser:
    """Parse numpy .npy image files and create ImageData."""

    def parse_npy(
        self, npy_path: Path, metadata_json_path: Path, log
    ) -> ImageData:
        """
        Parse NPY image file with associated metadata.

        Args:
            npy_path: Path to .npy image file
            metadata_json_path: Path to metadata.json file
            log: Logger instance

        Returns:
            ImageData with dimensions and ROI info
        """
        try:
            # Load NPY data
            image_data_array = np.load(npy_path)
            log.info(
                'Loaded NPY file: %s with shape %s',
                npy_path.name,
                image_data_array.shape,
            )

            # Load associated metadata
            with open(metadata_json_path, encoding='utf-8') as f:
                metadata_dict = json.load(f)

            # Create ImageData
            image_data = ImageData()

            # Create dimensions subsection
            dimensions = ImageDimensions()
            if len(image_data_array.shape) == GRAYSCALE_SHAPE_DIM:
                dimensions.height = int(image_data_array.shape[0])
                dimensions.width = int(image_data_array.shape[1])
                dimensions.channels = 1
                dimensions.is_color = False
            elif len(image_data_array.shape) == COLOR_SHAPE_DIM:
                dimensions.height = int(image_data_array.shape[0])
                dimensions.width = int(image_data_array.shape[1])
                dimensions.channels = int(image_data_array.shape[2])
                dimensions.is_color = dimensions.channels >= MIN_COLOR_CHANNELS

            # Get pixel value statistics
            dimensions.pixel_value_min = int(np.min(image_data_array))
            dimensions.pixel_value_max = int(np.max(image_data_array))

            image_data.dimensions = dimensions

            # Parse ROI if present
            roi_data = metadata_dict.get('circular_roi', {})
            if roi_data:
                roi = RegionOfInterest()
                roi.center_x_px = float(roi_data.get('center_x_px', 0))
                roi.center_y_px = float(roi_data.get('center_y_px', 0))
                roi.radius_px = float(roi_data.get('radius_px', 0))
                roi.square_crop_size_px = int(roi_data.get('square_crop_size_px', 0))

                # Parse bounding box if present
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

                image_data.roi = roi

            log.info(
                'Parsed image: %dx%d, channels=%d, range=[%d,%d]',
                dimensions.width,
                dimensions.height,
                dimensions.channels,
                dimensions.pixel_value_min,
                dimensions.pixel_value_max,
            )

            return image_data

        except FileNotFoundError:
            log.error('NPY file not found: %s', npy_path)
            return None
        except ValueError as exc:
            log.error('Error reading NPY file %s: %s', npy_path, str(exc))
            return None