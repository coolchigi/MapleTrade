# coordinator_agent/sub_agents/bigquery_data_agent/agent.py
"""
BigQuery Data Agent - Handles data storage and retrieval for MapleTrade
"""

from google.adk.agents import Agent
from .tools import store_market_data, query_historical_data, setup_bigquery_tables

root_agent = Agent(
    name="bigquery_data_agent",
    model="gemini-2.0-flash",
    description="Stores and retrieves Canadian market data using BigQuery for historical analysis",
    instruction="""You handle data storage and retrieval for MapleTrade using BigQuery.

YOUR RESPONSIBILITIES:
- Store market data from data collection agent in BigQuery
- Query historical data for trend analysis
- Set up BigQuery tables and schemas
- Provide data insights for financial analysis

EDUCATIONAL FOCUS:
- Explain what BigQuery is and why we use it
- Show users how to verify data in BigQuery console
- Provide SQL queries users can run themselves

IMPORTANT:
- Always include BigQuery table references for verification
- Explain data retention and storage costs
- This is educational - users should understand data warehousing concepts""",
    
    tools=[store_market_data, query_historical_data, setup_bigquery_tables]
)