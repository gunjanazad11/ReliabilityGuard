import pandas as pd

from data_validator import validate_market_data


def test_valid_market_data_passes():
    """Clean market data should pass all validation checks."""

    data = pd.DataFrame(
        {
            "timestamp": [
                "2026-07-26 10:00:00",
                "2026-07-26 10:05:00"
            ],
            "symbol": ["AAPL", "AAPL"],
            "price": [190.00, 192.00],
            "volume": [1000, 1200]
        }
    )

    normalized_data, issues, summary = validate_market_data(
        data,
        stale_minutes=15,
        price_change_threshold=20
    )

    assert len(normalized_data) == 2
    assert issues.empty
    assert summary["rows_checked"] == 2
    assert summary["issues_found"] == 0
    assert summary["status"] == "PASSED"


def test_missing_required_column_is_detected():
    """The validator should detect a missing required column."""

    data = pd.DataFrame(
        {
            "timestamp": ["2026-07-26 10:00:00"],
            "symbol": ["AAPL"],
            "price": [190.00]
        }
    )

    _, issues, summary = validate_market_data(data)

    assert not issues.empty
    assert "Missing required column" in issues["Problem"].values
    assert "Market Data / volume" in issues[
        "Affected Component"
    ].values
    assert summary["status"] == "FAILED"


def test_duplicate_rows_are_detected():
    """Both copies of an exact duplicate should be marked."""

    data = pd.DataFrame(
        {
            "timestamp": [
                "2026-07-26 10:00:00",
                "2026-07-26 10:00:00"
            ],
            "symbol": ["MSFT", "MSFT"],
            "price": [430.00, 430.00],
            "volume": [900, 900]
        }
    )

    _, issues, _ = validate_market_data(data)

    duplicate_issues = issues[
        issues["Problem"] == "Duplicate row"
    ]

    assert len(duplicate_issues) == 2


def test_negative_price_is_detected():
    """Financial prices must not be negative."""

    data = pd.DataFrame(
        {
            "timestamp": ["2026-07-26 10:00:00"],
            "symbol": ["GOOGL"],
            "price": [-150.00],
            "volume": [700]
        }
    )

    _, issues, summary = validate_market_data(data)

    assert "Negative price" in issues["Problem"].values
    assert summary["status"] == "ISSUES FOUND"


def test_invalid_volume_values_are_detected():
    """Zero, negative and non-numeric volumes should be detected."""

    data = pd.DataFrame(
        {
            "timestamp": [
                "2026-07-26 10:00:00",
                "2026-07-26 10:01:00",
                "2026-07-26 10:02:00"
            ],
            "symbol": ["TSLA", "AMZN", "META"],
            "price": [320.00, 185.00, 210.00],
            "volume": [0, -20, "many"]
        }
    )

    _, issues, _ = validate_market_data(data)

    detected_problems = issues["Problem"].tolist()

    assert detected_problems.count(
        "Zero or negative volume"
    ) == 2

    assert "Incorrect data type" in detected_problems


def test_stale_timestamp_is_detected():
    """Old records should be marked as stale."""

    data = pd.DataFrame(
        {
            "timestamp": [
                "2026-07-26 09:00:00",
                "2026-07-26 10:00:00"
            ],
            "symbol": ["AAPL", "MSFT"],
            "price": [190.00, 430.00],
            "volume": [1000, 900]
        }
    )

    _, issues, _ = validate_market_data(
        data,
        stale_minutes=15
    )

    stale_issues = issues[
        issues["Problem"] == "Stale timestamp"
    ]

    assert len(stale_issues) == 1
    assert stale_issues.iloc[0]["Row"] == 2


def test_abnormal_price_change_is_detected():
    """A large price change for the same symbol should be flagged."""

    data = pd.DataFrame(
        {
            "timestamp": [
                "2026-07-26 10:00:00",
                "2026-07-26 10:05:00"
            ],
            "symbol": ["AAPL", "AAPL"],
            "price": [100.00, 150.00],
            "volume": [1000, 1100]
        }
    )

    _, issues, _ = validate_market_data(
        data,
        stale_minutes=15,
        price_change_threshold=20
    )

    abnormal_issues = issues[
        issues["Problem"]
        == "Sudden abnormal price change"
    ]

    assert len(abnormal_issues) == 1
    assert abnormal_issues.iloc[0]["Row"] == 3