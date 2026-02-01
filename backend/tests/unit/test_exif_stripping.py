"""
Unit Tests: EXIF Data Stripping

Tests that EXIF metadata (including GPS data) is properly stripped from photos.

Privacy requirement: All location and camera metadata must be removed from
uploaded photos to prevent unintentional disclosure of sensitive information.
"""

import io
import os
import pytest
from PIL import Image
from PIL.ExifTags import TAGS, GPS

from src.workers.moderation import strip_exif_data


def create_test_image_with_exif(width: int = 800, height: int = 600) -> bytes:
    """
    Create a test JPEG image with EXIF data including GPS coordinates.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        JPEG image bytes with EXIF data
    """
    try:
        import piexif
        
        # Create a simple image
        img = Image.new('RGB', (width, height), color='blue')
        
        # Create EXIF data using piexif
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Make: b"Test Camera",
                piexif.ImageIFD.Model: b"Test Model v1",
                piexif.ImageIFD.Software: b"Test Software",
                piexif.ImageIFD.DateTime: b"2026:02:01 12:00:00",
                piexif.ImageIFD.Artist: b"Test Photographer",
                piexif.ImageIFD.Copyright: b"Copyright Test 2026",
            },
            "GPS": {
                piexif.GPSIFD.GPSLatitudeRef: b"N",
                piexif.GPSIFD.GPSLatitude: ((40, 1), (38, 1), (51, 100)),
                piexif.GPSIFD.GPSLongitudeRef: b"W",
                piexif.GPSIFD.GPSLongitude: ((73, 1), (46, 1), (44, 100)),
                piexif.GPSIFD.GPSAltitudeRef: 0,
                piexif.GPSIFD.GPSAltitude: (10, 1),
            }
        }
        
        # Convert to bytes
        exif_bytes = piexif.dump(exif_dict)
        
        # Save with EXIF
        output = io.BytesIO()
        img.save(output, format='JPEG', exif=exif_bytes)
        
        return output.getvalue()
    except ImportError:
        # Fallback: create image without EXIF and warn
        img = Image.new('RGB', (width, height), color='blue')
        output = io.BytesIO()
        img.save(output, format='JPEG')
        return output.getvalue()


def get_exif_data(image_bytes: bytes) -> dict:
    """
    Extract EXIF data from image bytes.
    
    Args:
        image_bytes: JPEG image bytes
        
    Returns:
        Dictionary of EXIF tags
    """
    img = Image.open(io.BytesIO(image_bytes))
    exif = img.getexif()
    
    if exif is None:
        return {}
    
    exif_data = {}
    for tag_id, value in exif.items():
        tag_name = TAGS.get(tag_id, tag_id)
        exif_data[tag_name] = value
    
    return exif_data


def has_gps_data(image_bytes: bytes) -> bool:
    """
    Check if image contains GPS data.
    
    Args:
        image_bytes: JPEG image bytes
        
    Returns:
        True if GPS data present, False otherwise
    """
    img = Image.open(io.BytesIO(image_bytes))
    exif = img.getexif()
    
    if exif is None:
        return False
    
    # Check for GPS IFD tag (0x8825)
    gps_ifd = exif.get_ifd(0x8825)
    return gps_ifd is not None and len(gps_ifd) > 0


@pytest.mark.unit
def test_create_image_has_exif():
    """
    Verify that our test image creation function produces images with EXIF data.
    """
    image_bytes = create_test_image_with_exif()
    exif_data = get_exif_data(image_bytes)
    
    # Should have EXIF data
    assert len(exif_data) > 0, "Test image should contain EXIF data"
    
    # Should have GPS data
    assert has_gps_data(image_bytes), "Test image should contain GPS data"


@pytest.mark.unit
def test_strip_exif_removes_all_metadata():
    """
    Test that strip_exif_data removes all EXIF metadata.
    
    TC-006: EXIF Stripping Validation
    
    Privacy requirement: No metadata should remain after stripping.
    """
    # Create image with EXIF
    original_bytes = create_test_image_with_exif()
    
    # Verify EXIF present before stripping
    exif_before = get_exif_data(original_bytes)
    assert len(exif_before) > 0, "Original image should have EXIF data"
    
    # Strip EXIF
    stripped_bytes = strip_exif_data(original_bytes)
    
    # Verify EXIF absent after stripping
    exif_after = get_exif_data(stripped_bytes)
    assert len(exif_after) == 0, "Stripped image should have no EXIF data"


@pytest.mark.unit
def test_strip_exif_removes_gps_data():
    """
    Test that GPS coordinates are specifically removed.
    
    Privacy requirement: GPS coordinates must be removed to prevent
    location tracking from uploaded photos.
    """
    # Create image with GPS data
    original_bytes = create_test_image_with_exif()
    
    # Verify GPS present before stripping
    assert has_gps_data(original_bytes), "Original image should have GPS data"
    
    # Strip EXIF
    stripped_bytes = strip_exif_data(original_bytes)
    
    # Verify GPS absent after stripping
    assert not has_gps_data(stripped_bytes), "Stripped image should have no GPS data"


@pytest.mark.unit
def test_strip_exif_preserves_image_content():
    """
    Test that EXIF stripping preserves the actual image pixels.
    
    The image should remain visually identical after stripping.
    """
    # Create image
    original_bytes = create_test_image_with_exif(width=100, height=100)
    
    # Strip EXIF
    stripped_bytes = strip_exif_data(original_bytes)
    
    # Load both images
    original_img = Image.open(io.BytesIO(original_bytes))
    stripped_img = Image.open(io.BytesIO(stripped_bytes))
    
    # Check dimensions preserved
    assert original_img.size == stripped_img.size, "Image dimensions should be preserved"
    
    # Check pixels are identical (or very close due to compression)
    original_pixels = list(original_img.getdata())
    stripped_pixels = list(stripped_img.getdata())
    
    # Allow for minor JPEG compression differences
    matching_pixels = sum(1 for o, s in zip(original_pixels, stripped_pixels) if o == s)
    total_pixels = len(original_pixels)
    match_ratio = matching_pixels / total_pixels
    
    assert match_ratio > 0.95, f"Pixels should match (got {match_ratio:.1%})"


@pytest.mark.unit
def test_strip_exif_reduces_file_size():
    """
    Test that EXIF stripping reduces file size.
    
    Removing metadata should reduce the file size (privacy benefit + performance).
    """
    # Create image with EXIF
    original_bytes = create_test_image_with_exif()
    
    # Strip EXIF
    stripped_bytes = strip_exif_data(original_bytes)
    
    # Compare sizes
    original_size = len(original_bytes)
    stripped_size = len(stripped_bytes)
    
    assert stripped_size <= original_size, \
        f"Stripped image should be smaller or equal (got {stripped_size} vs {original_size} bytes)"


@pytest.mark.unit
def test_strip_exif_handles_image_without_exif():
    """
    Test that stripping handles images that have no EXIF data gracefully.
    """
    # Create image without EXIF
    img = Image.new('RGB', (100, 100), color='red')
    output = io.BytesIO()
    img.save(output, format='JPEG')
    original_bytes = output.getvalue()
    
    # Verify no EXIF present
    exif_before = get_exif_data(original_bytes)
    assert len(exif_before) == 0, "Image should have no EXIF data"
    
    # Strip EXIF (should not crash)
    stripped_bytes = strip_exif_data(original_bytes)
    
    # Verify still no EXIF
    exif_after = get_exif_data(stripped_bytes)
    assert len(exif_after) == 0, "Image should still have no EXIF data"
    
    # Image should still be valid
    img_after = Image.open(io.BytesIO(stripped_bytes))
    assert img_after.size == (100, 100)


@pytest.mark.unit
def test_strip_exif_validates_input_type():
    """
    Test that strip_exif_data validates input is valid image data.
    """
    # Test with invalid input
    invalid_inputs = [
        b"",  # Empty bytes
        b"not an image",  # Random bytes
        b"GIF89a...",  # Wrong format (GIF)
    ]
    
    for invalid_input in invalid_inputs:
        with pytest.raises((ValueError, IOError, Exception)):
            strip_exif_data(invalid_input)
