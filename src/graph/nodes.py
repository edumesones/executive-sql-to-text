"""
Node Functions for LangGraph Workflow with Logging and Metrics
"""
from typing import Dict, Any
import asyncio
import time

from ..agents import SQLAgent, AnalystAgent, VizAgent, InsightAgent
from ..utils.logging import get_logger
from ..utils.metrics import TimerContext

# Get logger
logger = get_logger("workflow.nodes")


async def sql_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    SQL Agent Node - Generate SQL query from natural language
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with sql_query
    """
    session_id = state.get("session_id", "unknown")
    user_query = state.get("user_query", "")
    
    logger.info(
        "sql_agent_started",
        session_id=session_id,
        query_preview=user_query[:100] if user_query else "empty"
    )
    
    with TimerContext() as timer:
        try:
            agent = SQLAgent()
            result = agent.process(state)
            
            logger.info(
                "sql_agent_completed",
                session_id=session_id,
                duration_ms=timer.duration_ms,
                sql_generated=result.get("sql_query") is not None,
                has_errors=bool(result.get("errors"))
            )
            
            # Add timing to state
            if "metrics" not in state:
                state["metrics"] = {}
            state["metrics"]["sql_agent_duration_ms"] = timer.duration_ms
            
            return {**state, **result}
            
        except Exception as e:
            logger.error(
                "sql_agent_error",
                session_id=session_id,
                duration_ms=timer.duration_ms,
                error=str(e),
                exc_info=True
            )
            return {
                **state,
                "errors": state.get("errors", []) + [f"SQL Agent error: {str(e)}"]
            }


async def analyst_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyst Agent Node - Execute query and analyze results
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with query_results and metrics
    """
    session_id = state.get("session_id", "unknown")
    
    # Skip if previous errors
    if state.get("errors"):
        logger.warning("analyst_agent_skipped", session_id=session_id, reason="previous_errors")
        return state
    
    logger.info("analyst_agent_started", session_id=session_id)
    
    with TimerContext() as timer:
        try:
            agent = AnalystAgent()
            result = agent.process(state)
            
            logger.info(
                "analyst_agent_completed",
                session_id=session_id,
                duration_ms=timer.duration_ms,
                result_count=result.get("result_count", 0),
                has_metrics=bool(result.get("derived_metrics"))
            )
            
            # Add timing to state
            if "metrics" not in state:
                state["metrics"] = {}
            state["metrics"]["analyst_agent_duration_ms"] = timer.duration_ms
            
            return {**state, **result}
            
        except Exception as e:
            logger.error(
                "analyst_agent_error",
                session_id=session_id,
                duration_ms=timer.duration_ms,
                error=str(e),
                exc_info=True
            )
            return {
                **state,
                "errors": state.get("errors", []) + [f"Analyst Agent error: {str(e)}"]
            }


async def viz_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Viz Agent Node - Generate visualization
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with chart_config
    """
    # Skip if previous errors
    if state.get("errors"):
        return state
    
    agent = VizAgent()
    result = agent.process(state)
    return {**state, **result}


async def insight_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insight Agent Node - Generate business insights
    
    Args:
        state: Current workflow state
    
    Returns:
        Updated state with insights and recommendations
    """
    session_id = state.get("session_id", "unknown")
    
    # Skip if previous errors
    if state.get("errors"):
        logger.warning("insight_agent_skipped", session_id=session_id, reason="previous_errors")
        return state
    
    logger.info("insight_agent_started", session_id=session_id)
    
    with TimerContext() as timer:
        try:
            agent = InsightAgent()
            result = agent.process(state)
            
            logger.info(
                "insight_agent_completed",
                session_id=session_id,
                duration_ms=timer.duration_ms,
                insight_count=len(result.get("insights", [])),
                recommendation_count=len(result.get("recommendations", []))
            )
            
            # Add timing to state
            if "metrics" not in state:
                state["metrics"] = {}
            state["metrics"]["insight_agent_duration_ms"] = timer.duration_ms
            
            # Calculate total duration
            metrics = state.get("metrics", {})
            total_duration = sum([
                metrics.get("sql_agent_duration_ms", 0),
                metrics.get("analyst_agent_duration_ms", 0),
                metrics.get("viz_agent_duration_ms", 0),
                metrics.get("insight_agent_duration_ms", 0)
            ])
            state["metrics"]["total_duration_ms"] = total_duration
            
            logger.info(
                "workflow_completed",
                session_id=session_id,
                total_duration_ms=total_duration,
                breakdown=metrics
            )
            
            return {**state, **result}
            
        except Exception as e:
            logger.error(
                "insight_agent_error",
                session_id=session_id,
                duration_ms=timer.duration_ms,
                error=str(e),
                exc_info=True
            )
            return {
                **state,
                "errors": state.get("errors", []) + [f"Insight Agent error: {str(e)}"]
            }


def should_continue(state: Dict[str, Any]) -> str:
    """
    Decision function for conditional edges
    
    Args:
        state: Current workflow state
    
    Returns:
        "continue" if no errors, "end" otherwise
    """
    if state.get("errors"):
        return "end"
    return "continue"
