# Referee Agent - ODD EVEN Tournament

Referee agent for coordinating matches in the ODD EVEN tournament system.

## Features

- Registers with league manager on startup
- Listens on localhost:8002 for match assignments
- Coordinates games between two players
- Collects player choices (odd/even)
- Draws random number (1-10) and determines winner
- Reports results to league manager
- Handles player timeouts and network failures

## Game Rules

1. Both players choose "odd" or "even"
2. Referee draws random number 1-10
3. **If both players chose same parity**: DRAW (1 point each)
4. **Otherwise**: Player matching drawn number parity WINS (3 points), other LOSES (0 points)

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Referee

**IMPORTANT**: Start the league manager first (on port 8000)

```bash
python main.py
```

The referee will:
1. Register with league manager at http://localhost:8000
2. Receive referee ID (REF02) and auth token
3. Start listening on http://localhost:8002
4. Wait for match assignments

## File Structure

- `main.py` - Entry point and registration
- `referee_server.py` - FastAPI application
- `config.py` - Configuration constants
- `models.py` - Pydantic data models
- `protocol.py` - JSON-RPC message creation
- `http_client.py` - HTTP communication with retry
- `game_logic.py` - Match result calculation

## Match Flow

1. **Round Announcement**: League manager assigns match
2. **Player Invitation**: Referee invites both players
3. **Choice Collection**: Referee requests odd/even from each player
4. **Result Calculation**: Draw number, determine winner, assign points
5. **Result Reporting**: Send results to league manager

## Error Handling

- **Network failures**: Automatic retry with exponential backoff (max 3 attempts)
- **Player timeout**: Non-responding player gets 0 points
- **Both timeout**: Double forfeit (0-0)
- **Invalid responses**: Logged and treated as timeout

## Ports

- Referee-1: 8001
- Referee-2: 8002
- League Manager: 8000
- Players: 8101-8104

## Logging

Comprehensive logging to console with timestamps, showing:
- Registration status
- Match assignments
- Player invitations and responses
- Drawn numbers and choices
- Match outcomes
- Result reporting
