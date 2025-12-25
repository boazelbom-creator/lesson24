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
        sender: Sender ID (player_id)
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
        "timestamp": datetime.utcnow().isoformat() + "Z",
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
    """Create player registration request"""
    envelope = create_envelope("PLAYER_REGISTER_REQUEST", "player_unregistered")

    return {
        **envelope,
        "display_name": display_name,
        "version": version,
        "game_types": game_types,
        "contact_endpoint": contact_endpoint,
        "max_concurrent_matches": max_concurrent_matches
    }


def create_join_ack(
    player_id: str,
    auth_token: str,
    conversation_id: str
) -> Dict[str, Any]:
    """Create game join acknowledgment"""
    envelope = create_envelope("GAME_JOIN_ACK", player_id, auth_token, conversation_id)

    return {
        **envelope,
        "player_id": player_id,
        "arrival_timestamp": datetime.utcnow().isoformat() + "Z",
        "accept": True
    }


def create_choice_response(
    player_id: str,
    choice: str,
    auth_token: str,
    conversation_id: str
) -> Dict[str, Any]:
    """Create parity choice response"""
    envelope = create_envelope("CHOOSE_PARITY_RESPONSE", player_id, auth_token, conversation_id)

    return {
        **envelope,
        "player_id": player_id,
        "choice": choice
    }


def parse_message(data: Dict[str, Any]) -> tuple:
    """
    Parse incoming message and extract type and content

    Returns:
        Tuple of (message_type, data)
    """
    message_type = data.get("message_type", "")
    return message_type, data
