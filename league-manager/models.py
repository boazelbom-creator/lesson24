"""Data models for League Manager"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    """Message types for JSON-RPC protocol"""
    REFEREE_REGISTER_REQUEST = "REFEREE_REGISTER_REQUEST"
    REFEREE_REGISTER_RESPONSE = "REFEREE_REGISTER_RESPONSE"
    PLAYER_REGISTER_REQUEST = "PLAYER_REGISTER_REQUEST"
    PLAYER_REGISTER_RESPONSE = "PLAYER_REGISTER_RESPONSE"
    ROUND_ANNOUNCEMENT = "ROUND_ANNOUNCEMENT"
    MATCH_RESULT_REPORT = "MATCH_RESULT_REPORT"
    LEAGUE_STANDINGS_UPDATE = "LEAGUE_STANDINGS_UPDATE"


class MessageEnvelope(BaseModel):
    """Standard JSON-RPC 2.0 message envelope"""
    protocol: str = "league.v2"
    message_type: str
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: str = ""
    league_id: str = "league_2025_even_odd"


class RegistrationRequest(BaseModel):
    """Registration request from referee or player"""
    display_name: str
    version: str
    game_types: List[str]
    contact_endpoint: str
    max_concurrent_matches: int


class RegistrationResponse(BaseModel):
    """Registration response"""
    status: str = "ACCEPTED"
    participant_id: str  # REF01, REF02, P01-P04
    auth_token: str


class Participant(BaseModel):
    """Internal participant data"""
    participant_id: str
    display_name: str
    contact_endpoint: str
    auth_token: str
    registered_at: datetime


class Match(BaseModel):
    """Match definition"""
    match_id: str
    game_type: str = "even_odd"
    player_A_id: str
    player_B_id: str
    referee_id: str


class RoundAnnouncement(BaseModel):
    """Round announcement to referee"""
    round_id: str
    matches: List[Dict[str, Any]]


class MatchResult(BaseModel):
    """Match result from referee"""
    round_id: str
    match_id: str
    winner: Optional[str]  # None for draw
    score: Dict[str, int]  # {player_id: points}
    details: Optional[Dict[str, Any]] = None


class PlayerStanding(BaseModel):
    """Player standing data"""
    rank: int
    player_id: str
    display_name: str
    played: int
    wins: int
    draws: int
    losses: int
    points: int


class StandingsUpdate(BaseModel):
    """Standings update to players"""
    round_id: str
    standings: List[PlayerStanding]


class StandingsData(BaseModel):
    """Internal standings tracking"""
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    points: int = 0
    display_name: str = ""
