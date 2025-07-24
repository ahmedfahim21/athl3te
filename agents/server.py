from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
from datetime import datetime

# Import the bot agents
from goal_setting_bot import GoalSettingAgent
from nutrition_bot import NutritionAgent
from injury_bot import InjuryAgent
from community_bot import CommunityAgent
from spoon_ai.chat import ChatBot

# Initialize bot agents globally
goal_agent = None
nutrition_agent = None
injury_agent = None
community_agent = None

async def initialize_agents():
    """Initialize all bot agents"""
    global goal_agent, nutrition_agent, injury_agent, community_agent
    
    llm = ChatBot(llm_provider="openai", model_name="gpt-4o-mini")
    
    goal_agent = GoalSettingAgent(llm=llm)
    nutrition_agent = NutritionAgent(llm=llm)
    injury_agent = InjuryAgent(llm=llm)
    community_agent = CommunityAgent(llm=llm)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_agents()
    yield
    # Shutdown (cleanup if needed)
    pass

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Athl3te AI Assistant API",
    description="AI-powered fitness assistant with goal setting, nutrition, injury prevention, and community features",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_type: str
    timestamp: str
    session_id: Optional[str] = None

class GoalRequest(BaseModel):
    user_input: str
    user_id: Optional[str] = None

class NutritionAnalysisRequest(BaseModel):
    nutrition_goal: Optional[Dict[str, Any]] = None
    nutrition_logs: List[Dict[str, Any]]
    question: str = "How am I doing with my nutrition?"
    user_id: Optional[str] = None

class NutritionLogRequest(BaseModel):
    user_input: str
    date: Optional[str] = None
    user_id: Optional[str] = None

class InjuryRequest(BaseModel):
    user_profile: Dict[str, Any]
    question: str
    request_type: str  # "prevention" or "recovery"
    activity: Optional[str] = "general"
    injury_details: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

class CommunityRequest(BaseModel):
    message: str
    community_data: Optional[Dict[str, Any]] = None
    request_type: str  # "insights", "motivation", "challenge"
    user_id: Optional[str] = None

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Goal Setting Endpoints
@app.post("/api/goals/set", response_model=ChatResponse)
async def set_goals(request: GoalRequest):
    """Parse natural language goal descriptions into structured fitness goals"""
    try:
        if not goal_agent:
            raise HTTPException(status_code=500, detail="Goal agent not initialized")
        
        goal_agent.clear()  # Reset conversation state
        response = await goal_agent.run(request.user_input)
        
        return ChatResponse(
            response=response,
            agent_type="goal_setting",
            timestamp=datetime.now().isoformat(),
            session_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing goal request: {str(e)}")

@app.post("/api/goals/chat", response_model=ChatResponse)
async def chat_goals(request: ChatRequest):
    """General chat about goal setting"""
    try:
        if not goal_agent:
            raise HTTPException(status_code=500, detail="Goal agent not initialized")
        
        response = await goal_agent.run(request.message)
        
        return ChatResponse(
            response=response,
            agent_type="goal_setting",
            timestamp=datetime.now().isoformat(),
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in goal chat: {str(e)}")

# Nutrition Endpoints
@app.post("/api/nutrition/analyze", response_model=ChatResponse)
async def analyze_nutrition(request: NutritionAnalysisRequest):
    """Analyze nutrition logs against goals and provide feedback"""
    try:
        if not nutrition_agent:
            raise HTTPException(status_code=500, detail="Nutrition agent not initialized")
        
        nutrition_agent.clear()  # Reset conversation state
        
        # Construct the message for the nutrition agent
        message = f"Please analyze my nutrition data. Question: {request.question}"
        response = await nutrition_agent.run(message)
        
        return ChatResponse(
            response=response,
            agent_type="nutrition",
            timestamp=datetime.now().isoformat(),
            session_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing nutrition: {str(e)}")

@app.post("/api/nutrition/log", response_model=ChatResponse)
async def log_nutrition(request: NutritionLogRequest):
    """Log daily nutrition intake"""
    try:
        if not nutrition_agent:
            raise HTTPException(status_code=500, detail="Nutrition agent not initialized")
        
        nutrition_agent.clear()  # Reset conversation state
        
        # Construct the message for logging
        message = f"Please log this nutrition data: {request.user_input}"
        if request.date:
            message += f" for date {request.date}"
            
        response = await nutrition_agent.run(message)
        
        return ChatResponse(
            response=response,
            agent_type="nutrition",
            timestamp=datetime.now().isoformat(),
            session_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging nutrition: {str(e)}")

@app.post("/api/nutrition/chat", response_model=ChatResponse)
async def chat_nutrition(request: ChatRequest):
    """General nutrition consultation"""
    try:
        if not nutrition_agent:
            raise HTTPException(status_code=500, detail="Nutrition agent not initialized")
        
        response = await nutrition_agent.run(request.message)
        
        return ChatResponse(
            response=response,
            agent_type="nutrition",
            timestamp=datetime.now().isoformat(),
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in nutrition chat: {str(e)}")

# Injury Prevention & Recovery Endpoints
@app.post("/api/injury/prevention", response_model=ChatResponse)
async def injury_prevention(request: InjuryRequest):
    """Get personalized injury prevention advice"""
    try:
        if not injury_agent:
            raise HTTPException(status_code=500, detail="Injury agent not initialized")
        
        injury_agent.clear()  # Reset conversation state
        
        message = f"I need injury prevention advice. My question: {request.question}"
        response = await injury_agent.run(message)
        
        return ChatResponse(
            response=response,
            agent_type="injury_prevention",
            timestamp=datetime.now().isoformat(),
            session_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting prevention advice: {str(e)}")

@app.post("/api/injury/recovery", response_model=ChatResponse)
async def injury_recovery(request: InjuryRequest):
    """Get personalized injury recovery advice"""
    try:
        if not injury_agent:
            raise HTTPException(status_code=500, detail="Injury agent not initialized")
        
        injury_agent.clear()  # Reset conversation state
        
        message = f"I need recovery advice. My question: {request.question}"
        response = await injury_agent.run(message)
        
        return ChatResponse(
            response=response,
            agent_type="injury_recovery",
            timestamp=datetime.now().isoformat(),
            session_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recovery advice: {str(e)}")

@app.post("/api/injury/chat", response_model=ChatResponse)
async def chat_injury(request: ChatRequest):
    """General injury consultation"""
    try:
        if not injury_agent:
            raise HTTPException(status_code=500, detail="Injury agent not initialized")
        
        response = await injury_agent.run(request.message)
        
        return ChatResponse(
            response=response,
            agent_type="injury",
            timestamp=datetime.now().isoformat(),
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in injury chat: {str(e)}")

# Community Endpoints
@app.post("/api/community/insights", response_model=ChatResponse)
async def community_insights(request: CommunityRequest):
    """Get community insights and highlights"""
    try:
        if not community_agent:
            raise HTTPException(status_code=500, detail="Community agent not initialized")
        
        community_agent.clear()  # Reset conversation state
        response = await community_agent.run(request.message)
        
        return ChatResponse(
            response=response,
            agent_type="community",
            timestamp=datetime.now().isoformat(),
            session_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting community insights: {str(e)}")

@app.post("/api/community/motivation", response_model=ChatResponse)
async def community_motivation(request: CommunityRequest):
    """Get motivational content and encouragement"""
    try:
        if not community_agent:
            raise HTTPException(status_code=500, detail="Community agent not initialized")
        
        community_agent.clear()  # Reset conversation state
        response = await community_agent.run(request.message)
        
        return ChatResponse(
            response=response,
            agent_type="community",
            timestamp=datetime.now().isoformat(),
            session_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting motivation: {str(e)}")

@app.post("/api/community/challenges", response_model=ChatResponse)
async def community_challenges(request: CommunityRequest):
    """Manage community challenges"""
    try:
        if not community_agent:
            raise HTTPException(status_code=500, detail="Community agent not initialized")
        
        community_agent.clear()  # Reset conversation state
        response = await community_agent.run(request.message)
        
        return ChatResponse(
            response=response,
            agent_type="community",
            timestamp=datetime.now().isoformat(),
            session_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error managing challenges: {str(e)}")

@app.post("/api/community/chat", response_model=ChatResponse)
async def chat_community(request: ChatRequest):
    """General community interaction"""
    try:
        if not community_agent:
            raise HTTPException(status_code=500, detail="Community agent not initialized")
        
        response = await community_agent.run(request.message)
        
        return ChatResponse(
            response=response,
            agent_type="community",
            timestamp=datetime.now().isoformat(),
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in community chat: {str(e)}")

# Universal Chat Endpoint
@app.post("/api/chat", response_model=ChatResponse)
async def universal_chat(request: ChatRequest):
    """
    Universal chat endpoint that routes to the most appropriate agent
    based on message content analysis
    """
    try:
        message_lower = request.message.lower()
        
        # Simple keyword-based routing
        if any(word in message_lower for word in ['goal', 'target', 'aim', 'plan', 'objective']):
            agent = goal_agent
            agent_type = "goal_setting"
        elif any(word in message_lower for word in ['nutrition', 'food', 'eat', 'calories', 'protein', 'diet']):
            agent = nutrition_agent
            agent_type = "nutrition"
        elif any(word in message_lower for word in ['injury', 'pain', 'hurt', 'recovery', 'prevention', 'heal']):
            agent = injury_agent
            agent_type = "injury"
        elif any(word in message_lower for word in ['community', 'challenge', 'motivation', 'encourage', 'leaderboard']):
            agent = community_agent
            agent_type = "community"
        else:
            # Default to goal setting for general fitness queries
            agent = goal_agent
            agent_type = "goal_setting"
        
        if not agent:
            raise HTTPException(status_code=500, detail="Selected agent not initialized")
        
        response = await agent.run(request.message)
        
        return ChatResponse(
            response=response,
            agent_type=agent_type,
            timestamp=datetime.now().isoformat(),
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in universal chat: {str(e)}")

# Agent Status Endpoint
@app.get("/api/agents/status")
async def get_agents_status():
    """Get the status of all agents"""
    return {
        "goal_agent": "initialized" if goal_agent else "not_initialized",
        "nutrition_agent": "initialized" if nutrition_agent else "not_initialized",
        "injury_agent": "initialized" if injury_agent else "not_initialized",
        "community_agent": "initialized" if community_agent else "not_initialized",
        "timestamp": datetime.now().isoformat()
    }

# Reset Agent Session Endpoint
@app.post("/api/agents/{agent_type}/reset")
async def reset_agent_session(agent_type: str):
    """Reset the conversation state for a specific agent"""
    try:
        if agent_type == "goal":
            if goal_agent:
                goal_agent.clear()
        elif agent_type == "nutrition":
            if nutrition_agent:
                nutrition_agent.clear()
        elif agent_type == "injury":
            if injury_agent:
                injury_agent.clear()
        elif agent_type == "community":
            if community_agent:
                community_agent.clear()
        else:
            raise HTTPException(status_code=400, detail="Invalid agent type")
        
        return {"status": "success", "message": f"{agent_type} agent session reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting agent: {str(e)}")

# Development/Testing Endpoints
@app.get("/api/test/{agent_type}")
async def test_agent(agent_type: str):
    """Test endpoint for agent functionality"""
    test_messages = {
        "goal": "I want to run 5km three times a week",
        "nutrition": "I had 2000 calories today with 150g protein",
        "injury": "How can I prevent knee injuries while running?",
        "community": "Show me our top performers this week"
    }
    
    if agent_type not in test_messages:
        raise HTTPException(status_code=400, detail="Invalid agent type for testing")
    
    try:
        request = ChatRequest(message=test_messages[agent_type])
        
        if agent_type == "goal":
            return await chat_goals(request)
        elif agent_type == "nutrition":
            return await chat_nutrition(request)
        elif agent_type == "injury":
            return await chat_injury(request)
        elif agent_type == "community":
            return await chat_community(request)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing {agent_type} agent: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
