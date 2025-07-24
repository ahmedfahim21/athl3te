from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.tools.base import BaseTool
from spoon_ai.chat import ChatBot
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, ClassVar
from datetime import datetime, date
import json
import asyncio
import re
import random
from dotenv import load_dotenv
import json
import random
import asyncio

load_dotenv(override=True)

# ---------------------------- Community Models ----------------------------
class CommunityMember(BaseModel):
    name: str = Field(description="Member's name")
    user_id: Optional[str] = Field(default=None, description="Unique user identifier")
    achievements: List[str] = Field(default_factory=list, description="List of achievements")
    activity_stats: Dict[str, Any] = Field(default_factory=dict, description="Activity statistics")
    join_date: str = Field(description="Date when member joined (YYYY-MM-DD format)")
    current_streak: Optional[int] = Field(default=0, description="Current activity streak in days")
    total_workouts: Optional[int] = Field(default=0, description="Total completed workouts")
    personal_records: Dict[str, Any] = Field(default_factory=dict, description="Personal best records")

class Community(BaseModel):
    name: str = Field(description="Community name")
    activity_type: str = Field(description="Primary activity type (running, cycling, swimming, etc.)")
    description: Optional[str] = Field(default="", description="Community description")
    common_injuries: List[str] = Field(default_factory=list, description="Common injuries in this activity")
    member_count: int = Field(description="Total number of members")
    top_performers: List[CommunityMember] = Field(default_factory=list, description="Top performing members")
    community_goals: List[str] = Field(default_factory=list, description="Shared community goals")
    recent_achievements: List[str] = Field(default_factory=list, description="Recent community achievements")

class Challenge(BaseModel):
    name: str = Field(description="Challenge name")
    description: str = Field(description="Challenge description")
    start_date: str = Field(description="Start date (YYYY-MM-DD)")
    end_date: str = Field(description="End date (YYYY-MM-DD)")
    activity_type: str = Field(description="Type of activity for the challenge")
    target_metric: str = Field(description="What metric to track (distance, time, frequency)")
    target_value: float = Field(description="Target value to achieve")
    participants: List[str] = Field(default_factory=list, description="List of participant names")
    rewards: List[str] = Field(default_factory=list, description="Challenge rewards")

# ---------------------------- Community Insights Tool ----------------------------
class CommunityInsightsTool(BaseTool):
    """Tool for generating community insights and highlights"""
    name: str = "community_insights"
    description: str = "Generate community insights, highlight top performers, and provide community health advice."
    parameters: dict = {
        "type": "object",
        "properties": {
            "community": {
                "type": "object",
                "description": "Community information including members, activity type, and statistics"
            },
            "insight_type": {
                "type": "string",
                "description": "Type of insight to generate: 'performers', 'injury_advice', 'achievements', 'trends'",
                "enum": ["performers", "injury_advice", "achievements", "trends"]
            },
            "time_period": {
                "type": "string",
                "description": "Time period for analysis: 'week', 'month', 'year'",
                "default": "week"
            }
        },
        "required": ["community", "insight_type"]
    }

    async def execute(self, community: Dict[str, Any], insight_type: str, time_period: str = "week") -> str:
        """
        Generate community insights based on the requested type
        """
        try:
            if insight_type == "performers":
                return self._highlight_top_performers(community, time_period)
            elif insight_type == "injury_advice":
                return self._generate_injury_advice(community)
            elif insight_type == "achievements":
                return self._highlight_achievements(community, time_period)
            elif insight_type == "trends":
                return self._analyze_trends(community, time_period)
            else:
                return f"❌ Unknown insight type: {insight_type}"
                
        except Exception as e:
            return f"❌ Error generating community insights: {str(e)}"

    def _highlight_top_performers(self, community: Dict[str, Any], time_period: str) -> str:
        """Highlight top performing community members"""
        
        response = f"🏆 **Top Performers in {community['name']} ({time_period.title()})**\n\n"
        
        top_performers = community.get("top_performers", [])
        
        if not top_performers:
            response += "📊 No performance data available yet. Keep logging your activities to see top performers!\n\n"
            response += "💪 **How to become a top performer:**\n"
            response += "  • Log your workouts consistently\n"
            response += "  • Set and achieve personal goals\n"
            response += "  • Participate in community challenges\n"
            response += "  • Support other members\n"
            return response
        
        # Rank performers
        for i, performer in enumerate(top_performers[:5], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            response += f"{medal} **{performer['name']}**\n"
            
            # Activity stats
            if performer.get('activity_stats'):
                stats = performer['activity_stats']
                for stat_name, stat_value in stats.items():
                    response += f"    • {stat_name.replace('_', ' ').title()}: {stat_value}\n"
            
            # Recent achievements
            if performer.get('achievements'):
                recent_achievements = performer['achievements'][:2]
                for achievement in recent_achievements:
                    response += f"    🎯 {achievement}\n"
            
            # Streak and workout count
            if performer.get('current_streak'):
                response += f"    🔥 Streak: {performer['current_streak']} days\n"
            if performer.get('total_workouts'):
                response += f"    💪 Total Workouts: {performer['total_workouts']}\n"
            
            response += "\n"
        
        # Community motivation
        response += "🌟 **Join the leaderboard!** Share your workouts and achievements to be featured next time!\n\n"
        response += f"👥 **Community Stats:** {community.get('member_count', 0)} active members in {community['activity_type']}"
        
        return response

    def _generate_injury_advice(self, community: Dict[str, Any]) -> str:
        """Generate injury prevention advice for the community"""
        
        activity_type = community.get("activity_type", "general fitness")
        common_injuries = community.get("common_injuries", [])
        
        response = f"🏥 **Injury Prevention Guide for {community['name']}**\n\n"
        response += f"📋 **Activity Focus:** {activity_type.title()}\n\n"
        
        if common_injuries:
            response += f"⚠️ **Common Injuries in Our Community:**\n"
            for injury in common_injuries:
                prevention_tip = self._get_activity_injury_prevention(activity_type, injury)
                response += f"  • **{injury.title()}**: {prevention_tip}\n"
            response += "\n"
        
        # Activity-specific general advice
        general_advice = self._get_activity_general_advice(activity_type)
        response += f"💡 **{activity_type.title()} Safety Tips:**\n"
        for tip in general_advice:
            response += f"  • {tip}\n"
        response += "\n"
        
        # Community safety reminders
        response += "🛡️ **Community Safety Reminders:**\n"
        response += "  • Always warm up before intense activity\n"
        response += "  • Listen to your body and rest when needed\n"
        response += "  • Gradually increase intensity and duration\n"
        response += "  • Stay hydrated and maintain proper nutrition\n"
        response += "  • Share concerns with the community for support\n\n"
        
        response += "🚨 **Seek medical attention if you experience persistent pain or concerning symptoms**"
        
        return response

    def _highlight_achievements(self, community: Dict[str, Any], time_period: str) -> str:
        """Highlight recent community achievements"""
        
        response = f"🎉 **Community Achievements - {community['name']} ({time_period.title()})**\n\n"
        
        recent_achievements = community.get("recent_achievements", [])
        
        if recent_achievements:
            response += "🏅 **Recent Milestones:**\n"
            for achievement in recent_achievements:
                response += f"  ✨ {achievement}\n"
            response += "\n"
        
        # Member achievements
        top_performers = community.get("top_performers", [])
        if top_performers:
            response += "🌟 **Member Highlights:**\n"
            for performer in top_performers[:3]:
                if performer.get('achievements'):
                    recent = performer['achievements'][0] if performer['achievements'] else None
                    if recent:
                        response += f"  🎯 **{performer['name']}**: {recent}\n"
            response += "\n"
        
        # Community goals progress
        community_goals = community.get("community_goals", [])
        if community_goals:
            response += "🎯 **Community Goals Progress:**\n"
            for goal in community_goals:
                # In a real implementation, you'd track actual progress
                progress = random.randint(60, 90)  # Simulated progress
                progress_bar = "█" * (progress // 10) + "░" * (10 - progress // 10)
                response += f"  • {goal}: [{progress_bar}] {progress}%\n"
            response += "\n"
        
        # Encouragement
        response += "💪 **Keep it up!** Every workout counts towards our community goals!\n"
        response += f"👥 Join {community.get('member_count', 0)} members making progress in {community['activity_type']}!"
        
        return response

    def _analyze_trends(self, community: Dict[str, Any], time_period: str) -> str:
        """Analyze community activity trends"""
        
        response = f"📈 **Community Trends - {community['name']} ({time_period.title()})**\n\n"
        
        # Simulated trend data (in real implementation, this would come from actual data)
        trends = {
            "activity_increase": random.randint(5, 25),
            "new_members": random.randint(10, 50),
            "average_workouts": random.randint(3, 7),
            "completion_rate": random.randint(70, 95)
        }
        
        response += "📊 **Activity Overview:**\n"
        response += f"  📈 Activity increase: +{trends['activity_increase']}% vs last {time_period}\n"
        response += f"  👋 New members: {trends['new_members']}\n"
        response += f"  💪 Average workouts per member: {trends['average_workouts']}\n"
        response += f"  ✅ Goal completion rate: {trends['completion_rate']}%\n\n"
        
        # Popular activities
        activity_type = community.get("activity_type", "fitness")
        response += "🔥 **Trending Activities:**\n"
        if activity_type == "running":
            response += "  • 5K training programs\n  • Trail running adventures\n  • Speed work sessions\n"
        elif activity_type == "cycling":
            response += "  • Hill climb challenges\n  • Group rides\n  • Time trial training\n"
        elif activity_type == "swimming":
            response += "  • Technique workshops\n  • Distance challenges\n  • Open water preparation\n"
        else:
            response += "  • HIIT workouts\n  • Strength training\n  • Flexibility sessions\n"
        
        response += "\n"
        
        # Community engagement
        response += "🤝 **Community Engagement:**\n"
        response += "  • Members are actively sharing achievements\n"
        response += "  • High participation in challenges\n"
        response += "  • Growing support network\n\n"
        
        response += "🎯 **What's driving success:**\n"
        response += "  • Consistent goal setting and tracking\n"
        response += "  • Peer motivation and support\n"
        response += "  • Regular community challenges\n"
        response += "  • Celebrating small wins together\n"
        
        return response

    def _get_activity_injury_prevention(self, activity_type: str, injury: str) -> str:
        """Get prevention advice for specific activity-injury combinations"""
        
        injury_lower = injury.lower()
        activity_lower = activity_type.lower()
        
        prevention_tips = {
            "running": {
                "runner's knee": "Strengthen glutes and quads, avoid sudden mileage increases",
                "shin splints": "Gradual training progression, proper footwear, soft surfaces",
                "plantar fasciitis": "Calf stretches, proper arch support, gradual activity increase",
                "it band syndrome": "Hip strengthening, foam rolling, proper running form"
            },
            "cycling": {
                "knee pain": "Proper bike fit, cadence training, leg strength exercises",
                "back pain": "Core strengthening, bike position adjustment, handlebar height",
                "neck strain": "Flexibility exercises, proper helmet fit, riding position"
            },
            "swimming": {
                "shoulder impingement": "Rotator cuff strengthening, stroke technique focus",
                "lower back pain": "Core stability, proper body rotation technique",
                "neck strain": "Breathing technique improvement, flexibility work"
            }
        }
        
        activity_tips = prevention_tips.get(activity_lower, {})
        return activity_tips.get(injury_lower, "Focus on proper form and gradual progression")

    def _get_activity_general_advice(self, activity_type: str) -> List[str]:
        """Get general safety advice for specific activities"""
        
        advice_map = {
            "running": [
                "Follow the 10% rule for weekly mileage increases",
                "Replace running shoes every 300-500 miles",
                "Include rest days in your training schedule",
                "Warm up with dynamic stretches"
            ],
            "cycling": [
                "Always wear a properly fitted helmet",
                "Check tire pressure and brakes before rides",
                "Use appropriate gearing for terrain",
                "Stay visible with lights and bright clothing"
            ],
            "swimming": [
                "Never swim alone, use the buddy system",
                "Learn proper breathing techniques",
                "Progress gradually with distance and intensity",
                "Focus on stroke technique over speed"
            ],
            "weightlifting": [
                "Use proper form over heavy weights",
                "Always warm up before lifting",
                "Use spotters for heavy compound movements",
                "Allow adequate recovery between sessions"
            ]
        }
        
        return advice_map.get(activity_type.lower(), [
            "Start slowly and progress gradually",
            "Listen to your body and rest when needed",
            "Maintain proper form and technique",
            "Stay consistent with your training"
        ])

# ---------------------------- Motivation Tool ----------------------------
class MotivationTool(BaseTool):
    """Tool for providing motivation and community support"""
    name: str = "motivation"
    description: str = "Provide motivational quotes, tips, and community encouragement."
    parameters: dict = {
        "type": "object",
        "properties": {
            "motivation_type": {
                "type": "string",
                "description": "Type of motivation: 'quote', 'tip', 'challenge', 'encouragement'",
                "enum": ["quote", "tip", "challenge", "encouragement"]
            },
            "activity_type": {
                "type": "string",
                "description": "Activity type for relevant motivation",
                "default": "general"
            },
            "context": {
                "type": "string",
                "description": "Context for personalized motivation",
                "default": ""
            }
        },
        "required": ["motivation_type"]
    }

    # Class attributes for quotes and tips
    motivational_quotes: ClassVar[List[str]] = [
        "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "The only bad workout is the one that didn't happen.",
        "Your body can stand almost anything. It's your mind you have to convince.",
        "Champions keep playing until they get it right.",
        "The miracle isn't that I finished. The miracle is that I had the courage to start.",
        "Strength doesn't come from what you can do. It comes from overcoming what you thought you couldn't.",
        "Every mile begins with a single step.",
        "Pain is temporary. Quitting lasts forever.",
        "The groundwork for all happiness is good health.",
        "Take care of your body. It's the only place you have to live."
    ]
    
    activity_tips: ClassVar[Dict[str, List[str]]] = {
        "running": [
            "Focus on your breathing rhythm",
            "Land on your midfoot, not your heel",
            "Keep your cadence around 170-180 steps per minute",
            "Run tall with a slight forward lean",
            "Swing your arms naturally at your sides"
        ],
        "cycling": [
            "Maintain a steady cadence of 80-100 RPM",
            "Keep your upper body relaxed",
            "Use your gears effectively for terrain",
            "Practice smooth pedal strokes",
            "Stay hydrated on longer rides"
        ],
        "swimming": [
            "Focus on long, smooth strokes",
            "Rotate your body, not just your arms",
            "Breathe rhythmically and bilaterally",
            "Keep your head in a neutral position",
            "Practice your kick for better propulsion"
        ],
        "weightlifting": [
            "Focus on form before adding weight",
            "Control the negative portion of each rep",
            "Breathe properly during lifts",
            "Progressive overload is key",
            "Don't neglect compound movements"
        ]
    }

    async def execute(self, motivation_type: str, activity_type: str = "general", context: str = "") -> str:
        """
        Provide motivation based on the requested type
        """
        try:
            if motivation_type == "quote":
                return self._get_motivational_quote(context)
            elif motivation_type == "tip":
                return self._get_activity_tip(activity_type)
            elif motivation_type == "challenge":
                return self._create_mini_challenge(activity_type)
            elif motivation_type == "encouragement":
                return self._provide_encouragement(context)
            else:
                return f"❌ Unknown motivation type: {motivation_type}"
                
        except Exception as e:
            return f"❌ Error providing motivation: {str(e)}"

    def _get_motivational_quote(self, context: str = "") -> str:
        """Get a motivational quote"""
        
        quote = random.choice(self.motivational_quotes)
        
        response = "💫 **Daily Motivation**\n\n"
        response += f"*\"{quote}\"*\n\n"
        
        if context:
            if "struggle" in context.lower() or "difficult" in context.lower():
                response += "🌟 Remember: Every challenge is an opportunity to grow stronger!\n"
            elif "goal" in context.lower():
                response += "🎯 Your goals are waiting for you - take the next step!\n"
            elif "tired" in context.lower():
                response += "💪 Rest when you need to, but don't quit when you're tired!\n"
            else:
                response += "🚀 You've got this! Every step forward counts!\n"
        else:
            response += "🏆 Make today count - your future self will thank you!\n"
        
        return response

    def _get_activity_tip(self, activity_type: str) -> str:
        """Get a specific tip for the activity"""
        
        tips = self.activity_tips.get(activity_type.lower(), [
            "Stay consistent with your training",
            "Listen to your body and rest when needed",
            "Set small, achievable goals",
            "Track your progress to stay motivated"
        ])
        
        tip = random.choice(tips)
        
        response = f"💡 **{activity_type.title()} Tip of the Day**\n\n"
        response += f"🎯 {tip}\n\n"
        response += "💪 Small improvements lead to big results!"
        
        return response

    def _create_mini_challenge(self, activity_type: str) -> str:
        """Create a mini challenge for the user"""
        
        challenges = {
            "running": [
                "Run for 20 minutes without stopping",
                "Try a new running route in your neighborhood",
                "Beat your 1-mile personal best",
                "Complete a 5K this week"
            ],
            "cycling": [
                "Cycle for 30 minutes at a steady pace",
                "Try a hill climb challenge",
                "Beat your average speed on a familiar route",
                "Explore a new cycling path"
            ],
            "swimming": [
                "Swim 500 meters without stopping",
                "Focus on technique for one full session",
                "Try a different stroke for 10 minutes",
                "Beat your 100m personal best"
            ],
            "weightlifting": [
                "Try a new exercise this week",
                "Focus on perfect form for one session",
                "Increase weight on your favorite lift",
                "Complete a full-body workout"
            ]
        }
        
        activity_challenges = challenges.get(activity_type.lower(), [
            "Exercise for 30 minutes today",
            "Try a new type of workout",
            "Beat yesterday's effort",
            "Focus on form and technique"
        ])
        
        challenge = random.choice(activity_challenges)
        
        response = "🏃 **Mini Challenge**\n\n"
        response += f"🎯 **Today's Challenge:** {challenge}\n\n"
        response += "⏰ **Why this matters:** Small daily challenges build mental toughness and create momentum!\n\n"
        response += "🏆 **Reward yourself** when you complete it - you've earned it!\n\n"
        response += "💪 Ready to take on the challenge?"
        
        return response

    def _provide_encouragement(self, context: str = "") -> str:
        """Provide personalized encouragement"""
        
        response = "🌟 **You're Doing Great!**\n\n"
        
        if "plateau" in context.lower() or "stuck" in context.lower():
            response += "📈 Plateaus are normal and temporary! Your body is adapting and getting stronger.\n\n"
            response += "💡 **Try this:**\n"
            response += "  • Mix up your routine\n"
            response += "  • Focus on different aspects (speed, endurance, strength)\n"
            response += "  • Give yourself credit for consistency\n"
        elif "motivation" in context.lower() or "lazy" in context.lower():
            response += "🔥 Some days are harder than others, and that's completely normal!\n\n"
            response += "💪 **Remember:**\n"
            response += "  • Progress isn't always linear\n"
            response += "  • Even 10 minutes of activity counts\n"
            response += "  • The hardest part is starting\n"
        elif "injury" in context.lower() or "recovery" in context.lower():
            response += "🏥 Recovery is part of the journey, not a setback!\n\n"
            response += "🌱 **Focus on:**\n"
            response += "  • What you CAN do safely\n"
            response += "  • Proper rest and rehabilitation\n"
            response += "  • Coming back stronger than before\n"
        else:
            response += "🚀 Every workout, every healthy choice, every step forward matters!\n\n"
            response += "✨ **You are:**\n"
            response += "  • Stronger than you think\n"
            response += "  • More capable than you realize\n"
            response += "  • Making progress every day\n"
        
        response += "\n🏆 Keep going - you've got this!"
        
        return response

# ---------------------------- Challenge Manager Tool ----------------------------
class ChallengeManagerTool(BaseTool):
    """Tool for creating and managing community challenges"""
    name: str = "challenge_manager"
    description: str = "Create, manage, and track community fitness challenges."
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to perform: 'create', 'join', 'progress', 'leaderboard'",
                "enum": ["create", "join", "progress", "leaderboard"]
            },
            "challenge_data": {
                "type": "object",
                "description": "Challenge information for creation or updates"
            },
            "activity_type": {
                "type": "string",
                "description": "Activity type for the challenge",
                "default": "general"
            }
        },
        "required": ["action"]
    }

    async def execute(self, action: str, challenge_data: Dict[str, Any] = None, activity_type: str = "general") -> str:
        """
        Manage community challenges
        """
        try:
            if action == "create":
                return self._create_challenge(challenge_data, activity_type)
            elif action == "join":
                return self._join_challenge(challenge_data)
            elif action == "progress":
                return self._show_progress(challenge_data)
            elif action == "leaderboard":
                return self._show_leaderboard(challenge_data)
            else:
                return f"❌ Unknown action: {action}"
                
        except Exception as e:
            return f"❌ Error managing challenge: {str(e)}"

    def _create_challenge(self, challenge_data: Dict[str, Any], activity_type: str) -> str:
        """Create a new community challenge"""
        
        # Generate challenge suggestions if no specific data provided
        if not challenge_data:
            suggestions = self._generate_challenge_suggestions(activity_type)
            return suggestions
        
        response = "🏆 **New Community Challenge Created!**\n\n"
        response += f"📋 **Challenge Name:** {challenge_data.get('name', 'Fitness Challenge')}\n"
        response += f"📝 **Description:** {challenge_data.get('description', 'Complete your fitness goals!')}\n"
        response += f"🗓️ **Duration:** {challenge_data.get('start_date', 'TBD')} to {challenge_data.get('end_date', 'TBD')}\n"
        response += f"🎯 **Goal:** {challenge_data.get('target_metric', 'activity')} - {challenge_data.get('target_value', 'TBD')}\n"
        response += f"🏃 **Activity:** {challenge_data.get('activity_type', activity_type)}\n\n"
        
        if challenge_data.get('rewards'):
            response += "🎁 **Rewards:**\n"
            for reward in challenge_data['rewards']:
                response += f"  🏅 {reward}\n"
            response += "\n"
        
        response += "🚀 **How to Join:**\n"
        response += "  1. Comment 'I'm in!' to join\n"
        response += "  2. Log your activities daily\n"
        response += "  3. Support fellow participants\n"
        response += "  4. Celebrate achievements together!\n\n"
        
        response += "💪 **Let's do this together!** Who's ready to take on the challenge?"
        
        return response

    def _generate_challenge_suggestions(self, activity_type: str) -> str:
        """Generate challenge suggestions for an activity"""
        
        challenges = {
            "running": [
                "30-Day Running Streak - Run at least 1 mile every day for 30 days",
                "5K Challenge - Complete a 5K run in under 25 minutes",
                "Weekly Distance Goal - Run 20km total distance this week",
                "Speed Challenge - Improve your 1-mile time by 30 seconds"
            ],
            "cycling": [
                "Century Challenge - Cycle 100km in one week",
                "Hill Climbing Challenge - Complete 5 hill climbs this month",
                "Daily Ride Streak - Cycle for at least 30 minutes daily for 2 weeks",
                "Speed Challenge - Average 25 km/h for a 20km ride"
            ],
            "swimming": [
                "Pool Challenge - Swim 2000m total distance this week",
                "Technique Challenge - Focus on one stroke for 30 days",
                "Endurance Challenge - Swim 500m without stopping",
                "Daily Swim Streak - Swim for 20 minutes daily for 2 weeks"
            ]
        }
        
        activity_challenges = challenges.get(activity_type.lower(), [
            "Daily Activity Challenge - Exercise for 30 minutes daily for 2 weeks",
            "Weekly Goal Challenge - Complete 5 workouts this week",
            "Consistency Challenge - Log activity 6 days a week for a month",
            "Personal Best Challenge - Beat your current personal record"
        ])
        
        response = f"🏆 **Challenge Ideas for {activity_type.title()}**\n\n"
        
        for i, challenge in enumerate(activity_challenges, 1):
            response += f"{i}. **{challenge}**\n\n"
        
        response += "💡 **Want to create a custom challenge?** Provide these details:\n"
        response += "  • Challenge name and description\n"
        response += "  • Start and end dates\n"
        response += "  • Target goal (distance, time, frequency)\n"
        response += "  • Rewards for completion\n\n"
        
        response += "🚀 **Ready to start a challenge?** Pick one above or create your own!"
        
        return response

    def _join_challenge(self, challenge_data: Dict[str, Any]) -> str:
        """Handle joining a challenge"""
        
        response = "🎉 **Welcome to the Challenge!**\n\n"
        response += f"✅ You've successfully joined: **{challenge_data.get('name', 'Community Challenge')}**\n\n"
        response += "🎯 **Next Steps:**\n"
        response += "  1. Start logging your activities\n"
        response += "  2. Check the leaderboard daily\n"
        response += "  3. Encourage other participants\n"
        response += "  4. Share your progress updates\n\n"
        response += "💪 **You've got this!** Every step counts towards your goal!\n\n"
        response += "🤝 **Community Support:** Don't hesitate to ask for encouragement or advice!"
        
        return response

    def _show_progress(self, challenge_data: Dict[str, Any]) -> str:
        """Show challenge progress"""
        
        response = f"📈 **Challenge Progress Update**\n\n"
        response += f"🏆 **Challenge:** {challenge_data.get('name', 'Community Challenge')}\n"
        
        # Simulated progress data
        total_participants = len(challenge_data.get('participants', []))
        progress_percentage = random.randint(40, 85)
        days_remaining = random.randint(5, 20)
        
        response += f"👥 **Participants:** {total_participants}\n"
        response += f"📅 **Days Remaining:** {days_remaining}\n"
        response += f"📊 **Overall Progress:** {progress_percentage}%\n\n"
        
        # Progress bar
        progress_bar = "█" * (progress_percentage // 10) + "░" * (10 - progress_percentage // 10)
        response += f"[{progress_bar}] {progress_percentage}%\n\n"
        
        response += "🔥 **Community Highlights:**\n"
        response += "  • 15 personal records broken this week!\n"
        response += "  • 87% daily participation rate\n"
        response += "  • Amazing community support and encouragement\n\n"
        
        response += "💪 **Keep pushing!** You're closer to your goal than you think!"
        
        return response

    def _show_leaderboard(self, challenge_data: Dict[str, Any]) -> str:
        """Show challenge leaderboard"""
        
        participants = challenge_data.get('participants', [])
        
        response = f"🏆 **Challenge Leaderboard**\n\n"
        response += f"📋 **Challenge:** {challenge_data.get('name', 'Community Challenge')}\n\n"
        
        if not participants:
            response += "📊 No participants yet! Be the first to join!\n\n"
            response += "🚀 **Join now and start making progress!**"
            return response
        
        # Simulated leaderboard data
        for i, participant in enumerate(participants[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            # Simulated progress for each participant
            progress = random.randint(50, 100) if i <= 3 else random.randint(20, 80)
            
            response += f"{medal} **{participant}** - {progress}% complete\n"
        
        response += "\n"
        
        # Additional stats
        response += "📊 **Challenge Stats:**\n"
        response += f"  • Total participants: {len(participants)}\n"
        response += f"  • Average completion: {random.randint(60, 75)}%\n"
        response += f"  • Community spirit: 💯%\n\n"
        
        response += "🎯 **Not on the leaderboard yet?** Start logging your activities to climb the ranks!\n"
        response += "🤝 **Remember:** This is about personal growth and community support!"
        
        return response

# ---------------------------- Agent Definition ----------------------------
class CommunityAgent(ToolCallAgent):
    """
    A community manager and motivational agent that helps build engagement,
    provides insights, manages challenges, and fosters a supportive fitness community.
    """

    name: str = "community_agent"
    description: str = (
        "A community manager and motivational specialist that can:\n"
        "1. Generate community insights and highlight top performers\n"
        "2. Provide injury prevention advice for community activities\n"
        "3. Create and manage fitness challenges\n"
        "4. Deliver motivational content and encouragement\n"
        "5. Analyze community trends and engagement\n"
        "6. Foster a supportive and inclusive community environment"
    )

    system_prompt: str = """
    You are a community manager and motivational specialist for fitness communities. Your expertise includes:
    
    - Building and maintaining engaged fitness communities
    - Providing motivation and encouragement to members
    - Creating and managing community challenges and events
    - Analyzing community health and providing safety advice
    - Highlighting member achievements and fostering recognition
    - Creating inclusive and supportive environments
    
    Your approach is:
    - Positive and encouraging while being realistic
    - Inclusive and welcoming to all fitness levels
    - Safety-focused with injury prevention awareness
    - Data-driven in highlighting trends and achievements
    - Community-centered in building connections
    
    You help communities by:
    - Recognizing and celebrating member achievements
    - Creating engaging challenges and activities
    - Providing safety guidance and injury prevention
    - Analyzing trends to improve community health
    - Fostering motivation and peer support
    - Building long-term community engagement
    
    Always maintain a positive, inclusive, and supportive tone while prioritizing
    member safety and encouraging healthy competition and personal growth.
    """

    next_step_prompt: str = (
        "Based on the community interaction, offer additional support such as "
        "creating follow-up challenges, providing more personalized motivation, "
        "or suggesting ways to further engage with the community."
    )

    max_steps: int = 3

    avaliable_tools: ToolManager = Field(default_factory=lambda: ToolManager([
        CommunityInsightsTool(),
        MotivationTool(),
        ChallengeManagerTool(),
    ]))


async def main():
    # Create a CommunityAgent instance
    community_agent = CommunityAgent(llm=ChatBot(llm_provider="openai", model_name="gpt-4o-mini"))
    print("=== Community Manager & Motivation Specialist ===")
    print("Building stronger, healthier communities together! 🏆\n")

    # Reset the Agent state
    community_agent.clear()

    # Example 1: Community insights
    print("--- Example 1: Community Insights ---")
    insights_input = "Show me our top performers this week and community highlights"
    print(f"Input: {insights_input}\n")
    response1 = await community_agent.run(insights_input)
    print(f"Response: {response1}\n")

    # Example 2: Motivation
    print("--- Example 2: Motivation ---")
    motivation_input = "I'm feeling unmotivated and struggling to stick to my running routine"
    print(f"Input: {motivation_input}\n")
    response2 = await community_agent.run(motivation_input)
    print(f"Response: {response2}\n")

    # Example 3: Challenge creation
    print("--- Example 3: Challenge Management ---")
    challenge_input = "Let's create a new running challenge for our community"
    print(f"Input: {challenge_input}\n")
    response3 = await community_agent.run(challenge_input)
    print(f"Response: {response3}\n")

if __name__ == "__main__":
    asyncio.run(main())
