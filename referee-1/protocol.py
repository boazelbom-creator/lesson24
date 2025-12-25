"""JSON-RPC protocol message handling"""
from datetime import datetime
from typing import Dict, Any
import uuid
from config import PROTOCOL_VERSION, LEAGUE_ID


def create_envelope(
    message_type: str,
    sender: str,
    auth_token: str = "",
    conversation_id: str = None
) -> Dict[str, Any]:
    """
    Create standard JSON-RPC message envelope

    Args:
        message_type: Type of message
        sender: Sender ID (referee_id)
        auth_token: Authentication token
        conversation_id: Optional conversation ID

    Returns:
        Message envelope dictionary
    """
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())

    return {
        "protocol": PROTOCOL_VERSION,
        "message_type": message_type,
        "sender": sender,
        "timestamp": datetime.now().isoformat(),
        "conversation_id": conversation_id,
        "auth_token": auth_token,
        "league_id": LEAGUE_ID
    }


def create_registration_request(
    display_name: str,
    version: str,
    game_types: list,
    contact_endpoint: str,
    max_concurrent_matches: int
) -> Dict[str, Any]:
    """Create referee registration request"""
    envelope = create_envelope("REFEREE_REGISTER_REQUEST", "referee_unregistered")

    return {
        **envelope,
        "display_name": display_name,
        "version": version,
        "game_types": game_types,
        "contact_endpoint": contact_endpoint,
        "max_concurrent_matches": max_concurrent_matches
    }


def create_game_invitation(
    match_id: str,
    round_id: str,
    player_id: str,
    opponent_id: str,
    game_type: str,
    referee_id: str,
    auth_token: str
) -> Dict[str, Any]:
    """Create game invitation for player"""
    envelope = create_envelope("GAME_INVITATION", referee_id, auth_token)

    return {
        **envelope,
        "match_id": match_id,
        "round_id": round_id,
        "opponent_id": opponent_id,
        "game_type": game_type
    }


def create_choice_request(
    match_id: str,
    round_id: str,
    referee_id: str,
    auth_token: str
) -> Dict[str, Any]:
    """Create parity choice request"""
    envelope = create_envelope("CHOOSE_PARITY_REQUEST", referee_id, auth_token)

    return {
        **envelope,
        "match_id": match_id,
        "round_id": round_id
    }


def create_result_report(
    round_id: str,
    match_id: str,
    winner: str,
    score: Dict[str, int],
    details: Dict[str, Any],
    referee_id: str,
    auth_token: str
) -> Dict[str, Any]:
    """Create match result report"""
    envelope = create_envelope("MATCH_RESULT_REPORT", referee_id, auth_token)

    return {
        **envelope,
        "round_id": round_id,
        "match_id": match_id,
        "winner": winner if winner else None,
        "score": score,
        "details": details
    }


def parse_message(data: Dict[str, Any]) -> tuple:
    """
    Parse incoming message and extract type and content

    Returns:
        Tuple of (message_type, data)
    """
    message_type = data.get("message_type", "")
    return message_type, data
