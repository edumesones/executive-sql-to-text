"""
API Routes for Executive Analytics Assistant
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
import uuid

from .schemas import QueryRequest, QueryResponse, HealthResponse, ErrorResponse
from ..graph import get_workflow, create_initial_state
from ..utils.logging import get_logger
from ..database.connection import test_connection

# Get logger
logger = get_logger("api.routes")

# Create router
router = APIRouter(prefix="/api", tags=["analytics"])


@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def execute_query(request: QueryRequest):
    """
    Execute a natural language query and return SQL, results, charts, and insights
    
    Args:
        request: QueryRequest with natural language query and session_id
        
    Returns:
        QueryResponse with complete analysis results
    """
    logger.info(
        "api_query_received",
        session_id=request.session_id,
        query_preview=request.query[:100]
    )
    
    try:
        # Get workflow
        workflow = get_workflow()
        
        # Create initial state
        state = create_initial_state(
            user_query=request.query,
            session_id=request.session_id
        )
        
        # Execute workflow
        result = await workflow.ainvoke(state)
        
        # Log completion
        logger.info(
            "api_query_completed",
            session_id=request.session_id,
            success=not result.get("errors"),
            duration_ms=result.get("metrics", {}).get("total_duration_ms", 0)
        )
        
        # Return response
        return QueryResponse(
            session_id=request.session_id,
            sql_query=result.get("sql_query"),
            query_results=result.get("query_results"),
            result_count=result.get("result_count", 0),
            derived_metrics=result.get("derived_metrics"),
            chart_type=result.get("chart_type"),
            chart_config=result.get("chart_config"),
            insights=result.get("insights", []),
            recommendations=result.get("recommendations", []),
            errors=result.get("errors", []),
            warnings=result.get("warnings", []),
            metrics=result.get("metrics")
        )
        
    except Exception as e:
        logger.error(
            "api_query_error",
            session_id=request.session_id,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify service and database connectivity
    
    Returns:
        HealthResponse with service and database status
    """
    logger.info("health_check_requested")
    
    try:
        # Test database connection
        db_connected = test_connection()
        db_status = "connected" if db_connected else "disconnected"
        
        logger.info("health_check_completed", database=db_status)
        
        return HealthResponse(
            status="healthy" if db_connected else "degraded",
            database=db_status
        )
        
    except Exception as e:
        logger.error("health_check_error", error=str(e), exc_info=True)
        return HealthResponse(
            status="unhealthy",
            database="error"
        )


@router.get("/history/{session_id}", response_model=List[QueryResponse])
async def get_session_history(session_id: str):
    """
    Get query history for a specific session
    
    Args:
        session_id: Session identifier
        
    Returns:
        List of previous queries and their results
        
    Note:
        This is a placeholder. Full implementation would query
        a conversations table in the database.
    """
    logger.info("history_requested", session_id=session_id)
    
    # TODO: Implement database query for conversation history
    # For now, return empty list
    logger.warning("history_not_implemented", session_id=session_id)
    
    return []
