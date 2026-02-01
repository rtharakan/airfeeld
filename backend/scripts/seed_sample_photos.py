#!/usr/bin/env python3
"""
Seed Sample Photos for Testing

Creates sample test photos for gameplay testing without full Wikimedia Commons integration.
This script downloads a few sample airport photos from public domain sources and seeds them
into the database.

Usage:
    python scripts/seed_sample_photos.py --count 5
    python scripts/seed_sample_photos.py --dry-run
"""

import argparse
import sys
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings
from src.models.photo import Photo
from src.models.base import Airport


# Sample airport photos from Wikimedia Commons (CC0 / Public Domain)
SAMPLE_PHOTOS = [
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/John_F_Kennedy_Airport_%28Unsplash%29.jpg/800px-John_F_Kennedy_Airport_%28Unsplash%29.jpg",
        "icao": "KJFK",
        "airport_name": "John F. Kennedy International Airport",
        "attribution_author": "Unsplash",
        "attribution_license": "CC0 1.0",
        "attribution_source": "Wikimedia Commons",
        "attribution_url": "https://commons.wikimedia.org/wiki/File:John_F_Kennedy_Airport_(Unsplash).jpg"
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Heathrow_Terminal_5C_Iwelumo.jpg/800px-Heathrow_Terminal_5C_Iwelumo.jpg",
        "icao": "EGLL",
        "airport_name": "London Heathrow Airport",
        "attribution_author": "Iwelumo",
        "attribution_license": "CC BY-SA 4.0",
        "attribution_source": "Wikimedia Commons",
        "attribution_url": "https://commons.wikimedia.org/wiki/File:Heathrow_Terminal_5C_Iwelumo.jpg"
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/San_Francisco_International_Airport.jpg/800px-San_Francisco_International_Airport.jpg",
        "icao": "KSFO",
        "airport_name": "San Francisco International Airport",
        "attribution_author": "King of Hearts",
        "attribution_license": "CC BY-SA 4.0",
        "attribution_source": "Wikimedia Commons",
        "attribution_url": "https://commons.wikimedia.org/wiki/File:San_Francisco_International_Airport.jpg"
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Frankfurt_Airport_from_Main_Tower.jpg/800px-Frankfurt_Airport_from_Main_Tower.jpg",
        "icao": "EDDF",
        "airport_name": "Frankfurt Airport",
        "attribution_author": "Dontworry",
        "attribution_license": "CC BY-SA 3.0",
        "attribution_source": "Wikimedia Commons",
        "attribution_url": "https://commons.wikimedia.org/wiki/File:Frankfurt_Airport_from_Main_Tower.jpg"
    },
    {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Narita_International_Airport.jpg/800px-Narita_International_Airport.jpg",
        "icao": "RJAA",
        "airport_name": "Narita International Airport",
        "attribution_author": "Wiiii",
        "attribution_license": "CC BY-SA 3.0",
        "attribution_source": "Wikimedia Commons",
        "attribution_url": "https://commons.wikimedia.org/wiki/File:Narita_International_Airport.jpg"
    }
]


def download_image(url: str) -> bytes:
    """Download image from URL."""
    print(f"  Downloading: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.content


def process_image(image_data: bytes, max_width: int = 800) -> bytes:
    """
    Process image: resize, optimize, convert to WebP, strip EXIF.
    
    Args:
        image_data: Raw image bytes
        max_width: Maximum width in pixels
        
    Returns:
        Processed image bytes (WebP format)
    """
    # Open image
    img = Image.open(BytesIO(image_data))
    
    # Strip EXIF data (important for privacy!)
    if hasattr(img, 'getexif'):
        img = img.convert('RGB')  # Remove all metadata
    
    # Resize if needed (maintain aspect ratio)
    if img.width > max_width:
        aspect_ratio = img.height / img.width
        new_height = int(max_width * aspect_ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    
    # Convert to WebP with optimization
    output = BytesIO()
    img.save(output, format='WEBP', quality=85, method=6, optimize=True)
    return output.getvalue()


def save_photo_file(photo_data: bytes, photo_id: str) -> Path:
    """Save photo file to storage."""
    settings = get_settings()
    photo_path = settings.photo_storage_path / f"{photo_id}.webp"
    
    # Ensure directory exists
    photo_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file
    photo_path.write_bytes(photo_data)
    return photo_path


def seed_photos(count: int, dry_run: bool = False):
    """
    Seed sample photos into the database.
    
    Args:
        count: Number of photos to seed (max: len(SAMPLE_PHOTOS))
        dry_run: If True, don't actually save anything
    """
    settings = get_settings()
    
    # Use synchronous SQLite URL for seeding script
    db_url = settings.database_url.replace('+aiosqlite', '')
    engine = create_engine(db_url, echo=False)
    
    # Limit count to available samples
    count = min(count, len(SAMPLE_PHOTOS))
    
    print(f"{'[DRY RUN] ' if dry_run else ''}Seeding {count} sample photos...\n")
    
    with Session(engine) as session:
        seeded_count = 0
        
        for i, photo_info in enumerate(SAMPLE_PHOTOS[:count]):
            try:
                print(f"Photo {i+1}/{count}: {photo_info['airport_name']}")
                
                # Check if airport exists
                airport = session.execute(
                    select(Airport).where(Airport.icao_code == photo_info['icao'])
                ).scalar_one_or_none()
                
                if not airport:
                    print(f"  ⚠️  Airport {photo_info['icao']} not found in database. Creating...")
                    # Create basic airport entry for testing
                    airport = Airport(
                        icao_code=photo_info['icao'],
                        name=photo_info['airport_name'],
                        country="TEST",  # Will be updated later
                        latitude=0.0,
                        longitude=0.0,
                        elevation_ft=0,
                        airport_type="large_airport"
                    )
                    if not dry_run:
                        session.add(airport)
                        session.flush()
                
                # Download and process image
                image_data = download_image(photo_info['url'])
                processed_data = process_image(image_data)
                file_size = len(processed_data)
                
                print(f"  ✓ Processed: {file_size // 1024}KB (WebP)")
                
                # Generate photo ID
                photo_id = str(uuid.uuid4())
                
                # Save file
                if not dry_run:
                    photo_path = save_photo_file(processed_data, photo_id)
                    print(f"  ✓ Saved: {photo_path}")
                else:
                    print(f"  [DRY RUN] Would save: storage/photos/{photo_id}.webp")
                
                # Create database entry
                photo = Photo(
                    id=photo_id,
                    airport_id=airport.id,
                    filename=f"{photo_id}.webp",
                    file_path=f"storage/photos/{photo_id}.webp",
                    file_size=file_size,
                    mime_type="image/webp",
                    width=800,  # Approximate
                    height=600,  # Approximate
                    uploaded_at=datetime.utcnow(),
                    attribution_author=photo_info.get('attribution_author'),
                    attribution_source=photo_info.get('attribution_source'),
                    attribution_url=photo_info.get('attribution_url'),
                    attribution_license=photo_info.get('attribution_license'),
                    verification_status='approved',  # Pre-approved for testing
                    moderation_status='approved',
                    exif_stripped=True
                )
                
                if not dry_run:
                    session.add(photo)
                    session.flush()
                    print(f"  ✓ Added to database: {photo.id}")
                else:
                    print(f"  [DRY RUN] Would add to database")
                
                seeded_count += 1
                print()
                
            except Exception as e:
                print(f"  ✗ Error: {e}\n")
                continue
        
        if not dry_run:
            session.commit()
            print(f"✓ Successfully seeded {seeded_count}/{count} photos")
        else:
            print(f"[DRY RUN] Would have seeded {seeded_count}/{count} photos")


def main():
    parser = argparse.ArgumentParser(
        description="Seed sample photos for testing gameplay"
    )
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help=f'Number of photos to seed (max: {len(SAMPLE_PHOTOS)})'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without actually downloading or saving'
    )
    
    args = parser.parse_args()
    
    # Validate count
    if args.count < 1:
        print("Error: count must be at least 1")
        sys.exit(1)
    if args.count > len(SAMPLE_PHOTOS):
        print(f"Warning: count limited to {len(SAMPLE_PHOTOS)} available samples")
        args.count = len(SAMPLE_PHOTOS)
    
    try:
        seed_photos(args.count, args.dry_run)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
