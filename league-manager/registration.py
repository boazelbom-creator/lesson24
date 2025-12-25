"""Registration management for referees and players"""
import secrets
from datetime import datetime
from typing import Dict, Optional, Tuple
from models import Participant, RegistrationRequest, RegistrationResponse
import logging

logger = logging.getLogger(__name__)


class RegistrationManager:
    """Manages referee and player registrations"""

    def __init__(self):
        self.referees: Dict[str, Participant] = {}
        self.players: Dict[str, Participant] = {}
        self.referee_count = 0
        self.player_count = 0

    def generate_token(self) -> str:
        """Generate 32-byte random auth token"""
        return secrets.token_hex(32)

    def register_referee(self, request: RegistrationRequest) -> Optional[RegistrationResponse]:
        """Register a referee (max 2)"""
        if self.referee_count >= 2:
            logger.warning("Attempted to register more than 2 referees")
            return None

        self.referee_count += 1
        referee_id = f"REF{self.referee_count:02d}"
        auth_token = self.generate_token()

        participant = Participant(
            participant_id=referee_id,
            display_name=request.display_name,
            contact_endpoint=request.contact_endpoint,
            auth_token=auth_token,
            registered_at=datetime.now()
        )

        self.referees[referee_id] = participant

        logger.info(f"Registered referee: {referee_id} ({request.display_name})")
        print(f"✓ Registered: {referee_id} - {request.display_name}")

        return RegistrationResponse(
            status="ACCEPTED",
            participant_id=referee_id,
            auth_token=auth_token
        )

    def register_player(self, request: RegistrationRequest) -> Optional[RegistrationResponse]:
        """Register a player (max 4)"""
        if self.player_count >= 4:
            logger.warning("Attempted to register more than 4 players")
            return None

        self.player_count += 1
        player_id = f"P{self.player_count:02d}"
        auth_token = self.generate_token()

        participant = Participant(
            participant_id=player_id,
            display_name=request.display_name,
            contact_endpoint=request.contact_endpoint,
            auth_token=auth_token,
            registered_at=datetime.now()
        )

        self.players[player_id] = participant

        logger.info(f"Registered player: {player_id} ({request.display_name})")
        print(f"✓ Registered: {player_id} - {request.display_name}")

        return RegistrationResponse(
            status="ACCEPTED",
            participant_id=player_id,
            auth_token=auth_token
        )

    def all_registered(self) -> bool:
        """Check if all participants are registered (2 referees + 4 players)"""
        return self.referee_count == 2 and self.player_count == 4

    def get_participant(self, participant_id: str) -> Optional[Participant]:
        """Get participant by ID"""
        if participant_id.startswith("REF"):
            return self.referees.get(participant_id)
        elif participant_id.startswith("P"):
            return self.players.get(participant_id)
        return None

    def validate_token(self, participant_id: str, token: str) -> bool:
        """Validate auth token for participant"""
        participant = self.get_participant(participant_id)
        if not participant:
            return False
        return participant.auth_token == token

    def get_referee_endpoint(self, referee_id: str) -> Optional[str]:
        """Get referee contact endpoint"""
        referee = self.referees.get(referee_id)
        return referee.contact_endpoint if referee else None

    def get_player_endpoint(self, player_id: str) -> Optional[str]:
        """Get player contact endpoint"""
        player = self.players.get(player_id)
        return player.contact_endpoint if player else None

    def get_all_player_ids(self) -> list:
        """Get list of all registered player IDs"""
        return list(self.players.keys())
