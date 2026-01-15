"""
SQLAlchemy models for the Executive Analytics Assistant
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Numeric, Date, DateTime, 
    Text, Boolean, JSON, Index, text
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Loan(Base):
    """Main loans table model"""
    __tablename__ = 'loans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Loan identifiers
    loan_id = Column(String(50), unique=True, index=True)
    member_id = Column(String(50))
    
    # Loan details
    loan_amnt = Column(Numeric(12, 2), nullable=False)
    funded_amnt = Column(Numeric(12, 2))
    funded_amnt_inv = Column(Numeric(12, 2))
    term = Column(String(20), nullable=False, index=True)
    int_rate = Column(Numeric(6, 3), nullable=False)
    installment = Column(Numeric(10, 2))
    
    # Grade and subgrade
    grade = Column(String(1), nullable=False, index=True)
    sub_grade = Column(String(2), nullable=False, index=True)
    
    # Borrower information
    emp_title = Column(String(200))
    emp_length = Column(String(20))
    home_ownership = Column(String(20), index=True)
    annual_inc = Column(Numeric(12, 2))
    verification_status = Column(String(50))
    
    # Loan status
    loan_status = Column(String(50), nullable=False, index=True)
    pymnt_plan = Column(String(10))
    purpose = Column(String(50), index=True)
    title = Column(String(200))
    
    # Geographic
    zip_code = Column(String(5))
    addr_state = Column(String(2), index=True)
    
    # Financial metrics
    dti = Column(Numeric(6, 3))
    delinq_2yrs = Column(Integer)
    earliest_cr_line = Column(Date)
    inq_last_6mths = Column(Integer)
    open_acc = Column(Integer)
    pub_rec = Column(Integer)
    revol_bal = Column(Numeric(12, 2))
    revol_util = Column(Numeric(6, 3))
    total_acc = Column(Integer)
    
    # Payment information
    out_prncp = Column(Numeric(12, 2))
    out_prncp_inv = Column(Numeric(12, 2))
    total_pymnt = Column(Numeric(12, 2))
    total_pymnt_inv = Column(Numeric(12, 2))
    total_rec_prncp = Column(Numeric(12, 2))
    total_rec_int = Column(Numeric(12, 2))
    total_rec_late_fee = Column(Numeric(10, 2))
    recoveries = Column(Numeric(12, 2))
    collection_recovery_fee = Column(Numeric(10, 2))
    last_pymnt_d = Column(Date)
    last_pymnt_amnt = Column(Numeric(12, 2))
    
    # Dates
    issue_d = Column(Date, nullable=False, index=True)
    next_pymnt_d = Column(Date)
    last_credit_pull_d = Column(Date)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite indexes
    __table_args__ = (
        Index('idx_loans_grade_status', 'grade', 'loan_status'),
        Index('idx_loans_issue_status', 'issue_d', 'loan_status'),
    )
    
    def __repr__(self):
        return f"<Loan(id={self.id}, loan_id={self.loan_id}, grade={self.grade}, status={self.loan_status})>"


class Conversation(Base):
    """Conversation history table"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True, server_default=text('uuid_generate_v4()'))
    user_query = Column(Text, nullable=False)
    sql_query = Column(Text)
    results = Column(JSON)
    chart_config = Column(JSON)
    insights = Column(ARRAY(Text))
    execution_time_ms = Column(Integer)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id={self.session_id}, query={self.user_query[:50]}...)>"


class QueryCache(Base):
    """Query cache table for performance optimization"""
    __tablename__ = 'query_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_hash = Column(String(64), unique=True, nullable=False, index=True)
    sql_query = Column(Text, nullable=False)
    results = Column(JSON, nullable=False)
    row_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow, index=True)
    access_count = Column(Integer, default=1)
    
    def __repr__(self):
        return f"<QueryCache(hash={self.query_hash[:16]}, accessed={self.access_count} times)>"


class UserSession(Base):
    """User session management"""
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, server_default=text('uuid_generate_v4()'))
    user_id = Column(String(100), index=True)
    context = Column(JSON)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<UserSession(session_id={self.session_id}, active={self.is_active})>"


class CustomerConnection(Base):
    """Customer database connections for multi-tenant support"""
    __tablename__ = 'customer_connections'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'))
    user_id = Column(UUID(as_uuid=True), index=True)  # FK to user when auth is added
    name = Column(String(200), nullable=False)
    db_type = Column(String(20), nullable=False)  # postgresql | mysql
    encrypted_url = Column(Text, nullable=False)  # Fernet encrypted DATABASE_URL
    ssl_mode = Column(String(20), nullable=False, default='prefer')  # require | prefer | disable
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CustomerConnection(id={self.id}, name={self.name}, db_type={self.db_type})>"


class TableConfig(Base):
    """Configuration for enabled tables in customer connections"""
    __tablename__ = 'table_configs'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'))
    connection_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # FK to customer_connections
    table_name = Column(String(200), nullable=False)
    schema_name = Column(String(200), nullable=False, default='public')
    columns = Column(JSON, nullable=False)  # [{name, type}]
    is_enabled = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_table_config_connection_enabled', 'connection_id', 'is_enabled'),
        Index('idx_table_config_unique', 'connection_id', 'schema_name', 'table_name', unique=True),
    )

    def __repr__(self):
        return f"<TableConfig(table={self.schema_name}.{self.table_name}, enabled={self.is_enabled})>"


class QueryUsage(Base):
    """Track query usage per connection for free tier limits"""
    __tablename__ = 'query_usage'

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'))
    connection_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # FK to customer_connections
    query_count = Column(Integer, nullable=False, default=0)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)  # 2024, 2025, etc
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_query_usage_unique', 'connection_id', 'year', 'month', unique=True),
    )

    def __repr__(self):
        return f"<QueryUsage(connection_id={self.connection_id}, count={self.query_count}, period={self.year}-{self.month:02d})>"
