"""Configuration for Player Agent"""

# Player configuration
PLAYER_DISPLAY_NAME = "Player-2"
PLAYER_VERSION = "1.0.0"
PLAYER_PORT = 8102  # Player-2 listens on 8102
GAME_TYPES = ["even_odd"]
MAX_CONCURRENT_MATCHES = 1

# League Manager configuration
LEAGUE_MANAGER_HOST = "localhost"
LEAGUE_MANAGER_PORT = 8000
LEAGUE_MANAGER_URL = f"http://{LEAGUE_MANAGER_HOST}:{LEAGUE_MANAGER_PORT}"

# Protocol settings
PROTOCOL_VERSION = "league.v2"
LEAGUE_ID = "league_2025_even_odd"

# Timeouts (seconds)
REGISTRATION_TIMEOUT = 5
MESSAGE_TIMEOUT = 10

# HTTP retry settings
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
