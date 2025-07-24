from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.tools.base import BaseTool
from spoon_ai.chat import ChatBot
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json
import asyncio
import re
from dotenv import load_dotenv
import json
import asyncio

load_dotenv(override=True)

# ---------------------------- Nutrition Models ----------------------------
class BaseGoal(BaseModel):
    frequency: Optional[float] = Field(default=None, description="Frequency of the goal in days")
    duration: Optional[float] = Field(default=None, description="Duration of the goal in days")

class NutritionGoal(BaseGoal):
    protein: Optional[float] = Field(default=None, description="Protein target in grams")
    fats: Optional[float] = Field(default=None, description="Fats target in grams")
    carbs: Optional[float] = Field(default=None, description="Carbohydrates target in grams")
    calories_consumed: Optional[float] = Field(default=None, description="Calories consumption target")
    water_consumed: Optional[float] = Field(default=None, description="Water consumption target in milliliters")

class NutritionLog(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    protein: float = Field(description="Protein consumed in grams")
    fats: float = Field(description="Fats consumed in grams")
    carbs: float = Field(description="Carbohydrates consumed in grams")
    calories_consumed: float = Field(description="Total calories consumed")
    water_consumed: float = Field(description="Water consumed in milliliters")

class NutritionAnalysis(BaseModel):
    average_calories: float
    average_protein: float
    average_carbs: float
    average_fats: float
    average_water: float
    goal_completion_rate: Dict[str, float]
    recommendations: List[str]

# ---------------------------- Nutrition Analysis Tool ----------------------------
class NutritionAnalysisTool(BaseTool):
    """Nutrition Analysis Tool for analyzing nutrition logs against goals"""
    name: str = "nutrition_analysis"
    description: str = "Analyze nutrition logs against goals and provide personalized feedback and recommendations."
    parameters: dict = {
        "type": "object",
        "properties": {
            "nutrition_goal": {
                "type": "object",
                "description": "User's nutrition goals including protein, carbs, fats, calories, and water targets"
            },
            "nutrition_logs": {
                "type": "array",
                "description": "List of nutrition logs with daily intake data",
                "items": {
                    "type": "object"
                }
            },
            "question": {
                "type": "string",
                "description": "Specific question or request about nutrition analysis",
                "default": "How am I doing with my nutrition?"
            }
        },
        "required": ["nutrition_logs"]
    }

    async def execute(self, nutrition_goal: Dict[str, Any] = None, nutrition_logs: List[Dict[str, Any]] = None, question: str = "How am I doing with my nutrition?") -> str:
        """
        Analyze nutrition logs and provide personalized feedback
        """
        try:
            if not nutrition_logs:
                return "❌ No nutrition logs provided for analysis. Please log your daily nutrition intake first."

            # Analyze the logs
            analysis = self._analyze_logs(nutrition_logs)
            
            # Calculate goal completion if goals are provided
            if nutrition_goal:
                analysis.goal_completion_rate = self._calculate_goal_completion(nutrition_goal, analysis)
            
            # Generate comprehensive feedback
            return self._generate_feedback(nutrition_goal, nutrition_logs, analysis, question)
            
        except Exception as e:
            return f"❌ Error analyzing nutrition data: {str(e)}"

    def _analyze_logs(self, logs: List[Dict[str, Any]]) -> NutritionAnalysis:
        """Analyze nutrition logs and generate statistical summary"""
        if not logs:
            return None
            
        total_days = len(logs)
        
        # Calculate averages
        avg_calories = sum(log.get("calories_consumed", 0) for log in logs) / total_days
        avg_protein = sum(log.get("protein", 0) for log in logs) / total_days
        avg_carbs = sum(log.get("carbs", 0) for log in logs) / total_days
        avg_fats = sum(log.get("fats", 0) for log in logs) / total_days
        avg_water = sum(log.get("water_consumed", 0) for log in logs) / total_days
        
        # Generate basic recommendations
        recommendations = []
        
        # Protein recommendations
        if avg_protein < 50:
            recommendations.append("Consider increasing protein intake with lean meats, eggs, or legumes")
        elif avg_protein > 200:
            recommendations.append("Monitor protein intake - consider balancing with other macronutrients")
        
        # Hydration recommendations
        if avg_water < 2000:
            recommendations.append("Increase water intake - aim for at least 2-3 liters daily")
        
        # Calorie recommendations
        if avg_calories < 1200:
            recommendations.append("Consider increasing calorie intake to meet basic metabolic needs")
        elif avg_calories > 3000:
            recommendations.append("Monitor calorie intake if weight management is a goal")
        
        return NutritionAnalysis(
            average_calories=avg_calories,
            average_protein=avg_protein,
            average_carbs=avg_carbs,
            average_fats=avg_fats,
            average_water=avg_water,
            goal_completion_rate={},
            recommendations=recommendations
        )

    def _calculate_goal_completion(self, goal: Dict[str, Any], analysis: NutritionAnalysis) -> Dict[str, float]:
        """Calculate completion rates for each nutrition goal"""
        completion_rates = {}
        
        if goal.get('calories_consumed'):
            completion_rates['calories'] = round((analysis.average_calories / goal['calories_consumed']) * 100, 1)
        if goal.get('protein'):
            completion_rates['protein'] = round((analysis.average_protein / goal['protein']) * 100, 1)
        if goal.get('carbs'):
            completion_rates['carbs'] = round((analysis.average_carbs / goal['carbs']) * 100, 1)
        if goal.get('fats'):
            completion_rates['fats'] = round((analysis.average_fats / goal['fats']) * 100, 1)
        if goal.get('water_consumed'):
            completion_rates['water'] = round((analysis.average_water / goal['water_consumed']) * 100, 1)
            
        return completion_rates

    def _generate_feedback(self, goal: Dict[str, Any], logs: List[Dict[str, Any]], analysis: NutritionAnalysis, question: str) -> str:
        """Generate comprehensive nutrition feedback"""
        
        response = f"🥗 **Nutrition Analysis Report**\n\n"
        response += f"📊 **Average Daily Intake** (based on {len(logs)} days):\n"
        response += f"  • Calories: {analysis.average_calories:.0f} kcal\n"
        response += f"  • Protein: {analysis.average_protein:.1f}g\n"
        response += f"  • Carbohydrates: {analysis.average_carbs:.1f}g\n"
        response += f"  • Fats: {analysis.average_fats:.1f}g\n"
        response += f"  • Water: {analysis.average_water:.0f}ml\n\n"
        
        # Goal completion section
        if goal and analysis.goal_completion_rate:
            response += "🎯 **Goal Progress:**\n"
            for nutrient, rate in analysis.goal_completion_rate.items():
                emoji = "✅" if 90 <= rate <= 110 else "⚠️" if 80 <= rate <= 120 else "❌"
                response += f"  {emoji} {nutrient.title()}: {rate}% of target\n"
            response += "\n"
        
        # Macro distribution
        total_macros = analysis.average_protein + analysis.average_carbs + analysis.average_fats
        if total_macros > 0:
            protein_pct = (analysis.average_protein * 4 / analysis.average_calories) * 100
            carbs_pct = (analysis.average_carbs * 4 / analysis.average_calories) * 100
            fats_pct = (analysis.average_fats * 9 / analysis.average_calories) * 100
            
            response += "📈 **Macronutrient Distribution:**\n"
            response += f"  • Protein: {protein_pct:.1f}% (recommended: 15-25%)\n"
            response += f"  • Carbs: {carbs_pct:.1f}% (recommended: 45-60%)\n"
            response += f"  • Fats: {fats_pct:.1f}% (recommended: 20-35%)\n\n"
        
        # Recommendations
        if analysis.recommendations:
            response += "💡 **Recommendations:**\n"
            for i, rec in enumerate(analysis.recommendations, 1):
                response += f"  {i}. {rec}\n"
            response += "\n"
        
        # Personalized insights based on question
        response += "🔍 **Insights:**\n"
        if "hydration" in question.lower() or "water" in question.lower():
            if analysis.average_water >= 2500:
                response += "  • Excellent hydration levels! Keep it up.\n"
            elif analysis.average_water >= 2000:
                response += "  • Good hydration, consider increasing slightly for optimal performance.\n"
            else:
                response += "  • Focus on increasing water intake throughout the day.\n"
        elif "protein" in question.lower():
            if analysis.average_protein >= 1.2 * 70:  # Assuming 70kg average weight
                response += "  • Protein intake looks good for muscle maintenance and recovery.\n"
            else:
                response += "  • Consider adding more protein sources to support your fitness goals.\n"
        else:
            # General insights
            if goal and analysis.goal_completion_rate:
                on_track = sum(1 for rate in analysis.goal_completion_rate.values() if 90 <= rate <= 110)
                total_goals = len(analysis.goal_completion_rate)
                if on_track >= total_goals * 0.8:
                    response += "  • You're doing great! Most of your nutrition goals are on track.\n"
                elif on_track >= total_goals * 0.5:
                    response += "  • Good progress! Focus on the areas that need improvement.\n"
                else:
                    response += "  • There's room for improvement. Consider adjusting your nutrition plan.\n"
            else:
                response += "  • Set specific nutrition goals to track your progress more effectively.\n"
        
        return response

# ---------------------------- Nutrition Logging Tool ----------------------------
class NutritionLoggingTool(BaseTool):
    """Tool for logging daily nutrition intake"""
    name: str = "nutrition_logging"
    description: str = "Log daily nutrition intake including calories, macronutrients, and water consumption."
    parameters: dict = {
        "type": "object",
        "properties": {
            "user_input": {
                "type": "string",
                "description": "Natural language description of food consumed and nutrition intake"
            },
            "date": {
                "type": "string",
                "description": "Date for the nutrition log (YYYY-MM-DD format), defaults to today"
            }
        },
        "required": ["user_input"]
    }

    async def execute(self, user_input: str, date: str = None) -> str:
        """
        Parse nutrition intake from natural language and create a log entry
        """
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Parse nutrition information from user input
            nutrition_data = self._parse_nutrition_input(user_input)
            
            # Create nutrition log
            nutrition_log = {
                "date": date,
                **nutrition_data
            }
            
            # Format response
            response = f"📝 **Nutrition Log Created for {date}**\n\n"
            response += f"🍽️ **Intake Summary:**\n"
            response += f"  • Calories: {nutrition_data['calories_consumed']} kcal\n"
            response += f"  • Protein: {nutrition_data['protein']}g\n"
            response += f"  • Carbohydrates: {nutrition_data['carbs']}g\n"
            response += f"  • Fats: {nutrition_data['fats']}g\n"
            response += f"  • Water: {nutrition_data['water_consumed']}ml\n\n"
            response += f"💾 **Log Data:**\n```json\n{json.dumps(nutrition_log, indent=2)}\n```"
            
            return response
            
        except Exception as e:
            return f"❌ Error logging nutrition data: {str(e)}"

    def _parse_nutrition_input(self, text: str) -> Dict[str, float]:
        """Parse nutrition information from natural language input"""
        import re
        
        # Initialize with default values
        nutrition = {
            "protein": 0.0,
            "carbs": 0.0,
            "fats": 0.0,
            "calories_consumed": 0.0,
            "water_consumed": 0.0
        }
        
        text = text.lower()
        
        # Parse calories
        calories_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:calories|kcal|cal)',
        ]
        for pattern in calories_patterns:
            match = re.search(pattern, text)
            if match:
                nutrition["calories_consumed"] = float(match.group(1))
                break
        
        # Parse protein
        protein_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:g|grams?)\s*(?:of\s*)?protein',
            r'protein[:\s]*(\d+(?:\.\d+)?)\s*(?:g|grams?)?',
        ]
        for pattern in protein_patterns:
            match = re.search(pattern, text)
            if match:
                nutrition["protein"] = float(match.group(1))
                break
        
        # Parse carbs
        carbs_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:g|grams?)\s*(?:of\s*)?(?:carbs|carbohydrates?)',
            r'(?:carbs|carbohydrates?)[:\s]*(\d+(?:\.\d+)?)\s*(?:g|grams?)?',
        ]
        for pattern in carbs_patterns:
            match = re.search(pattern, text)
            if match:
                nutrition["carbs"] = float(match.group(1))
                break
        
        # Parse fats
        fats_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:g|grams?)\s*(?:of\s*)?fats?',
            r'fats?[:\s]*(\d+(?:\.\d+)?)\s*(?:g|grams?)?',
        ]
        for pattern in fats_patterns:
            match = re.search(pattern, text)
            if match:
                nutrition["fats"] = float(match.group(1))
                break
        
        # Parse water
        water_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:ml|milliliters?)\s*(?:of\s*)?water',
            r'(\d+(?:\.\d+)?)\s*(?:l|liters?)\s*(?:of\s*)?water',
            r'water[:\s]*(\d+(?:\.\d+)?)\s*(?:ml|milliliters?|l|liters?)?',
        ]
        for pattern in water_patterns:
            match = re.search(pattern, text)
            if match:
                water = float(match.group(1))
                if 'l' in pattern and 'ml' not in pattern:
                    water *= 1000  # Convert liters to milliliters
                nutrition["water_consumed"] = water
                break
        
        # If no explicit values found, try to estimate from food descriptions
        if all(v == 0.0 for v in nutrition.values()):
            nutrition = self._estimate_from_food_description(text)
        
        return nutrition

    def _estimate_from_food_description(self, text: str) -> Dict[str, float]:
        """Provide rough estimates based on common food descriptions"""
        
        # Simple food database for estimation
        food_estimates = {
            "chicken breast": {"protein": 25, "carbs": 0, "fats": 3, "calories": 130},
            "rice": {"protein": 3, "carbs": 45, "fats": 0, "calories": 200},
            "banana": {"protein": 1, "carbs": 27, "fats": 0, "calories": 105},
            "apple": {"protein": 0, "carbs": 25, "fats": 0, "calories": 95},
            "eggs": {"protein": 12, "carbs": 1, "fats": 10, "calories": 140},
            "bread": {"protein": 8, "carbs": 45, "fats": 2, "calories": 220},
            "milk": {"protein": 8, "carbs": 12, "fats": 8, "calories": 150},
        }
        
        nutrition = {"protein": 0.0, "carbs": 0.0, "fats": 0.0, "calories_consumed": 0.0, "water_consumed": 1000.0}
        
        # Check for common foods in the text
        for food, values in food_estimates.items():
            if food in text:
                for nutrient, value in values.items():
                    if nutrient != "calories":
                        nutrition[nutrient] = float(value)
                    else:
                        nutrition["calories_consumed"] = float(value)
                break
        
        return nutrition

# ---------------------------- Agent Definition ----------------------------
class NutritionAgent(ToolCallAgent):
    """
    A nutrition specialist agent that can analyze nutrition logs, provide personalized feedback,
    and help users log their daily nutrition intake.
    """

    name: str = "nutrition_agent"
    description: str = (
        "A nutrition specialist that can:\n"
        "1. Analyze nutrition logs against personal goals\n"
        "2. Provide personalized nutrition feedback and recommendations\n"
        "3. Log daily nutrition intake from natural language descriptions\n"
        "4. Track macronutrient distribution and hydration levels\n"
        "5. Generate detailed nutrition reports with actionable insights"
    )

    system_prompt: str = """
    You are a professional nutrition specialist and dietary advisor. Your expertise includes:
    
    - Analyzing nutrition logs and comparing them against personal goals
    - Providing evidence-based nutrition recommendations
    - Helping users understand macronutrient balance and caloric needs
    - Tracking hydration and micronutrient intake
    - Creating personalized nutrition plans and feedback
    
    You can help users with:
    - Logging their daily food intake and nutrition data
    - Analyzing their nutrition patterns and goal progress
    - Providing specific recommendations for improvement
    - Understanding macronutrient distribution
    - Optimizing nutrition for fitness and health goals
    
    Always provide evidence-based advice and encourage healthy, sustainable nutrition practices.
    Be supportive and motivating while helping users achieve their nutrition goals.
    """

    next_step_prompt: str = (
        "Based on the nutrition analysis or logging result, provide additional guidance, "
        "ask follow-up questions about their nutrition goals, or offer to help with "
        "further nutrition planning and optimization."
    )

    max_steps: int = 3

    avaliable_tools: ToolManager = Field(default_factory=lambda: ToolManager([
        NutritionAnalysisTool(),
        NutritionLoggingTool(),
    ]))


async def main():
    # Create a NutritionAgent instance
    nutrition_agent = NutritionAgent(llm=ChatBot(llm_provider="openai", model_name="gpt-4o-mini"))
    print("=== Nutrition Specialist Assistant ===")
    print("I can help you analyze your nutrition, log your daily intake, and provide personalized recommendations!\n")

    # Reset the Agent state
    nutrition_agent.clear()

    # Example 1: Log nutrition intake
    print("--- Example 1: Logging Nutrition ---")
    log_input = "Today I had 2000 calories, 150g protein, 250g carbs, 70g fats, and drank 2.5 liters of water"
    print(f"Input: {log_input}\n")
    response1 = await nutrition_agent.run(f"Please log this nutrition data: {log_input}")
    print(f"Response: {response1}\n")

    # Example 2: Analyze nutrition (would need actual logs in real usage)
    print("--- Example 2: Nutrition Analysis ---")
    # Sample nutrition logs for demonstration
    sample_logs = [
        {"date": "2024-07-20", "protein": 130, "carbs": 220, "fats": 65, "calories_consumed": 2000, "water_consumed": 2500},
        {"date": "2024-07-21", "protein": 145, "carbs": 260, "fats": 75, "calories_consumed": 2300, "water_consumed": 2800},
        {"date": "2024-07-22", "protein": 140, "carbs": 240, "fats": 70, "calories_consumed": 2150, "water_consumed": 2600}
    ]
    
    # Sample nutrition goal
    sample_goal = {
        "protein": 150,
        "carbs": 250,
        "fats": 70,
        "calories_consumed": 2200,
        "water_consumed": 3000
    }

    analysis_input = "How am I doing with my nutrition goals? Any recommendations?"
    print(f"Input: {analysis_input}")
    print("Note: In real usage, this would use actual stored nutrition logs and goals\n")

if __name__ == "__main__":
    asyncio.run(main())
