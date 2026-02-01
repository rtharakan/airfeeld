#!/usr/bin/env python3
"""
Seed script for Airfeeld database
Creates sample data for development and testing
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend src to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from src.database import engine, async_session
from src.models import Player, Photo, Base
import uuid
from datetime import datetime

# Sample airports for testing
SAMPLE_AIRPORTS = [
    {
        "name": "Los Angeles International Airport",
        "iata_code": "LAX",
        "difficulty": "easy",
    },
    {
        "name": "John F. Kennedy International Airport",
        "iata_code": "JFK",
        "difficulty": "easy",
    },
    {
        "name": "London Heathrow Airport",
        "iata_code": "LHR",
        "difficulty": "easy",
    },
    {
        "name": "Tokyo Narita International Airport",
        "iata_code": "NRT",
        "difficulty": "medium",
    },
    {
        "name": "Dubai International Airport",
        "iata_code": "DXB",
        "difficulty": "medium",
    },
    {
        "name": "Singapore Changi Airport",
        "iata_code": "SIN",
        "difficulty": "medium",
    },
    {
        "name": "Queenstown Airport",
        "iata_code": "ZQN",
        "difficulty": "hard",
    },
    {
        "name": "Reykjavik Keflavik Airport",
        "iata_code": "KEF",
        "difficulty": "hard",
    },
]

# Sample players for testing
SAMPLE_PLAYERS = [
    {"username": "AviationFan42", "total_score": 1250, "rounds_played": 45, "correct_guesses": 38},
    {"username": "PlaneSpotter99", "total_score": 980, "rounds_played": 35, "correct_guesses": 28},
    {"username": "SkyWatcher", "total_score": 750, "rounds_played": 28, "correct_guesses": 21},
    {"username": "RunwayHunter", "total_score": 620, "rounds_played": 25, "correct_guesses": 18},
    {"username": "CloudChaser", "total_score": 450, "rounds_played": 20, "correct_guesses": 12},
]


async def seed_database():
    """Seed the database with sample data"""
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        print("🌱 Seeding database...")
        
        # Create sample players
        print("  Creating sample players...")
        for player_data in SAMPLE_PLAYERS:
            player = Player(
                id=str(uuid.uuid4()),
                username=player_data["username"],
                total_score=player_data["total_score"],
                rounds_played=player_data["rounds_played"],
                correct_guesses=player_data["correct_guesses"],
                hashed_ip="seed_" + player_data["username"].lower(),
                created_at=datetime.utcnow(),
            )
            session.add(player)
        
        # Create sample photos (without actual image data)
        print("  Creating sample photo entries...")
        for airport in SAMPLE_AIRPORTS:
            photo = Photo(
                id=str(uuid.uuid4()),
                airport_name=airport["name"],
                iata_code=airport["iata_code"],
                difficulty=airport["difficulty"],
                file_path=f"photos/{airport['iata_code'].lower()}_sample.jpg",
                file_hash="sample_hash_" + airport["iata_code"],
                perceptual_hash="sample_phash_" + airport["iata_code"],
                moderation_status="approved",
                times_played=0,
                times_guessed_correctly=0,
                created_at=datetime.utcnow(),
            )
            session.add(photo)
        
        await session.commit()
        print("✅ Database seeded successfully!")
        print(f"   - {len(SAMPLE_PLAYERS)} players created")
        print(f"   - {len(SAMPLE_AIRPORTS)} photos created")


async def clear_database():
    """Clear all data from the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("🗑️  Database cleared!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        asyncio.run(clear_database())
    else:
        asyncio.run(seed_database())
