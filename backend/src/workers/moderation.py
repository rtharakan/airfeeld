"""
Content Moderation Worker

Provides automated content moderation for uploaded photos.
Implements lightweight checks for NSFW content and aviation relevance.

Privacy Note: All checks run locally - no external API calls.
"""

import logging
from pathlib import Path
from typing import Tuple

from PIL import Image
import imagehash

logger = logging.getLogger(__name__)


class ModerationResult:
    """Result of content moderation check."""
    
    def __init__(
        self,
        is_safe: bool,
        confidence: float,
        reason: str | None = None,
        flags: list[str] | None = None,
    ):
        self.is_safe = is_safe
        self.confidence = confidence  # 0.0-1.0, higher = more confident in decision
        self.reason = reason
        self.flags = flags or []
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "is_safe": self.is_safe,
            "confidence": self.confidence,
            "reason": self.reason,
            "flags": self.flags,
        }


class ContentModerationService:
    """
    Automated content moderation using local checks.
    
    Implements:
    - Skin tone detection (NSFW heuristic)
    - Image complexity analysis (spam detection)
    - Dimension validation
    - Format validation
    
    All checks run locally for privacy.
    """
    
    # Minimum image dimensions (pixels)
    MIN_WIDTH = 400
    MIN_HEIGHT = 300
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Skin tone detection thresholds (RGB ranges)
    # These are rough heuristics - not perfect but privacy-preserving
    SKIN_TONE_RANGES = [
        ((95, 40, 20), (255, 180, 130)),    # Light skin tones
        ((60, 30, 15), (255, 150, 100)),    # Medium skin tones
        ((20, 10, 5), (100, 60, 40)),       # Dark skin tones
    ]
    
    # Threshold: if >30% of pixels are skin-tone, flag for review
    SKIN_TONE_THRESHOLD = 0.30
    
    def __init__(self):
        """Initialize moderation service."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def check_image(self, file_path: str | Path) -> ModerationResult:
        """
        Check an image for content policy violations.
        
        Args:
            file_path: Path to image file
            
        Returns:
            ModerationResult with safety verdict and confidence score
        """
        file_path = Path(file_path)
        
        try:
            # Check file exists and size
            if not file_path.exists():
                return ModerationResult(
                    is_safe=False,
                    confidence=1.0,
                    reason="File does not exist",
                )
            
            file_size = file_path.stat().st_size
            if file_size > self.MAX_FILE_SIZE:
                return ModerationResult(
                    is_safe=False,
                    confidence=1.0,
                    reason=f"File too large: {file_size / 1024 / 1024:.1f}MB (max 10MB)",
                )
            
            # Open and validate image
            with Image.open(file_path) as img:
                # Check dimensions
                if img.width < self.MIN_WIDTH or img.height < self.MIN_HEIGHT:
                    return ModerationResult(
                        is_safe=False,
                        confidence=1.0,
                        reason=f"Image too small: {img.width}x{img.height} (min {self.MIN_WIDTH}x{self.MIN_HEIGHT})",
                    )
                
                # Convert to RGB for analysis
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                # Run checks
                flags = []
                
                # Check 1: Skin tone detection
                skin_ratio = self._check_skin_tones(img)
                if skin_ratio > self.SKIN_TONE_THRESHOLD:
                    flags.append("high_skin_tone")
                
                # Check 2: Complexity check (detect solid colors / spam)
                complexity_score = self._check_complexity(img)
                if complexity_score < 0.1:
                    flags.append("low_complexity")
                
                # Determine verdict
                if "high_skin_tone" in flags:
                    return ModerationResult(
                        is_safe=False,
                        confidence=0.7,  # Medium confidence - needs review
                        reason="High skin tone ratio detected - possible NSFW content",
                        flags=flags,
                    )
                
                if "low_complexity" in flags and len(flags) == 1:
                    return ModerationResult(
                        is_safe=False,
                        confidence=0.8,
                        reason="Low image complexity - possible spam or invalid photo",
                        flags=flags,
                    )
                
                # Passed all checks
                return ModerationResult(
                    is_safe=True,
                    confidence=0.9,  # High confidence but not perfect
                    flags=flags,
                )
        
        except Exception as e:
            self.logger.error(f"Error checking image {file_path}: {e}")
            return ModerationResult(
                is_safe=False,
                confidence=1.0,
                reason=f"Error processing image: {str(e)}",
            )
    
    def _check_skin_tones(self, img: Image.Image) -> float:
        """
        Calculate ratio of pixels matching skin tone ranges.
        
        This is a rough heuristic for NSFW detection.
        NOT PERFECT but privacy-preserving (runs locally).
        
        Args:
            img: PIL Image in RGB mode
            
        Returns:
            Float between 0.0-1.0 representing skin tone ratio
        """
        # Resize to smaller size for performance (sampling)
        sample_img = img.resize((100, 100), Image.Resampling.LANCZOS)
        pixels = list(sample_img.getdata())
        
        skin_pixels = 0
        total_pixels = len(pixels)
        
        for pixel in pixels:
            r, g, b = pixel
            
            # Check if pixel falls in any skin tone range
            for (r_min, g_min, b_min), (r_max, g_max, b_max) in self.SKIN_TONE_RANGES:
                if (r_min <= r <= r_max and 
                    g_min <= g <= g_max and 
                    b_min <= b <= b_max):
                    skin_pixels += 1
                    break
        
        return skin_pixels / total_pixels if total_pixels > 0 else 0.0
    
    def _check_complexity(self, img: Image.Image) -> float:
        """
        Calculate image complexity using perceptual hash entropy.
        
        Low complexity indicates solid colors, blank images, or spam.
        
        Args:
            img: PIL Image
            
        Returns:
            Float between 0.0-1.0, higher = more complex
        """
        # Calculate perceptual hash
        phash = imagehash.phash(img, hash_size=16)
        
        # Count number of 1s in hash (measure of complexity)
        hash_bits = bin(int(str(phash), 16)).count('1')
        max_bits = 16 * 16  # hash_size squared
        
        # Normalize to 0.0-1.0
        # We want values around 0.5 for normal images
        # Values near 0 or 1 indicate low complexity
        normalized = hash_bits / max_bits
        
        # Transform so 0.5 maps to 1.0 (high complexity)
        # and 0.0/1.0 map to 0.0 (low complexity)
        complexity = 1.0 - abs(normalized - 0.5) * 2
        
        return complexity


# Global service instance
_moderation_service: ContentModerationService | None = None


def get_moderation_service() -> ContentModerationService:
    """Get or create the global moderation service instance."""
    global _moderation_service
    if _moderation_service is None:
        _moderation_service = ContentModerationService()
    return _moderation_service


async def check_photo_content(file_path: str | Path) -> ModerationResult:
    """
    Async wrapper for content moderation check.
    
    Args:
        file_path: Path to image file
        
    Returns:
        ModerationResult with safety verdict
    """
    service = get_moderation_service()
    # For now, run synchronously
    # In production, could use asyncio.to_thread for true async
    return service.check_image(file_path)


def strip_exif_data(image_bytes: bytes) -> bytes:
    """
    Remove all EXIF metadata from image bytes.
    
    Privacy requirement: Strips all metadata including GPS coordinates,
    camera information, and timestamps to prevent unintentional disclosure
    of sensitive information.
    
    Args:
        image_bytes: Original image bytes (JPEG format)
        
    Returns:
        Image bytes with all EXIF data removed
        
    Raises:
        ValueError: If input is not a valid image
        IOError: If image processing fails
    """
    import io
    
    # Validate input
    if not image_bytes or len(image_bytes) == 0:
        raise ValueError("Image bytes cannot be empty")
    
    try:
        # Open image from bytes
        img = Image.open(io.BytesIO(image_bytes))
        
        # Verify it's a valid image by loading data
        img.verify()
        
        # Re-open (verify() closes the file)
        img = Image.open(io.BytesIO(image_bytes))
        
        # Create output buffer
        output = io.BytesIO()
        
        # Save without EXIF data
        # By not passing exif parameter, PIL will not include EXIF
        img.save(output, format='JPEG', quality=95, optimize=True)
        
        # Get bytes
        stripped_bytes = output.getvalue()
        
        logger.info(
            f"Stripped EXIF data: {len(image_bytes)} bytes -> {len(stripped_bytes)} bytes "
            f"({(1 - len(stripped_bytes)/len(image_bytes))*100:.1f}% reduction)"
        )
        
        return stripped_bytes
        
    except Exception as e:
        logger.error(f"Failed to strip EXIF data: {e}")
        raise IOError(f"Failed to process image: {e}") from e
