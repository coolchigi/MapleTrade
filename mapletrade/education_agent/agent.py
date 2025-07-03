from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="education_agent",
    model="gemini-2.0-flash",
    description="Explains financial concepts and trading education",
    instruction="You explain financial concepts clearly using Google Search. Focus on education, not investment advice.",
    tools=[google_search]
)