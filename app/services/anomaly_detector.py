from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = f"sqlite:///{BASE_DIR / 'data' / 'tickets.db'}"


def load_tickets() -> pd.DataFrame:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

    df = pd.read_sql(
        "SELECT * FROM tickets",
        engine,
    )

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce",
    )

    return df


def detect_anomalies() -> list[dict]:

    df = load_tickets()

    anomalies = []

    # --------------------------------------------------
    # Rule 1:
    # High-priority unresolved tickets older than 24h
    # --------------------------------------------------

    cutoff = datetime.now() - timedelta(hours=24)

    old_unresolved = df[
        (
            df["priority"]
            .astype(str)
            .str.lower()
            .isin(["high", "critical"])
        )
        &
        (
            df["status"]
            .astype(str)
            .str.lower()
            != "resolved"
        )
        &
        (
            df["created_at"] < cutoff
        )
    ]

    for _, row in old_unresolved.iterrows():

        anomalies.append({
            "ticket_id": row["ticket_id"],
            "anomaly_type": "old_high_priority_unresolved",
            "severity": (
                "critical"
                if str(row["priority"]).lower() == "critical"
                else "high"
            ),
            "priority": row["priority"],
            "status": row["status"],
            "created_at": str(row["created_at"]),
            "description": (
                "High-priority ticket remains unresolved "
                "for more than 24 hours."
            ),
        })

    # --------------------------------------------------
    # Rule 2:
    # Abnormally long resolution time
    # IQR-based detection
    # --------------------------------------------------

    resolved_times = df[
        df["resolution_time_hrs"].notna()
    ]["resolution_time_hrs"]

    if len(resolved_times) >= 4:

        q1 = resolved_times.quantile(0.25)
        q3 = resolved_times.quantile(0.75)

        iqr = q3 - q1

        upper_bound = q3 + (1.5 * iqr)

        long_resolution = df[
            df["resolution_time_hrs"] > upper_bound
        ]

        for _, row in long_resolution.iterrows():

            anomalies.append({
                "ticket_id": row["ticket_id"],
                "anomaly_type": "abnormally_long_resolution",
                "severity": "medium",
                "resolution_time_hrs": row[
                    "resolution_time_hrs"
                ],
                "threshold_hrs": round(
                    float(upper_bound),
                    2,
                ),
                "description": (
                    "Resolution time is unusually high "
                    "relative to the dataset."
                ),
            })

    return anomalies