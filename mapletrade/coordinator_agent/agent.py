# coordinator_agent/agent.py
"""
Coordinator Agent using proper ADK session state communication
"""

from google.adk.agents import LlmAgent
from .sub_agents.data_collection_agent.agent import root_agent as data_agent
from .sub_agents.financial_analysis_agent.agent import root_agent as financial_agent
from .sub_agents.bigquery_data_agent.agent import root_agent as bigquery_agent
from .sub_agents.compliance_agent.agent import root_agent as compliance_agent
# from .sub_agents.financial_education_agent.agent import root_agent as education_agent

root_agent = LlmAgent(
    name="mapletrade_coordinator",
    model="gemini-2.0-flash",
    description="Canadian trading assistant coordinator using session state communication",
    instruction="""You coordinate Canadian trading analysis using proper multi-agent workflows.

AGENT DELEGATION WORKFLOW:
1. Data Collection → financial analysis → BigQuery storage → compliance check → education
2. Use session state for data flow between agents
3. Always provide educational context

DELEGATION STRATEGY:
- Complex financial analysis: → financial_analysis_agent  
- Data collection: → data_collection_agent
- Historical analysis: → bigquery_data_agent
- Tax/compliance questions: → compliance_agent
- Educational content: → financial_education_agent


Always explain the multi-agent workflow to users for transparency.""",
    
    sub_agents=[data_agent, financial_agent, bigquery_agent, compliance_agent]
)