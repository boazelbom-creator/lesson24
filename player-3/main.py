"""Main entry point for Player Agent"""
import asyncio
import logging
import uvicorn
from models import PlayerContext, PlayerState
from config import (
    PLAYER_DISPLAY_NAME, PLAYER_VERSION, GAME_TYPES,
    MAX_CONCURRENT_MATCHES, PLAYER_PORT
)
from protocol import create_registration_request
from http_client import register_with_league_manager
import player_server

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def register_player() -> PlayerContext:
    """
    Register player with league manager

    Returns:
        PlayerContext with player_id and auth_token
    """
    logger.info("Starting player registration")

    contact_endpoint = f"http://localhost:{PLAYER_PORT}"

    # Create registration request
    registration_payload = create_registration_request(
        display_name=PLAYER_DISPLAY_NAME,
        version=PLAYER_VERSION,
        game_types=GAME_TYPES,
        contact_endpoint=contact_endpoint,
        max_concurrent_matches=MAX_CONCURRENT_MATCHES
    )

    # Send registration
    response = await register_with_league_manager(registration_payload)

    if not response:
        logger.error("Registration failed")
        raise Exception("Failed to register with league manager")

    # Extract registration data
    player_id = response.get("player_id")
    auth_token = response.get("auth_token")

    logger.info(f"Successfully registered as {player_id}")
    print(f"\n{'='*60}")
    print(f"PLAYER REGISTERED")
    print(f"{'='*60}")
    print(f"Player ID: {player_id}")
    print(f"Name: {PLAYER_DISPLAY_NAME}")
    print(f"Listening on: {contact_endpoint}")
    print(f"{'='*60}\n")

    # Create context
    context = PlayerContext(
        player_id=player_id,
        auth_token=auth_token,
        state=PlayerState.IDLE
    )

    return context


async def startup():
    """Startup routine - register with league manager"""
    try:
        context = await register_player()
        player_server.set_context(context)
        logger.info("Player agent ready to receive game invitations")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


def main():
    """Main entry point"""
    print("="*60)
    print("PLAYER AGENT - ODD EVEN TOURNAMENT")
    print("="*60)
    print(f"Name: {PLAYER_DISPLAY_NAME}")
    print(f"Port: {PLAYER_PORT}")
    print("="*60 + "\n")

    # Create event loop for startup
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Run registration
        loop.run_until_complete(startup())
    except Exception as e:
        logger.error(f"Failed to start: {e}")
        return
    finally:
        loop.close()

    # Start FastAPI server
    logger.info(f"Starting FastAPI server on port {PLAYER_PORT}")
    uvicorn.run(
        player_server.app,
        host="0.0.0.0",
        port=PLAYER_PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()
