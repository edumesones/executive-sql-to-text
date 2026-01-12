"""
Performance metrics tracking for workflow execution
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import time


@dataclass
class WorkflowMetrics:
    """
    Tracks performance metrics for a complete workflow execution
    """
    session_id: str
    total_duration_ms: int = 0
    sql_agent_duration_ms: int = 0
    analyst_agent_duration_ms: int = 0
    viz_agent_duration_ms: int = 0
    insight_agent_duration_ms: int = 0
    result_count: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary format"""
        return {
            "session_id": self.session_id,
            "total_duration_ms": self.total_duration_ms,
            "breakdown": {
                "sql_agent": self.sql_agent_duration_ms,
                "analyst_agent": self.analyst_agent_duration_ms,
                "viz_agent": self.viz_agent_duration_ms,
                "insight_agent": self.insight_agent_duration_ms
            },
            "result_count": self.result_count,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
    
    def add_error(self, error: str) -> None:
        """Add an error to the metrics"""
        self.errors.append(error)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the metrics"""
        self.warnings.append(warning)
    
    def start(self) -> None:
        """Mark workflow start time"""
        self.started_at = datetime.utcnow()
    
    def complete(self) -> None:
        """Mark workflow completion time"""
        self.completed_at = datetime.utcnow()
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.total_duration_ms = int(delta.total_seconds() * 1000)


class TimerContext:
    """Context manager for timing operations"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.duration_ms = 0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration_ms = int((self.end_time - self.start_time) * 1000)
        return False
