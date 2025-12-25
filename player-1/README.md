# Player Agent - ODD EVEN Tournament

Player agent for participating in the ODD EVEN tournament system.

## Features

- Registers with league manager on startup
- Listens on localhost:8101 for game invitations
- Accepts game invitations from referees
- Makes moves by drawing random number (1-10) and choosing odd/even based on parity
- Receives and logs match results
- Displays league standings updates

## Strategy

Player uses a simple random strategy:
1. Draw random number between 1 and 10
2. If number is even, choose "even"
3. If number is odd, choose "odd"

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

## Running the Player

**IMPORTANT**: Start the league manager first (on port 8000)

```bash
python main.py
```

The player will:
1. Register with league manager at http://localhost:8000
2. Receive player ID (P01) and auth token
3. Start listening on http://localhost:8101
4. Wait for game invitations from referees

## File Structure

- `main.py` - Entry point and registration
- `player_server.py` - FastAPI application with message handlers
- `config.py` - Configuration constants
- `models.py` - Pydantic data models
- `protocol.py` - JSON-RPC message creation
- `http_client.py` - HTTP communication
- `game_logic.py` - Move decision logic

## Message Flow

1. **Game Invitation**: Referee invites player → Player sends GAME_JOIN_ACK
2. **Choice Request**: Referee requests move → Player draws number and responds with odd/even
3. **Match Result**: Referee reports outcome → Player logs result
4. **Standings Update**: League manager broadcasts standings → Player displays table

## Game Participation

When invited to a match, the player:
- Accepts invitation immediately
- Draws random number when asked for move
- Chooses parity based on number (even/odd)
- Logs result when match completes
- Displays updated standings after each round

## Ports

- Player-1: 8101
- Player-2: 8102
- Player-3: 8103
- Player-4: 8104
- League Manager: 8000
- Referees: 8001-8002

## Logging

Comprehensive logging showing:
- Registration status
- Game invitations received
- Move decisions (number drawn, choice made)
- Match results (win/loss/draw)
- Standings updates
