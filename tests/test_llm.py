from app.services.sql_generator import SQLGenerator
from app.services.sql_validator import validate_sql


def test_critical_unresolved():
    generator = SQLGenerator()

    result = generator.generate(
        "How many critical tickets are unresolved?"
    )

    sql = validate_sql(result["sql"])

    normalized = sql.lower().replace(" ", "")

    assert "priority='critical'" in normalized
    assert "status!='resolved'" in normalized


def test_technical_unresolved():
    generator = SQLGenerator()

    result = generator.generate(
        "How many technical tickets are unresolved?"
    )

    sql = validate_sql(result["sql"])

    normalized = sql.lower().replace(" ", "")

    assert "category='technical'" in normalized
    assert "status!='resolved'" in normalized


def test_all_tickets():
    generator = SQLGenerator()

    result = generator.generate(
        "How many tickets are there?"
    )

    sql = validate_sql(result["sql"])

    normalized = sql.lower().replace(" ", "")

    assert "fromtickets" in normalized
    assert "count(" in normalized


def test_high_priority_open():
    generator = SQLGenerator()

    result = generator.generate(
        "How many high priority tickets are open?"
    )

    sql = validate_sql(result["sql"])

    normalized = sql.lower().replace(" ", "")

    assert "priority='high'" in normalized
    assert "status='open'" in normalized


def test_high_priority_unresolved():
    generator = SQLGenerator()

    result = generator.generate(
        "How many high priority tickets are unresolved?"
    )

    sql = validate_sql(result["sql"])

    normalized = sql.lower().replace(" ", "")

    assert "priority='high'" in normalized
    assert "status!='resolved'" in normalized


def test_escalated_critical():
    generator = SQLGenerator()

    result = generator.generate(
        "How many escalated critical tickets are there?"
    )

    sql = validate_sql(result["sql"])

    normalized = sql.lower().replace(" ", "")

    assert "priority='critical'" in normalized
    assert "status='escalated'" in normalized


def test_open_tickets():
    generator = SQLGenerator()

    result = generator.generate(
        "How many open tickets are there?"
    )

    sql = validate_sql(result["sql"])

    normalized = sql.lower().replace(" ", "")

    assert "status='open'" in normalized


def test_unresolved_tickets():
    generator = SQLGenerator()

    result = generator.generate(
        "How many unresolved tickets are there?"
    )

    sql = validate_sql(result["sql"])

    normalized = sql.lower().replace(" ", "")

    assert "status!='resolved'" in normalized