from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names so the rest of the application
    can work with predictable names.
    """

    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    return df


def load_csv(csv_path: str | Path) -> pd.DataFrame:
    """
    Load and normalize a CSV file.
    """

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    if df.empty:
        raise ValueError("CSV file is empty.")

    df = normalize_columns(df)

    return df


def save_to_database(
    df: pd.DataFrame,
    database_url: str,
    table_name: str = "tickets",
) -> int:
    """
    Store the dataframe in SQLite.
    """

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )

    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False,
    )

    return len(df)