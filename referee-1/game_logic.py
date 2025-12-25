"""Game logic for ODD EVEN tournament"""
import random
import logging
from typing import Tuple, Dict, Optional

logger = logging.getLogger(__name__)


def draw_random_number() -> int:
    """Draw a random number between 1 and 10 (inclusive)"""
    number = random.randint(1, 10)
    logger.info(f"Drew random number: {number}")
    return number


def get_parity(number: int) -> str:
    """
    Get parity of a number

    Args:
        number: Integer to check

    Returns:
        "odd" or "even"
    """
    return "odd" if number % 2 == 1 else "even"


def calculate_match_result(
    player_A_id: str,
    player_A_choice: str,
    player_B_id: str,
    player_B_choice: str,
    drawn_number: int
) -> Tuple[Optional[str], Dict[str, int], Dict[str, any]]:
    """
    Calculate match result based on ODD EVEN game rules

    Rules:
    1. If both players chose the same parity (both odd OR both even): DRAW (1 point each)
    2. Otherwise: Player whose choice matches drawn number parity WINS (3 points), other LOSES (0 points)

    Args:
        player_A_id: Player A identifier
        player_A_choice: Player A's choice ("odd" or "even")
        player_B_id: Player B identifier
        player_B_choice: Player B's choice ("odd" or "even")
        drawn_number: The number drawn by referee (1-10)

    Returns:
        Tuple of (winner_id or None, score_dict, details_dict)
    """
    drawn_parity = get_parity(drawn_number)

    # Normalize choices
    choice_A = player_A_choice.lower()
    choice_B = player_B_choice.lower()

    logger.info(f"Calculating result: {player_A_id}={choice_A}, {player_B_id}={choice_B}, drawn={drawn_number}({drawn_parity})")

    # Rule 1: Both players chose same parity = DRAW
    if choice_A == choice_B:
        logger.info("Both players chose same parity - DRAW")
        winner = None
        score = {player_A_id: 1, player_B_id: 1}
        outcome = "DRAW"
    else:
        # Rule 2: Player matching drawn parity wins
        if choice_A == drawn_parity:
            winner = player_A_id
            score = {player_A_id: 3, player_B_id: 0}
            outcome = f"{player_A_id} WINS"
        else:
            winner = player_B_id
            score = {player_A_id: 0, player_B_id: 3}
            outcome = f"{player_B_id} WINS"

        logger.info(f"Result: {outcome}")

    details = {
        "drawn_number": drawn_number,
        "drawn_parity": drawn_parity,
        "player_A_choice": choice_A,
        "player_B_choice": choice_B,
        "outcome": outcome
    }

    return winner, score, details


def handle_player_timeout(
    player_A_id: str,
    player_B_id: str,
    player_A_responded: bool,
    player_B_responded: bool
) -> Tuple[Optional[str], Dict[str, int], Dict[str, any]]:
    """
    Handle case where one or both players timeout

    Player who doesn't respond gets 0 points
    Player who responds gets 3 points (or 0 if both timeout)

    Args:
        player_A_id: Player A identifier
        player_B_id: Player B identifier
        player_A_responded: Whether player A responded in time
        player_B_responded: Whether player B responded in time

    Returns:
        Tuple of (winner_id or None, score_dict, details_dict)
    """
    if not player_A_responded and not player_B_responded:
        # Both timeout - double forfeit
        logger.warning("Both players timeout - double forfeit")
        return None, {player_A_id: 0, player_B_id: 0}, {"outcome": "DOUBLE_FORFEIT"}

    elif not player_A_responded:
        # Player A timeout
        logger.warning(f"{player_A_id} timeout - forfeit")
        return player_B_id, {player_A_id: 0, player_B_id: 3}, {"outcome": f"{player_A_id}_FORFEIT"}

    else:
        # Player B timeout
        logger.warning(f"{player_B_id} timeout - forfeit")
        return player_A_id, {player_A_id: 3, player_B_id: 0}, {"outcome": f"{player_B_id}_FORFEIT"}
