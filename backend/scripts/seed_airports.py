"""
Airport Data Seeding Script

Seeds the database with airport data for gameplay.
Uses a curated list of major airports.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database import get_database
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Curated list of major airports for gameplay
AIRPORTS = [
    # North America
    {"code": "KJFK", "iata": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "United States"},
    {"code": "KLAX", "iata": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "United States"},
    {"code": "KORD", "iata": "ORD", "name": "O'Hare International Airport", "city": "Chicago", "country": "United States"},
    {"code": "KDFW", "iata": "DFW", "name": "Dallas/Fort Worth International Airport", "city": "Dallas", "country": "United States"},
    {"code": "KDEN", "iata": "DEN", "name": "Denver International Airport", "city": "Denver", "country": "United States"},
    {"code": "KSFO", "iata": "SFO", "name": "San Francisco International Airport", "city": "San Francisco", "country": "United States"},
    {"code": "KATL", "iata": "ATL", "name": "Hartsfield-Jackson Atlanta International Airport", "city": "Atlanta", "country": "United States"},
    {"code": "KMIA", "iata": "MIA", "name": "Miami International Airport", "city": "Miami", "country": "United States"},
    {"code": "KBOS", "iata": "BOS", "name": "Boston Logan International Airport", "city": "Boston", "country": "United States"},
    {"code": "KSEA", "iata": "SEA", "name": "Seattle-Tacoma International Airport", "city": "Seattle", "country": "United States"},
    {"code": "CYYZ", "iata": "YYZ", "name": "Toronto Pearson International Airport", "city": "Toronto", "country": "Canada"},
    {"code": "CYVR", "iata": "YVR", "name": "Vancouver International Airport", "city": "Vancouver", "country": "Canada"},
    {"code": "MMMX", "iata": "MEX", "name": "Mexico City International Airport", "city": "Mexico City", "country": "Mexico"},
    
    # Europe
    {"code": "EGLL", "iata": "LHR", "name": "London Heathrow Airport", "city": "London", "country": "United Kingdom"},
    {"code": "LFPG", "iata": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris", "country": "France"},
    {"code": "EDDF", "iata": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany"},
    {"code": "EHAM", "iata": "AMS", "name": "Amsterdam Airport Schiphol", "city": "Amsterdam", "country": "Netherlands"},
    {"code": "LEMD", "iata": "MAD", "name": "Adolfo Suárez Madrid–Barajas Airport", "city": "Madrid", "country": "Spain"},
    {"code": "LEBL", "iata": "BCN", "name": "Barcelona–El Prat Airport", "city": "Barcelona", "country": "Spain"},
    {"code": "LIRF", "iata": "FCO", "name": "Leonardo da Vinci–Fiumicino Airport", "city": "Rome", "country": "Italy"},
    {"code": "LSZH", "iata": "ZRH", "name": "Zurich Airport", "city": "Zurich", "country": "Switzerland"},
    {"code": "LOWW", "iata": "VIE", "name": "Vienna International Airport", "city": "Vienna", "country": "Austria"},
    {"code": "ESSA", "iata": "ARN", "name": "Stockholm Arlanda Airport", "city": "Stockholm", "country": "Sweden"},
    
    # Asia-Pacific
    {"code": "RJAA", "iata": "NRT", "name": "Narita International Airport", "city": "Tokyo", "country": "Japan"},
    {"code": "RJTT", "iata": "HND", "name": "Tokyo Haneda Airport", "city": "Tokyo", "country": "Japan"},
    {"code": "RKSI", "iata": "ICN", "name": "Incheon International Airport", "city": "Seoul", "country": "South Korea"},
    {"code": "VHHH", "iata": "HKG", "name": "Hong Kong International Airport", "city": "Hong Kong", "country": "Hong Kong"},
    {"code": "WSSS", "iata": "SIN", "name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore"},
    {"code": "VTBS", "iata": "BKK", "name": "Suvarnabhumi Airport", "city": "Bangkok", "country": "Thailand"},
    {"code": "YSSY", "iata": "SYD", "name": "Sydney Kingsford Smith Airport", "city": "Sydney", "country": "Australia"},
    {"code": "YMML", "iata": "MEL", "name": "Melbourne Airport", "city": "Melbourne", "country": "Australia"},
    {"code": "NZAA", "iata": "AKL", "name": "Auckland Airport", "city": "Auckland", "country": "New Zealand"},
    
    # Middle East
    {"code": "OMDB", "iata": "DXB", "name": "Dubai International Airport", "city": "Dubai", "country": "United Arab Emirates"},
    {"code": "OTHH", "iata": "DOH", "name": "Hamad International Airport", "city": "Doha", "country": "Qatar"},
    {"code": "OEJN", "iata": "JED", "name": "King Abdulaziz International Airport", "city": "Jeddah", "country": "Saudi Arabia"},
    {"code": "LLBG", "iata": "TLV", "name": "Ben Gurion Airport", "city": "Tel Aviv", "country": "Israel"},
    
    # South America
    {"code": "SBGR", "iata": "GRU", "name": "São Paulo/Guarulhos International Airport", "city": "São Paulo", "country": "Brazil"},
    {"code": "SCEL", "iata": "SCL", "name": "Arturo Merino Benítez International Airport", "city": "Santiago", "country": "Chile"},
    {"code": "SAEZ", "iata": "EZE", "name": "Ministro Pistarini International Airport", "city": "Buenos Aires", "country": "Argentina"},
    
    # Africa
    {"code": "FACT", "iata": "CPT", "name": "Cape Town International Airport", "city": "Cape Town", "country": "South Africa"},
    {"code": "HECA", "iata": "CAI", "name": "Cairo International Airport", "city": "Cairo", "country": "Egypt"},
]


async def seed_airports():
    """Seed airport data."""
    settings = get_settings()
    db = get_database()
    
    async with db.get_session() as session:
        logger.info(f"Seeding {len(AIRPORTS)} airports...")
        
        # For now, just log the airports since we don't have an Airport model
        # This will be updated when the Airport model is created
        for airport in AIRPORTS:
            logger.info(
                f"Airport: {airport['code']} - {airport['name']}, "
                f"{airport['city']}, {airport['country']}"
            )
        
        logger.info("Airport seeding complete (logged only - no Airport model yet)")


if __name__ == "__main__":
    asyncio.run(seed_airports())
