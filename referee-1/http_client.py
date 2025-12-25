"""HTTP client for communication with league manager and players"""
import httpx
import logging
import asyncio
from typing import Dict, Any, Optional
from config import (
    MAX_RETRIES, RETRY_DELAY, REGISTRATION_TIMEOUT,
    PLAYER_INVITE_TIMEOUT, PLAYER_CHOICE_TIMEOUT, RESULT_REPORT_TIMEOUT,
    PLAYER_PORT_MAP, LEAGUE_MANAGER_URL
)

logger = logging.getLogger(__name__)


async def send_with_retry(
    url: str,
    payload: Dict[str, Any],
    timeout: float,
    max_retries: int = MAX_RETRIES
) -> Optional[Dict[str, Any]]:
    """
    Send HTTP POST request with retry logic

    Args:
        url: Target URL
        payload: JSON payload
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts

    Returns:
        Response JSON or None on failure
    """
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                logger.info(f"Request to {url} succeeded")
                return response.json()
        except httpx.TimeoutException:
            logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries} to {url}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} from {url}")
            return None
        except Exception as e:
            logger.error(f"Error on attempt {attempt + 1}/{max_retries} to {url}: {e}")

        if attempt < max_retries - 1:
            await asyncio.sleep(RETRY_DELAY)

    logger.error(f"All retry attempts failed for {url}")
    return None


async def register_with_league_manager(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Register referee with league manager"""
    url = f"{LEAGUE_MANAGER_URL}/MCP"
    logger.info(f"Registering with league manager at {url}")
    return await send_with_retry(url, payload, REGISTRATION_TIMEOUT)


async def send_invitation_to_player(
    player_id: str,
    payload: Dict[str, Any]
) -> bool:
    """Send game invitation to a player"""
    port = PLAYER_PORT_MAP.get(player_id)
    if not port:
        logger.error(f"Unknown player ID: {player_id}")
        return False

    url = f"http://localhost:{port}/MCP"
    logger.info(f"Sending invitation to {player_id} at {url}")

    response = await send_with_retry(url, payload, PLAYER_INVITE_TIMEOUT)
    return response is not None


async def request_player_choice(
    player_id: str,
    payload: Dict[str, Any]
) -> Optional[str]:
    """
    Request parity choice from player

    Returns:
        Player's choice ("odd" or "even") or None on failure
    """
    port = PLAYER_PORT_MAP.get(player_id)
    if not port:
        logger.error(f"Unknown player ID: {player_id}")
        return None

    url = f"http://localhost:{port}/MCP"
    logger.info(f"Requesting choice from {player_id} at {url}")

    response = await send_with_retry(url, payload, PLAYER_CHOICE_TIMEOUT)
    if response:
        choice = response.get("choice", "").lower()
        logger.info(f"Received choice from {player_id}: {choice}")
        return choice

    logger.warning(f"No response from {player_id}")
    return None


async def report_result_to_league_manager(payload: Dict[str, Any]) -> bool:
    """Report match result to league manager"""
    url = f"{LEAGUE_MANAGER_URL}/MCP"
    logger.info(f"Reporting result to league manager at {url}")

    response = await send_with_retry(url, payload, RESULT_REPORT_TIMEOUT)
    return response is not None
