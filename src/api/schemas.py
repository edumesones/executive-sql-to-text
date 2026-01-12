"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str = Field(..., description="Natural language query", min_length=1, max_length=500)
    session_id: str = Field(..., description="Session ID for tracking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Show me the top 10 loans by amount",
                "session_id": "abc-123-def-456"
            }
        }


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    session_id: str
    sql_query: Optional[str] = None
    query_results: Optional[List[Dict[str, Any]]] = None
    result_count: int = 0
    derived_metrics: Optional[Dict[str, Any]] = None
    chart_type: Optional[str] = None
    chart_config: Optional[Dict[str, Any]] = None
    insights: List[str] = []
    recommendations: List[str] = []
    errors: List[str] = []
    warnings: List[str] = []
    metrics: Optional[Dict[str, int]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc-123",
                "sql_query": "SELECT * FROM loans LIMIT 10",
                "result_count": 10,
                "chart_type": "bar",
                "insights": ["Top loans average $35,000"],
                "metrics": {"total_duration_ms": 2500}
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    database: str = Field(..., description="Database status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "0.1.0"
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "database": "connected",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "0.1.0"
            }
        }


class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
