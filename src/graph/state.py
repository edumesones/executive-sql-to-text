"""
State management for the LangGraph workflow
"""
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from dataclasses import dataclass, field
from datetime import datetime
import operator


class AgentState(TypedDict):
    """
    State that gets passed between agents in the workflow.
    Each agent reads from and writes to this shared state.
    """
    # User input
    user_query: str
    session_id: str
    
    # SQL Agent outputs
    sql_query: Optional[str]
    sql_explanation: Optional[str]
    
    # Analyst Agent outputs  
    query_results: Optional[List[Dict[str, Any]]]
    result_count: int
    derived_metrics: Optional[Dict[str, Any]]
    data_quality_issues: Annotated[List[str], operator.add]
    
    # Viz Agent outputs
    chart_type: Optional[str]
    chart_config: Optional[Dict[str, Any]]
    
    # Insight Agent outputs
    insights: Annotated[List[str], operator.add]
    recommendations: Annotated[List[str], operator.add]
    
    # Metadata
    execution_time_ms: Optional[int]
    errors: Annotated[List[str], operator.add]
    warnings: Annotated[List[str], operator.add]
    current_step: str
    
    # Conversation context
    conversation_history: List[Dict[str, str]]


@dataclass
class WorkflowMetrics:
    """Metrics for monitoring workflow execution"""
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    total_duration_ms: Optional[int] = None
    
    sql_generation_ms: Optional[int] = None
    query_execution_ms: Optional[int] = None
    analysis_ms: Optional[int] = None
    visualization_ms: Optional[int] = None
    insight_generation_ms: Optional[int] = None
    
    tokens_used: int = 0
    api_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    def finalize(self):
        """Calculate final metrics"""
        self.end_time = datetime.utcnow()
        self.total_duration_ms = int((self.end_time - self.start_time).total_seconds() * 1000)


def create_initial_state(user_query: str, session_id: str) -> AgentState:
    """Create initial state for a new workflow execution"""
    return {
        "user_query": user_query,
        "session_id": session_id,
        "sql_query": None,
        "sql_explanation": None,
        "query_results": None,
        "result_count": 0,
        "derived_metrics": None,
        "data_quality_issues": [],
        "chart_type": None,
        "chart_config": None,
        "insights": [],
        "recommendations": [],
        "execution_time_ms": None,
        "errors": [],
        "warnings": [],
        "current_step": "initialization",
        "conversation_history": []
    }
