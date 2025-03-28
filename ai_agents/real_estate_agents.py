from crewai import Agent, Task, Crew
from crewai_tools import FirecrawlScrapeWebsiteTool
from typing import List
import os
import json
from datetime import datetime

class RealEstateAgentSystem:
    def __init__(self):
        # Initialize our agents with specific roles and goals
        self.property_researcher = Agent(
            role="Senior Property Researcher",
            goal="Find and extract property listings based on criteria",
            backstory="Expert in real estate data extraction with years of experience in aggregating property data from multiple sources. Known for accurate and comprehensive data collection.",
            verbose=True
        )
        
        self.market_analyst = Agent(
            role="Real Estate Market Analyst",
            goal="Analyze property data and identify best investment opportunities",
            backstory="A seasoned analyst with deep understanding of real estate markets and valuation techniques. Specializes in comparative market analysis and investment potential assessment.",
            verbose=True
        )
        
        self.location_analyst = Agent(
            role="Location Intelligence Specialist",
            goal="Analyze location-based price trends and market dynamics",
            backstory="An urban economist with expertise in geographic market trends and neighborhood valuation patterns. Combines GIS data with market intelligence for accurate predictions.",
            verbose=True
        )
        
        self.report_editor = Agent(
            role="Senior Real Estate Editor",
            goal="Compile analysis into professional reports",
            backstory="A former property journalist with exceptional skills in structuring complex data into clear, actionable insights. Ensures reports are accurate and client-ready.",
            verbose=True
        )
    
    def setup_tasks(self, city, property_type, max_price, property_urls):
        # Define tasks for each agent
        self.property_search_task = Task(
            description=f"Search for {property_type} properties in {city} under {max_price} from these sources: {property_urls}. Focus only on properties matching the exact criteria.",
            expected_output="Structured data of 5-10 relevant properties with complete details including price, location, and features.",
            agent=self.property_researcher,
            tools=[FirecrawlScrapeWebsiteTool()],
        )
        
        self.market_analysis_task = Task(
            description=f"Analyze properties in {city} and identify top 3 investment opportunities based on the search results",
            expected_output="Comparative analysis report highlighting price-value ratios, future appreciation potential, and risk factors.",
            agent=self.market_analyst
        )
        
        self.location_analysis_task = Task(
            description=f"Analyze price trends and neighborhood dynamics for {city}",
            expected_output="Report detailing price trends, rental yields, and emerging hotspots in different localities.",
            agent=self.location_analyst
        )
        
        self.report_task = Task(
            description="Compile all analyses into final client-ready report",
            expected_output="Well-structured markdown report with sections for property recommendations, market analysis, and location insights.",
            agent=self.report_editor
        )
    
    def run_analysis(self, city, property_type, max_price, property_urls):
        """Run the full property analysis using a crew of AI agents"""
        try:
            # Setup the tasks with specific parameters
            self.setup_tasks(city, property_type, max_price, property_urls)
            
            # Create and configure the crew
            crew = Crew(
                agents=[
                    self.property_researcher,
                    self.market_analyst,
                    self.location_analyst,
                    self.report_editor
                ],
                tasks=[
                    self.property_search_task,
                    self.market_analysis_task,
                    self.location_analysis_task,
                    self.report_task
                ],
                verbose=2
            )
            
            # Execute the crew's analysis
            result = crew.kickoff()
            
            # Add timestamp and metadata to the report
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            metadata = f"\n\n---\nReport generated on: {timestamp}\nCity: {city}\nProperty Type: {property_type}\nMax Price: {max_price}"
            
            return result + metadata
            
        except Exception as e:
            # Return a formatted error message if something goes wrong
            error_report = f"""
# Error in Property Analysis

An error occurred while analyzing properties in {city}:

{str(e)}

Please try again or contact support if the issue persists.
"""
            return error_report 