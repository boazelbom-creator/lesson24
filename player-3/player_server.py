"""FastAPI server for Player Agent"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any

from models import PlayerContext, PlayerState, MessageType
from protocol import parse_message, create_join_ack, create_choice_response
from game_logic import make_move, format_standings

logger = logging.getLogger(__name__)

app = FastAPI(title="Player Agent", version="1.0.0")

# Global player context
context = PlayerContext()


@app.post("/MCP")
async def mcp_endpoint(request: Request):
    """Main MCP endpoint for receiving messages"""
    try:
        data = await request.json()
        message_type, content = parse_message(data)

        logger.info(f"Received message: {message_type}")

        if message_type == MessageType.GAME_INVITATION:
            return await handle_game_invitation(content)
        elif message_type == MessageType.CHOOSE_PARITY_REQUEST:
            return await handle_choice_request(content)
        elif message_type == MessageType.MATCH_RESULT_REPORT:
            return await handle_match_result(content)
        elif message_type == MessageType.LEAGUE_STANDINGS_UPDATE:
            return await handle_standings_update(content)
        else:
            logger.warning(f"Unknown message type: {message_type}")
            return JSONResponse(content={"status": "unknown_message_type"})

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_game_invitation(data: Dict[str, Any]) -> JSONResponse:
    """Handle game invitation from referee"""
    global context

    match_id = data.get("match_id")
    round_id = data.get("round_id")
    opponent_id = data.get("opponent_id")
    conversation_id = data.get("conversation_id")

    logger.info(f"Invited to match {match_id} in round {round_id} vs {opponent_id}")

    # Update context
    context.state = PlayerState.IN_GAME
    context.current_match_id = match_id
    context.current_round_id = round_id
    context.current_conversation_id = conversation_id

    # Send acknowledgment
    ack_response = create_join_ack(
        context.player_id,
        context.auth_token,
        conversation_id
    )

    logger.info(f"Accepted invitation for match {match_id}")
    return JSONResponse(content=ack_response)


async def handle_choice_request(data: Dict[str, Any]) -> JSONResponse:
    """Handle parity choice request from referee"""
    global context

    match_id = data.get("match_id")
    conversation_id = data.get("conversation_id", context.current_conversation_id)

    logger.info(f"Received choice request for match {match_id}")

    # Make move decision
    drawn_number, choice = make_move()

    # Create response
    choice_response = create_choice_response(
        context.player_id,
        choice,
        context.auth_token,
        conversation_id
    )

    logger.info(f"Responding with choice: {choice} (drawn: {drawn_number})")
    return JSONResponse(content=choice_response)


async def handle_match_result(data: Dict[str, Any]) -> JSONResponse:
    """Handle match result from referee"""
    global context

    match_id = data.get("match_id")
    winner = data.get("winner")
    score = data.get("score", {})
    details = data.get("details", {})

    logger.info(f"Match {match_id} result received")

    # Log result details
    if winner:
        if winner == context.player_id:
            logger.info(f"WON match {match_id}! Score: {score}")
        else:
            logger.info(f"LOST match {match_id}. Score: {score}")
    else:
        logger.info(f"DRAW in match {match_id}. Score: {score}")

    if details:
        logger.info(f"Details: {details}")

    # Reset match context
    context.state = PlayerState.IDLE
    context.current_match_id = None

    return JSONResponse(content={"status": "acknowledged"})


async def handle_standings_update(data: Dict[str, Any]) -> JSONResponse:
    """Handle league standings update"""
    # Check if this is JSON-RPC wrapper
    params = data.get("params", data)

    round_id = params.get("round_id")
    standings = params.get("standings", [])

    logger.info(f"Received standings update for {round_id}")

    # Format and display standings
    standings_table = format_standings(standings)
    print(f"\n{standings_table}\n")

    return JSONResponse(content={"status": "acknowledged"})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "player_id": context.player_id,
        "state": context.state,
        "registered": context.state != PlayerState.NOT_REGISTERED
    }


def set_context(player_context: PlayerContext):
    """Set the global player context"""
    global context
    context = player_context
