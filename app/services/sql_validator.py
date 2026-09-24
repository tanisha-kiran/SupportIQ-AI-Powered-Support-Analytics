import re


FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "REPLACE",
    "VACUUM",
    "REINDEX",
}


def validate_sql(sql: str) -> str:
    if not sql or not sql.strip():
        raise ValueError("SQL query is empty.")

    cleaned = sql.strip()

    # Remove one trailing semicolon
    cleaned = cleaned.rstrip(";").strip()

    # Prevent multiple SQL statements
    if ";" in cleaned:
        raise ValueError(
            "Multiple SQL statements are not allowed."
        )

    normalized = re.sub(
        r"\s+",
        " ",
        cleaned.upper(),
    )

    # Only SELECT / WITH
    if not (
        normalized.startswith("SELECT ")
        or normalized.startswith("WITH ")
    ):
        raise ValueError(
            "Only SELECT/WITH queries are allowed."
        )

    # Block dangerous SQL keywords
    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{keyword}\b"

        if re.search(pattern, normalized):
            raise ValueError(
                f"Forbidden SQL keyword: {keyword}"
            )

    # Ensure the query references the tickets table
    if not re.search(
        r"\bFROM\s+TICKETS\b",
        normalized,
    ):
        raise ValueError(
            "Query must reference the tickets table."
        )

    # Block obvious attempts to access another table
    table_references = re.findall(
        r"\b(?:FROM|JOIN)\s+([A-Z_][A-Z0-9_]*)",
        normalized,
    )

    allowed_tables = {"TICKETS"}

    for table in table_references:
        if table not in allowed_tables:
            raise ValueError(
                f"Unauthorized table reference: {table}"
            )

    return cleaned