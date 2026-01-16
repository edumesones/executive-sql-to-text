"""
API Routes for Executive Analytics Assistant
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
import os

from .schemas import QueryRequest, QueryResponse, HealthResponse, ErrorResponse
from ..graph import get_workflow, create_initial_state
from ..utils.logging import get_logger
from ..utils.custom_tracer import get_local_tracer
from ..database.connection import test_connection
from ..database.models import User
from ..auth.dependencies import get_current_user, get_current_user_optional
from typing import Optional

# Get logger
logger = get_logger("api.routes")

# Create main router
# Initialize Local JSON Tracer (with error handling)
try:
    local_tracer = get_local_tracer(enabled=True)
    logger.info("local_json_tracer_initialized", trace_dir="traces")
except Exception as e:
    logger.warning("local_json_tracer_init_failed", error=str(e))
    local_tracer = None

# Create router
router = APIRouter(prefix="/api", tags=["analytics"])

# Import connections router
from .connections import router as connections_router


@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def execute_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Execute a natural language query and return SQL, results, charts, and insights

    Requires authentication via JWT cookie.

    Args:
        request: QueryRequest with natural language query and session_id
        current_user: Authenticated user (injected by dependency)

    Returns:
        QueryResponse with complete analysis results
    """
    logger.info(
        "api_query_received",
        session_id=request.session_id,
        user_id=str(current_user.id),
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
        
        # Execute workflow with local JSON tracing
        config = {"callbacks": [local_tracer]} if local_tracer else {}
        result = await workflow.ainvoke(state, config=config)
        
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


@router.post("/demo-query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def execute_demo_query(
    request: QueryRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Execute a natural language query on demo database.

    Works for both authenticated and anonymous users.
    Anonymous users are tracked by session_id (frontend enforces query limit).

    Args:
        request: QueryRequest with natural language query and session_id
        current_user: Optional authenticated user

    Returns:
        QueryResponse with complete analysis results
    """
    user_id = str(current_user.id) if current_user else "anonymous"
    is_anonymous = current_user is None

    logger.info(
        "demo_query_received",
        session_id=request.session_id,
        user_id=user_id,
        is_anonymous=is_anonymous,
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

        # Execute workflow with local JSON tracing
        config = {"callbacks": [local_tracer]} if local_tracer else {}
        result = await workflow.ainvoke(state, config=config)

        # Log completion
        logger.info(
            "demo_query_completed",
            session_id=request.session_id,
            user_id=user_id,
            is_anonymous=is_anonymous,
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
            "demo_query_error",
            session_id=request.session_id,
            user_id=user_id,
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
    try:
        logger.info("health_check_requested")
        
        # Test database connection with error handling
        db_connected = False
        db_status = "error"
        
        try:
            db_connected = test_connection()
            db_status = "connected" if db_connected else "disconnected"
        except Exception as db_error:
            logger.warning("database_connection_test_failed", error=str(db_error))
            db_status = "error"
        
        # Service is healthy even if DB is disconnected (degraded mode)
        service_status = "healthy" if db_connected else "degraded"
        
        logger.info("health_check_completed", status=service_status, database=db_status)
        
        return HealthResponse(
            status=service_status,
            database=db_status
        )
        
    except Exception as e:
        logger.error("health_check_error", error=str(e), exc_info=True)
        # Return unhealthy status but don't raise exception
        return HealthResponse(
            status="unhealthy",
            database="error"
        )


@router.get("/history/{session_id}", response_model=List[QueryResponse])
async def get_session_history(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get query history for a specific session

    Requires authentication via JWT cookie.

    Args:
        session_id: Session identifier
        current_user: Authenticated user (injected by dependency)

    Returns:
        List of previous queries and their results

    Note:
        This is a placeholder. Full implementation would query
        a conversations table in the database.
    """
    logger.info("history_requested", session_id=session_id, user_id=str(current_user.id))
    
    # TODO: Implement database query for conversation history
    # For now, return empty list
    logger.warning("history_not_implemented", session_id=session_id)
    
    return []
