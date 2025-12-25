"""Pydantic models for Referee Agent messages"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class MessageType(str, Enum):
    """Message types for JSON-RPC protocol"""
    REFEREE_REGISTER_REQUEST = "REFEREE_REGISTER_REQUEST"
    REFEREE_REGISTER_RESPONSE = "REFEREE_REGISTER_RESPONSE"
    ROUND_ANNOUNCEMENT = "ROUND_ANNOUNCEMENT"
    GAME_INVITATION = "GAME_INVITATION"
    GAME_JOIN_ACK = "GAME_JOIN_ACK"
    CHOOSE_PARITY_REQUEST = "CHOOSE_PARITY_REQUEST"
    CHOOSE_PARITY_RESPONSE = "CHOOSE_PARITY_RESPONSE"
    MATCH_RESULT_REPORT = "MATCH_RESULT_REPORT"


class RefereeState(str, Enum):
    """Referee agent states"""
    NOT_REGISTERED = "NOT_REGISTERED"
    REGISTERED = "REGISTERED"
    IDLE = "IDLE"
    CONDUCTING_MATCH = "CONDUCTING_MATCH"
    REPORTING = "REPORTING"


class MessageEnvelope(BaseModel):
    """Standard message envelope"""
    protocol: str
    message_type: str
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: str = ""
    league_id: str


class RegistrationRequest(BaseModel):
    """Referee registration request"""
    display_name: str
    version: str
    game_types: List[str]
    contact_endpoint: str
    max_concurrent_matches: int


class RegistrationResponse(BaseModel):
    """Registration response from league manager"""
    status: str
    referee_id: str
    auth_token: str


class MatchData(BaseModel):
    """Match assignment data"""
    match_id: str
    game_type: str
    player_A_id: str
    player_B_id: str
    referee_endpoint: str


class RoundAnnouncement(BaseModel):
    """Round announcement from league manager"""
    round_id: str
    matches: List[Dict[str, Any]]


class GameInvitation(BaseModel):
    """Game invitation to player"""
    match_id: str
    round_id: str
    opponent_id: str
    game_type: str


class PlayerChoice(BaseModel):
    """Player's parity choice"""
    player_id: str
    choice: str  # "odd" or "even"


class MatchResult(BaseModel):
    """Match result report"""
    round_id: str
    match_id: str
    winner: Optional[str]  # None for draw
    score: Dict[str, int]  # {player_id: points}
    details: Dict[str, Any]


class RefereeContext(BaseModel):
    """Current match context"""
    referee_id: str = ""
    auth_token: str = ""
    state: RefereeState = RefereeState.NOT_REGISTERED
    current_round_id: Optional[str] = None
    current_match_id: Optional[str] = None
    player_A_id: Optional[str] = None
    player_B_id: Optional[str] = None
    player_A_choice: Optional[str] = None
    player_B_choice: Optional[str] = None
