from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = f"sqlite:///{BASE_DIR / 'data' / 'tickets.db'}"


def get_engine():
    return create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )


def execute_query(sql: str) -> list[dict]:
    """
    Execute a read-only SQL query and return rows as dictionaries.
    """

    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text(sql))

        return [
            dict(row._mapping)
            for row in result
        ]


def get_summary() -> dict:
    """
    Return high-level statistics about the ticket dataset.
    """

    engine = get_engine()

    query = """
        SELECT
            COUNT(*) AS total_tickets,

            SUM(
                CASE
                    WHEN LOWER(status) != 'resolved'
                    THEN 1 ELSE 0
                END
            ) AS unresolved_tickets,

            SUM(
                CASE
                    WHEN LOWER(priority) = 'critical'
                    THEN 1 ELSE 0
                END
            ) AS critical_tickets,

            SUM(
                CASE
                    WHEN LOWER(priority) = 'critical'
                    AND LOWER(status) != 'resolved'
                    THEN 1 ELSE 0
                END
            ) AS unresolved_critical_tickets,

            AVG(customer_rating) AS average_customer_rating,

            AVG(resolution_time_hrs) AS average_resolution_time_hrs

        FROM tickets
    """

    with engine.connect() as connection:
        row = connection.execute(text(query)).fetchone()

        return dict(row._mapping)