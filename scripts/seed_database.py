"""
Seed database with Lending Club data
"""
import os
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from tqdm import tqdm

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.models import Base
from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """Get database URL from environment"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://analyst:lending_secure_pass_2024@localhost:5432/lending_club"
    )


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare data for database insertion"""
    print("\nCleaning data...")
    
    # Convert dates
    date_columns = ['issue_d', 'earliest_cr_line', 'last_pymnt_d', 
                   'next_pymnt_d', 'last_credit_pull_d']
    
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Convert numeric columns
    numeric_columns = ['loan_amnt', 'funded_amnt', 'int_rate', 'installment',
                      'annual_inc', 'dti', 'revol_bal', 'revol_util']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove % from int_rate if present
    if 'int_rate' in df.columns and df['int_rate'].dtype == 'object':
        df['int_rate'] = df['int_rate'].str.rstrip('%').astype('float')
    
    # Fill NaN values
    df = df.fillna({
        'emp_length': 'Unknown',
        'emp_title': 'Not Provided',
        'dti': 0.0,
        'annual_inc': 0.0
    })
    
    print(f"✓ Data cleaned: {len(df)} rows")
    return df


def load_data_to_db(csv_path: Path, batch_size: int = 10000):
    """
    Load CSV data into PostgreSQL database
    
    Args:
        csv_path: Path to the CSV file
        batch_size: Number of rows to insert per batch
    """
    print("=" * 60)
    print("Database Seeding - Lending Club Dataset")
    print("=" * 60)
    
    # Connect to database
    database_url = get_database_url()
    print(f"\nConnecting to database...")
    engine = create_engine(database_url)
    
    # Test connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("\nMake sure Docker containers are running:")
        print("  docker-compose up -d")
        sys.exit(1)
    
    # Read CSV
    print(f"\nReading CSV: {csv_path}")
    if not csv_path.exists():
        print(f"✗ File not found: {csv_path}")
        print("\nRun 'python scripts/download_data.py' first")
        sys.exit(1)
    
    df = pd.read_csv(csv_path)
    print(f"✓ Loaded {len(df):,} rows with {len(df.columns)} columns")
    
    # Clean data
    df = clean_data(df)
    
    # Map columns to database schema
    column_mapping = {
        'id': 'loan_id',
        'member_id': 'member_id',
        'loan_amnt': 'loan_amnt',
        'funded_amnt': 'funded_amnt', 
        'funded_amnt_inv': 'funded_amnt_inv',
        'term': 'term',
        'int_rate': 'int_rate',
        'installment': 'installment',
        'grade': 'grade',
        'sub_grade': 'sub_grade',
        'emp_title': 'emp_title',
        'emp_length': 'emp_length',
        'home_ownership': 'home_ownership',
        'annual_inc': 'annual_inc',
        'verification_status': 'verification_status',
        'issue_d': 'issue_d',
        'loan_status': 'loan_status',
        'pymnt_plan': 'pymnt_plan',
        'purpose': 'purpose',
        'title': 'title',
        'zip_code': 'zip_code',
        'addr_state': 'addr_state',
        'dti': 'dti',
        'delinq_2yrs': 'delinq_2yrs',
        'earliest_cr_line': 'earliest_cr_line',
        'inq_last_6mths': 'inq_last_6mths',
        'open_acc': 'open_acc',
        'pub_rec': 'pub_rec',
        'revol_bal': 'revol_bal',
        'revol_util': 'revol_util',
        'total_acc': 'total_acc',
    }
    
    # Select and rename columns that exist
    available_cols = {k: v for k, v in column_mapping.items() if v in df.columns}
    df_db = df[list(available_cols.values())].rename(columns={v: k for k, v in available_cols.items()})
    
    # Clear existing data
    print("\nClearing existing loan data...")
    with engine.connect() as conn:
        # Delete sample data first
        conn.execute(text("DELETE FROM loans WHERE loan_id LIKE 'SAMPLE%'"))
        conn.commit()
    print("✓ Existing data cleared")
    
    # Insert data in batches
    print(f"\nInserting {len(df_db):,} rows in batches of {batch_size}...")
    
    total_inserted = 0
    with tqdm(total=len(df_db), desc="Inserting") as pbar:
        for i in range(0, len(df_db), batch_size):
            batch = df_db.iloc[i:i + batch_size]
            batch.to_sql('loans', engine, if_exists='append', index=False)
            total_inserted += len(batch)
            pbar.update(len(batch))
    
    print(f"\n✓ Successfully inserted {total_inserted:,} rows")
    
    # Verify data
    print("\nVerifying data...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM loans"))
        count = result.scalar()
        print(f"✓ Total rows in database: {count:,}")
        
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_loans,
                COUNT(DISTINCT grade) as unique_grades,
                COUNT(DISTINCT loan_status) as unique_statuses,
                AVG(loan_amnt) as avg_loan_amount,
                AVG(int_rate) as avg_interest_rate
            FROM loans
        """))
        stats = result.fetchone()
        
        print("\nDatabase Statistics:")
        print(f"  Total loans: {stats[0]:,}")
        print(f"  Unique grades: {stats[1]}")
        print(f"  Unique statuses: {stats[2]}")
        print(f"  Avg loan amount: ${stats[3]:,.2f}")
        print(f"  Avg interest rate: {stats[4]:.2f}%")
    
    print("\n" + "=" * 60)
    print("✓ Database seeding completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Start the API: uvicorn src.api.main:app --reload")
    print("  2. Start the frontend: streamlit run frontend/streamlit_app.py")


if __name__ == "__main__":
    # Find CSV file
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    
    # Look for downloaded file or sample file
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        print("✗ No CSV files found in data/raw/")
        print("\nRun 'python scripts/download_data.py' first")
        sys.exit(1)
    
    # Use the first CSV file found
    csv_path = csv_files[0]
    print(f"Using dataset: {csv_path.name}")
    
    try:
        load_data_to_db(csv_path)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
