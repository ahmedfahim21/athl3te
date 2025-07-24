from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.tools.base import BaseTool
from spoon_ai.chat import ChatBot
from pydantic import BaseModel, Field
from typing import Optional
import json
import asyncio
import re
from dotenv import load_dotenv
import json
import asyncio

load_dotenv(override=True)

# ---------------------------- Goal Models ----------------------------
class BaseGoal(BaseModel):
    frequency: Optional[float] = Field(default=None, description="Frequency of the goal in days, how often the goal has to be attained, in number of days")
    duration: Optional[float] = Field(default=None, description="Duration of the goal in days")

class SportsGoal(BaseGoal):
    distance: Optional[float] = Field(default=None, description="Distance target in kilometers")
    time: Optional[float] = Field(default=None, description="Time target in minutes")
    speed: Optional[float] = Field(default=None, description="Speed target in kilometers per hour")
    calories: Optional[float] = Field(default=None, description="Calories to burn")

class NutritionGoal(BaseGoal):
    protein: Optional[float] = Field(default=None, description="Protein target in grams")
    fats: Optional[float] = Field(default=None, description="Fats target in grams")
    carbs: Optional[float] = Field(default=None, description="Carbohydrates target in grams")
    calories_consumed: Optional[float] = Field(default=None, description="Calories consumption target")
    water_consumed: Optional[float] = Field(default=None, description="Water consumption target in milliliters")

class UserGoal(BaseModel):
    cycling: Optional[SportsGoal] = Field(default=None, description="Cycling goals")
    running: Optional[SportsGoal] = Field(default=None, description="Running goals")
    swimming: Optional[SportsGoal] = Field(default=None, description="Swimming goals")
    walking: Optional[SportsGoal] = Field(default=None, description="Walking goals")
    nutrition: Optional[NutritionGoal] = Field(default=None, description="Nutrition goals")

# ---------------------------- Goal Setting Tool ----------------------------
class GoalSettingTool(BaseTool):
    """Goal Setting Tool for fitness and nutrition goals"""
    name: str = "goal_setting"
    description: str = "Parse natural language descriptions into structured fitness and nutrition goals."
    parameters: dict = {
        "type": "object",
        "properties": {
            "user_input": {
                "type": "string",
                "description": "Natural language description of fitness or nutrition goals"
            }
        },
        "required": ["user_input"]
    }

    async def execute(self, user_input: str) -> str:
        """
        Parse user input and extract structured goal information
        """
        try:
            # Initialize empty goal structure
            goals = UserGoal()
            
            # Convert to lowercase for easier parsing
            text = user_input.lower()
            
            # Parse cycling goals
            if any(word in text for word in ['cycle', 'cycling', 'bike', 'biking']):
                cycling_goal = SportsGoal()
                cycling_goal = self._extract_sports_metrics(text, cycling_goal)
                goals.cycling = cycling_goal
            
            # Parse running goals
            if any(word in text for word in ['run', 'running', 'jog', 'jogging']):
                running_goal = SportsGoal()
                running_goal = self._extract_sports_metrics(text, running_goal)
                goals.running = running_goal
            
            # Parse swimming goals
            if any(word in text for word in ['swim', 'swimming']):
                swimming_goal = SportsGoal()
                swimming_goal = self._extract_sports_metrics(text, swimming_goal)
                goals.swimming = swimming_goal
            
            # Parse walking goals
            if any(word in text for word in ['walk', 'walking']):
                walking_goal = SportsGoal()
                walking_goal = self._extract_sports_metrics(text, walking_goal)
                goals.walking = walking_goal
            
            # Parse nutrition goals
            if any(word in text for word in ['nutrition', 'eat', 'food', 'protein', 'carbs', 'calories', 'water']):
                nutrition_goal = NutritionGoal()
                nutrition_goal = self._extract_nutrition_metrics(text, nutrition_goal)
                goals.nutrition = nutrition_goal
            
            # Format the response
            return self._format_goals_response(goals)
            
        except Exception as e:
            return f"Error parsing goals: {str(e)}"
    
    def _extract_sports_metrics(self, text: str, goal: SportsGoal) -> SportsGoal:
        """Extract sports-related metrics from text"""
        import re
        
        # Extract distance (km, kilometers, miles)
        distance_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:km|kilometers?)',
            r'(\d+(?:\.\d+)?)\s*(?:miles?)',
        ]
        for pattern in distance_patterns:
            match = re.search(pattern, text)
            if match:
                distance = float(match.group(1))
                if 'mile' in pattern:
                    distance *= 1.60934  # Convert miles to km
                goal.distance = distance
                break
        
        # Extract time (minutes, hours)
        time_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:minutes?|mins?)',
            r'(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)',
        ]
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                time = float(match.group(1))
                if 'hour' in pattern or 'hr' in pattern:
                    time *= 60  # Convert hours to minutes
                goal.time = time
                break
        
        # Extract speed (kmph, mph)
        speed_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:kmph|km/h|kilometers? per hour)',
            r'(\d+(?:\.\d+)?)\s*(?:mph|miles? per hour)',
        ]
        for pattern in speed_patterns:
            match = re.search(pattern, text)
            if match:
                speed = float(match.group(1))
                if 'mph' in pattern or 'miles per hour' in pattern:
                    speed *= 1.60934  # Convert mph to kmph
                goal.speed = speed
                break
        
        # Extract calories
        calories_match = re.search(r'(\d+(?:\.\d+)?)\s*calories?', text)
        if calories_match:
            goal.calories = float(calories_match.group(1))
        
        # Extract frequency (times per week, daily, etc.)
        frequency_patterns = [
            r'(\d+)\s*times?\s*(?:per|a)\s*week',
            r'(\d+)\s*times?\s*weekly',
            r'daily|every day',
        ]
        for pattern in frequency_patterns:
            match = re.search(pattern, text)
            if match:
                if 'daily' in pattern or 'every day' in pattern:
                    goal.frequency = 1.0  # Daily = every 1 day
                else:
                    times_per_week = int(match.group(1))
                    goal.frequency = 7.0 / times_per_week  # Convert to days between sessions
                break
        
        # Extract duration (weeks, months, days)
        duration_patterns = [
            r'(?:for|over)\s*(\d+)\s*(?:weeks?)',
            r'(?:for|over)\s*(\d+)\s*(?:months?)',
            r'(?:for|over)\s*(\d+)\s*(?:days?)',
        ]
        for pattern in duration_patterns:
            match = re.search(pattern, text)
            if match:
                duration = int(match.group(1))
                if 'week' in pattern:
                    duration *= 7  # Convert weeks to days
                elif 'month' in pattern:
                    duration *= 30  # Convert months to days
                goal.duration = float(duration)
                break
        
        return goal
    
    def _extract_nutrition_metrics(self, text: str, goal: NutritionGoal) -> NutritionGoal:
        """Extract nutrition-related metrics from text"""
        import re
        
        # Extract protein
        protein_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:g|grams?)\s*(?:of\s*)?protein', text)
        if protein_match:
            goal.protein = float(protein_match.group(1))
        
        # Extract carbs
        carbs_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:g|grams?)\s*(?:of\s*)?(?:carbs|carbohydrates?)',
        ]
        for pattern in carbs_patterns:
            match = re.search(pattern, text)
            if match:
                goal.carbs = float(match.group(1))
                break
        
        # Extract fats
        fats_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:g|grams?)\s*(?:of\s*)?fats?', text)
        if fats_match:
            goal.fats = float(fats_match.group(1))
        
        # Extract calories consumed
        calories_consumed_match = re.search(r'(\d+(?:\.\d+)?)\s*calories?\s*(?:per day|daily|consumed?)', text)
        if calories_consumed_match:
            goal.calories_consumed = float(calories_consumed_match.group(1))
        
        # Extract water consumption
        water_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:ml|milliliters?)\s*(?:of\s*)?water',
            r'(\d+(?:\.\d+)?)\s*(?:l|liters?)\s*(?:of\s*)?water',
        ]
        for pattern in water_patterns:
            match = re.search(pattern, text)
            if match:
                water = float(match.group(1))
                if 'l' in pattern and 'ml' not in pattern:
                    water *= 1000  # Convert liters to milliliters
                goal.water_consumed = water
                break
        
        return goal
    
    def _format_goals_response(self, goals: UserGoal) -> str:
        """Format the parsed goals into a readable response"""
        response = "🎯 **Parsed Goals:**\n\n"
        
        # Sports goals
        for sport_name, sport_goal in [
            ("🚴 Cycling", goals.cycling),
            ("🏃 Running", goals.running),
            ("🏊 Swimming", goals.swimming),
            ("🚶 Walking", goals.walking)
        ]:
            if sport_goal and any([sport_goal.distance, sport_goal.time, sport_goal.speed, sport_goal.calories, sport_goal.frequency, sport_goal.duration]):
                response += f"{sport_name}:\n"
                if sport_goal.distance:
                    response += f"  • Distance: {sport_goal.distance} km\n"
                if sport_goal.time:
                    response += f"  • Time: {sport_goal.time} minutes\n"
                if sport_goal.speed:
                    response += f"  • Speed: {sport_goal.speed} km/h\n"
                if sport_goal.calories:
                    response += f"  • Calories to burn: {sport_goal.calories}\n"
                if sport_goal.frequency:
                    response += f"  • Frequency: Every {sport_goal.frequency} days\n"
                if sport_goal.duration:
                    response += f"  • Duration: {sport_goal.duration} days\n"
                response += "\n"
        
        # Nutrition goals
        if goals.nutrition and any([goals.nutrition.protein, goals.nutrition.carbs, goals.nutrition.fats, goals.nutrition.calories_consumed, goals.nutrition.water_consumed]):
            response += "🥗 Nutrition:\n"
            if goals.nutrition.protein:
                response += f"  • Protein: {goals.nutrition.protein}g\n"
            if goals.nutrition.carbs:
                response += f"  • Carbohydrates: {goals.nutrition.carbs}g\n"
            if goals.nutrition.fats:
                response += f"  • Fats: {goals.nutrition.fats}g\n"
            if goals.nutrition.calories_consumed:
                response += f"  • Calories: {goals.nutrition.calories_consumed}\n"
            if goals.nutrition.water_consumed:
                response += f"  • Water: {goals.nutrition.water_consumed}ml\n"
            response += "\n"
        
        if response == "� **Parsed Goals:**\n\n":
            response = "No specific fitness or nutrition goals were detected in your input. Please provide more specific details about your goals."
        
        # Add JSON format for structured data
        response += "\n📋 **Structured Data:**\n```json\n"
        response += json.dumps(goals.model_dump(), indent=2, default=str)
        response += "\n```"
        
        return response

# ---------------------------- Agent Definition ----------------------------
class GoalSettingAgent(ToolCallAgent):
    """
    A fitness and nutrition goal setting assistant that can parse natural language
    descriptions into structured goal data for cycling, running, swimming, walking, and nutrition.
    """

    name: str = "goal_setting_agent"
    description: str = (
        "A fitness and nutrition goal setting assistant that can:\n"
        "1. Parse natural language descriptions into structured fitness goals\n"
        "2. Extract metrics for cycling, running, swimming, walking activities\n"
        "3. Parse nutrition goals including protein, carbs, fats, calories, and water intake\n"
        "4. Provide structured goal data in JSON format"
    )

    system_prompt: str = """
    You are a fitness and nutrition goal setting assistant. Your primary function is to help users
    convert their natural language descriptions of fitness and nutrition goals into structured data.
    
    You can process goals for:
    - Cycling (distance, time, speed, calories, frequency, duration)
    - Running (distance, time, speed, calories, frequency, duration)
    - Swimming (distance, time, speed, calories, frequency, duration)
    - Walking (distance, time, speed, calories, frequency, duration)
    - Nutrition (protein, carbs, fats, calories consumed, water intake)
    
    When a user describes their goals, use the goal_setting tool to parse their input and
    provide them with structured goal data. Be encouraging and helpful in your responses.
    
    If the user asks about anything other than setting fitness or nutrition goals,
    politely redirect them back to goal setting topics.
    """

    next_step_prompt: str = (
        "Based on the goal parsing result, provide encouragement and ask if the user "
        "would like to set additional goals or modify any of the parsed goals."
    )

    max_steps: int = 3

    avaliable_tools: ToolManager = Field(default_factory=lambda: ToolManager([
        GoalSettingTool(),
    ]))


async def main():
    # Create a GoalSettingAgent instance
    goal_agent = GoalSettingAgent(llm=ChatBot(llm_provider="openai", model_name="gpt-4o-mini"))
    print("=== Fitness & Nutrition Goal Setting Assistant ===")
    print("Tell me about your fitness or nutrition goals, and I'll help structure them!\n")

    # Reset the Agent state
    goal_agent.clear()

    # Example goal setting
    test_input = """I want to cycle 20km three times a week for the next month, 
    targeting a speed of 25kmph. I also want to track my nutrition, 
    aiming for 2000 calories per day with 150g protein."""
    
    print(f"Example input: {test_input}\n")
    response = await goal_agent.run(test_input)
    print(f"Response: {response}\n")

if __name__ == "__main__":
    asyncio.run(main()) 
