import logging
from pathlib import Path

import numpy as np
from PIL import Image

logger_module = logging.getLogger(__name__)


class NPYImageConverter:
    """Convert numpy .npy image files to PNG format for visualization."""

    def convert_npy_to_png(self, npy_path: Path, log) -> str:
        """
        Convert NPY image file to PNG for visualization.

        Args:
            npy_path: Path to .npy image file
            log: Logger instance

        Returns:
            str: Path to the generated PNG file, or None if conversion fails
        """
        try:
            # Load the NPY file
            image_array = np.load(str(npy_path))
            log.info(
                'Loaded NPY array with shape: %s, dtype: %s',
                image_array.shape,
                image_array.dtype,
            )

            if image_array.size == 0:
                log.warning('Image array is empty')
                return None

            # Normalize image to 0-255 range for display
            img_normalized = self._normalize_array(image_array)

            # Handle different image shapes
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                # RGB image
                pil_image = Image.fromarray(
                    img_normalized.astype(np.uint8), mode='RGB'
                )
                log.info('Converted to RGB image')
            elif len(image_array.shape) == 3 and image_array.shape[2] == 1:
                # Grayscale with channel dimension
                pil_image = Image.fromarray(
                    img_normalized[:, :, 0].astype(np.uint8), mode='L'
                )
                log.info('Converted to grayscale (single channel)')
            elif len(image_array.shape) == 2:
                # Grayscale without channel dimension
                pil_image = Image.fromarray(
                    img_normalized.astype(np.uint8), mode='L'
                )
                log.info('Converted to grayscale')
            elif len(image_array.shape) == 3 and image_array.shape[2] == 4:
                # RGBA image
                pil_image = Image.fromarray(
                    img_normalized.astype(np.uint8), mode='RGBA'
                )
                log.info('Converted to RGBA image')
            else:
                log.warning('Unsupported image shape: %s', image_array.shape)
                return None

            # Save as PNG
            png_path = npy_path.parent / 'image_preview.png'
            pil_image.save(str(png_path))
            log.info('Saved PNG preview to: %s', png_path)

            return str(png_path)

        except FileNotFoundError:
            log.error('NPY file not found: %s', npy_path)
            return None
        except ValueError as exc:
            log.error('Error reading NPY file %s: %s', npy_path, str(exc))
            return None

    def _normalize_array(self, array: np.ndarray) -> np.ndarray:
        """
        Normalize array values to 0-255 range for visualization.

        Args:
            array: Input numpy array (can be any shape)

        Returns:
            np.ndarray: Normalized array scaled to 0-255 range
        """
        arr_min = array.min()
        arr_max = array.max()

        if arr_max == arr_min:
            # Constant array - fill with mid-gray
            return np.full_like(array, 128, dtype=np.float32)

        # Scale to 0-255
        normalized = ((array - arr_min) / (arr_max - arr_min) * 255)
        return normalized