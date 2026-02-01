"""
Photo Processing Service

Handles image upload, EXIF stripping, and storage.
All privacy-sensitive metadata is removed before storage.

Privacy Features:
- EXIF data completely stripped
- Original filename not preserved
- File stored with random UUID name
- Perceptual hash for duplicate detection
"""

import hashlib
import io
import os
import uuid
from pathlib import Path
from typing import BinaryIO

import imagehash
from PIL import Image

from src.config import Settings, get_settings
from src.utils.errors import (
    DuplicatePhotoError,
    PhotoProcessingError,
    PhotoTooLargeError,
    PhotoValidationError,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

# Minimum dimensions
MIN_WIDTH = 400
MIN_HEIGHT = 300

# Maximum dimensions (resize if larger)
MAX_WIDTH = 2048
MAX_HEIGHT = 2048


class PhotoProcessor:
    """
    Service for processing uploaded photos.
    
    Responsibilities:
    - Validate image format and dimensions
    - Strip all EXIF metadata
    - Generate perceptual hash for duplicates
    - Save to storage with privacy-safe filename
    """
    
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.storage_path = Path(self.settings.photo_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def process_upload(
        self,
        file: BinaryIO,
        original_filename: str,
    ) -> dict:
        """
        Process an uploaded photo file.
        
        Steps:
        1. Read and validate image
        2. Check file size
        3. Strip EXIF metadata
        4. Resize if too large
        5. Generate file hash
        6. Generate perceptual hash
        7. Save to storage
        
        Args:
            file: File-like object containing image data
            original_filename: Original filename (for extension detection only)
        
        Returns:
            Dictionary with processed photo metadata:
            - filename: Storage filename
            - file_hash: SHA-256 hash
            - file_size: Size in bytes
            - width: Pixel width
            - height: Pixel height
            - mime_type: MIME type
            - perceptual_hash: Perceptual hash
        
        Raises:
            PhotoValidationError: If image is invalid
            PhotoTooLargeError: If file exceeds size limit
            PhotoProcessingError: If processing fails
        """
        try:
            # Read file data
            file_data = file.read()
            
            # Check file size
            if len(file_data) > self.settings.max_photo_size:
                raise PhotoTooLargeError(
                    len(file_data), self.settings.max_photo_size
                )
            
            # Open and validate image
            image = Image.open(io.BytesIO(file_data))
            
            # Verify format
            mime_type = Image.MIME.get(image.format)
            if mime_type not in ALLOWED_MIME_TYPES:
                raise PhotoValidationError(
                    f"Unsupported image format: {image.format}"
                )
            
            # Check dimensions
            if image.width < MIN_WIDTH or image.height < MIN_HEIGHT:
                raise PhotoValidationError(
                    f"Image too small. Minimum: {MIN_WIDTH}x{MIN_HEIGHT}, "
                    f"got: {image.width}x{image.height}"
                )
            
            # Strip EXIF and other metadata
            clean_image = self._strip_metadata(image)
            
            # Resize if too large
            if clean_image.width > MAX_WIDTH or clean_image.height > MAX_HEIGHT:
                clean_image = self._resize_image(clean_image)
            
            # Generate perceptual hash (before compression)
            phash = self._generate_perceptual_hash(clean_image)
            
            # Convert to bytes for storage
            output_buffer = io.BytesIO()
            save_format = "JPEG" if mime_type == "image/jpeg" else image.format
            
            if save_format == "JPEG":
                clean_image.save(
                    output_buffer,
                    format=save_format,
                    quality=85,
                    optimize=True,
                )
            else:
                clean_image.save(output_buffer, format=save_format, optimize=True)
            
            output_data = output_buffer.getvalue()
            
            # Generate file hash
            file_hash = hashlib.sha256(output_data).hexdigest()
            
            # Generate storage filename
            extension = ALLOWED_MIME_TYPES[mime_type]
            storage_filename = f"{uuid.uuid4()}{extension}"
            
            # Save to storage
            storage_path = self.storage_path / storage_filename
            storage_path.write_bytes(output_data)
            
            logger.info(
                f"Processed photo: {storage_filename}, "
                f"{clean_image.width}x{clean_image.height}, "
                f"{len(output_data)} bytes"
            )
            
            return {
                "filename": storage_filename,
                "stored_path": str(storage_path),
                "file_hash": file_hash,
                "file_size": len(output_data),
                "width": clean_image.width,
                "height": clean_image.height,
                "mime_type": mime_type,
                "perceptual_hash": phash,
            }
            
        except PhotoValidationError:
            raise
        except PhotoTooLargeError:
            raise
        except Exception as e:
            logger.exception(f"Photo processing failed: {e}")
            raise PhotoProcessingError(str(e))
    
    def _strip_metadata(self, image: Image.Image) -> Image.Image:
        """
        Strip all metadata from image.
        
        Creates a new image with only pixel data,
        removing EXIF, ICC profiles, and other metadata.
        """
        # Create a new image with just the pixel data
        # This removes all EXIF, IPTC, XMP, etc.
        
        if image.mode == "RGBA":
            # Keep alpha channel for PNG
            clean = Image.new("RGBA", image.size)
        elif image.mode in ("L", "LA", "P"):
            # Convert palette/grayscale to RGB
            image = image.convert("RGB")
            clean = Image.new("RGB", image.size)
        else:
            # RGB or similar
            clean = Image.new("RGB", image.size)
            if image.mode != "RGB":
                image = image.convert("RGB")
        
        clean.paste(image)
        return clean
    
    def _resize_image(self, image: Image.Image) -> Image.Image:
        """
        Resize image to fit within maximum dimensions.
        
        Maintains aspect ratio.
        """
        ratio = min(MAX_WIDTH / image.width, MAX_HEIGHT / image.height)
        new_width = int(image.width * ratio)
        new_height = int(image.height * ratio)
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _generate_perceptual_hash(self, image: Image.Image) -> str:
        """
        Generate perceptual hash for duplicate detection.
        
        Uses average hash which is fast and handles
        minor modifications well.
        """
        # Convert to grayscale for hashing
        gray = image.convert("L")
        
        # Generate average hash
        ahash = imagehash.average_hash(gray, hash_size=16)
        
        return str(ahash)
    
    def get_photo_path(self, filename: str) -> Path:
        """Get full path to a stored photo."""
        return self.storage_path / filename
    
    def delete_photo(self, filename: str) -> bool:
        """
        Delete a photo from storage.
        
        Returns True if deleted, False if not found.
        """
        path = self.get_photo_path(filename)
        if path.exists():
            path.unlink()
            logger.info(f"Deleted photo: {filename}")
            return True
        return False
    
    def check_duplicate(
        self,
        perceptual_hash: str,
        existing_hashes: list[str],
        threshold: int = 10,
    ) -> bool:
        """
        Check if a photo is a duplicate based on perceptual hash.
        
        Args:
            perceptual_hash: Hash of the new photo
            existing_hashes: List of existing photo hashes
            threshold: Maximum hamming distance for duplicate
        
        Returns:
            True if duplicate found, False otherwise
        """
        new_hash = imagehash.hex_to_hash(perceptual_hash)
        
        for existing in existing_hashes:
            try:
                existing_hash = imagehash.hex_to_hash(existing)
                distance = new_hash - existing_hash
                if distance <= threshold:
                    return True
            except ValueError:
                continue
        
        return False
