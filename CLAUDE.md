# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based multiplayer online Chemistry Turtle Soup reasoning game platform that combines AI-driven game hosting with collaborative puzzle-solving. The platform features both regular turtle soup games and specialized chemistry-themed puzzles with built-in problem sets.

**Key Architecture**: Single Flask app (`app.py`) serving both web UI and REST APIs, using in-memory data storage for game sessions and file system for story persistence.

## Development Commands

### Running the Application
```bash
python app.py
```
- Starts Flask server on port 5002 (configurable via PORT env var)
- Serves main game interface at `http://localhost:5002`
- Provides API test interface at `http://localhost:5002/test`

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Testing the APIs
- Access `/test` endpoint for comprehensive API testing interface
- Use `/health` for health checks
- Chemistry game APIs are at `/api/game/*` endpoints
- Original turtle soup APIs use different patterns

## Architecture Overview

### Core Components

**Flask Application** (`app.py`):
- Single monolithic Flask app handling both chemistry and original turtle soup games
- Built-in chemistry problems with educational content (lines 47-131)
- OpenAI API integration for AI game hosting
- In-memory session management with automatic cleanup
- ThreadPoolExecutor for async AI processing

**Game Types**:
1. **Chemistry Turtle Soup**: Educational chemistry puzzles with pre-loaded problems
2. **Original Turtle Soup**: User-uploaded story-based puzzles

**Data Storage**:
- Sessions: In-memory (`active_sessions` dict)
- Chemistry problems: Built-in + loadable from `data/` directory
- Original stories: File system in `upload/json/` structure
- Configuration: `config.json`

### Key Data Structures

**Chemistry Session**:
```python
{
    'session_id': str,
    'current_problem': str,
    'problem_data': dict,
    'conversation_history': list,
    'hints_used': int,
    'start_time': float,
    'status': 'playing'|'completed'
}
```

**Chemistry Problem**:
```python
{
    'id': str,
    'title': str,
    'surface': str,           # Question/setup
    'answer': str,           # Complete explanation
    'victory_condition': str, # Win condition
    'hints': list,           # Progressive hints
    'difficulty': int,       # 1-5 scale
    'category': str,         # e.g., "氧化还原反应"
    'keywords': list
}
```

## Key Features

### Chemistry Game System
- Pre-loaded educational chemistry problems covering oxidation-reduction reactions and acid-base chemistry
- Progressive hint system (max 3 hints per game)
- AI judges story restoration attempts
- Automatic session timeout (1 hour default)

### AI Integration
- OpenAI API with configurable models and endpoints
- Structured prompt engineering for chemistry education
- Async processing with ThreadPoolExecutor
- Built-in error handling and timeout management

### Session Management
- Memory-based storage (data lost on restart)
- Automatic cleanup of expired sessions (10-minute intervals)
- Heart-beat style API for real-time gaming

## API Architecture

### Chemistry Game APIs (`/api/game/*`)
- `POST /api/game/start` - Start new chemistry game session
- `POST /api/game/ask` - Submit question to AI host
- `POST /api/game/hint` - Request progressive hints
- `GET /api/game/status` - Get current game state
- `GET /api/categories` - Get problem categories
- `GET /api/problems` - List available problems

### Original Turtle Soup APIs (`/api/*`)
- Room-based multiplayer system with invite codes
- File upload for custom stories
- Story plaza for community sharing
- Admin panel for content moderation

## Configuration

### Environment Variables
- `PORT`: Server port (default: 5002)

### config.json Structure
```json
{
  "ai_settings": {
    "base_url": "http://api.0ha.top/v1",
    "api_key": "your-key-here",
    "model": "gpt-4o-mini"
  },
  "game_settings": {
    "session_timeout": 3600,
    "max_hints": 3
  }
}
```

## File Structure

**Data Files**:
- `data/chemistry_problems.json` - External chemistry problem sets
- `data/categories.json` - Problem categorization
- `upload/json/release/` - Published community stories
- `upload/json/norelease/` - Pending story submissions

**Static Assets**: Currently empty (`static/`, `templates/` directories exist but unused - app serves embedded HTML)

## Testing and Development

### Built-in Test Interface
Access `/test` for comprehensive API testing with:
- Game session management
- Real-time chat simulation  
- Hint progression testing
- API logging and debugging

### Development Notes
- Server runs in non-debug mode by default
- All AI processing is asynchronous to prevent blocking
- Memory-only storage means sessions don't persist across restarts
- Chemistry problems have built-in fallbacks if external files missing

## Integration Points

**AI Model Configuration**: Easily swap OpenAI models via config.json
**Problem Sets**: Add new chemistry problems via JSON files in `data/` directory
**UI Extensions**: Can add static files and templates for enhanced frontend
**Database Migration**: Current in-memory storage can be replaced with persistent storage

## Common Development Tasks

### Adding New Chemistry Problems
1. Edit `data/chemistry_problems.json` or modify built-in problems in `load_builtin_problems()`
2. Follow existing problem structure with required fields
3. Update categories in `data/categories.json` if needed

### Modifying AI Behavior
- Edit `ChemistryPromptManager.build_system_prompt()` for game rules
- Update context dictionaries for different problem categories
- Adjust victory detection logic in ask_question endpoint

### Extending APIs
- Add new endpoints following existing pattern in app.py
- Use consistent JSON response format with error handling
- Consider async processing for AI-dependent operations