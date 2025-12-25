"""Game logic for player move decisions"""
import random
import logging

logger = logging.getLogger(__name__)


def make_move() -> tuple:
    """
    Make a move by drawing a random number and determining parity

    Returns:
        Tuple of (drawn_number, choice) where choice is "odd" or "even"
    """
    # Draw random number between 1 and 10 (inclusive)
    drawn_number = random.randint(1, 10)

    # Determine parity
    if drawn_number % 2 == 0:
        choice = "even"
    else:
        choice = "odd"

    logger.info(f"Drew number {drawn_number}, choosing '{choice}'")

    return drawn_number, choice


def format_standings(standings: list) -> str:
    """
    Format standings into a readable table

    Args:
        standings: List of standing dictionaries

    Returns:
        Formatted string table
    """
    if not standings:
        return "No standings available"

    lines = []
    lines.append("=" * 80)
    lines.append("LEAGUE STANDINGS")
    lines.append("=" * 80)
    lines.append(f"{'Rank':<6} {'ID':<6} {'Name':<20} {'P':<4} {'W':<4} {'D':<4} {'L':<4} {'Pts':<4}")
    lines.append("-" * 80)

    for s in standings:
        lines.append(
            f"{s.get('rank', 0):<6} "
            f"{s.get('player_id', ''):<6} "
            f"{s.get('display_name', ''):<20} "
            f"{s.get('played', 0):<4} "
            f"{s.get('wins', 0):<4} "
            f"{s.get('draws', 0):<4} "
            f"{s.get('losses', 0):<4} "
            f"{s.get('points', 0):<4}"
        )

    lines.append("=" * 80)
    return "\n".join(lines)
