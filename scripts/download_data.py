"""
Download Lending Club dataset from Kaggle
"""
import os
import sys
from pathlib import Path
import requests
import zipfile
from typing import Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


def download_file(url: str, dest_path: Path, chunk_size: int = 8192) -> None:
    """Download file with progress indication"""
    print(f"Downloading from {url}...")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(dest_path, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rProgress: {percent:.1f}%", end='')
    
    print(f"\n✓ Downloaded to {dest_path}")


def extract_zip(zip_path: Path, extract_dir: Path) -> None:
    """Extract ZIP file"""
    print(f"Extracting {zip_path.name}...")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    print(f"✓ Extracted to {extract_dir}")


def download_lending_club_data(
    sample_size: Optional[int] = 100000,
    output_dir: Optional[Path] = None
) -> Path:
    """
    Download Lending Club dataset
    
    For this demo, we'll use a sample dataset.
    In production, you would use the full Kaggle dataset with API key.
    
    Args:
        sample_size: Number of rows to download (None for full dataset)
        output_dir: Directory to save data (default: data/raw)
        
    Returns:
        Path to the downloaded CSV file
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data" / "raw"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Lending Club Dataset Download")
    print("=" * 60)
    
    # NOTE: For the actual dataset, you need Kaggle API credentials
    # Install: pip install kaggle
    # Setup: https://github.com/Kaggle/kaggle-api#api-credentials
    
    print("\n⚠️  IMPORTANT: Dataset Download Instructions")
    print("-" * 60)
    print("This script requires manual dataset download.")
    print("\nOption 1: Download from Kaggle (Recommended)")
    print("  1. Go to: https://www.kaggle.com/datasets/wordsforthewise/lending-club")
    print("  2. Click 'Download' button")
    print(f"  3. Extract to: {output_dir}")
    print("  4. Ensure file is named: accepted_2007_to_2018Q4.csv")
    
    print("\nOption 2: Use sample data (Quick start)")
    print("  We'll create a sample dataset for testing")
    
    choice = input("\nCreate sample dataset for testing? (y/n): ").strip().lower()
    
    if choice == 'y':
        sample_path = output_dir / "lending_club_sample.csv"
        create_sample_data(sample_path, sample_size)
        return sample_path
    else:
        print("\n✓ Please download the dataset manually and run again.")
        print(f"  Expected location: {output_dir / 'accepted_2007_to_2018Q4.csv'}")
        sys.exit(1)


def create_sample_data(output_path: Path, num_rows: int = 100000):
    """Create sample dataset for testing"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    print(f"\nCreating sample dataset with {num_rows} rows...")
    
    np.random.seed(42)
    
    # Generate synthetic data
    data = {
        'loan_id': [f'LOAN{i:08d}' for i in range(num_rows)],
        'member_id': [f'MEM{i:08d}' for i in range(num_rows)],
        'loan_amnt': np.random.choice([5000, 10000, 15000, 20000, 25000, 30000, 35000], num_rows),
        'funded_amnt': None,  # Will fill based on loan_amnt
        'term': np.random.choice(['36 months', '60 months'], num_rows, p=[0.7, 0.3]),
        'int_rate': np.random.uniform(5, 25, num_rows).round(2),
        'grade': np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G'], num_rows, p=[0.15, 0.25, 0.25, 0.20, 0.10, 0.03, 0.02]),
        'sub_grade': None,  # Will generate from grade
        'emp_length': np.random.choice(['< 1 year', '1 year', '2 years', '3 years', '5 years', '10+ years'], num_rows),
        'home_ownership': np.random.choice(['RENT', 'MORTGAGE', 'OWN'], num_rows, p=[0.4, 0.45, 0.15]),
        'annual_inc': np.random.lognormal(10.8, 0.7, num_rows).round(2),
        'loan_status': np.random.choice(
            ['Fully Paid', 'Current', 'Charged Off', 'Default', 'Late (31-120 days)'],
            num_rows,
            p=[0.5, 0.3, 0.12, 0.05, 0.03]
        ),
        'purpose': np.random.choice(
            ['debt_consolidation', 'credit_card', 'home_improvement', 'other', 'major_purchase', 'small_business'],
            num_rows,
            p=[0.4, 0.2, 0.15, 0.1, 0.1, 0.05]
        ),
        'addr_state': np.random.choice(['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH'], num_rows),
        'dti': np.random.uniform(0, 40, num_rows).round(2),
        'issue_d': None,  # Will generate dates
    }
    
    df = pd.DataFrame(data)
    
    # Fill derived fields
    df['funded_amnt'] = df['loan_amnt'] * np.random.uniform(0.95, 1.0, num_rows)
    df['sub_grade'] = df['grade'] + df['grade'].map(lambda x: str(np.random.randint(1, 6)))
    
    # Generate dates between 2015-2018
    start_date = datetime(2015, 1, 1)
    end_date = datetime(2018, 12, 31)
    date_range = (end_date - start_date).days
    df['issue_d'] = [start_date + timedelta(days=np.random.randint(0, date_range)) for _ in range(num_rows)]
    df['issue_d'] = df['issue_d'].dt.strftime('%Y-%m-%d')
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"✓ Sample data created: {output_path}")
    print(f"  Rows: {len(df):,}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  File size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    try:
        csv_path = download_lending_club_data(sample_size=100000)
        print(f"\n✓ Dataset ready: {csv_path}")
        print("\nNext step: Run 'python scripts/seed_database.py' to load data into PostgreSQL")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
