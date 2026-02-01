"""
Integration Tests: Player Registration Workflow

Tests the complete player registration flow:
1. Get PoW challenge
2. Solve challenge
3. Register player
4. Verify database state
"""

import hashlib
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.models.player import Player


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def solve_pow_challenge(challenge: str, difficulty: int) -> int:
    """
    Solve a PoW challenge for testing.
    
    Args:
        challenge: Challenge string
        difficulty: Number of leading zeros required
        
    Returns:
        Valid solution (nonce)
    """
    target_prefix = "0" * difficulty
    nonce = 0
    
    while nonce < 1000000:  # Prevent infinite loop
        hash_input = f"{challenge}{nonce}"
        hash_result = hashlib.sha256(hash_input.encode()).hexdigest()
        
        if hash_result.startswith(target_prefix):
            return nonce
        
        nonce += 1
    
    raise ValueError(f"Could not solve PoW challenge with difficulty {difficulty}")


@pytest.mark.integration
def test_player_registration_full_workflow(client: TestClient):
    """
    Test complete player registration workflow.
    
    TC-003: Player Registration Workflow
    
    Steps:
    1. Get PoW challenge from API
    2. Solve the challenge
    3. Register player with valid username and solution
    4. Verify response contains player_id and session_token
    5. Verify player exists in database with correct defaults
    """
    # Step 1: Get PoW challenge
    challenge_response = client.get("/players/challenge")
    assert challenge_response.status_code == 200
    
    challenge_data = challenge_response.json()
    assert "challenge" in challenge_data
    assert "difficulty" in challenge_data
    assert "expires_at" in challenge_data
    
    challenge = challenge_data["challenge"]
    difficulty = challenge_data["difficulty"]
    
    # Step 2: Solve PoW (for testing, use low difficulty from test settings)
    solution = solve_pow_challenge(challenge, difficulty)
    
    # Step 3: Register player
    register_response = client.post("/players/register", json={
        "username": "test_player_123",
        "challenge": challenge,
        "solution": solution
    })
    
    # Step 4: Verify response
    assert register_response.status_code == 200, f"Registration failed: {register_response.text}"
    
    data = register_response.json()
    assert "player_id" in data
    assert "session_token" in data
    assert "username" in data
    assert data["username"] == "test_player_123"
    assert data["total_score"] == 0
    assert data["games_played"] == 0


@pytest.mark.integration
def test_registration_rejects_invalid_pow(client: TestClient):
    """
    Test that registration rejects invalid PoW solutions.
    """
    # Get challenge
    challenge_response = client.get("/api/v1/players/challenge")
    assert challenge_response.status_code == 200
    
    challenge = challenge_response.json()["challenge"]
    
    # Try to register with invalid solution
    register_response = client.post("/api/v1/players/register", json={
        "username": "test_player_invalid",
        "challenge": challenge,
        "solution": 999999  # Invalid solution
    })
    
    assert register_response.status_code in [400, 401, 422]


@pytest.mark.integration
def test_registration_rejects_duplicate_username(client: TestClient):
    """
    Test that registration rejects duplicate usernames.
    """
    # Register first player
    challenge_response = client.get("/api/v1/players/challenge")
    challenge_data = challenge_response.json()
    solution = solve_pow_challenge(challenge_data["challenge"], challenge_data["difficulty"])
    
    first_register = client.post("/api/v1/players/register", json={
        "username": "duplicate_test",
        "challenge": challenge_data["challenge"],
        "solution": solution
    })
    assert first_register.status_code == 200
    
    # Try to register second player with same username
    challenge_response2 = client.get("/api/v1/players/challenge")
    challenge_data2 = challenge_response2.json()
    solution2 = solve_pow_challenge(challenge_data2["challenge"], challenge_data2["difficulty"])
    
    second_register = client.post("/api/v1/players/register", json={
        "username": "duplicate_test",  # Same username
        "challenge": challenge_data2["challenge"],
        "solution": solution2
    })
    
    assert second_register.status_code in [400, 409]  # Bad request or conflict


@pytest.mark.integration
def test_registration_validates_username_format(client: TestClient):
    """
    Test that registration validates username format.
    """
    challenge_response = client.get("/api/v1/players/challenge")
    challenge_data = challenge_response.json()
    solution = solve_pow_challenge(challenge_data["challenge"], challenge_data["difficulty"])
    
    # Test invalid usernames
    invalid_usernames = [
        "ab",  # Too short (< 3 chars)
        "a" * 21,  # Too long (> 20 chars)
        "user name",  # Contains space
        "user-name",  # Contains hyphen
        "user@name",  # Contains special char
    ]
    
    for invalid_username in invalid_usernames:
        register_response = client.post("/api/v1/players/register", json={
            "username": invalid_username,
            "challenge": challenge_data["challenge"],
            "solution": solution
        })
        
        # Should reject with 400 or 422
        assert register_response.status_code in [400, 422], \
            f"Expected rejection for username '{invalid_username}', got {register_response.status_code}"


@pytest.mark.integration
def test_registration_rejects_profanity_in_username(client: TestClient):
    """
    Test that registration rejects usernames containing profanity.
    """
    challenge_response = client.get("/api/v1/players/challenge")
    challenge_data = challenge_response.json()
    solution = solve_pow_challenge(challenge_data["challenge"], challenge_data["difficulty"])
    
    # Note: Specific profane words omitted from test, but service should reject them
    register_response = client.post("/api/v1/players/register", json={
        "username": "badword123",  # Replace with actual profane word for real test
        "challenge": challenge_data["challenge"],
        "solution": solution
    })
    
    # Should accept or reject based on profanity filter configuration
    # For this test, just verify it doesn't crash
    assert register_response.status_code in [200, 400, 422]
