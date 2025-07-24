# Athl3te AI Assistant API Documentation

A comprehensive FastAPI server that provides AI-powered fitness assistance through multiple specialized agents.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API key (set in `.env` file)

### Installation
```bash
cd spoonos
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file in the spoonos directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Running the Server
```bash
python server.py
```

The server will start on `http://localhost:8000`

### API Documentation
Once running, visit `http://localhost:8000/docs` for interactive Swagger documentation.

## 🤖 Available Agents

### 1. Goal Setting Agent
Parses natural language fitness goals into structured data.

**Endpoints:**
- `POST /api/goals/set` - Parse and structure fitness goals
- `POST /api/goals/chat` - General goal setting conversation

**Example Request:**
```json
{
  "user_input": "I want to run 5km three times a week for the next month",
  "user_id": "user123"
}
```

### 2. Nutrition Agent
Analyzes nutrition data and provides dietary guidance.

**Endpoints:**
- `POST /api/nutrition/analyze` - Analyze nutrition logs against goals
- `POST /api/nutrition/log` - Log daily nutrition intake
- `POST /api/nutrition/chat` - General nutrition consultation

**Example Request (Log):**
```json
{
  "user_input": "Today I had 2000 calories, 150g protein, 250g carbs, 70g fats",
  "date": "2024-07-25",
  "user_id": "user123"
}
```

### 3. Injury Agent
Provides injury prevention and recovery guidance.

**Endpoints:**
- `POST /api/injury/prevention` - Get injury prevention advice
- `POST /api/injury/recovery` - Get injury recovery guidance
- `POST /api/injury/chat` - General injury consultation

**Example Request:**
```json
{
  "user_profile": {
    "injuries": ["knee pain"],
    "personal_info": "30-year-old runner",
    "activities": ["running"]
  },
  "question": "How can I prevent knee injuries while running?",
  "request_type": "prevention",
  "user_id": "user123"
}
```

### 4. Community Agent
Manages community engagement, challenges, and motivation.

**Endpoints:**
- `POST /api/community/insights` - Get community insights
- `POST /api/community/motivation` - Get motivational content
- `POST /api/community/challenges` - Manage community challenges
- `POST /api/community/chat` - General community interaction

**Example Request:**
```json
{
  "message": "I need some motivation to keep going with my fitness goals",
  "request_type": "motivation",
  "user_id": "user123"
}
```

## 🌐 Universal Endpoints

### Universal Chat
Automatically routes messages to the most appropriate agent based on content analysis.

**Endpoint:** `POST /api/chat`

**Example Request:**
```json
{
  "message": "What should I eat after my workout?",
  "session_id": "session123"
}
```

### Utility Endpoints

#### Health Check
`GET /health` - Server health status

#### Agents Status
`GET /api/agents/status` - Check initialization status of all agents

#### Reset Agent Session
`POST /api/agents/{agent_type}/reset` - Reset conversation state for specific agent

Agent types: `goal`, `nutrition`, `injury`, `community`

#### Test Endpoints
`GET /api/test/{agent_type}` - Test specific agent functionality

## 📋 Request/Response Models

### Common Response Format
```json
{
  "response": "AI agent response text",
  "agent_type": "goal_setting|nutrition|injury|community",
  "timestamp": "2024-07-25T10:30:00.000000",
  "session_id": "optional_session_id"
}
```

### Error Response Format
```json
{
  "detail": "Error description"
}
```

## 🔧 Testing

Run the test suite:
```bash
python test_api.py
```

This will test all endpoints and verify the server is working correctly.

## 📝 Content-Based Routing

The universal chat endpoint uses keyword analysis to route messages:

- **Goal Setting**: keywords like 'goal', 'target', 'aim', 'plan', 'objective'
- **Nutrition**: keywords like 'nutrition', 'food', 'eat', 'calories', 'protein', 'diet'
- **Injury**: keywords like 'injury', 'pain', 'hurt', 'recovery', 'prevention', 'heal'
- **Community**: keywords like 'community', 'challenge', 'motivation', 'encourage', 'leaderboard'

## 🚦 CORS Configuration

The server is configured to allow all origins for development. For production, update the CORS settings in `server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict to your domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 🔐 Security Considerations

For production deployment:
1. Set specific CORS origins
2. Add authentication middleware
3. Rate limiting
4. Input validation and sanitization
5. HTTPS only
6. Environment variable management

## 📈 Scaling

The server can be scaled using:
- Multiple Uvicorn workers
- Load balancers
- Containerization with Docker
- Cloud deployment (AWS, GCP, Azure)

## 🐛 Troubleshooting

### Common Issues

1. **Agent not initialized**: Ensure OpenAI API key is set in `.env`
2. **Import errors**: Verify all bot files are in the same directory
3. **Timeout errors**: Increase timeout values for complex requests
4. **Memory issues**: Consider implementing agent pooling for high load

### Logs
Check server logs for detailed error information. The server provides comprehensive error handling and logging.

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Run
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```
