"""
Integration Tests: Leaderboard

Tests the leaderboard functionality:
1. Display player rankings
2. Correct sorting by score
3. Privacy (no sensitive data exposed)
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def create_test_player(client: TestClient, username: str) -> dict:
    """
    Helper to create a test player.
    
    Args:
        client: Test client
        username: Username for player
        
    Returns:
        Player data including session_token
    """
    import hashlib
    
    # Get challenge
    challenge_response = client.get("/api/v1/players/challenge")
    challenge_data = challenge_response.json()
    
    challenge = challenge_data["challenge"]
    difficulty = challenge_data["difficulty"]
    
    # Solve PoW
    nonce = 0
    target_prefix = "0" * difficulty
    
    while nonce < 1000000:
        hash_input = f"{challenge}{nonce}"
        hash_result = hashlib.sha256(hash_input.encode()).hexdigest()
        if hash_result.startswith(target_prefix):
            break
        nonce += 1
    
    # Register
    register_response = client.post("/api/v1/players/register", json={
        "username": username,
        "challenge": challenge,
        "solution": nonce
    })
    
    assert register_response.status_code == 200
    return register_response.json()


@pytest.mark.integration
def test_leaderboard_returns_player_list(client: TestClient):
    """
    Test that leaderboard returns list of players.
    
    TC-005: Leaderboard Display
    """
    # Query leaderboard
    leaderboard_response = client.get("/api/v1/players/leaderboard")
    
    assert leaderboard_response.status_code == 200
    
    leaderboard = leaderboard_response.json()
    assert "players" in leaderboard or isinstance(leaderboard, list)
    
    # If players list exists, verify structure
    players = leaderboard.get("players", leaderboard)
    
    if len(players) > 0:
        # Check first player has required fields
        first_player = players[0]
        assert "username" in first_player
        assert "total_score" in first_player
        assert "games_played" in first_player


@pytest.mark.integration
def test_leaderboard_sorting(client: TestClient):
    """
    Test that leaderboard is sorted by score (descending).
    """
    # Create multiple players and have them play games
    player1 = create_test_player(client, f"test_leader_a")
    player2 = create_test_player(client, f"test_leader_b")
    player3 = create_test_player(client, f"test_leader_c")
    
    # Play games to generate different scores
    for player in [player1, player2, player3]:
        session_token = player["session_token"]
        
        # Start and complete a game
        game_response = client.post(
            "/api/v1/games/start",
            headers={"Authorization": f"Bearer {session_token}"}
        )
        
        if game_response.status_code == 200:
            game_data = game_response.json()
            
            # Submit guess
            client.post(
                f"/api/v1/games/{game_data['round_id']}/guess",
                headers={"Authorization": f"Bearer {session_token}"},
                json={
                    "guess": "KJFK",
                    "round_token": game_data["round_token"],
                    "attempt": 1
                }
            )
    
    # Get leaderboard
    leaderboard_response = client.get("/api/v1/players/leaderboard")
    assert leaderboard_response.status_code == 200
    
    leaderboard = leaderboard_response.json()
    players = leaderboard.get("players", leaderboard)
    
    # Verify sorting (descending by score)
    if len(players) > 1:
        scores = [p["total_score"] for p in players]
        assert scores == sorted(scores, reverse=True), "Leaderboard should be sorted by score descending"


@pytest.mark.integration
def test_leaderboard_limits_to_100(client: TestClient):
    """
    Test that leaderboard returns maximum 100 players.
    """
    leaderboard_response = client.get("/api/v1/players/leaderboard")
    assert leaderboard_response.status_code == 200
    
    leaderboard = leaderboard_response.json()
    players = leaderboard.get("players", leaderboard)
    
    assert len(players) <= 100, "Leaderboard should return maximum 100 players"


@pytest.mark.integration
def test_leaderboard_privacy(client: TestClient):
    """
    Test that leaderboard does not expose sensitive data.
    
    Privacy requirements:
    - No session tokens
    - No IP addresses
    - No email addresses
    - No internal IDs exposed
    """
    # Create a test player
    player = create_test_player(client, f"privacy_test_player")
    
    # Get leaderboard
    leaderboard_response = client.get("/api/v1/players/leaderboard")
    assert leaderboard_response.status_code == 200
    
    leaderboard = leaderboard_response.json()
    players = leaderboard.get("players", leaderboard)
    
    # Check each player for privacy violations
    for player_data in players:
        # Should have these fields
        assert "username" in player_data
        assert "total_score" in player_data
        
        # Should NOT have these fields
        assert "session_token" not in player_data
        assert "ip_address" not in player_data
        assert "email" not in player_data
        assert "password" not in player_data
        
        # Player ID can be exposed (it's not sensitive), but verify it's not a raw DB ID
        if "player_id" in player_data:
            player_id = player_data["player_id"]
            # Should be UUID format, not sequential integer
            assert len(str(player_id)) > 10, "Player ID should be UUID, not sequential integer"


@pytest.mark.integration
def test_leaderboard_accessible_without_auth(client: TestClient):
    """
    Test that leaderboard is accessible without authentication.
    
    Leaderboard should be public data.
    """
    # No authentication header
    leaderboard_response = client.get("/api/v1/players/leaderboard")
    
    # Should succeed (200 OK)
    assert leaderboard_response.status_code == 200


@pytest.mark.integration
def test_leaderboard_handles_no_players(client: TestClient):
    """
    Test that leaderboard handles empty case gracefully.
    """
    leaderboard_response = client.get("/api/v1/players/leaderboard")
    assert leaderboard_response.status_code == 200
    
    leaderboard = leaderboard_response.json()
    players = leaderboard.get("players", leaderboard)
    
    # Should return empty list, not error
    assert isinstance(players, list)


@pytest.mark.integration
def test_leaderboard_includes_rank(client: TestClient):
    """
    Test that leaderboard includes rank for each player.
    """
    # Create test players
    for i in range(3):
        create_test_player(client, f"ranked_player_{i}")
    
    leaderboard_response = client.get("/api/v1/players/leaderboard")
    assert leaderboard_response.status_code == 200
    
    leaderboard = leaderboard_response.json()
    players = leaderboard.get("players", leaderboard)
    
    if len(players) > 0:
        # Check if rank is included (optional requirement)
        # If implemented, verify ranks are sequential
        if "rank" in players[0]:
            ranks = [p["rank"] for p in players]
            assert ranks == list(range(1, len(players) + 1)), "Ranks should be sequential starting from 1"
