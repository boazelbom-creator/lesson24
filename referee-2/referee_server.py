"""FastAPI server for Referee Agent"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import asyncio
from typing import Dict, Any

from models import RefereeContext, RefereeState, MessageType
from protocol import parse_message
from http_client import send_invitation_to_player, request_player_choice, report_result_to_league_manager
from game_logic import draw_random_number, calculate_match_result, handle_player_timeout
import protocol

logger = logging.getLogger(__name__)

app = FastAPI(title="Referee Agent", version="1.0.0")

# Global referee context
context = RefereeContext()


@app.post("/MCP")
async def mcp_endpoint(request: Request):
    """Main MCP endpoint for receiving messages"""
    try:
        data = await request.json()
        message_type, content = parse_message(data)

        logger.info(f"Received message: {message_type}")

        if message_type == MessageType.ROUND_ANNOUNCEMENT:
            return await handle_round_announcement(content)
        else:
            logger.warning(f"Unknown message type: {message_type}")
            return JSONResponse(content={"status": "unknown_message_type"})

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_round_announcement(data: Dict[str, Any]) -> JSONResponse:
    """
    Handle round announcement from league manager
    Start conducting the assigned matches
    """
    global context

    if context.state == RefereeState.CONDUCTING_MATCH:
        logger.warning("Already conducting a match, cannot accept new assignment")
        return JSONResponse(content={"status": "busy"})

    round_id = data.get("round_id")
    matches = data.get("matches", [])

    logger.info(f"Received round announcement for {round_id} with {len(matches)} matches")

    # Process each match assigned to this referee
    for match_data in matches:
        asyncio.create_task(conduct_match(round_id, match_data))

    return JSONResponse(content={"status": "acknowledged"})


async def conduct_match(round_id: str, match_data: Dict[str, Any]):
    """Conduct a complete match between two players"""
    global context

    match_id = match_data.get("match_id")
    player_A_id = match_data.get("player_A_id")
    player_B_id = match_data.get("player_B_id")

    logger.info(f"Starting match {match_id}: {player_A_id} vs {player_B_id}")

    # Update context
    context.state = RefereeState.CONDUCTING_MATCH
    context.current_round_id = round_id
    context.current_match_id = match_id
    context.player_A_id = player_A_id
    context.player_B_id = player_B_id

    # Step 1: Send invitations to both players
    invitation_A = protocol.create_game_invitation(
        match_id, round_id, player_A_id, player_B_id, "even_odd",
        context.referee_id, context.auth_token
    )
    invitation_B = protocol.create_game_invitation(
        match_id, round_id, player_B_id, player_A_id, "even_odd",
        context.referee_id, context.auth_token
    )

    invite_A_success = await send_invitation_to_player(player_A_id, invitation_A)
    invite_B_success = await send_invitation_to_player(player_B_id, invitation_B)

    if not invite_A_success or not invite_B_success:
        logger.error("Failed to invite players")
        # Continue anyway, will handle timeouts in choice collection

    # Step 2: Collect choices from both players
    choice_request = protocol.create_choice_request(
        match_id, round_id, context.referee_id, context.auth_token
    )

    choice_A = await request_player_choice(player_A_id, choice_request)
    choice_B = await request_player_choice(player_B_id, choice_request)

    # Step 3: Calculate result
    if choice_A and choice_B:
        # Both players responded
        drawn_number = draw_random_number()
        winner, score, details = calculate_match_result(
            player_A_id, choice_A, player_B_id, choice_B, drawn_number
        )
    else:
        # Handle timeouts
        winner, score, details = handle_player_timeout(
            player_A_id, player_B_id,
            choice_A is not None, choice_B is not None
        )

    # Step 4: Report result to league manager
    result_report = protocol.create_result_report(
        round_id, match_id, winner, score, details,
        context.referee_id, context.auth_token
    )

    await report_result_to_league_manager(result_report)

    logger.info(f"Match {match_id} complete")

    # Reset context
    context.state = RefereeState.IDLE
    context.current_match_id = None
    context.player_A_id = None
    context.player_B_id = None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "referee_id": context.referee_id,
        "state": context.state,
        "registered": context.state != RefereeState.NOT_REGISTERED
    }


def set_context(ref_context: RefereeContext):
    """Set the global referee context"""
    global context
    context = ref_context
