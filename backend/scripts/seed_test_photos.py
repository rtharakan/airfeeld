#!/usr/bin/env python3
"""
Seed Test Photos - Quick Setup

Creates a few test photos using simple colored images for gameplay testing.
This is for rapid testing without requiring external downloads.

Usage:
    python scripts/seed_test_photos.py
"""

import sys
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings


# Test airports and their corresponding colors/themes
TEST_PHOTOS = [
    {
        "airport_code": "KJFK",
        "airport_name": "JFK International",
        "color": "#1E40AF",  # Blue
        "text": "New York JFK"
    },
    {
        "airport_code": "EGLL",
        "airport_name": "London Heathrow",
        "color": "#DC2626",  # Red
        "text": "London LHR"
    },
    {
        "airport_code": "KSFO",
        "airport_name": "San Francisco Int'l",
        "color": "#059669",  # Green
        "text": "San Francisco SFO"
    },
    {
        "airport_code": "EDDF",
        "airport_name": "Frankfurt Airport",
        "color": "#7C3AED",  # Purple
        "text": "Frankfurt FRA"
    },
    {
        "airport_code": "RJAA",
        "airport_name": "Tokyo Narita",
        "color": "#EA580C",  # Orange
        "text": "Tokyo NRT"
    }
]


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_test_image(text: str, color: str, width: int = 800, height: int = 600) -> bytes:
    """Create a simple test image with text."""
    # Create image with solid color background
    rgb_color = hex_to_rgb(color)
    img = Image.new('RGB', (width, height), color=rgb_color)
    
    # Add text
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to bitmap if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position (centered)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text in white
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Convert to WebP
    output = BytesIO()
    img.save(output, format='WEBP', quality=85)
    return output.getvalue()


def calculate_file_hash(data: bytes) -> str:
    """Calculate SHA-256 hash of file data."""
    return hashlib.sha256(data).hexdigest()


def seed_test_photos():
    """Seed test photos into the database."""
    settings = get_settings()
    
    # Use synchronous SQLite URL
    db_url = settings.database_url.replace('+aiosqlite', '')
    engine = create_engine(db_url, echo=False)
    
    print(f"Seeding {len(TEST_PHOTOS)} test photos...\n")
    
    with Session(engine) as session:
        seeded_count = 0
        
        for i, photo_info in enumerate(TEST_PHOTOS):
            try:
                print(f"Photo {i+1}/{len(TEST_PHOTOS)}: {photo_info['airport_name']}")
                
                # Generate test image
                image_data = create_test_image(
                    photo_info['text'],
                    photo_info['color']
                )
                
                # Calculate hash
                file_hash = calculate_file_hash(image_data)
                
                # Check if photo already exists
                existing = session.execute(
                    text("SELECT id FROM photos WHERE file_hash = :hash"),
                    {"hash": file_hash}
                ).fetchone()
                
                if existing:
                    print(f"  ⚠️  Photo already exists (hash: {file_hash[:8]}...)")
                    continue
                
                # Generate photo ID
                photo_id = str(uuid.uuid4())
                filename = f"{photo_id}.webp"
                file_path = f"storage/photos/{filename}"
                
                # Save file
                full_path = Path(settings.photo_storage_path) / filename
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_bytes(image_data)
                
                print(f"  ✓ Saved: {file_path} ({len(image_data) // 1024}KB)")
                
                # Insert into database
                session.execute(text("""
                    INSERT INTO photos (
                        id, created_at, updated_at,
                        filename, file_hash, file_size,
                        width, height, mime_type,
                        aircraft_type, airport_code,
                        status, times_used, total_score_awarded
                    ) VALUES (
                        :id, :created_at, :updated_at,
                        :filename, :file_hash, :file_size,
                        :width, :height, :mime_type,
                        :aircraft_type, :airport_code,
                        :status, :times_used, :total_score_awarded
                    )
                """), {
                    "id": photo_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "filename": filename,
                    "file_hash": file_hash,
                    "file_size": len(image_data),
                    "width": 800,
                    "height": 600,
                    "mime_type": "image/webp",
                    "aircraft_type": "Test Airport Photo",
                    "airport_code": photo_info['airport_code'],
                    "status": "approved",
                    "times_used": 0,
                    "total_score_awarded": 0
                })
                
                print(f"  ✓ Added to database: {photo_id}")
                seeded_count += 1
                print()
                
            except Exception as e:
                print(f"  ✗ Error: {e}\n")
                continue
        
        session.commit()
        print(f"✓ Successfully seeded {seeded_count}/{len(TEST_PHOTOS)} photos")
        
        # Show total photos in database
        total = session.execute(text("SELECT COUNT(*) FROM photos")).scalar()
        print(f"📊 Total photos in database: {total}")


if __name__ == '__main__':
    try:
        seed_test_photos()
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)
