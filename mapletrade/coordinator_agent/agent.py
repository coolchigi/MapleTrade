# coordinator_agent/agent.py
from google.adk.agents import LlmAgent
from .sub_agents.financial_analysis_agent.agent import root_agent as financial_agent
from .sub_agents.compliance_agent.agent import root_agent as compliance_agent
from .sub_agents.bigquery_data_agent.agent import root_agent as bigquery_data_agent
from .sub_agents.data_collection_agent.agent import root_agent as data_collection_agent


root_agent = LlmAgent(
    name="mapletrade_coordinator",
    model="gemini-2.0-flash",
    description="Canadian trading assistant coordinator - routes to specialized agents",
    instruction="""You coordinate Canadian trading analysis. Route requests to:

- financial_analysis_agent: Financial ratios, P/E, ROE calculations
- compliance_agent: TFSA, RRSP, tax rules, Canadian regulations
- data_collection_agent: Market data, prices, volumes  
- market_intelligence_agent: News, sentiment analysis

Always explain which agent you're using and why.""",
    
    sub_agents=[
        financial_agent,
        compliance_agent,
        bigquery_data_agent,
        data_collection_agent
    ]
)