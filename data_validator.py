import pandas as pd


REQUIRED_COLUMNS = ["timestamp", "symbol", "price", "volume"]


def load_market_data(source):
    """Read market data from a CSV file or uploaded file."""

    # Reset an uploaded file before reading it again.
    if hasattr(source, "seek"):
        source.seek(0)

    return pd.read_csv(source)


def validate_market_data(
    dataframe,
    stale_minutes=15,
    price_change_threshold=20
):
    """
    Validate financial market data.

    Returns:
        normalized_data: Data with converted timestamp and numeric columns.
        issue_table: Every validation problem detected.
        summary: Overall validation statistics.
    """

    issues = []

    # Work on a copy so the original DataFrame is not changed.
    data = dataframe.copy()

    # Make column names consistent.
    # Example: " Price " becomes "price".
    data.columns = [
        str(column).strip().lower()
        for column in data.columns
    ]

    def add_issue(row, problem, severity, component, details):
        """Add one detected problem to the issue list."""

        issues.append(
            {
                "Row": row,
                "Problem": problem,
                "Severity": severity,
                "Affected Component": component,
                "Details": details
            }
        )

    # -----------------------------------------------------
    # 1. CHECK REQUIRED COLUMNS
    # -----------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        for column in missing_columns:
            add_issue(
                row="File",
                problem="Missing required column",
                severity="Critical",
                component=f"Market Data / {column}",
                details=(
                    f"The CSV does not contain the required "
                    f"'{column}' column."
                )
            )

        issue_table = pd.DataFrame(issues)

        summary = {
            "rows_checked": len(data),
            "issues_found": len(issue_table),
            "rows_with_issues": 0,
            "status": "FAILED"
        }

        return data, issue_table, summary

    raw_data = data.copy()

    # -----------------------------------------------------
    # 2. CHECK MISSING VALUES
    # -----------------------------------------------------

    for column in REQUIRED_COLUMNS:
        missing_mask = (
            raw_data[column].isna()
            | raw_data[column].astype(str).str.strip().eq("")
        )

        for index in raw_data.index[missing_mask]:
            add_issue(
                row=int(index) + 2,
                problem="Missing value",
                severity="High",
                component=f"Market Data / {column}",
                details=f"The '{column}' value is missing."
            )

    # -----------------------------------------------------
    # 3. CHECK DUPLICATE ROWS
    # -----------------------------------------------------

    duplicate_mask = raw_data.duplicated(keep=False)

    for index in raw_data.index[duplicate_mask]:
        add_issue(
            row=int(index) + 2,
            problem="Duplicate row",
            severity="Medium",
            component="Market Data",
            details=(
                "This row is an exact duplicate of another row."
            )
        )

    # -----------------------------------------------------
    # 4. CONVERT DATA TYPES
    # -----------------------------------------------------

    timestamp_text = (
        raw_data["timestamp"]
        .astype(str)
        .str.strip()
    )

    price_text = (
        raw_data["price"]
        .astype(str)
        .str.strip()
    )

    volume_text = (
        raw_data["volume"]
        .astype(str)
        .str.strip()
    )

    parsed_timestamp = pd.to_datetime(
        raw_data["timestamp"],
        errors="coerce",
        utc=True
    )

    numeric_price = pd.to_numeric(
        raw_data["price"],
        errors="coerce"
    )

    numeric_volume = pd.to_numeric(
        raw_data["volume"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # 5. CHECK INCORRECT TIMESTAMP TYPE
    # -----------------------------------------------------

    invalid_timestamp_mask = (
        raw_data["timestamp"].notna()
        & timestamp_text.ne("")
        & parsed_timestamp.isna()
    )

    for index in raw_data.index[invalid_timestamp_mask]:
        add_issue(
            row=int(index) + 2,
            problem="Incorrect data type",
            severity="High",
            component="Market Data / timestamp",
            details=(
                "Timestamp could not be converted into a "
                "valid date and time."
            )
        )

    # -----------------------------------------------------
    # 6. CHECK INCORRECT PRICE TYPE
    # -----------------------------------------------------

    invalid_price_mask = (
        raw_data["price"].notna()
        & price_text.ne("")
        & numeric_price.isna()
    )

    for index in raw_data.index[invalid_price_mask]:
        add_issue(
            row=int(index) + 2,
            problem="Incorrect data type",
            severity="High",
            component="Market Data / price",
            details="Price must be a numeric value."
        )

    # -----------------------------------------------------
    # 7. CHECK INCORRECT VOLUME TYPE
    # -----------------------------------------------------

    invalid_volume_mask = (
        raw_data["volume"].notna()
        & volume_text.ne("")
        & numeric_volume.isna()
    )

    for index in raw_data.index[invalid_volume_mask]:
        add_issue(
            row=int(index) + 2,
            problem="Incorrect data type",
            severity="High",
            component="Market Data / volume",
            details="Volume must be a numeric value."
        )

    # -----------------------------------------------------
    # 8. CHECK NEGATIVE PRICES
    # -----------------------------------------------------

    negative_price_mask = numeric_price < 0

    for index in raw_data.index[negative_price_mask]:
        add_issue(
            row=int(index) + 2,
            problem="Negative price",
            severity="Critical",
            component="Market Data / price",
            details=(
                f"Price is {numeric_price.loc[index]}, "
                f"but price cannot be negative."
            )
        )

    # -----------------------------------------------------
    # 9. CHECK ZERO OR NEGATIVE VOLUME
    # -----------------------------------------------------

    invalid_volume_value_mask = numeric_volume <= 0

    for index in raw_data.index[invalid_volume_value_mask]:
        add_issue(
            row=int(index) + 2,
            problem="Zero or negative volume",
            severity="High",
            component="Market Data / volume",
            details=(
                f"Volume is {numeric_volume.loc[index]}, "
                f"but it must be greater than zero."
            )
        )

    # -----------------------------------------------------
    # 10. CHECK STALE TIMESTAMPS
    # -----------------------------------------------------

    latest_timestamp = parsed_timestamp.max()

    if pd.notna(latest_timestamp):
        stale_limit = latest_timestamp - pd.Timedelta(
            minutes=stale_minutes
        )

        stale_mask = (
            parsed_timestamp.notna()
            & (parsed_timestamp < stale_limit)
        )

        for index in raw_data.index[stale_mask]:
            add_issue(
                row=int(index) + 2,
                problem="Stale timestamp",
                severity="Medium",
                component="Market Data / timestamp",
                details=(
                    f"Timestamp is more than {stale_minutes} "
                    f"minutes older than the latest record."
                )
            )

    # -----------------------------------------------------
    # 11. CHECK SUDDEN PRICE CHANGES
    # -----------------------------------------------------

    price_change_data = pd.DataFrame(
        {
            "original_index": raw_data.index,
            "symbol": (
                raw_data["symbol"]
                .astype("string")
                .str.strip()
            ),
            "timestamp": parsed_timestamp,
            "price": numeric_price
        }
    )

    # Remove records that cannot be used for comparison.
    price_change_data = price_change_data[
        price_change_data["symbol"].notna()
        & price_change_data["symbol"].ne("")
        & price_change_data["timestamp"].notna()
        & price_change_data["price"].notna()
    ]

    # Sort records so every price is compared with the
    # previous price of the same symbol.
    price_change_data = price_change_data.sort_values(
        ["symbol", "timestamp", "original_index"]
    )

    price_change_data["previous_price"] = (
        price_change_data
        .groupby("symbol")["price"]
        .shift(1)
    )

    valid_previous_price = (
        price_change_data["previous_price"].notna()
        & price_change_data["previous_price"].ne(0)
    )

    price_change_data["change_percent"] = float("nan")

    price_change_data.loc[
        valid_previous_price,
        "change_percent"
    ] = (
        (
            price_change_data.loc[
                valid_previous_price,
                "price"
            ]
            - price_change_data.loc[
                valid_previous_price,
                "previous_price"
            ]
        )
        / price_change_data.loc[
            valid_previous_price,
            "previous_price"
        ].abs()
        * 100
    )

    abnormal_rows = price_change_data[
        price_change_data["change_percent"].abs()
        > price_change_threshold
    ]

    for _, record in abnormal_rows.iterrows():
        add_issue(
            row=int(record["original_index"]) + 2,
            problem="Sudden abnormal price change",
            severity="High",
            component=(
                f"Market Data / {record['symbol']}"
            ),
            details=(
                f"Price changed by approximately "
                f"{record['change_percent']:.2f}%, exceeding "
                f"the {price_change_threshold}% threshold."
            )
        )

    # -----------------------------------------------------
    # 12. CREATE NORMALIZED DATA
    # -----------------------------------------------------

    normalized_data = raw_data.copy()

    normalized_data["timestamp"] = parsed_timestamp
    normalized_data["price"] = numeric_price
    normalized_data["volume"] = numeric_volume

    issue_table = pd.DataFrame(
        issues,
        columns=[
            "Row",
            "Problem",
            "Severity",
            "Affected Component",
            "Details"
        ]
    )

    if issue_table.empty:
        numeric_issue_rows = set()
    else:
        numeric_issue_rows = {
            row
            for row in issue_table["Row"].tolist()
            if isinstance(row, int)
        }

    summary = {
        "rows_checked": len(raw_data),
        "issues_found": len(issue_table),
        "rows_with_issues": len(numeric_issue_rows),
        "status": (
            "PASSED"
            if issue_table.empty
            else "ISSUES FOUND"
        )
    }

    return normalized_data, issue_table, summary