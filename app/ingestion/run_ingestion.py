from pathlib import Path

from app.core.database import DATABASE_URL
from app.ingestion.csv_loader import load_csv, save_to_database


BASE_DIR = Path(__file__).resolve().parents[2]
CSV_PATH = BASE_DIR / "data" / "tickets.csv"


def main():
    print("=" * 60)
    print("DOTMAPPERS AI SYSTEM — DATA INGESTION")
    print("=" * 60)

    print(f"\nLoading: {CSV_PATH}")

    df = load_csv(CSV_PATH)

    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nMissing values:")
    print(df.isnull().sum())

    rows = save_to_database(
        df,
        DATABASE_URL,
    )

    print(f"\nSuccessfully stored {rows} rows in SQLite.")
    print(f"Database: {DATABASE_URL}")


if __name__ == "__main__":
    main()