# coordinator_agent/sub_agents/financial_analysis_agent/agent.py
"""
Financial Analysis Agent - Reads BigQuery data from session state
"""

from google.adk.agents import LlmAgent
from typing import Dict
from .tools import calculate_basic_ratios

def analyze_with_session_data(context) -> Dict:
    """
    Analyze financial ratios using data from session state.
    
    Args:
        context: ADK invocation context with session state
        
    Returns:
        Financial analysis with educational explanations
    """
    try:
        # Read historical data from BigQuery agent
        historical_data = context.session.state.get('bigquery_results')
        market_data = context.session.state.get('collected_market_data')
        
        analysis = {
            "data_sources_used": [],
            "analysis_type": "Session state + API data",
            "educational_flow": [
                "📊 Step 1: Data Collection Agent gathered market data",
                "📊 Step 2: BigQuery Agent stored/retrieved historical data", 
                "📊 Step 3: Financial Agent calculates ratios with context"
            ]
        }
        
        if historical_data:
            analysis["data_sources_used"].append("Historical data from BigQuery")
            analysis["trend_context"] = "Using historical context for better analysis"
            
        if market_data:
            analysis["data_sources_used"].append("Current market data from collection")
            
        return analysis
        
    except Exception as e:
        return {
            "error": f"Session data analysis failed: {str(e)}",
            "fallback": "Using direct API calculation"
        }

root_agent = LlmAgent(
    name="financial_analysis_agent",
    model="gemini-2.0-flash", 
    description="Calculates financial ratios using session state data from other agents",
    instruction="""You analyze financial data using session state communication.

WORKFLOW:
1. Read current market data from session state (data collection agent)
2. Read historical data from session state (BigQuery agent)  
3. Calculate ratios with full context
4. Provide educational explanations with data source attribution

SESSION STATE KEYS YOU READ:
- 'collected_market_data': Current prices, volumes
- 'bigquery_results': Historical trends, comparisons
- 'historical_data': Multi-period analysis

EDUCATIONAL FOCUS:
- Show how agents collaborate through session state
- Explain ratio calculations with source data
- Provide verification links for all data sources
- Demonstrate multi-agent data flow

When analyzing, mention that you're reading data from session state that other agents collected.""",
    
    tools=[calculate_basic_ratios],  # Remove the problematic function
    output_key="financial_analysis"
)