"""
Unit tests for content moderation service.

Tests the local NSFW detection and spam filtering.
"""

import pytest
from pathlib import Path
from PIL import Image
import tempfile
import os

from src.workers.moderation import (
    ContentModerationService,
    ModerationResult,
    check_photo_content,
)


@pytest.fixture
def moderation_service():
    """Create a moderation service instance."""
    return ContentModerationService()


@pytest.fixture
def temp_image_path():
    """Create a temporary file path for test images."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        path = Path(f.name)
    yield path
    # Cleanup
    if path.exists():
        path.unlink()


def create_test_image(path: Path, width: int, height: int, color: tuple):
    """Helper to create a test image."""
    img = Image.new("RGB", (width, height), color)
    img.save(path, "JPEG")


def create_complex_image(path: Path, width: int, height: int):
    """Helper to create a complex test image with varied colors."""
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    
    # Create a pattern with varied colors
    for y in range(height):
        for x in range(width):
            # Create a gradient-like pattern
            r = int((x / width) * 255)
            g = int((y / height) * 255)
            b = int(((x + y) / (width + height)) * 255)
            pixels[x, y] = (r, g, b)
    
    img.save(path, "JPEG")


class TestModerationResult:
    """Test ModerationResult class."""
    
    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = ModerationResult(
            is_safe=True,
            confidence=0.95,
            reason="Test reason",
            flags=["flag1", "flag2"],
        )
        
        data = result.to_dict()
        assert data["is_safe"] is True
        assert data["confidence"] == 0.95
        assert data["reason"] == "Test reason"
        assert data["flags"] == ["flag1", "flag2"]
    
    def test_to_dict_no_flags(self):
        """Test to_dict with no flags."""
        result = ModerationResult(
            is_safe=False,
            confidence=0.5,
        )
        
        data = result.to_dict()
        assert data["flags"] == []
        assert data["reason"] is None


class TestContentModerationService:
    """Test ContentModerationService."""
    
    def test_file_not_exists(self, moderation_service):
        """Test checking a non-existent file."""
        result = moderation_service.check_image("/nonexistent/file.jpg")
        
        assert result.is_safe is False
        assert result.confidence == 1.0
        assert "does not exist" in result.reason
    
    def test_file_too_large(self, moderation_service, temp_image_path):
        """Test checking an oversized file."""
        # Create a large file (11MB)
        with open(temp_image_path, "wb") as f:
            f.write(b"0" * (11 * 1024 * 1024))
        
        result = moderation_service.check_image(temp_image_path)
        
        assert result.is_safe is False
        assert result.confidence == 1.0
        assert "too large" in result.reason
    
    def test_image_too_small(self, moderation_service, temp_image_path):
        """Test checking an image below minimum dimensions."""
        create_test_image(temp_image_path, 200, 150, (100, 100, 100))
        
        result = moderation_service.check_image(temp_image_path)
        
        assert result.is_safe is False
        assert result.confidence == 1.0
        assert "too small" in result.reason
    
    def test_valid_complex_image(self, moderation_service, temp_image_path):
        """Test a valid, complex image passes."""
        create_complex_image(temp_image_path, 800, 600)
        
        result = moderation_service.check_image(temp_image_path)
        
        assert result.is_safe is True
        assert result.confidence > 0.5
    
    def test_low_complexity_detection(self, moderation_service, temp_image_path):
        """Test detection of solid color images."""
        # Create a solid blue image (low complexity)
        create_test_image(temp_image_path, 800, 600, (0, 0, 255))
        
        result = moderation_service.check_image(temp_image_path)
        
        assert "low_complexity" in result.flags
    
    def test_skin_tone_detection(self, moderation_service, temp_image_path):
        """Test detection of high skin tone ratios."""
        # Create image with skin tone color
        create_test_image(temp_image_path, 800, 600, (200, 120, 80))
        
        result = moderation_service.check_image(temp_image_path)
        
        # Should flag high skin tone
        assert "high_skin_tone" in result.flags
        assert result.is_safe is False
        assert "skin tone" in result.reason.lower()
    
    def test_check_complexity_varied_image(self, moderation_service, temp_image_path):
        """Test complexity check with varied colors."""
        create_complex_image(temp_image_path, 800, 600)
        
        with Image.open(temp_image_path) as img:
            complexity = moderation_service._check_complexity(img)
        
        # Complex image should have medium-to-high complexity score
        assert complexity > 0.3
    
    def test_check_complexity_solid_color(self, moderation_service, temp_image_path):
        """Test complexity check with solid color."""
        create_test_image(temp_image_path, 800, 600, (128, 128, 128))
        
        with Image.open(temp_image_path) as img:
            complexity = moderation_service._check_complexity(img)
        
        # Solid color should have low complexity
        assert complexity < 0.5
    
    def test_check_skin_tones_no_skin(self, moderation_service):
        """Test skin tone detection with non-skin colors."""
        # Create blue image
        img = Image.new("RGB", (100, 100), (0, 0, 255))
        
        skin_ratio = moderation_service._check_skin_tones(img)
        
        assert skin_ratio < 0.1
    
    def test_check_skin_tones_high_skin(self, moderation_service):
        """Test skin tone detection with high skin tone ratio."""
        # Create image with skin tone
        img = Image.new("RGB", (100, 100), (200, 120, 80))
        
        skin_ratio = moderation_service._check_skin_tones(img)
        
        assert skin_ratio > 0.8  # Should detect most pixels as skin tone
    
    def test_normal_aviation_photo(self, moderation_service, temp_image_path):
        """Test a normal aviation photo (blue sky, metal aircraft)."""
        # Create image with aviation colors (blue sky, gray aircraft)
        # Add some texture/noise to increase complexity
        img = Image.new("RGB", (800, 600))
        pixels = img.load()
        
        import random
        random.seed(42)  # Deterministic
        
        # Top half: blue sky with some variation
        for y in range(300):
            for x in range(800):
                noise = random.randint(-20, 20)
                pixels[x, y] = (
                    max(0, min(255, 50 + noise)),
                    max(0, min(255, 100 + noise)),
                    max(0, min(255, 200 + noise))
                )
        
        # Bottom half: gray aircraft with some variation
        for y in range(300, 600):
            for x in range(800):
                noise = random.randint(-15, 15)
                pixels[x, y] = (
                    max(0, min(255, 180 + noise)),
                    max(0, min(255, 180 + noise)),
                    max(0, min(255, 190 + noise))
                )
        
        img.save(temp_image_path, "JPEG")
        
        result = moderation_service.check_image(temp_image_path)
        
        # Aviation photo should pass
        assert result.is_safe is True
        assert "high_skin_tone" not in result.flags


@pytest.mark.asyncio
async def test_check_photo_content_async(temp_image_path):
    """Test async wrapper for content moderation."""
    create_complex_image(temp_image_path, 800, 600)
    
    result = await check_photo_content(temp_image_path)
    
    assert isinstance(result, ModerationResult)
    assert result.is_safe is True


@pytest.mark.asyncio
async def test_check_photo_content_invalid(temp_image_path):
    """Test async wrapper with invalid image."""
    create_test_image(temp_image_path, 100, 100, (255, 255, 255))
    
    result = await check_photo_content(temp_image_path)
    
    assert result.is_safe is False
    assert "too small" in result.reason
