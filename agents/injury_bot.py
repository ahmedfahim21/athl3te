from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.tools.base import BaseTool
from spoon_ai.chat import ChatBot
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import asyncio
import re
from dotenv import load_dotenv
import json
import asyncio

load_dotenv(override=True)

# ---------------------------- Health Profile Models ----------------------------
class UserHealthProfile(BaseModel):
    injuries: List[str] = Field(default_factory=list, description="List of current or past injuries")
    personal_info: str = Field(default="", description="Personal information including age, fitness level, medical conditions")
    age: Optional[int] = Field(default=None, description="User's age")
    fitness_level: Optional[str] = Field(default=None, description="Beginner, Intermediate, Advanced")
    activities: List[str] = Field(default_factory=list, description="Primary physical activities")
    medical_conditions: List[str] = Field(default_factory=list, description="Relevant medical conditions")

class InjuryRecord(BaseModel):
    injury_name: str = Field(description="Name/type of injury")
    date_occurred: Optional[str] = Field(default=None, description="When the injury occurred")
    severity: Optional[str] = Field(default=None, description="Mild, Moderate, Severe")
    status: Optional[str] = Field(default=None, description="Current, Recovering, Healed")
    affected_area: Optional[str] = Field(default=None, description="Body part affected")
    cause: Optional[str] = Field(default=None, description="How the injury occurred")

# ---------------------------- Injury Prevention Tool ----------------------------
class InjuryPreventionTool(BaseTool):
    """Tool for providing personalized injury prevention advice"""
    name: str = "injury_prevention"
    description: str = "Provide personalized injury prevention advice based on user's health profile and activity history."
    parameters: dict = {
        "type": "object",
        "properties": {
            "user_profile": {
                "type": "object",
                "description": "User's health profile including injuries, personal info, and activities"
            },
            "question": {
                "type": "string",
                "description": "Specific question about injury prevention"
            },
            "activity": {
                "type": "string",
                "description": "Specific activity or sport for prevention advice",
                "default": "general"
            }
        },
        "required": ["user_profile", "question"]
    }

    async def execute(self, user_profile: Dict[str, Any], question: str, activity: str = "general") -> str:
        """
        Provide personalized injury prevention advice
        """
        try:
            # Analyze user profile for risk factors
            risk_analysis = self._analyze_injury_risks(user_profile)
            
            # Generate prevention strategies
            prevention_advice = self._generate_prevention_advice(user_profile, question, activity, risk_analysis)
            
            return prevention_advice
            
        except Exception as e:
            return f"❌ Error generating prevention advice: {str(e)}"

    def _analyze_injury_risks(self, profile: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analyze user profile to identify injury risk factors"""
        risks = {
            "high_risk_areas": [],
            "risk_factors": [],
            "protective_factors": []
        }
        
        injuries = profile.get("injuries", [])
        personal_info = profile.get("personal_info", "").lower()
        activities = profile.get("activities", [])
        
        # Analyze injury history for patterns
        for injury in injuries:
            injury_lower = injury.lower()
            if any(knee_term in injury_lower for knee_term in ["knee", "acl", "mcl", "meniscus"]):
                risks["high_risk_areas"].append("knee")
            elif any(ankle_term in injury_lower for ankle_term in ["ankle", "sprain"]):
                risks["high_risk_areas"].append("ankle")
            elif any(back_term in injury_lower for back_term in ["back", "spine", "disc"]):
                risks["high_risk_areas"].append("lower back")
            elif any(shoulder_term in injury_lower for shoulder_term in ["shoulder", "rotator"]):
                risks["high_risk_areas"].append("shoulder")
        
        # Analyze personal info for risk factors
        if any(term in personal_info for term in ["desk job", "sedentary", "sitting"]):
            risks["risk_factors"].append("prolonged sitting")
        if any(term in personal_info for term in ["flat feet", "overpronation"]):
            risks["risk_factors"].append("foot mechanics issues")
        if any(term in personal_info for term in ["overweight", "obesity"]):
            risks["risk_factors"].append("excess weight")
        
        # Analyze activities for specific risks
        high_impact_activities = ["running", "basketball", "soccer", "tennis", "volleyball"]
        if any(activity.lower() in [act.lower() for act in activities] for activity in high_impact_activities):
            risks["risk_factors"].append("high-impact activities")
        
        return risks

    def _generate_prevention_advice(self, profile: Dict[str, Any], question: str, activity: str, risks: Dict[str, List[str]]) -> str:
        """Generate comprehensive prevention advice"""
        
        response = "🛡️ **Injury Prevention Guide**\n\n"
        
        # Personal risk assessment
        if risks["high_risk_areas"]:
            response += f"⚠️ **Your High-Risk Areas:** {', '.join(set(risks['high_risk_areas']))}\n\n"
        
        # Specific prevention strategies based on injury history
        injuries = profile.get("injuries", [])
        if injuries:
            response += "🎯 **Targeted Prevention (Based on Your History):**\n"
            for injury in injuries[:3]:  # Limit to top 3 injuries
                prevention_tip = self._get_injury_specific_prevention(injury)
                response += f"  • **{injury}**: {prevention_tip}\n"
            response += "\n"
        
        # Activity-specific advice
        if activity and activity != "general":
            activity_advice = self._get_activity_specific_prevention(activity, risks)
            if activity_advice:
                response += f"🏃 **{activity.title()} Prevention Tips:**\n{activity_advice}\n\n"
        
        # General prevention strategies
        response += "💪 **General Prevention Strategies:**\n"
        
        # Warm-up and cool-down
        response += "  • **Warm-up (5-10 min)**: Dynamic stretching, light cardio to prepare muscles\n"
        response += "  • **Cool-down (5-10 min)**: Static stretching, gradual activity reduction\n"
        
        # Strength and conditioning
        if "knee" in risks["high_risk_areas"]:
            response += "  • **Knee Protection**: Strengthen quadriceps, hamstrings, and glutes\n"
        if "ankle" in risks["high_risk_areas"]:
            response += "  • **Ankle Stability**: Balance exercises, calf strengthening\n"
        if "lower back" in risks["high_risk_areas"]:
            response += "  • **Core Strength**: Planks, bird dogs, dead bugs for spinal stability\n"
        
        # General recommendations
        response += "  • **Progressive Loading**: Gradually increase intensity, duration, and frequency\n"
        response += "  • **Recovery**: Ensure adequate sleep (7-9 hours) and rest days\n"
        response += "  • **Hydration**: Maintain proper fluid intake before, during, and after activity\n"
        response += "  • **Proper Equipment**: Use appropriate, well-fitted gear and footwear\n\n"
        
        # Specific recommendations based on risk factors
        if "prolonged sitting" in risks["risk_factors"]:
            response += "🪑 **Desk Worker Tips:**\n"
            response += "  • Hip flexor stretches and glute activation exercises\n"
            response += "  • Regular movement breaks every 30-60 minutes\n\n"
        
        # Red flags
        response += "🚨 **When to Stop and Seek Help:**\n"
        response += "  • Sharp, sudden pain\n"
        response += "  • Pain that persists or worsens\n"
        response += "  • Swelling, numbness, or loss of function\n"
        response += "  • Any concerning symptoms\n\n"
        
        response += "💡 **Remember**: Prevention is always better than treatment. Listen to your body!"
        
        return response

    def _get_injury_specific_prevention(self, injury: str) -> str:
        """Get specific prevention advice for common injuries"""
        injury_lower = injury.lower()
        
        if "knee" in injury_lower or "acl" in injury_lower:
            return "Focus on leg strength, proper landing mechanics, and balance training"
        elif "ankle" in injury_lower or "sprain" in injury_lower:
            return "Improve proprioception with balance exercises and strengthen peroneals"
        elif "back" in injury_lower or "spine" in injury_lower:
            return "Strengthen core muscles and improve hip flexibility"
        elif "shoulder" in injury_lower or "rotator" in injury_lower:
            return "Strengthen rotator cuff and improve shoulder blade stability"
        elif "hamstring" in injury_lower:
            return "Maintain hamstring flexibility and strengthen glutes"
        elif "shin" in injury_lower or "splint" in injury_lower:
            return "Gradual mileage increase and proper footwear selection"
        else:
            return "Maintain proper form, adequate warm-up, and progressive training"

    def _get_activity_specific_prevention(self, activity: str, risks: Dict[str, List[str]]) -> str:
        """Get prevention advice specific to activities"""
        activity_lower = activity.lower()
        
        if "running" in activity_lower:
            return ("  • Follow 10% rule for weekly mileage increases\n"
                   "  • Replace shoes every 300-500 miles\n"
                   "  • Incorporate cross-training and strength work\n"
                   "  • Pay attention to running surface variety")
        elif "cycling" in activity_lower:
            return ("  • Ensure proper bike fit and positioning\n"
                   "  • Gradually increase distance and intensity\n"
                   "  • Strengthen core and glutes for stability\n"
                   "  • Use appropriate gear ratios")
        elif "swimming" in activity_lower:
            return ("  • Focus on proper stroke technique\n"
                   "  • Strengthen shoulder stabilizers\n"
                   "  • Gradually increase yardage\n"
                   "  • Include dryland training")
        elif "weight" in activity_lower or "lifting" in activity_lower:
            return ("  • Prioritize proper form over heavy weight\n"
                   "  • Use spotters for heavy lifts\n"
                   "  • Allow adequate recovery between sessions\n"
                   "  • Progress gradually with weight increases")
        else:
            return None

# ---------------------------- Injury Recovery Tool ----------------------------
class InjuryRecoveryTool(BaseTool):
    """Tool for providing personalized injury recovery advice"""
    name: str = "injury_recovery"
    description: str = "Provide personalized injury recovery advice and rehabilitation guidance."
    parameters: dict = {
        "type": "object",
        "properties": {
            "user_profile": {
                "type": "object",
                "description": "User's health profile including current injuries and personal info"
            },
            "injury_details": {
                "type": "object",
                "description": "Specific details about the injury requiring recovery advice"
            },
            "question": {
                "type": "string",
                "description": "Specific question about injury recovery"
            }
        },
        "required": ["user_profile", "question"]
    }

    async def execute(self, user_profile: Dict[str, Any], question: str, injury_details: Dict[str, Any] = None) -> str:
        """
        Provide personalized injury recovery advice
        """
        try:
            # Generate recovery plan
            recovery_advice = self._generate_recovery_advice(user_profile, question, injury_details)
            
            return recovery_advice
            
        except Exception as e:
            return f"❌ Error generating recovery advice: {str(e)}"

    def _generate_recovery_advice(self, profile: Dict[str, Any], question: str, injury_details: Dict[str, Any] = None) -> str:
        """Generate comprehensive recovery advice"""
        
        response = "🏥 **Injury Recovery Guide**\n\n"
        
        current_injuries = profile.get("injuries", [])
        
        if current_injuries:
            response += f"🩹 **Current Injuries:** {', '.join(current_injuries)}\n\n"
        
        # Recovery phases
        response += "📈 **Recovery Phases:**\n\n"
        
        response += "**Phase 1: Acute (0-72 hours)**\n"
        response += "  • **RICE Protocol**: Rest, Ice, Compression, Elevation\n"
        response += "  • **Pain Management**: Over-the-counter pain relievers if needed\n"
        response += "  • **Avoid**: Heat, alcohol, running, massage initially\n\n"
        
        response += "**Phase 2: Early Recovery (3-7 days)**\n"
        response += "  • **Gentle Movement**: Pain-free range of motion\n"
        response += "  • **Gradual Activity**: Light activities as tolerated\n"
        response += "  • **Monitor**: Swelling, pain levels, function\n\n"
        
        response += "**Phase 3: Progressive Recovery (1-6 weeks)**\n"
        response += "  • **Strengthening**: Gradual resistance exercises\n"
        response += "  • **Flexibility**: Gentle stretching within comfort\n"
        response += "  • **Functional Training**: Sport-specific movements\n\n"
        
        # Injury-specific recovery advice
        if current_injuries:
            response += "🎯 **Injury-Specific Recovery:**\n"
            for injury in current_injuries[:2]:  # Limit to top 2 injuries
                specific_advice = self._get_injury_specific_recovery(injury)
                response += f"  • **{injury}**: {specific_advice}\n"
            response += "\n"
        
        # General recovery principles
        response += "💡 **Recovery Principles:**\n"
        response += "  • **Listen to Your Body**: Pain is a signal to modify activity\n"
        response += "  • **Gradual Progression**: Slowly increase activity intensity\n"
        response += "  • **Quality Sleep**: 7-9 hours for optimal healing\n"
        response += "  • **Nutrition**: Adequate protein and anti-inflammatory foods\n"
        response += "  • **Hydration**: Support healing with proper fluid intake\n"
        response += "  • **Stress Management**: Chronic stress can slow healing\n\n"
        
        # Return to activity guidelines
        response += "🔄 **Return to Activity Guidelines:**\n"
        response += "  • **Pain-Free**: No pain during or after activity\n"
        response += "  • **Full Range of Motion**: Normal movement patterns\n"
        response += "  • **Strength**: 90% of uninjured side strength\n"
        response += "  • **Confidence**: Mental readiness to return\n\n"
        
        # When to seek professional help
        response += "🚨 **Seek Professional Help If:**\n"
        response += "  • Pain worsens or doesn't improve after 72 hours\n"
        response += "  • Significant swelling or deformity\n"
        response += "  • Inability to bear weight or use the injured area\n"
        response += "  • Numbness, tingling, or loss of sensation\n"
        response += "  • Signs of infection (fever, warmth, redness)\n\n"
        
        # Recovery timeline expectations
        response += "⏰ **Typical Recovery Timelines:**\n"
        response += "  • **Muscle Strain**: 2-6 weeks\n"
        response += "  • **Ligament Sprain**: 2-8 weeks\n"
        response += "  • **Bone Stress**: 6-12 weeks\n"
        response += "  • **Tendon Issues**: 6-12 weeks\n\n"
        
        response += "💪 **Remember**: Patience and consistency are key to successful recovery!"
        
        return response

    def _get_injury_specific_recovery(self, injury: str) -> str:
        """Get specific recovery advice for common injuries"""
        injury_lower = injury.lower()
        
        if "ankle" in injury_lower and "sprain" in injury_lower:
            return "RICE initially, then progressive weight-bearing and balance exercises"
        elif "knee" in injury_lower:
            return "Protect from further stress, strengthen surrounding muscles, gradual loading"
        elif "back" in injury_lower:
            return "Maintain gentle movement, core strengthening, avoid bed rest"
        elif "shoulder" in injury_lower:
            return "Maintain pain-free range of motion, progressive strengthening"
        elif "hamstring" in injury_lower:
            return "Gentle stretching, eccentric strengthening, gradual return to sprinting"
        elif "shin" in injury_lower:
            return "Rest from impact activities, address biomechanical factors"
        else:
            return "Follow RICE protocol initially, then progressive rehabilitation"

# ---------------------------- Agent Definition ----------------------------
class InjuryAgent(ToolCallAgent):
    """
    An injury prevention and recovery specialist that provides personalized advice
    based on user's health profile, injury history, and current activities.
    """

    name: str = "injury_agent"
    description: str = (
        "An injury prevention and recovery specialist that can:\n"
        "1. Analyze injury risk factors based on personal health profile\n"
        "2. Provide personalized injury prevention strategies\n"
        "3. Offer comprehensive injury recovery guidance\n"
        "4. Give activity-specific injury prevention advice\n"
        "5. Help create safe return-to-activity plans\n"
        "6. Identify when professional medical help is needed"
    )

    system_prompt: str = """
    You are a certified injury prevention and rehabilitation specialist with expertise in:
    
    - Sports medicine and injury prevention strategies
    - Rehabilitation protocols and recovery timelines
    - Risk factor assessment and movement analysis
    - Activity-specific injury prevention
    - Safe return-to-play guidelines
    
    Your approach is:
    - Evidence-based and conservative in recommendations
    - Focused on long-term health and injury prevention
    - Personalized to individual risk factors and goals
    - Clear about when professional medical care is needed
    - Supportive and encouraging during recovery
    
    You can help users with:
    - Identifying injury risk factors
    - Creating prevention strategies
    - Developing recovery plans
    - Understanding rehabilitation phases
    - Making safe activity modifications
    - Knowing when to seek professional help
    
    Always prioritize safety and recommend professional medical evaluation
    for significant injuries or concerning symptoms.
    """

    next_step_prompt: str = (
        "Based on the injury advice provided, offer additional guidance such as "
        "specific exercises, timeline expectations, or suggest follow-up questions "
        "about prevention or recovery strategies."
    )

    max_steps: int = 3

    avaliable_tools: ToolManager = Field(default_factory=lambda: ToolManager([
        InjuryPreventionTool(),
        InjuryRecoveryTool(),
    ]))


async def main():
    # Create an InjuryAgent instance
    injury_agent = InjuryAgent(llm=ChatBot(llm_provider="openai", model_name="gpt-4o-mini"))
    print("=== Injury Prevention & Recovery Specialist ===")
    print("I can help you prevent injuries and recover safely from existing ones!\n")

    # Reset the Agent state
    injury_agent.clear()

    # Example 1: Prevention advice
    print("--- Example 1: Injury Prevention ---")
    sample_profile = {
        "injuries": ["sprained ankle", "runner's knee"],
        "personal_info": "32-year-old recreational runner, runs 20km per week, has flat feet, works desk job",
        "activities": ["running", "cycling"],
        "age": 32,
        "fitness_level": "intermediate"
    }
    
    prevention_input = "How can I prevent further knee injuries while continuing to run?"
    print(f"Input: {prevention_input}\n")
    response1 = await injury_agent.run(f"I need injury prevention advice. My question: {prevention_input}")
    print(f"Response: {response1}\n")

    # Example 2: Recovery advice
    print("--- Example 2: Injury Recovery ---")
    recovery_input = "What should I do to recover from my sprained ankle?"
    print(f"Input: {recovery_input}\n")
    response2 = await injury_agent.run(f"I need recovery advice. My question: {recovery_input}")
    print(f"Response: {response2}\n")

if __name__ == "__main__":
    asyncio.run(main())
