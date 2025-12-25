"""Main entry point for Referee Agent"""
import asyncio
import logging
import uvicorn
from models import RefereeContext, RefereeState
from config import (
    REFEREE_DISPLAY_NAME, REFEREE_VERSION, GAME_TYPES,
    MAX_CONCURRENT_MATCHES, REFEREE_PORT
)
from protocol import create_registration_request
from http_client import register_with_league_manager
import referee_server

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def register_referee() -> RefereeContext:
    """
    Register referee with league manager

    Returns:
        RefereeContext with referee_id and auth_token
    """
    logger.info("Starting referee registration")

    contact_endpoint = f"http://localhost:{REFEREE_PORT}"

    # Create registration request
    registration_payload = create_registration_request(
        display_name=REFEREE_DISPLAY_NAME,
        version=REFEREE_VERSION,
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
    referee_id = response.get("referee_id")
    auth_token = response.get("auth_token")

    logger.info(f"Successfully registered as {referee_id}")
    print(f"\n{'='*60}")
    print(f"REFEREE REGISTERED")
    print(f"{'='*60}")
    print(f"Referee ID: {referee_id}")
    print(f"Listening on: {contact_endpoint}")
    print(f"{'='*60}\n")

    # Create context
    context = RefereeContext(
        referee_id=referee_id,
        auth_token=auth_token,
        state=RefereeState.IDLE
    )

    return context


async def startup():
    """Startup routine - register with league manager"""
    try:
        context = await register_referee()
        referee_server.set_context(context)
        logger.info("Referee agent ready to receive match assignments")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


def main():
    """Main entry point"""
    print("="*60)
    print("REFEREE AGENT - ODD EVEN TOURNAMENT")
    print("="*60)
    print(f"Name: {REFEREE_DISPLAY_NAME}")
    print(f"Port: {REFEREE_PORT}")
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
    logger.info(f"Starting FastAPI server on port {REFEREE_PORT}")
    uvicorn.run(
        referee_server.app,
        host="0.0.0.0",
        port=REFEREE_PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()
