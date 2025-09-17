# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- **Install dependencies**: `pip install -r requirements.txt`
- **Run application**: `python app.py`
- **Access application**: http://localhost:5000

## High-Level Architecture

This is a Flask-based multiplayer "Turtle Soup" (海龟汤) riddle game platform with AI host capabilities. The architecture follows a traditional web application pattern with real-time features implemented via polling.

### Core Components

**Backend (app.py)**:
- Flask web server handling all HTTP routes and API endpoints
- OpenAI API integration for AI game host functionality 
- In-memory room storage with thread-safe operations using `rooms_lock`
- Asynchronous AI processing using ThreadPoolExecutor to prevent blocking
- File-based story management with approval workflow

**Frontend**:
- Single-page application in `static/main.js` with page switching
- Real-time updates via polling mechanisms (messages, online users, chat)
- Dual chat system: AI-moderated game chat + regular group chat

### Key Data Structures

**Room Object**:
```python
{
    'owner': str,           # Room creator nickname
    'base_url': str,        # OpenAI API endpoint
    'api_key': str,         # OpenAI API key
    'model': str,           # AI model name
    'messages': [],         # Game conversation history
    'members': {},          # Room participants
    'stories': [],          # Uploaded riddle stories
    'current_story': int,   # Active story index
    'chat_messages': [],    # Non-AI group chat
    'online_users': {},     # Heartbeat tracking
}
```

**Story Format**:
```json
{
    "surface": "riddle question",
    "answer": "complete story/answer", 
    "victory_condition": "winning criteria",
    "additional": "optional hints"
}
```

### Game Flow

1. **Room Creation**: Owner sets up room with OpenAI credentials
2. **Story Management**: Upload JSON stories or load from story plaza
3. **AI Interaction**: Players ask yes/no questions, AI responds according to turtle soup rules
4. **Story Restoration**: Players attempt to reconstruct the full story
5. **Answer Reveal**: Owner can reveal the answer when appropriate

### Story Plaza System

- **Upload Pipeline**: Stories uploaded to `upload/json/norelease/` for admin approval
- **Approval Process**: Admin moves approved stories to `upload/json/release/`
- **Story Numbering**: Auto-incrementing counter maintained in `config.json`
- **One-Click Start**: Direct loading of approved stories into game rooms

### Configuration

Critical settings in `config.json`:
- `preset`: AI host prompt template with game rules
- `admin`: Admin credentials for story approval and room management
- `story_counter`: Auto-incrementing story ID counter
- `options`: Dropdown choices for models, API endpoints, and keys

### Thread Safety

- All room operations protected by `rooms_lock`
- AI processing handled asynchronously to prevent request blocking
- Heartbeat system for online user tracking with cleanup

### File Storage

```
upload/json/
├── norelease/    # Pending approval stories
└── release/      # Published stories available for gameplay
```