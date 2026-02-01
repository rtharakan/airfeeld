"""
Integration Tests: Gameplay Workflow

Tests the complete gameplay flow:
1. Start game round (get photo)
2. Submit guess
3. Receive feedback
4. Verify score update
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def authenticated_player(client: TestClient):
    """
    Create and authenticate a test player.
    
    Returns:
        dict with player_id, username, session_token
    """
    # Get challenge
    challenge_response = client.get("/api/v1/players/challenge")
    challenge_data = challenge_response.json()
    
    # Solve PoW (simplified for testing)
    import hashlib
    challenge = challenge_data["challenge"]
    difficulty = challenge_data["difficulty"]
    
    nonce = 0
    target_prefix = "0" * difficulty
    
    while nonce < 1000000:
        hash_input = f"{challenge}{nonce}"
        hash_result = hashlib.sha256(hash_input.encode()).hexdigest()
        if hash_result.startswith(target_prefix):
            break
        nonce += 1
    
    # Register player
    register_response = client.post("/api/v1/players/register", json={
        "username": f"test_player_{hash(challenge) % 10000}",
        "challenge": challenge,
        "solution": nonce
    })
    
    assert register_response.status_code == 200
    return register_response.json()


@pytest.mark.integration
def test_complete_game_round(client: TestClient, authenticated_player: dict):
    """
    Test complete game round workflow.
    
    TC-004: Gameplay Full Round
    
    Steps:
    1. Start game (get photo and round token)
    2. Submit guess (first attempt)
    3. Verify feedback (correct/incorrect, score)
    4. Verify game round is completed
    5. Verify player score is updated
    """
    session_token = authenticated_player["session_token"]
    
    # Step 1: Start game
    game_response = client.post(
        "/api/v1/games/start",
        headers={"Authorization": f"Bearer {session_token}"}
    )
    
    assert game_response.status_code == 200, f"Game start failed: {game_response.text}"
    
    game_data = game_response.json()
    assert "round_id" in game_data
    assert "photo_url" in game_data
    assert "round_token" in game_data
    
    round_id = game_data["round_id"]
    round_token = game_data["round_token"]
    
    # Step 2: Submit guess
    # For testing, we'll try a valid airport code
    guess_response = client.post(
        f"/api/v1/games/{round_id}/guess",
        headers={"Authorization": f"Bearer {session_token}"},
        json={
            "guess": "KJFK",  # Try JFK
            "round_token": round_token,
            "attempt": 1
        }
    )
    
    assert guess_response.status_code == 200, f"Guess submission failed: {guess_response.text}"
    
    # Step 3: Verify feedback
    feedback = guess_response.json()
    assert "correct" in feedback
    assert "score" in feedback
    assert "correct_airport" in feedback
    assert isinstance(feedback["correct"], bool)
    assert isinstance(feedback["score"], (int, float))
    assert feedback["score"] >= 0
    
    # Valid scores: 0 (wrong), 3 (attempt 3), 5 (attempt 2), 10 (attempt 1)
    assert feedback["score"] in [0, 3, 5, 10]
    
    # If correct on first attempt, score should be 10
    if feedback["correct"]:
        assert feedback["score"] == 10
    
    # Step 4: Verify player stats updated
    # Get player stats (if endpoint exists) or check leaderboard
    leaderboard_response = client.get("/api/v1/players/leaderboard")
    assert leaderboard_response.status_code == 200
    
    leaderboard = leaderboard_response.json()
    # Player should appear in leaderboard with updated games_played
    player_in_leaderboard = next(
        (p for p in leaderboard.get("players", []) if p["player_id"] == authenticated_player["player_id"]),
        None
    )
    
    if player_in_leaderboard:
        assert player_in_leaderboard["games_played"] >= 1


@pytest.mark.integration
def test_game_round_multiple_attempts(client: TestClient, authenticated_player: dict):
    """
    Test game round with multiple guess attempts.
    """
    session_token = authenticated_player["session_token"]
    
    # Start game
    game_response = client.post(
        "/api/v1/games/start",
        headers={"Authorization": f"Bearer {session_token}"}
    )
    
    assert game_response.status_code == 200
    game_data = game_response.json()
    round_id = game_data["round_id"]
    round_token = game_data["round_token"]
    
    # Attempt 1: Wrong guess
    guess1 = client.post(
        f"/api/v1/games/{round_id}/guess",
        headers={"Authorization": f"Bearer {session_token}"},
        json={
            "guess": "XXXX",  # Invalid airport
            "round_token": round_token,
            "attempt": 1
        }
    )
    
    # Should get feedback (likely incorrect unless XXXX exists)
    assert guess1.status_code in [200, 400, 404]
    
    if guess1.status_code == 200:
        feedback1 = guess1.json()
        
        # If wrong, should allow attempt 2
        if not feedback1.get("correct"):
            guess2 = client.post(
                f"/api/v1/games/{round_id}/guess",
                headers={"Authorization": f"Bearer {session_token}"},
                json={
                    "guess": "KJFK",
                    "round_token": round_token,
                    "attempt": 2
                }
            )
            
            assert guess2.status_code == 200
            feedback2 = guess2.json()
            
            # If correct on attempt 2, score should be 5
            if feedback2.get("correct"):
                assert feedback2["score"] == 5


@pytest.mark.integration
def test_game_requires_authentication(client: TestClient):
    """
    Test that game endpoints require authentication.
    """
    # Try to start game without token
    game_response = client.post("/api/v1/games/start")
    assert game_response.status_code in [401, 403]
    
    # Try to submit guess without token
    guess_response = client.post(
        "/api/v1/games/some-round-id/guess",
        json={
            "guess": "KJFK",
            "round_token": "fake-token",
            "attempt": 1
        }
    )
    assert guess_response.status_code in [401, 403]


@pytest.mark.integration
def test_game_rejects_invalid_round_token(client: TestClient, authenticated_player: dict):
    """
    Test that game rejects invalid round tokens (security check).
    """
    session_token = authenticated_player["session_token"]
    
    # Start game
    game_response = client.post(
        "/api/v1/games/start",
        headers={"Authorization": f"Bearer {session_token}"}
    )
    
    assert game_response.status_code == 200
    game_data = game_response.json()
    round_id = game_data["round_id"]
    
    # Try to submit with wrong round token
    guess_response = client.post(
        f"/api/v1/games/{round_id}/guess",
        headers={"Authorization": f"Bearer {session_token}"},
        json={
            "guess": "KJFK",
            "round_token": "invalid-token",
            "attempt": 1
        }
    )
    
    # Should reject with 400 or 403
    assert guess_response.status_code in [400, 403]


@pytest.mark.integration
def test_game_prevents_replaying_same_round(client: TestClient, authenticated_player: dict):
    """
    Test that completed rounds cannot be replayed.
    """
    session_token = authenticated_player["session_token"]
    
    # Start game
    game_response = client.post(
        "/api/v1/games/start",
        headers={"Authorization": f"Bearer {session_token}"}
    )
    
    assert game_response.status_code == 200
    game_data = game_response.json()
    round_id = game_data["round_id"]
    round_token = game_data["round_token"]
    
    # Submit first guess
    guess1 = client.post(
        f"/api/v1/games/{round_id}/guess",
        headers={"Authorization": f"Bearer {session_token}"},
        json={
            "guess": "KJFK",
            "round_token": round_token,
            "attempt": 1
        }
    )
    
    assert guess1.status_code == 200
    
    # Try to submit again for same round
    guess2 = client.post(
        f"/api/v1/games/{round_id}/guess",
        headers={"Authorization": f"Bearer {session_token}"},
        json={
            "guess": "EGLL",
            "round_token": round_token,
            "attempt": 1  # Same attempt number
        }
    )
    
    # Should reject (round already has guess for attempt 1)
    # Acceptable status codes: 400 (bad request) or 409 (conflict)
    assert guess2.status_code in [400, 409]
