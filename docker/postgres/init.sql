-- Executive Analytics Assistant - Database Schema
-- Lending Club Loans Analysis Database

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main loans table
CREATE TABLE IF NOT EXISTS loans (
    id SERIAL PRIMARY KEY,
    
    -- Loan identifiers
    loan_id VARCHAR(50) UNIQUE,
    member_id VARCHAR(50),
    
    -- Loan details
    loan_amnt DECIMAL(12, 2) NOT NULL,
    funded_amnt DECIMAL(12, 2),
    funded_amnt_inv DECIMAL(12, 2),
    term VARCHAR(20) NOT NULL,
    int_rate DECIMAL(6, 3) NOT NULL,
    installment DECIMAL(10, 2),
    
    -- Grade and subgrade
    grade VARCHAR(1) NOT NULL,
    sub_grade VARCHAR(2) NOT NULL,
    
    -- Borrower information
    emp_title VARCHAR(200),
    emp_length VARCHAR(20),
    home_ownership VARCHAR(20),
    annual_inc DECIMAL(12, 2),
    verification_status VARCHAR(50),
    
    -- Loan status
    loan_status VARCHAR(50) NOT NULL,
    pymnt_plan VARCHAR(10),
    purpose VARCHAR(50),
    title VARCHAR(200),
    
    -- Geographic
    zip_code VARCHAR(5),
    addr_state VARCHAR(2),
    
    -- Financial metrics
    dti DECIMAL(6, 3),
    delinq_2yrs INTEGER,
    earliest_cr_line DATE,
    inq_last_6mths INTEGER,
    open_acc INTEGER,
    pub_rec INTEGER,
    revol_bal DECIMAL(12, 2),
    revol_util DECIMAL(6, 3),
    total_acc INTEGER,
    
    -- Payment information
    out_prncp DECIMAL(12, 2),
    out_prncp_inv DECIMAL(12, 2),
    total_pymnt DECIMAL(12, 2),
    total_pymnt_inv DECIMAL(12, 2),
    total_rec_prncp DECIMAL(12, 2),
    total_rec_int DECIMAL(12, 2),
    total_rec_late_fee DECIMAL(10, 2),
    recoveries DECIMAL(12, 2),
    collection_recovery_fee DECIMAL(10, 2),
    last_pymnt_d DATE,
    last_pymnt_amnt DECIMAL(12, 2),
    
    -- Dates
    issue_d DATE NOT NULL,
    next_pymnt_d DATE,
    last_credit_pull_d DATE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(loan_status);
CREATE INDEX IF NOT EXISTS idx_loans_grade ON loans(grade);
CREATE INDEX IF NOT EXISTS idx_loans_sub_grade ON loans(sub_grade);
CREATE INDEX IF NOT EXISTS idx_loans_issue_date ON loans(issue_d);
CREATE INDEX IF NOT EXISTS idx_loans_purpose ON loans(purpose);
CREATE INDEX IF NOT EXISTS idx_loans_state ON loans(addr_state);
CREATE INDEX IF NOT EXISTS idx_loans_term ON loans(term);
CREATE INDEX IF NOT EXISTS idx_loans_home_ownership ON loans(home_ownership);

-- Composite indexes for common analysis queries
CREATE INDEX IF NOT EXISTS idx_loans_grade_status ON loans(grade, loan_status);
CREATE INDEX IF NOT EXISTS idx_loans_issue_status ON loans(issue_d, loan_status);

-- Table for conversation history
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL DEFAULT uuid_generate_v4(),
    user_query TEXT NOT NULL,
    sql_query TEXT,
    results JSONB,
    chart_config JSONB,
    insights TEXT[],
    execution_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at DESC);

-- Table for query cache
CREATE TABLE IF NOT EXISTS query_cache (
    id SERIAL PRIMARY KEY,
    query_hash VARCHAR(64) UNIQUE NOT NULL,
    sql_query TEXT NOT NULL,
    results JSONB NOT NULL,
    row_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_query_cache_hash ON query_cache(query_hash);
CREATE INDEX IF NOT EXISTS idx_query_cache_accessed ON query_cache(last_accessed DESC);

-- Table for user sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    session_id UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100),
    context JSONB,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_sessions_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON user_sessions(is_active, last_activity DESC);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for loans table
CREATE TRIGGER update_loans_updated_at 
    BEFORE UPDATE ON loans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- View for loan summary statistics
CREATE OR REPLACE VIEW loan_summary_stats AS
SELECT
    COUNT(*) as total_loans,
    SUM(loan_amnt) as total_loan_amount,
    AVG(loan_amnt) as avg_loan_amount,
    AVG(int_rate) as avg_interest_rate,
    COUNT(DISTINCT grade) as unique_grades,
    COUNT(DISTINCT addr_state) as unique_states,
    COUNT(CASE WHEN loan_status IN ('Default', 'Charged Off') THEN 1 END) as defaulted_loans,
    ROUND(COUNT(CASE WHEN loan_status IN ('Default', 'Charged Off') THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as default_rate_pct
FROM loans;

-- View for grade-level analysis
CREATE OR REPLACE VIEW loan_grade_analysis AS
SELECT
    grade,
    COUNT(*) as loan_count,
    SUM(loan_amnt) as total_amount,
    AVG(loan_amnt) as avg_amount,
    AVG(int_rate) as avg_interest_rate,
    COUNT(CASE WHEN loan_status IN ('Default', 'Charged Off') THEN 1 END) as defaulted,
    ROUND(COUNT(CASE WHEN loan_status IN ('Default', 'Charged Off') THEN 1 END)::NUMERIC / COUNT(*) * 100, 2) as default_rate_pct,
    AVG(dti) as avg_dti,
    AVG(annual_inc) as avg_annual_income
FROM loans
GROUP BY grade
ORDER BY grade;

-- View for monthly loan issuance trends
CREATE OR REPLACE VIEW monthly_loan_trends AS
SELECT
    DATE_TRUNC('month', issue_d) as month,
    COUNT(*) as loans_issued,
    SUM(loan_amnt) as total_amount,
    AVG(loan_amnt) as avg_amount,
    AVG(int_rate) as avg_rate
FROM loans
WHERE issue_d IS NOT NULL
GROUP BY DATE_TRUNC('month', issue_d)
ORDER BY month;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO analyst;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO analyst;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO analyst;

-- Insert sample data for testing (will be replaced by real data from seed script)
-- This ensures the database works even before loading the full dataset
INSERT INTO loans (
    loan_id, loan_amnt, term, int_rate, grade, sub_grade,
    emp_length, home_ownership, annual_inc, loan_status,
    purpose, addr_state, issue_d
) VALUES
    ('SAMPLE001', 10000.00, '36 months', 10.65, 'B', 'B3', '10+ years', 'RENT', 50000.00, 'Fully Paid', 'debt_consolidation', 'CA', '2018-01-01'),
    ('SAMPLE002', 15000.00, '60 months', 15.27, 'C', 'C4', '5-9 years', 'MORTGAGE', 75000.00, 'Current', 'credit_card', 'NY', '2018-06-15'),
    ('SAMPLE003', 8000.00, '36 months', 7.89, 'A', 'A4', '10+ years', 'OWN', 90000.00, 'Fully Paid', 'home_improvement', 'TX', '2017-12-01')
ON CONFLICT (loan_id) DO NOTHING;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Database schema initialized successfully';
    RAISE NOTICE 'Tables created: loans, conversations, query_cache, user_sessions';
    RAISE NOTICE 'Views created: loan_summary_stats, loan_grade_analysis, monthly_loan_trends';
    RAISE NOTICE 'Sample data inserted for testing';
END $$;
