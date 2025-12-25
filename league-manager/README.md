# League Manager - ODD EVEN Tournament

Central coordinator for the ODD EVEN tournament system managing 4 players and 2 referees.

## Features

- HTTP server on localhost:8000
- Referee and player registration with authentication
- Round-robin tournament scheduling (3 rounds)
- Match coordination with referees
- Real-time standings tracking
- Automatic standings broadcast to players

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

## Running the League Manager

```bash
python server.py
```

The server will start on `http://localhost:8000` and wait for registrations.

## Expected Flow

1. **Registration Phase**:
   - 2 referees register (REF01, REF02)
   - 4 players register (P01, P02, P03, P04)

2. **Tournament Start**:
   - Schedule is generated and printed
   - Round 1 begins automatically

3. **Round Execution**:
   - League manager notifies referees to start matches
   - Referees report results back
   - Standings are updated and broadcast to players
   - 60-second delay before next round

4. **Tournament End**:
   - After 3 rounds, final standings are displayed

## API Endpoints

### POST /MCP
Main endpoint for JSON-RPC 2.0 messages:
- REFEREE_REGISTER_REQUEST
- PLAYER_REGISTER_REQUEST
- MATCH_RESULT_REPORT

### GET /health
Health check and status endpoint

## File Structure

- `server.py` - Main FastAPI application
- `models.py` - Data models and Pydantic schemas
- `registration.py` - Registration management
- `scheduler.py` - Round-robin tournament scheduler
- `standings.py` - Standings calculation and display
- `http_client.py` - HTTP communication with agents

## JSON-RPC Protocol

All messages use the `league.v2` protocol with standard envelope:
```json
{
  "protocol": "league.v2",
  "message_type": "<TYPE>",
  "sender": "league_manager",
  "timestamp": "<ISO-8601>",
  "conversation_id": "<UUID>",
  "auth_token": "<TOKEN>",
  "league_id": "league_2025_even_odd"
}
```

## Ports

- League Manager: 8000
- Referees: 8101, 8102
- Players: 8201-8204
