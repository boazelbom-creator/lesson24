"""HTTP client for communication with league manager"""
import httpx
import logging
import asyncio
from typing import Dict, Any, Optional
from config import (
    MAX_RETRIES, RETRY_DELAY, REGISTRATION_TIMEOUT,
    MESSAGE_TIMEOUT, LEAGUE_MANAGER_URL
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
    """Register player with league manager"""
    url = f"{LEAGUE_MANAGER_URL}/MCP"
    logger.info(f"Registering with league manager at {url}")
    return await send_with_retry(url, payload, REGISTRATION_TIMEOUT)
