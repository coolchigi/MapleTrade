# coordinator_agent/agent.py
"""
Coordinator Agent using proper ADK session state communication
"""

from google.adk.agents import LlmAgent
from .sub_agents.data_collection_agent.agent import root_agent as data_agent
from .sub_agents.financial_analysis_agent.agent import root_agent as financial_agent

root_agent = LlmAgent(
    name="mapletrade_coordinator",
    model="gemini-2.0-flash",
    description="Canadian trading assistant coordinator using session state communication",
    instruction="""You coordinate Canadian trading analysis using proper multi-agent workflows.

AGENT DELEGATION:
- Route data collection requests to data_collection_agent
- Route financial analysis requests to financial_analysis_agent
- Use session state to share data between agents

When user asks for financial analysis:
1. Delegate to financial_analysis_agent
2. Agent will read data from session state automatically
3. Explain the analysis results

Always actually delegate to sub-agents, don't just describe what you would do.""",
    
    sub_agents=[data_agent, financial_agent]  # Start with just one sub-agent
)