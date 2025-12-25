"""HTTP client for communication with referees and players"""
import httpx
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from models import Match, PlayerStanding, MessageEnvelope, MessageType
import uuid

logger = logging.getLogger(__name__)


class HTTPClient:
    """Handles HTTP requests to referees and players"""

    def __init__(self):
        self.timeout = 10.0

    def _create_envelope(self, message_type: str, auth_token: str = "") -> Dict[str, Any]:
        """Create standard message envelope"""
        return {
            "protocol": "league.v2",
            "message_type": message_type,
            "sender": "league_manager",
            "timestamp": datetime.now().isoformat(),
            "conversation_id": str(uuid.uuid4()),
            "auth_token": auth_token,
            "league_id": "league_2025_even_odd"
        }

    async def send_round_announcement(
        self,
        referee_endpoint: str,
        round_id: str,
        matches: List[Match],
        auth_token: str
    ) -> bool:
        """
        Send round announcement to referee
        No response expected (notification)
        """
        envelope = self._create_envelope(MessageType.ROUND_ANNOUNCEMENT, auth_token)

        matches_data = []
        for match in matches:
            matches_data.append({
                "match_id": match.match_id,
                "game_type": match.game_type,
                "player_A_id": match.player_A_id,
                "player_B_id": match.player_B_id,
                "referee_endpoint": referee_endpoint
            })

        payload = {
            **envelope,
            "round_id": round_id,
            "matches": matches_data
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{referee_endpoint}/MCP",
                    json=payload
                )
                logger.info(f"Round announcement sent to {referee_endpoint}: {round_id}")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send round announcement to {referee_endpoint}: {e}")
            return False

    async def send_standings_update(
        self,
        player_endpoint: str,
        round_id: str,
        standings: List[PlayerStanding],
        auth_token: str
    ) -> bool:
        """
        Send standings update to player
        Uses JSON-RPC 2.0 format with update_standings method
        No response expected (notification)
        """
        envelope = self._create_envelope(MessageType.LEAGUE_STANDINGS_UPDATE, auth_token)

        standings_data = []
        for s in standings:
            standings_data.append({
                "rank": s.rank,
                "player_id": s.player_id,
                "display_name": s.display_name,
                "played": s.played,
                "wins": s.wins,
                "draws": s.draws,
                "losses": s.losses,
                "points": s.points
            })

        # JSON-RPC 2.0 wrapper
        payload = {
            "jsonrpc": "2.0",
            "method": "update_standings",
            "params": {
                **envelope,
                "round_id": round_id,
                "standings": standings_data
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{player_endpoint}/MCP",
                    json=payload
                )
                logger.info(f"Standings update sent to {player_endpoint}")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send standings to {player_endpoint}: {e}")
            return False

    async def broadcast_standings(
        self,
        player_endpoints: Dict[str, str],
        player_tokens: Dict[str, str],
        round_id: str,
        standings: List[PlayerStanding]
    ):
        """Broadcast standings to all players"""
        for player_id, endpoint in player_endpoints.items():
            token = player_tokens.get(player_id, "")
            await self.send_standings_update(endpoint, round_id, standings, token)
