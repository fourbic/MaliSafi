from crewai import Agent, Task, Crew
# from langchain_community.tools import DuckDuckGoSearchRun
# from crewai_tools import FirecrawlScrapeWebsiteTool
from crewai_tools import ScrapeWebsiteTool
from typing import List, Dict, Optional
import os
import json
from datetime import datetime
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the PropertyUrls model
class PropertyUrls(BaseModel):
    urls: List[str] = Field(..., description="List of formatted URLs to scrape based on location")

class TokenUsage(BaseModel):
    """Track token usage for cost calculation"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0

class PropertyData(BaseModel):
    """Model for property data"""
    title: str
    location: str
    price: Optional[str] = None
    features: Optional[List[str]] = None
    url: Optional[str] = None

class AgentFactory:
    """Factory class for creating agents"""
    @staticmethod
    def create_researcher():
        return Agent(
            role="Property Researcher",
            goal="Find property listings matching criteria",
            backstory="Expert in real estate data extraction and analysis",
            verbose=True,
            allow_delegation=False
        )

    @staticmethod
    def create_analyst():
        return Agent(
            role="Market Analyst",
            goal="Analyze property data for investment opportunities",
            backstory="Specialist in real estate market analysis and valuation",
            verbose=True,
            allow_delegation=False
        )

    @staticmethod
    def create_location_analyst():
        return Agent(
            role="Location Analyst",
            goal="Analyze location trends and market dynamics",
            backstory="Expert in geographic market trends and neighborhood analysis",
            verbose=True,
            allow_delegation=False
        )

    @staticmethod
    def create_editor():
        return Agent(
            role="Report Editor",
            goal="Compile analysis into professional reports",
            backstory="Experienced in structuring real estate data into clear insights",
            verbose=True,
            allow_delegation=False
        )

class TaskFactory:
    """Factory class for creating tasks"""
    @staticmethod
    def create_search_task(agent, city, property_type, max_price, urls):
        return Task(
            description=f"Find {property_type} in {city} under {max_price} from: {urls}",
            expected_output="3-5 relevant properties with key details",
            agent=agent,
            tools=[ScrapeWebsiteTool()],
            output_json=PropertyData
        )

    @staticmethod
    def create_analysis_task(agent, city, property_count):
        return Task(
            description=f"Analyze {property_count} properties in {city} for opportunities",
            expected_output="Analysis of price-value ratios and potential",
            agent=agent
        )

    @staticmethod
    def create_location_task(agent, city):
        return Task(
            description=f"Analyze {city} location trends",
            expected_output="Report on price trends and hotspots",
            agent=agent
        )

    @staticmethod
    def create_report_task(agent):
        return Task(
            description="Compile final report",
            expected_output="Structured markdown report with key insights",
            agent=agent
        )

class TokenTracker:
    """Track and calculate token usage"""
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.usage = TokenUsage()

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int):
        """Calculate cost based on token usage"""
        # GPT-4 pricing (as of 2024)
        prompt_cost = (prompt_tokens / 1000) * 0.03
        completion_cost = (completion_tokens / 1000) * 0.06
        total_cost = prompt_cost + completion_cost
        
        self.usage.prompt_tokens += prompt_tokens
        self.usage.completion_tokens += completion_tokens
        self.usage.total_tokens += (prompt_tokens + completion_tokens)
        self.usage.cost += total_cost
        
        return total_cost

    def get_usage_summary(self) -> str:
        """Get formatted usage summary"""
        return f"""
Token Usage Summary:
- Prompt Tokens: {self.usage.prompt_tokens}
- Completion Tokens: {self.usage.completion_tokens}
- Total Tokens: {self.usage.total_tokens}
- Estimated Cost: ${self.usage.cost:.2f}
"""

class RealEstateAgentSystem:
    def __init__(self):
        self.agent_factory = AgentFactory()
        self.task_factory = TaskFactory()
        self.token_tracker = TokenTracker()
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
    def _initialize_agents(self) -> Dict[str, Agent]:
        """Initialize all agents"""
        return {
            'researcher': self.agent_factory.create_researcher(),
            'analyst': self.agent_factory.create_analyst(),
            'location': self.agent_factory.create_location_analyst(),
            'editor': self.agent_factory.create_editor()
        }

    def _create_tasks(self, city: str, property_type: str, max_price: str, urls: List[str]) -> List[Task]:
        """Create all tasks for the analysis"""
        return [
            self.task_factory.create_search_task(self.agents['researcher'], city, property_type, max_price, urls),
            self.task_factory.create_analysis_task(self.agents['analyst'], city, "3-5"),
            self.task_factory.create_location_task(self.agents['location'], city),
            self.task_factory.create_report_task(self.agents['editor'])
        ]

    def _create_crew(self, tasks: List[Task]) -> Crew:
        """Create and configure the crew"""
        return Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            verbose=2
        )

    def _format_report(self, result: str, city: str, property_type: str, max_price: str) -> str:
        """Format the final report with metadata"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata = f"\n\n---\nReport: {timestamp}\nCity: {city}\nType: {property_type}\nPrice: {max_price}"
        usage_summary = self.token_tracker.get_usage_summary()
        return f"{result}{metadata}\n{usage_summary}"

    def run_analysis(self, city: str, property_type: str, max_price: str, property_urls: List[str]) -> str:
        """Run the property analysis pipeline"""
        try:
            # Create tasks
            tasks = self._create_tasks(city, property_type, max_price, property_urls)
            
            # Create and run crew
            crew = self._create_crew(tasks)
            result = crew.kickoff()
            
            # Format and return report
            return self._format_report(result, city, property_type, max_price)
            
        except Exception as e:
            return f"""
# Analysis Error

Error analyzing {city} properties:
{str(e)}

Please try again or contact support.
""" 