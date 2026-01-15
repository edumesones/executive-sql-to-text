"""
API routes for customer database connection management.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, delete as sql_delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import CustomerConnection, TableConfig, QueryUsage
from src.database.connection import get_db
from src.database.encryption import encrypt_credential, decrypt_credential
from src.database.introspection import get_adapter, detect_db_type, TableInfo


router = APIRouter(prefix="/api/connections", tags=["connections"])


# Request/Response Models
class CreateConnectionRequest(BaseModel):
    """Request to create a new connection."""
    name: str = Field(..., min_length=1, max_length=200, description="Connection name")
    database_url: str = Field(..., description="DATABASE_URL (postgresql:// or mysql://)")
    ssl_mode: str = Field(default="prefer", description="SSL mode: require, prefer, or disable")


class ConnectionResponse(BaseModel):
    """Connection details response."""
    id: str
    name: str
    db_type: str
    ssl_mode: str
    is_active: bool
    created_at: datetime
    table_count: int = 0
    enabled_table_count: int = 0


class ConnectionTestResponse(BaseModel):
    """Connection test result."""
    success: bool
    message: str
    version: Optional[str] = None


class TableInfoResponse(BaseModel):
    """Table information response."""
    schema_name: str
    table_name: str
    column_count: int
    is_enabled: bool


class UpdateTablesRequest(BaseModel):
    """Request to update enabled tables."""
    enabled_table_names: List[str] = Field(..., description="List of table names to enable (schema.table format)")


class QueryLimitResponse(BaseModel):
    """Query usage limit response."""
    queries_used: int
    queries_limit: int
    queries_remaining: int
    period: str  # "2024-01"


# Helper functions
async def get_query_usage(db: AsyncSession, connection_id: UUID) -> QueryUsage:
    """Get or create query usage for current month."""
    now = datetime.utcnow()
    month, year = now.month, now.year

    result = await db.execute(
        select(QueryUsage).where(
            and_(
                QueryUsage.connection_id == connection_id,
                QueryUsage.month == month,
                QueryUsage.year == year
            )
        )
    )
    usage = result.scalar_one_or_none()

    if not usage:
        usage = QueryUsage(
            connection_id=connection_id,
            query_count=0,
            month=month,
            year=year
        )
        db.add(usage)
        await db.commit()
        await db.refresh(usage)

    return usage


async def check_query_limit(db: AsyncSession, connection_id: UUID, limit: int = 30) -> bool:
    """
    Check if connection has queries remaining.

    Args:
        db: Database session
        connection_id: Connection UUID
        limit: Query limit (default 30 for free tier)

    Returns:
        True if queries remaining, False otherwise
    """
    usage = await get_query_usage(db, connection_id)
    return usage.query_count < limit


async def increment_query_count(db: AsyncSession, connection_id: UUID):
    """Increment query count for current month."""
    usage = await get_query_usage(db, connection_id)
    usage.query_count += 1
    await db.commit()


# API Endpoints
@router.post("/", response_model=ConnectionResponse)
async def create_connection(
    request: CreateConnectionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new database connection.

    - Validates DATABASE_URL format
    - Tests connection before saving
    - Encrypts credentials
    - Introspects schema automatically
    """
    try:
        # Validate SSL mode
        if request.ssl_mode not in ['require', 'prefer', 'disable']:
            raise HTTPException(status_code=400, detail="Invalid ssl_mode. Must be: require, prefer, or disable")

        # Detect database type
        db_type = detect_db_type(request.database_url)

        # Test connection first
        adapter = get_adapter(request.database_url)
        test_result = await adapter.test_connection(request.database_url)

        if not test_result.success:
            raise HTTPException(status_code=400, detail=f"Connection test failed: {test_result.message}")

        # Encrypt credentials
        encrypted_url = encrypt_credential(request.database_url)

        # Create connection record
        connection = CustomerConnection(
            name=request.name,
            db_type=db_type,
            encrypted_url=encrypted_url,
            ssl_mode=request.ssl_mode,
            is_active=True
        )
        db.add(connection)
        await db.commit()
        await db.refresh(connection)

        # Introspect schema in background
        try:
            tables = await adapter.introspect_schema(request.database_url)

            # Store table metadata
            for table in tables:
                table_config = TableConfig(
                    connection_id=connection.id,
                    table_name=table.table_name,
                    schema_name=table.schema_name,
                    columns=[{"name": col.name, "type": col.data_type} for col in table.columns],
                    is_enabled=False  # Disabled by default
                )
                db.add(table_config)

            await db.commit()

        except Exception as e:
            # Connection created but introspection failed - log but don't fail
            print(f"Warning: Schema introspection failed: {e}")

        return ConnectionResponse(
            id=str(connection.id),
            name=connection.name,
            db_type=connection.db_type,
            ssl_mode=connection.ssl_mode,
            is_active=connection.is_active,
            created_at=connection.created_at,
            table_count=len(tables) if 'tables' in locals() else 0,
            enabled_table_count=0
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create connection: {str(e)}")


@router.get("/", response_model=List[ConnectionResponse])
async def list_connections(db: AsyncSession = Depends(get_db)):
    """List all connections for the current user."""
    result = await db.execute(select(CustomerConnection).where(CustomerConnection.is_active == True))
    connections = result.scalars().all()

    response = []
    for conn in connections:
        # Count tables
        table_result = await db.execute(
            select(TableConfig).where(TableConfig.connection_id == conn.id)
        )
        tables = table_result.scalars().all()
        enabled_count = sum(1 for t in tables if t.is_enabled)

        response.append(ConnectionResponse(
            id=str(conn.id),
            name=conn.name,
            db_type=conn.db_type,
            ssl_mode=conn.ssl_mode,
            is_active=conn.is_active,
            created_at=conn.created_at,
            table_count=len(tables),
            enabled_table_count=enabled_count
        ))

    return response


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(connection_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get connection details by ID."""
    result = await db.execute(
        select(CustomerConnection).where(CustomerConnection.id == connection_id)
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Count tables
    table_result = await db.execute(
        select(TableConfig).where(TableConfig.connection_id == connection.id)
    )
    tables = table_result.scalars().all()
    enabled_count = sum(1 for t in tables if t.is_enabled)

    return ConnectionResponse(
        id=str(connection.id),
        name=connection.name,
        db_type=connection.db_type,
        ssl_mode=connection.ssl_mode,
        is_active=connection.is_active,
        created_at=connection.created_at,
        table_count=len(tables),
        enabled_table_count=enabled_count
    )


@router.delete("/{connection_id}")
async def delete_connection(connection_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a connection and all associated data."""
    # Check if connection exists
    result = await db.execute(
        select(CustomerConnection).where(CustomerConnection.id == connection_id)
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Delete associated tables
    await db.execute(sql_delete(TableConfig).where(TableConfig.connection_id == connection_id))

    # Delete usage records
    await db.execute(sql_delete(QueryUsage).where(QueryUsage.connection_id == connection_id))

    # Delete connection
    await db.execute(sql_delete(CustomerConnection).where(CustomerConnection.id == connection_id))

    await db.commit()

    return {"message": "Connection deleted successfully"}


@router.post("/{connection_id}/test", response_model=ConnectionTestResponse)
async def test_connection(connection_id: UUID, db: AsyncSession = Depends(get_db)):
    """Test an existing connection."""
    result = await db.execute(
        select(CustomerConnection).where(CustomerConnection.id == connection_id)
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Decrypt URL and test
    url = decrypt_credential(connection.encrypted_url)
    adapter = get_adapter(url)
    test_result = await adapter.test_connection(url)

    return ConnectionTestResponse(
        success=test_result.success,
        message=test_result.message,
        version=test_result.details.get('version') if test_result.details else None
    )


@router.get("/{connection_id}/tables", response_model=List[TableInfoResponse])
async def get_tables(connection_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get all tables for a connection."""
    # Check if connection exists
    result = await db.execute(
        select(CustomerConnection).where(CustomerConnection.id == connection_id)
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Get tables
    table_result = await db.execute(
        select(TableConfig).where(TableConfig.connection_id == connection_id)
    )
    tables = table_result.scalars().all()

    return [
        TableInfoResponse(
            schema_name=table.schema_name,
            table_name=table.table_name,
            column_count=len(table.columns),
            is_enabled=table.is_enabled
        )
        for table in tables
    ]


@router.patch("/{connection_id}/tables")
async def update_tables(
    connection_id: UUID,
    request: UpdateTablesRequest,
    db: AsyncSession = Depends(get_db)
):
    """Enable/disable tables for queries."""
    # Check if connection exists
    result = await db.execute(
        select(CustomerConnection).where(CustomerConnection.id == connection_id)
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Get all tables
    table_result = await db.execute(
        select(TableConfig).where(TableConfig.connection_id == connection_id)
    )
    tables = table_result.scalars().all()

    # Update enabled status
    updated = 0
    for table in tables:
        full_name = f"{table.schema_name}.{table.table_name}"
        should_enable = full_name in request.enabled_table_names or table.table_name in request.enabled_table_names

        if table.is_enabled != should_enable:
            table.is_enabled = should_enable
            updated += 1

    await db.commit()

    return {"message": f"Updated {updated} tables", "enabled_count": sum(1 for t in tables if t.is_enabled)}


@router.get("/{connection_id}/usage", response_model=QueryLimitResponse)
async def get_usage(connection_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get query usage for current month."""
    # Check if connection exists
    result = await db.execute(
        select(CustomerConnection).where(CustomerConnection.id == connection_id)
    )
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    usage = await get_query_usage(db, connection_id)

    return QueryLimitResponse(
        queries_used=usage.query_count,
        queries_limit=30,  # Free tier
        queries_remaining=max(0, 30 - usage.query_count),
        period=f"{usage.year}-{usage.month:02d}"
    )
