from crewai import Agent, Task, Crew
from langchain_community.tools import DuckDuckGoSearchRun
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

class PropertyReport(BaseModel):
    """Structured property report model"""
    title: str = Field(..., description="Report title")
    summary: str = Field(..., description="Executive summary")
    properties: List[Dict] = Field(..., description="List of analyzed properties")
    market_analysis: Dict = Field(..., description="Market analysis details")
    location_insights: Dict = Field(..., description="Location-based insights")
    investment_recommendations: List[Dict] = Field(..., description="Top investment recommendations")
    negotiation_tips: List[str] = Field(default_factory=list, description="Negotiation strategies")
    metadata: Dict = Field(default_factory=dict, description="Report metadata")

class PropertyData(BaseModel):
    """Model for property data"""
    title: str
    location: str
    price: Optional[str] = None
    features: Optional[List[str]] = None
    url: Optional[str] = None

class AgentFactory:
    """Factory class for creating agents with GPT-3.5 Turbo"""
    
    @staticmethod
    def _create_base_agent(role: str, goal: str, backstory: str) -> Agent:
        """Base method for creating agents with GPT-3.5 Turbo configuration"""
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=True,
            allow_delegation=False,
            # Configure for GPT-3.5 Turbo
            llm_config={
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "request_timeout": 120
            }
        )

    @staticmethod
    def create_researcher():
        return AgentFactory._create_base_agent(
            role="Property Researcher",
            goal="Find and analyze property listings matching criteria",
            backstory="Expert in real estate data extraction and market research"
        )

    @staticmethod
    def create_analyst():
        return AgentFactory._create_base_agent(
            role="Market Analyst",
            goal="Analyze property data and identify investment opportunities",
            backstory="Specialist in real estate market analysis and property valuation"
        )

    @staticmethod
    def create_location_analyst():
        return AgentFactory._create_base_agent(
            role="Location Analyst",
            goal="Analyze location trends and market dynamics",
            backstory="Expert in geographic market trends and neighborhood analysis"
        )

    @staticmethod
    def create_editor():
        return AgentFactory._create_base_agent(
            role="Report Editor",
            goal="Compile and format analysis into clear, actionable reports",
            backstory="Experienced in structuring real estate data into clear insights"
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
            expected_output="Structured report with key insights",
            agent=agent
        )

class TokenTracker:
    """Track and calculate token usage for GPT-3.5 Turbo"""
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.usage = TokenUsage()
        
        # GPT-3.5 Turbo pricing (as of 2024)
        self.PROMPT_COST_PER_1K = 0.0015  # $0.0015 per 1K tokens
        self.COMPLETION_COST_PER_1K = 0.002  # $0.002 per 1K tokens

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int):
        """Calculate cost based on GPT-3.5 Turbo token usage"""
        prompt_cost = (prompt_tokens / 1000) * self.PROMPT_COST_PER_1K
        completion_cost = (completion_tokens / 1000) * self.COMPLETION_COST_PER_1K
        total_cost = prompt_cost + completion_cost
        
        self.usage.prompt_tokens += prompt_tokens
        self.usage.completion_tokens += completion_tokens
        self.usage.total_tokens += (prompt_tokens + completion_tokens)
        self.usage.cost += total_cost
        
        return total_cost

    def get_usage_summary(self) -> str:
        """Get formatted usage summary with GPT-3.5 Turbo costs"""
        return f"""
Token Usage Summary (GPT-3.5 Turbo):
- Prompt Tokens: {self.usage.prompt_tokens:,} (${(self.usage.prompt_tokens / 1000 * self.PROMPT_COST_PER_1K):.4f})
- Completion Tokens: {self.usage.completion_tokens:,} (${(self.usage.completion_tokens / 1000 * self.COMPLETION_COST_PER_1K):.4f})
- Total Tokens: {self.usage.total_tokens:,}
- Total Cost: ${self.usage.cost:.4f}
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

    def _format_report(self, raw_result: str, city: str, property_type: str, max_price: str) -> str:
        """Format the report into a structured, marketing-friendly format"""
        try:
            # Parse the raw result into sections
            sections = self._parse_report_sections(raw_result)
            
            # Create structured report
            report = PropertyReport(
                title=f"Real Estate Market Analysis: {property_type} in {city}",
                summary=sections.get('summary', 'Analysis of property opportunities'),
                properties=sections.get('properties', []),
                market_analysis=sections.get('market_analysis', {}),
                location_insights=sections.get('location_insights', {}),
                investment_recommendations=sections.get('recommendations', []),
                negotiation_tips=sections.get('negotiation_tips', []),
                metadata={
                    'city': city,
                    'property_type': property_type,
                    'max_price': max_price,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'token_usage': self.token_tracker.get_usage_summary()
                }
            )

            # Convert to marketing-friendly HTML
            return self._generate_html_report(report)
        except Exception as e:
            return f"""
                <div class="report-error">
                    <h2>Error Formatting Report</h2>
                    <p>An error occurred while formatting the report: {str(e)}</p>
                </div>
            """

    def _parse_report_sections(self, raw_result: str) -> Dict:
        """Parse raw report text into structured sections"""
        sections = {
            'summary': '',
            'properties': [],
            'market_analysis': {},
            'location_insights': {},
            'recommendations': [],
            'negotiation_tips': []
        }
        
        try:
            # Split the raw result into sections based on headers
            sections_text = raw_result.split('\n\n')
            
            for section in sections_text:
                if not section.strip():
                    continue
                    
                # Extract section title and content
                lines = section.split('\n')
                title = lines[0].strip().lower()
                content = '\n'.join(lines[1:]).strip()
                
                # Parse based on section type
                if 'summary' in title:
                    sections['summary'] = content
                elif 'property' in title:
                    # Parse property details
                    property_data = self._parse_property_details(content)
                    if property_data:
                        sections['properties'].append(property_data)
                elif 'market' in title:
                    sections['market_analysis'] = self._parse_key_value_pairs(content)
                elif 'location' in title:
                    sections['location_insights'] = self._parse_key_value_pairs(content)
                elif 'recommendation' in title:
                    sections['recommendations'].append({
                        'title': title.replace('recommendation:', '').strip(),
                        'description': content
                    })
                elif 'negotiation' in title:
                    sections['negotiation_tips'] = [tip.strip() for tip in content.split('\n') if tip.strip()]
            
            return sections
            
        except Exception as e:
            print(f"Error parsing report sections: {str(e)}")
            return sections

    def _parse_property_details(self, content: str) -> Optional[Dict]:
        """Parse property details from content string"""
        try:
            lines = content.split('\n')
            property_data = {
                'title': '',
                'location': '',
                'price': '',
                'features': []
            }
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('Title:'):
                    property_data['title'] = line.replace('Title:', '').strip()
                elif line.startswith('Location:'):
                    property_data['location'] = line.replace('Location:', '').strip()
                elif line.startswith('Price:'):
                    property_data['price'] = line.replace('Price:', '').strip()
                elif line.startswith('-'):
                    property_data['features'].append(line.replace('-', '').strip())
            
            return property_data if property_data['title'] else None
            
        except Exception as e:
            print(f"Error parsing property details: {str(e)}")
            return None

    def _parse_key_value_pairs(self, content: str) -> Dict:
        """Parse key-value pairs from content string"""
        pairs = {}
        try:
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if ':' in line:
                    key, value = line.split(':', 1)
                    pairs[key.strip()] = value.strip()
                elif line.startswith('-'):
                    # Handle list items
                    key = 'list_items'
                    if key not in pairs:
                        pairs[key] = []
                    pairs[key].append(line.replace('-', '').strip())
            
            return pairs
            
        except Exception as e:
            print(f"Error parsing key-value pairs: {str(e)}")
            return {}

    def _generate_html_report(self, report: PropertyReport) -> str:
        """Generate HTML report with modern card design"""
        return f"""
        <div class="report-card glass-card animate-fade-in">
            <div class="report-header">
                <h1>{report.title}</h1>
                <p class="report-summary">{report.summary}</p>
            </div>

            <div class="report-section">
                <h2>Top Property Picks</h2>
                <div class="property-grid">
                    {self._format_properties_html(report.properties)}
                </div>
            </div>

            <div class="report-section">
                <h2>Market Analysis</h2>
                <div class="market-insights">
                    {self._format_market_analysis_html(report.market_analysis)}
                </div>
            </div>

            <div class="report-section">
                <h2>Location Insights</h2>
                <div class="location-insights">
                    {self._format_location_insights_html(report.location_insights)}
                </div>
            </div>

            <div class="report-section">
                <h2>Investment Recommendations</h2>
                <div class="recommendations">
                    {self._format_recommendations_html(report.investment_recommendations)}
                </div>
            </div>

            <div class="report-section">
                <h2>Negotiation Strategy</h2>
                <ul class="negotiation-tips">
                    {self._format_negotiation_tips_html(report.negotiation_tips)}
                </ul>
            </div>

            <div class="report-footer">
                <p>Report generated on: {report.metadata['date']}</p>
                <p>Analysis for: {report.metadata['city']} - {report.metadata['property_type']}</p>
                <p>Budget: KES {report.metadata['max_price']}</p>
            </div>
        </div>
        """

    def _format_properties_html(self, properties: List[Dict]) -> str:
        """Format properties into HTML grid"""
        html = ""
        for prop in properties:
            html += f"""
            <div class="property-item glass-card">
                <h3>{prop.get('title', 'Property')}</h3>
                <p class="location">{prop.get('location', '')}</p>
                <p class="price">{prop.get('price', '')}</p>
                <ul class="features">
                    {self._format_features_html(prop.get('features', []))}
                </ul>
            </div>
            """
        return html

    def _format_features_html(self, features: List[str]) -> str:
        """Format property features into HTML list items"""
        return "".join([f"<li>{feature}</li>" for feature in features])

    def _format_market_analysis_html(self, analysis: Dict) -> str:
        """Format market analysis into HTML"""
        return "".join([f"<p><strong>{k}:</strong> {v}</p>" for k, v in analysis.items()])

    def _format_location_insights_html(self, insights: Dict) -> str:
        """Format location insights into HTML"""
        return "".join([f"<p><strong>{k}:</strong> {v}</p>" for k, v in insights.items()])

    def _format_recommendations_html(self, recommendations: List[Dict]) -> str:
        """Format recommendations into HTML"""
        html = ""
        for rec in recommendations:
            html += f"""
            <div class="recommendation-item">
                <h4>{rec.get('title', '')}</h4>
                <p>{rec.get('description', '')}</p>
            </div>
            """
        return html

    def _format_negotiation_tips_html(self, tips: List[str]) -> str:
        """Format negotiation tips into HTML list items"""
        return "".join([f"<li>{tip}</li>" for tip in tips])

    def run_analysis(self, city: str, property_type: str, max_price: str, property_urls: List[str]) -> str:
        """Run the property analysis pipeline"""
        try:
            # Validate inputs
            if not city or not property_type or not max_price:
                raise ValueError("Missing required parameters")
            
            if not property_urls:
                raise ValueError("No property URLs provided")
            
            # Create tasks
            tasks = self._create_tasks(city, property_type, max_price, property_urls)
            
            # Create and run crew
            crew = self._create_crew(tasks)
            result = crew.kickoff()
            
            # Format and return report
            return self._format_report(result, city, property_type, max_price)
            
        except ValueError as e:
            return self._format_error_message(
                title="Invalid Input",
                message=str(e),
                error_type="general"
            )
        except Exception as e:
            error_message = str(e)
            
            # Check for specific OpenAI API errors
            if "insufficient_quota" in error_message:
                return self._format_error_message(
                    title="Service Temporarily Unavailable",
                    message="We're currently experiencing high demand. Please try again in a few minutes.",
                    error_type="quota_exceeded"
                )
            elif "rate_limit_exceeded" in error_message:
                return self._format_error_message(
                    title="Please Wait",
                    message="Our AI is catching its breath. Please try again in a few seconds.",
                    error_type="rate_limit"
                )
            elif "api_error" in error_message:
                return self._format_error_message(
                    title="Service Error",
                    message="We're having trouble connecting to our AI service. Please try again shortly.",
                    error_type="api_error"
                )
            else:
                return self._format_error_message(
                    title="Analysis Error",
                    message=f"We encountered an issue while analyzing properties in {city}. Our team has been notified.",
                    error_type="general"
                )

    def _format_error_message(self, title: str, message: str, error_type: str) -> str:
        """Format error messages in a user-friendly way"""
        error_classes = {
            "quota_exceeded": "error-card quota-error",
            "rate_limit": "error-card rate-limit-error",
            "api_error": "error-card api-error",
            "general": "error-card"
        }
        
        error_class = error_classes.get(error_type, "error-card")
        
        return f"""
            <div class="{error_class}">
                <div class="error-icon">
                    {self._get_error_icon(error_type)}
                </div>
                <h2>{title}</h2>
                <p>{message}</p>
                <div class="error-actions">
                    <button onclick="window.location.reload()" class="retry-button">
                        Try Again
                    </button>
                    <a href="/" class="back-home">
                        Back to Home
                    </a>
                </div>
            </div>
        """

    def _get_error_icon(self, error_type: str) -> str:
        """Get appropriate icon for error type"""
        icons = {
            "quota_exceeded": """<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 2v20M2 12h20" stroke-width="2" stroke-linecap="round"/>
            </svg>""",
            "rate_limit": """<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10" stroke-width="2"/>
                <path d="M12 6v6l4 2" stroke-width="2" stroke-linecap="round"/>
            </svg>""",
            "api_error": """<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 8v8M12 16h.01" stroke-width="2" stroke-linecap="round"/>
                <circle cx="12" cy="12" r="10" stroke-width="2"/>
            </svg>""",
            "general": """<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10" stroke-width="2"/>
                <path d="M12 8v8M12 16h.01" stroke-width="2" stroke-linecap="round"/>
            </svg>"""
        }
        return icons.get(error_type, icons["general"]) 