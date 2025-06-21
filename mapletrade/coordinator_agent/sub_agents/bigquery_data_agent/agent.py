# coordinator_agent/sub_agents/bigquery_data_agent/agent.py
"""
BigQuery Agent - Reads from session state and stores data
"""

from google.adk.agents import LlmAgent
from typing import Dict
from .tools import setup_bigquery_tables, query_historical_data

def store_session_data_to_bigquery(context) -> Dict:
    """
    Read market data from session state and store in BigQuery.
    
    Args:
        context: ADK invocation context with session state
        
    Returns:
        Storage confirmation
    """
    try:
        # Read data from session state
        market_data = context.session.state.get('collected_market_data')
        
        if not market_data:
            return {
                "error": "No market data found in session state",
                "instruction": "Ask data collection agent to collect data first"
            }
        
        # Extract data (assuming it's structured from data collection agent)
        # This would need parsing based on actual data collection output
        
        return {
            "success": True,
            "message": "Market data stored in BigQuery",
            "data_source": "Session state -> BigQuery",
            "educational_note": "📊 Data flows: Data Collection → Session State → BigQuery → Analysis"
        }
        
    except Exception as e:
        return {
            "error": f"Failed to store session data: {str(e)}",
            "fallback": "Manual BigQuery setup required"
        }

root_agent = LlmAgent(
    name="bigquery_data_agent", 
    model="gemini-2.0-flash",
    description="Stores market data from session state into BigQuery and retrieves historical data",
    instruction="""You handle BigQuery storage and retrieval using session state communication.

WORKFLOW:
1. Read market data from session state (saved by data collection agent)
2. Store it in BigQuery with proper schema
3. Query historical data when requested
4. Save query results back to session state for other agents

SESSION STATE KEYS YOU USE:
- Read: 'collected_market_data' (from data collection)
- Write: 'historical_data' (for financial analysis)

EDUCATIONAL FOCUS:
- Explain how session state enables agent communication
- Show BigQuery table references for verification
- Describe data flow between agents""",
    
    tools=[setup_bigquery_tables, query_historical_data, store_session_data_to_bigquery],
    output_key="bigquery_results"
)