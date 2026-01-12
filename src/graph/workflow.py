"""
LangGraph Workflow - Multi-Agent Orchestration
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any

from .state import AgentState, create_initial_state
from .nodes import (
    sql_agent_node,
    analyst_agent_node,
    viz_agent_node,
    insight_agent_node,
    should_continue
)


def create_workflow():
    """
    Create and compile the multi-agent workflow
    
    Workflow sequence:
    1. SQL Agent: Generate SQL query
    2. Analyst Agent: Execute query and analyze
    3. Viz Agent: Create visualization
    4. Insight Agent: Generate insights
    
    Returns:
        Compiled LangGraph workflow
    """
    # Create StateGraph with AgentState type
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("sql_agent", sql_agent_node)
    workflow.add_node("analyst_agent", analyst_agent_node)
    workflow.add_node("viz_agent", viz_agent_node)
    workflow.add_node("insight_agent", insight_agent_node)
    
    # Set entry point
    workflow.set_entry_point("sql_agent")
    
    # Add conditional edges for error handling
    workflow.add_conditional_edges(
        "sql_agent",
        should_continue,
        {
            "continue": "analyst_agent",
            "end": END
        }
    )
    
    # Sequential edges between agents
    workflow.add_conditional_edges(
        "analyst_agent",
        should_continue,
        {
            "continue": "viz_agent",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "viz_agent",
        should_continue,
        {
            "continue": "insight_agent",
            "end": END
        }
    )
    
    # Final edge to END
    workflow.add_edge("insight_agent", END)
    
    # Compile and return
    return workflow.compile()


# Create singleton workflow instance
_workflow = None


def get_workflow():
    """Get or create workflow singleton"""
    global _workflow
    if _workflow is None:
        _workflow = create_workflow()
    return _workflow
