"""League Manager FastAPI Server"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
import uuid

from models import (
    MessageEnvelope, MessageType, RegistrationRequest, RegistrationResponse,
    MatchResult, StandingsUpdate
)
from registration import RegistrationManager
from scheduler import TournamentScheduler
from standings import StandingsManager
from http_client import HTTPClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="League Manager", version="1.0.0")

# Global state
registration_mgr = RegistrationManager()
standings_mgr = StandingsManager()
http_client = HTTPClient()
scheduler = None

# Tournament state
current_round = 0
match_results: Dict[str, MatchResult] = {}
tournament_started = False


@app.post("/MCP")
async def mcp_endpoint(request: Request):
    """Main MCP endpoint for all JSON-RPC messages"""
    try:
        data = await request.json()
        message_type = data.get("message_type", "")

        logger.info(f"Received message: {message_type}")

        if message_type == MessageType.REFEREE_REGISTER_REQUEST:
            return await handle_referee_registration(data)
        elif message_type == MessageType.PLAYER_REGISTER_REQUEST:
            return await handle_player_registration(data)
        elif message_type == MessageType.MATCH_RESULT_REPORT:
            return await handle_match_result(data)
        else:
            logger.warning(f"Unknown message type: {message_type}")
            raise HTTPException(status_code=400, detail="Unknown message type")

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_referee_registration(data: Dict[str, Any]) -> JSONResponse:
    """Handle referee registration request"""
    try:
        reg_request = RegistrationRequest(**data)
        response = registration_mgr.register_referee(reg_request)

        if not response:
            raise HTTPException(status_code=400, detail="Registration limit reached")

        # Create response envelope
        envelope = {
            "protocol": "league.v2",
            "message_type": MessageType.REFEREE_REGISTER_RESPONSE,
            "sender": "league_manager",
            "timestamp": datetime.now().isoformat(),
            "conversation_id": data.get("conversation_id", str(uuid.uuid4())),
            "auth_token": response.auth_token,
            "league_id": "league_2025_even_odd"
        }

        response_data = {
            **envelope,
            "status": response.status,
            "referee_id": response.participant_id,
            "auth_token": response.auth_token
        }

        # Check if all participants registered
        if registration_mgr.all_registered():
            asyncio.create_task(start_tournament())

        return JSONResponse(content=response_data)

    except Exception as e:
        logger.error(f"Error in referee registration: {e}")
        raise HTTPException(status_code=400, detail=str(e))


async def handle_player_registration(data: Dict[str, Any]) -> JSONResponse:
    """Handle player registration request"""
    try:
        reg_request = RegistrationRequest(**data)
        response = registration_mgr.register_player(reg_request)

        if not response:
            raise HTTPException(status_code=400, detail="Registration limit reached")

        # Initialize standings for this player
        standings_mgr.initialize_player(response.participant_id, reg_request.display_name)

        # Create response envelope
        envelope = {
            "protocol": "league.v2",
            "message_type": MessageType.PLAYER_REGISTER_RESPONSE,
            "sender": "league_manager",
            "timestamp": datetime.now().isoformat(),
            "conversation_id": data.get("conversation_id", str(uuid.uuid4())),
            "auth_token": response.auth_token,
            "league_id": "league_2025_even_odd"
        }

        response_data = {
            **envelope,
            "status": response.status,
            "player_id": response.participant_id,
            "auth_token": response.auth_token
        }

        # Check if all participants registered
        if registration_mgr.all_registered():
            asyncio.create_task(start_tournament())

        return JSONResponse(content=response_data)

    except Exception as e:
        logger.error(f"Error in player registration: {e}")
        raise HTTPException(status_code=400, detail=str(e))


async def handle_match_result(data: Dict[str, Any]) -> JSONResponse:
    """Handle match result report from referee"""
    global current_round, match_results

    try:
        result = MatchResult(**data)
        logger.info(f"Received result for {result.match_id}")

        # Update standings
        standings_mgr.update_from_result(result)

        # Store result
        match_results[result.match_id] = result

        # Check if round is complete (both matches finished)
        round_matches = scheduler.get_round_matches(current_round)
        round_complete = all(
            match.match_id in match_results
            for match in round_matches
        )

        if round_complete:
            # Run finish_round in background to avoid blocking response
            asyncio.create_task(finish_round())

        return JSONResponse(content={"status": "acknowledged"})

    except Exception as e:
        logger.error(f"Error handling match result: {e}")
        raise HTTPException(status_code=400, detail=str(e))


async def start_tournament():
    """Initialize and start the tournament"""
    global scheduler, tournament_started, current_round

    if tournament_started:
        return

    tournament_started = True
    logger.info("Starting tournament - all participants registered")

    # Get player and referee IDs
    player_ids = registration_mgr.get_all_player_ids()
    referee_ids = list(registration_mgr.referees.keys())

    # Create schedule
    scheduler = TournamentScheduler(player_ids, referee_ids)
    scheduler.generate_schedule()

    if not scheduler.validate_schedule():
        logger.error("Schedule validation failed!")
        return

    # Print schedule
    scheduler.print_schedule()

    # Start first round
    current_round = 1
    await start_round(current_round)


async def start_round(round_num: int):
    """Start a specific round by notifying referees"""
    logger.info(f"Starting Round {round_num}")
    print(f"\n>>> Starting Round {round_num} <<<\n")

    round_matches = scheduler.get_round_matches(round_num)
    round_id = f"R{round_num}"

    # Group matches by referee
    referee_matches: Dict[str, list] = {}
    for match in round_matches:
        if match.referee_id not in referee_matches:
            referee_matches[match.referee_id] = []
        referee_matches[match.referee_id].append(match)

    # Send announcements to referees
    for referee_id, matches in referee_matches.items():
        endpoint = registration_mgr.get_referee_endpoint(referee_id)
        referee = registration_mgr.get_participant(referee_id)
        token = referee.auth_token if referee else ""

        await http_client.send_round_announcement(
            endpoint, round_id, matches, token
        )


async def finish_round():
    """Complete current round and proceed to next or end tournament"""
    global current_round

    logger.info(f"Round {current_round} complete")
    print(f"\n>>> Round {current_round} Complete <<<")

    # Display standings
    standings_mgr.print_standings()

    # Broadcast standings to players
    player_endpoints = {}
    player_tokens = {}
    for player_id in registration_mgr.get_all_player_ids():
        player = registration_mgr.get_participant(player_id)
        player_endpoints[player_id] = player.contact_endpoint
        player_tokens[player_id] = player.auth_token

    standings = standings_mgr.get_sorted_standings()
    round_id = f"R{current_round}"

    await http_client.broadcast_standings(
        player_endpoints, player_tokens, round_id, standings
    )

    # Check if tournament is over
    if current_round >= scheduler.get_total_rounds():
        await end_tournament()
        return

    # Clear match results for next round
    match_results.clear()

    # Wait 60 seconds before next round
    logger.info("Waiting 60 seconds before next round...")
    await asyncio.sleep(60)

    # Start next round
    current_round += 1
    await start_round(current_round)


async def end_tournament():
    """End tournament and display final results"""
    logger.info("Tournament complete!")
    print("\n" + "="*80)
    print("TOURNAMENT COMPLETE - FINAL STANDINGS")
    print("="*80)
    standings_mgr.print_standings()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "referees_registered": registration_mgr.referee_count,
        "players_registered": registration_mgr.player_count,
        "tournament_started": tournament_started,
        "current_round": current_round
    }


if __name__ == "__main__":
    print("="*80)
    print("LEAGUE MANAGER - ODD EVEN TOURNAMENT")
    print("="*80)
    print("Listening on http://localhost:8000")
    print("Waiting for participant registrations...")
    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
