"""Configuration for Referee Agent"""

# Referee configuration
REFEREE_DISPLAY_NAME = "Referee-1"
REFEREE_VERSION = "1.0.0"
REFEREE_PORT = 8001  # Referee-1 listens on 8001
GAME_TYPES = ["even_odd"]
MAX_CONCURRENT_MATCHES = 1

# League Manager configuration
LEAGUE_MANAGER_HOST = "localhost"
LEAGUE_MANAGER_PORT = 8000
LEAGUE_MANAGER_URL = f"http://{LEAGUE_MANAGER_HOST}:{LEAGUE_MANAGER_PORT}"

# Player port mapping (players listen on 8101-8104)
PLAYER_PORT_MAP = {
    "P01": 8101,
    "P02": 8102,
    "P03": 8103,
    "P04": 8104
}

# Protocol settings
PROTOCOL_VERSION = "league.v2"
LEAGUE_ID = "league_2025_even_odd"

# Timeouts (seconds)
REGISTRATION_TIMEOUT = 5
PLAYER_INVITE_TIMEOUT = 10
PLAYER_CHOICE_TIMEOUT = 10
RESULT_REPORT_TIMEOUT = 10

# HTTP retry settings
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
