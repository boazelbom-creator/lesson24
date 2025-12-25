"""Round-robin tournament scheduler"""
from typing import List, Dict, Tuple
from models import Match
import logging

logger = logging.getLogger(__name__)


class TournamentScheduler:
    """Generates round-robin tournament schedule"""

    def __init__(self, player_ids: List[str], referee_ids: List[str]):
        """
        Initialize scheduler with player and referee IDs
        Args:
            player_ids: List of 4 player IDs (P01-P04)
            referee_ids: List of 2 referee IDs (REF01-REF02)
        """
        self.player_ids = sorted(player_ids)
        self.referee_ids = sorted(referee_ids)
        self.schedule: List[List[Match]] = []

    def generate_schedule(self) -> List[List[Match]]:
        """
        Generate 3-round tournament schedule
        Each player faces all 3 opponents exactly once
        Returns: List of rounds, each containing 2 matches
        """
        # Round-robin pairings for 4 players across 3 rounds
        # Each round has 2 matches (4 players / 2)
        pairings = [
            # Round 1
            [(0, 1), (2, 3)],
            # Round 2
            [(0, 2), (1, 3)],
            # Round 3
            [(0, 3), (1, 2)]
        ]

        self.schedule = []

        for round_idx, round_pairings in enumerate(pairings):
            round_num = round_idx + 1
            round_matches = []

            for match_idx, (p1_idx, p2_idx) in enumerate(round_pairings):
                match_num = match_idx + 1

                # Assign referee (alternate between REF01 and REF02)
                referee_idx = match_idx % len(self.referee_ids)
                referee_id = self.referee_ids[referee_idx]

                match = Match(
                    match_id=f"R{round_num}M{match_num}",
                    game_type="even_odd",
                    player_A_id=self.player_ids[p1_idx],
                    player_B_id=self.player_ids[p2_idx],
                    referee_id=referee_id
                )

                round_matches.append(match)

            self.schedule.append(round_matches)

        return self.schedule

    def print_schedule(self):
        """Print formatted game plan"""
        print("\n" + "="*70)
        print("TOURNAMENT SCHEDULE - EVEN ODD GAME")
        print("="*70)

        for round_idx, round_matches in enumerate(self.schedule):
            round_num = round_idx + 1
            print(f"\nROUND {round_num}:")
            print("-" * 70)

            for match_idx, match in enumerate(round_matches):
                match_num = match_idx + 1
                print(f"  Match {match_num} ({match.match_id}): "
                      f"{match.player_A_id} vs {match.player_B_id} "
                      f"[Referee: {match.referee_id}]")

        print("\n" + "="*70 + "\n")

    def get_round_matches(self, round_num: int) -> List[Match]:
        """Get matches for a specific round (1-indexed)"""
        if 1 <= round_num <= len(self.schedule):
            return self.schedule[round_num - 1]
        return []

    def get_total_rounds(self) -> int:
        """Get total number of rounds"""
        return len(self.schedule)

    def validate_schedule(self) -> bool:
        """Validate that schedule is correct"""
        # Check each player plays exactly 3 matches
        player_match_count = {pid: 0 for pid in self.player_ids}

        for round_matches in self.schedule:
            for match in round_matches:
                player_match_count[match.player_A_id] += 1
                player_match_count[match.player_B_id] += 1

        # Each player should play exactly 3 matches (one against each opponent)
        if not all(count == 3 for count in player_match_count.values()):
            logger.error("Schedule validation failed: not all players have 3 matches")
            return False

        # Check no duplicate pairings
        pairings_set = set()
        for round_matches in self.schedule:
            for match in round_matches:
                pairing = tuple(sorted([match.player_A_id, match.player_B_id]))
                if pairing in pairings_set:
                    logger.error(f"Schedule validation failed: duplicate pairing {pairing}")
                    return False
                pairings_set.add(pairing)

        logger.info("Schedule validation passed")
        return True
