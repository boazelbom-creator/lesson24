"""Pydantic models for Player Agent messages"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class MessageType(str, Enum):
    """Message types for JSON-RPC protocol"""
    PLAYER_REGISTER_REQUEST = "PLAYER_REGISTER_REQUEST"
    PLAYER_REGISTER_RESPONSE = "PLAYER_REGISTER_RESPONSE"
    GAME_INVITATION = "GAME_INVITATION"
    GAME_JOIN_ACK = "GAME_JOIN_ACK"
    CHOOSE_PARITY_REQUEST = "CHOOSE_PARITY_REQUEST"
    CHOOSE_PARITY_RESPONSE = "CHOOSE_PARITY_RESPONSE"
    MATCH_RESULT_REPORT = "MATCH_RESULT_REPORT"
    LEAGUE_STANDINGS_UPDATE = "LEAGUE_STANDINGS_UPDATE"


class PlayerState(str, Enum):
    """Player agent states"""
    NOT_REGISTERED = "NOT_REGISTERED"
    REGISTERED = "REGISTERED"
    IDLE = "IDLE"
    IN_GAME = "IN_GAME"


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
    """Player registration request"""
    display_name: str
    version: str
    game_types: List[str]
    contact_endpoint: str
    max_concurrent_matches: int


class RegistrationResponse(BaseModel):
    """Registration response from league manager"""
    status: str
    player_id: str
    auth_token: str


class GameInvitation(BaseModel):
    """Game invitation from referee"""
    match_id: str
    round_id: str
    opponent_id: str
    game_type: str


class GameJoinAck(BaseModel):
    """Acknowledgment of game invitation"""
    player_id: str
    arrival_timestamp: str
    accept: bool = True


class ChoiceRequest(BaseModel):
    """Parity choice request from referee"""
    match_id: str
    round_id: str


class ChoiceResponse(BaseModel):
    """Player's parity choice response"""
    player_id: str
    choice: str  # "odd" or "even"


class MatchResult(BaseModel):
    """Match result from referee"""
    round_id: str
    match_id: str
    winner: Optional[str]
    score: Dict[str, int]
    details: Dict[str, Any]


class Standing(BaseModel):
    """Player standing entry"""
    rank: int
    player_id: str
    display_name: str
    played: int
    wins: int
    draws: int
    losses: int
    points: int


class StandingsUpdate(BaseModel):
    """League standings update"""
    round_id: str
    standings: List[Standing]


class PlayerContext(BaseModel):
    """Current player context"""
    player_id: str = ""
    auth_token: str = ""
    state: PlayerState = PlayerState.NOT_REGISTERED
    current_match_id: Optional[str] = None
    current_round_id: Optional[str] = None
    current_conversation_id: Optional[str] = None
