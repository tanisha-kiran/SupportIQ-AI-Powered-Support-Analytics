from app.services.anomaly_detector import detect_anomalies
from app.services.query_engine import get_summary
from app.services.sql_validator import validate_sql


def test_summary():
    summary = get_summary()

    assert summary["total_tickets"] == 500
    assert summary["unresolved_tickets"] == 173
    assert summary["critical_tickets"] == 55
    assert summary["unresolved_critical_tickets"] == 31


def test_anomaly_detection():
    anomalies = detect_anomalies()

    assert isinstance(anomalies, list)
    assert len(anomalies) == 101


def test_anomaly_types():
    anomalies = detect_anomalies()

    old_priority = [
        item
        for item in anomalies
        if item["anomaly_type"]
        == "old_high_priority_unresolved"
    ]

    long_resolution = [
        item
        for item in anomalies
        if item["anomaly_type"]
        == "abnormally_long_resolution"
    ]

    assert len(old_priority) == 80
    assert len(long_resolution) == 21


def test_sql_validator_accepts_select():
    sql = """
        SELECT COUNT(*) AS count
        FROM tickets
        WHERE priority = 'Critical'
    """

    result = validate_sql(sql)

    assert result.startswith("SELECT")


def test_sql_validator_rejects_delete():
    sql = "DELETE FROM tickets"

    try:
        validate_sql(sql)
        assert False, "DELETE should have been rejected"
    except ValueError:
        pass


def test_sql_validator_rejects_multiple_statements():
    sql = """
        SELECT * FROM tickets;
        DELETE FROM tickets
    """

    try:
        validate_sql(sql)
        assert False, "Multiple statements should be rejected"
    except ValueError:
        pass