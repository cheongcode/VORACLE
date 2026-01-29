"""
Mock Data for VORACLE Testing

Provides realistic mock VALORANT match data for testing the pipeline
without requiring actual GRID API access.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
import random


# Sample team and player data
MOCK_TEAMS = {
    "Cloud9": {
        "id": "team_c9_001",
        "name": "Cloud9",
        "players": [
            {"id": "player_001", "name": "jakee", "role": "duelist"},
            {"id": "player_002", "name": "Xeppaa", "role": "initiator"},
            {"id": "player_003", "name": "runi", "role": "controller"},
            {"id": "player_004", "name": "moose", "role": "sentinel"},
            {"id": "player_005", "name": "eeiu", "role": "flex"},
        ],
    },
    "Sentinels": {
        "id": "team_sen_001",
        "name": "Sentinels",
        "players": [
            {"id": "player_011", "name": "TenZ", "role": "duelist"},
            {"id": "player_012", "name": "zekken", "role": "duelist"},
            {"id": "player_013", "name": "Sacy", "role": "initiator"},
            {"id": "player_014", "name": "johnqt", "role": "controller"},
            {"id": "player_015", "name": "bang", "role": "sentinel"},
        ],
    },
    "LOUD": {
        "id": "team_loud_001",
        "name": "LOUD",
        "players": [
            {"id": "player_021", "name": "aspas", "role": "duelist"},
            {"id": "player_022", "name": "Less", "role": "initiator"},
            {"id": "player_023", "name": "tuyz", "role": "controller"},
            {"id": "player_024", "name": "cauanzin", "role": "sentinel"},
            {"id": "player_025", "name": "qck", "role": "flex"},
        ],
    },
}

# VALORANT maps
MAPS = ["Ascent", "Bind", "Haven", "Split", "Icebox", "Breeze", "Fracture", "Pearl", "Lotus", "Sunset"]

# Agents by role
AGENTS = {
    "duelist": ["Jett", "Raze", "Reyna", "Phoenix", "Yoru", "Neon", "Iso"],
    "initiator": ["Sova", "Breach", "Skye", "KAY/O", "Fade", "Gekko"],
    "controller": ["Brimstone", "Omen", "Viper", "Astra", "Harbor", "Clove"],
    "sentinel": ["Sage", "Cypher", "Killjoy", "Chamber", "Deadlock"],
    "flex": ["Jett", "Raze", "Sova", "Skye", "KAY/O", "Omen", "Chamber"],
}


def _generate_player_stats(
    player: dict,
    match_id: str,
    team_name: str,
    is_winner: bool,
    round_count: int,
) -> dict[str, Any]:
    """Generate realistic player stats for a match."""
    role = player.get("role", "flex")
    
    # Base stats vary by role
    if role == "duelist":
        base_kills = random.randint(15, 28)
        base_deaths = random.randint(10, 18)
        fb_chance = 0.35
    elif role == "initiator":
        base_kills = random.randint(12, 22)
        base_deaths = random.randint(11, 17)
        fb_chance = 0.15
    elif role == "controller":
        base_kills = random.randint(10, 18)
        base_deaths = random.randint(12, 18)
        fb_chance = 0.10
    elif role == "sentinel":
        base_kills = random.randint(11, 19)
        base_deaths = random.randint(10, 16)
        fb_chance = 0.12
    else:
        base_kills = random.randint(12, 22)
        base_deaths = random.randint(11, 17)
        fb_chance = 0.20
    
    # Adjust for win/loss
    if is_winner:
        base_kills = int(base_kills * 1.1)
        base_deaths = int(base_deaths * 0.9)
    else:
        base_kills = int(base_kills * 0.9)
        base_deaths = int(base_deaths * 1.1)
    
    kills = max(1, base_kills)
    deaths = max(1, base_deaths)
    assists = random.randint(2, 10)
    
    # Calculate ACS (Average Combat Score)
    damage = kills * random.randint(120, 180) + assists * random.randint(20, 50)
    acs = round(damage / max(1, round_count), 1)
    
    # First bloods
    first_bloods = sum(1 for _ in range(round_count) if random.random() < fb_chance)
    
    # Pick agent based on role
    agent = random.choice(AGENTS.get(role, AGENTS["flex"]))
    
    return {
        "playerId": player["id"],
        "playerName": player["name"],
        "teamName": team_name,
        "agent": agent,
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "acs": acs,
        "firstBloods": first_bloods,
        "damagePerRound": round(damage / max(1, round_count), 1),
    }


def _generate_rounds(
    team_a: str,
    team_b: str,
    score_a: int,
    score_b: int,
) -> list[dict[str, Any]]:
    """Generate round-by-round data."""
    total_rounds = score_a + score_b
    rounds = []
    
    # Distribute wins across rounds
    team_a_wins = [True] * score_a + [False] * score_b
    random.shuffle(team_a_wins)
    
    for i, team_a_won in enumerate(team_a_wins):
        round_num = i + 1
        
        # Determine side (first 12 rounds: team_a attacks, then swap)
        if round_num <= 12:
            team_a_side = "attack"
        elif round_num <= 24:
            team_a_side = "defense"
        else:
            # Overtime
            team_a_side = "attack" if (round_num - 24) % 2 == 1 else "defense"
        
        winner = team_a if team_a_won else team_b
        winner_side = team_a_side if team_a_won else ("defense" if team_a_side == "attack" else "attack")
        
        # Economy type
        is_pistol = round_num in [1, 13, 25]
        if is_pistol:
            eco_type = "pistol"
        else:
            eco_type = random.choice(["full_buy", "full_buy", "full_buy", "eco", "force_buy", "half_buy"])
        
        rounds.append({
            "roundNumber": round_num,
            "winner": winner,
            "winnerSide": winner_side,
            "isPistol": is_pistol,
            "economyType": eco_type,
            "spikePlanted": random.random() < 0.65,
            "spikeDefused": random.random() < 0.25 if winner_side == "defense" else False,
        })
    
    return rounds


def _generate_match(
    match_id: str,
    team_name: str,
    opponent_name: str,
    date: datetime,
    team_data: dict,
    opponent_data: dict,
) -> dict[str, Any]:
    """Generate a complete mock match."""
    # Determine winner (slightly favor the target team for interesting data)
    team_wins = random.random() < 0.55
    
    # Generate scores
    if team_wins:
        score_team = 13 + random.randint(0, 3) if random.random() < 0.2 else 13
        score_opponent = random.randint(5, 12)
    else:
        score_opponent = 13 + random.randint(0, 3) if random.random() < 0.2 else 13
        score_team = random.randint(5, 12)
    
    winner = team_name if team_wins else opponent_name
    map_name = random.choice(MAPS)
    total_rounds = score_team + score_opponent
    
    # Generate player stats
    team_players = team_data.get("players", [])
    opponent_players = opponent_data.get("players", [])
    
    player_stats = []
    for player in team_players:
        stats = _generate_player_stats(player, match_id, team_name, team_wins, total_rounds)
        player_stats.append(stats)
    
    for player in opponent_players:
        stats = _generate_player_stats(player, match_id, opponent_name, not team_wins, total_rounds)
        player_stats.append(stats)
    
    # Generate rounds
    rounds = _generate_rounds(team_name, opponent_name, score_team, score_opponent)
    
    return {
        "id": match_id,
        "date": date.isoformat(),
        "map": map_name,
        "teams": [
            {
                "name": team_name,
                "score": score_team,
                "isWinner": team_wins,
            },
            {
                "name": opponent_name,
                "score": score_opponent,
                "isWinner": not team_wins,
            },
        ],
        "winner": winner,
        "players": player_stats,
        "rounds": rounds,
    }


def get_mock_match_list(team_name: str = "Cloud9", n_matches: int = 10) -> dict[str, Any]:
    """
    Get mock match list for a team.
    
    Args:
        team_name: Name of the team to fetch matches for.
        n_matches: Number of matches to generate.
        
    Returns:
        Mock API response with match list.
    """
    team_data = MOCK_TEAMS.get(team_name, MOCK_TEAMS["Cloud9"])
    opponents = [t for t in MOCK_TEAMS.keys() if t != team_name]
    
    matches = []
    base_date = datetime.now()
    
    for i in range(n_matches):
        match_id = f"match_{team_name.lower().replace(' ', '_')}_{i+1:03d}"
        opponent = random.choice(opponents)
        date = base_date - timedelta(days=i * random.randint(2, 7))
        
        matches.append({
            "id": match_id,
            "date": date.isoformat(),
            "opponent": opponent,
            "event": f"VCT {random.choice(['Americas', 'EMEA', 'Pacific'])} {random.choice(['Stage 1', 'Stage 2', 'Playoffs'])}",
        })
    
    return {
        "team": {
            "id": team_data["id"],
            "name": team_name,
            "matches": matches,
        }
    }


def get_mock_match_detail(match_id: str, team_name: str = "Cloud9") -> dict[str, Any]:
    """
    Get mock match details.
    
    Args:
        match_id: The match ID to fetch details for.
        team_name: Name of the primary team.
        
    Returns:
        Mock API response with full match details.
    """
    team_data = MOCK_TEAMS.get(team_name, MOCK_TEAMS["Cloud9"])
    opponents = [t for t in MOCK_TEAMS.keys() if t != team_name]
    opponent_name = random.choice(opponents)
    opponent_data = MOCK_TEAMS[opponent_name]
    
    # Generate a seeded random for consistent results per match_id
    random.seed(hash(match_id) % (2**32))
    
    match_data = _generate_match(
        match_id=match_id,
        team_name=team_name,
        opponent_name=opponent_name,
        date=datetime.now() - timedelta(days=random.randint(1, 30)),
        team_data=team_data,
        opponent_data=opponent_data,
    )
    
    # Reset random seed
    random.seed()
    
    return {"match": match_data}


def get_mock_matches(team_name: str = "Cloud9", n_matches: int = 10) -> list[dict[str, Any]]:
    """
    Get complete mock match data for a team.
    
    This combines match list and details into a single response,
    useful for testing the full pipeline.
    
    Args:
        team_name: Name of the team.
        n_matches: Number of matches to generate.
        
    Returns:
        List of complete match data dictionaries.
    """
    match_list = get_mock_match_list(team_name, n_matches)
    matches = []
    
    for match_info in match_list["team"]["matches"]:
        # Seed for consistent data per match
        random.seed(hash(match_info["id"]) % (2**32))
        
        team_data = MOCK_TEAMS.get(team_name, MOCK_TEAMS["Cloud9"])
        opponent_name = match_info["opponent"]
        opponent_data = MOCK_TEAMS.get(opponent_name, MOCK_TEAMS["Sentinels"])
        
        match_data = _generate_match(
            match_id=match_info["id"],
            team_name=team_name,
            opponent_name=opponent_name,
            date=datetime.fromisoformat(match_info["date"]),
            team_data=team_data,
            opponent_data=opponent_data,
        )
        matches.append(match_data)
        
        random.seed()
    
    return matches
