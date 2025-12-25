"""Standings management and calculation"""
from typing import Dict, List
from models import StandingsData, PlayerStanding, MatchResult
from tabulate import tabulate
import logging

logger = logging.getLogger(__name__)


class StandingsManager:
    """Manages player standings and statistics"""

    def __init__(self):
        self.standings: Dict[str, StandingsData] = {}

    def initialize_player(self, player_id: str, display_name: str):
        """Initialize standings for a player"""
        self.standings[player_id] = StandingsData(display_name=display_name)
        logger.info(f"Initialized standings for {player_id}")

    def update_from_result(self, result: MatchResult):
        """
        Update standings based on match result
        Points: Win = 3, Draw = 1, Loss = 0
        """
        score = result.score
        winner = result.winner

        # Get both players from the score dict
        players = list(score.keys())
        if len(players) != 2:
            logger.error(f"Invalid score format: {score}")
            return

        player_a, player_b = players

        # Update matches played for both
        self.standings[player_a].played += 1
        self.standings[player_b].played += 1

        # Determine outcome and update standings
        if winner is None or winner == "":
            # Draw - both get 1 point
            self.standings[player_a].draws += 1
            self.standings[player_a].points += 1
            self.standings[player_b].draws += 1
            self.standings[player_b].points += 1
            logger.info(f"Match result: {player_a} vs {player_b} - DRAW")
        elif winner == player_a:
            # Player A wins
            self.standings[player_a].wins += 1
            self.standings[player_a].points += 3
            self.standings[player_b].losses += 1
            logger.info(f"Match result: {player_a} WINS vs {player_b}")
        elif winner == player_b:
            # Player B wins
            self.standings[player_b].wins += 1
            self.standings[player_b].points += 3
            self.standings[player_a].losses += 1
            logger.info(f"Match result: {player_b} WINS vs {player_a}")
        else:
            logger.error(f"Unknown winner: {winner}")

    def get_sorted_standings(self) -> List[PlayerStanding]:
        """
        Get standings sorted by:
        1. Total points (descending)
        2. Wins (descending)
        Returns list of PlayerStanding with ranks assigned
        """
        standings_list = []

        for player_id, data in self.standings.items():
            standings_list.append({
                'player_id': player_id,
                'display_name': data.display_name,
                'played': data.played,
                'wins': data.wins,
                'draws': data.draws,
                'losses': data.losses,
                'points': data.points
            })

        # Sort by points (desc), then wins (desc)
        standings_list.sort(key=lambda x: (x['points'], x['wins']), reverse=True)

        # Assign ranks
        result = []
        for rank, standing in enumerate(standings_list, start=1):
            result.append(PlayerStanding(
                rank=rank,
                player_id=standing['player_id'],
                display_name=standing['display_name'],
                played=standing['played'],
                wins=standing['wins'],
                draws=standing['draws'],
                losses=standing['losses'],
                points=standing['points']
            ))

        return result

    def print_standings(self):
        """Print formatted standings table"""
        standings = self.get_sorted_standings()

        table_data = []
        for s in standings:
            table_data.append([
                s.rank,
                s.player_id,
                s.display_name,
                s.played,
                s.wins,
                s.draws,
                s.losses,
                s.points
            ])

        headers = ["Rank", "ID", "Name", "Played", "W", "D", "L", "Points"]

        print("\n" + "="*80)
        print("CURRENT STANDINGS")
        print("="*80)
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print("="*80 + "\n")

    def get_player_data(self, player_id: str) -> StandingsData:
        """Get standings data for specific player"""
        return self.standings.get(player_id)
