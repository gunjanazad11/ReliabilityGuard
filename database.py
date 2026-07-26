from datetime import datetime
from pathlib import Path
import sqlite3

import pandas as pd

from incident_report import (
    get_probable_cause,
    get_troubleshooting_action
)


DATABASE_PATH = Path("data/reliabilityguard.db")


def get_database_connection(database_path=DATABASE_PATH):
    """
    Open a connection to the SQLite database.

    The database file is created automatically if it
    does not already exist.
    """

    database_path = Path(database_path)

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(database_path)

    # Allows database rows to behave like dictionaries.
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database(database_path=DATABASE_PATH):
    """Create the incidents table if it does not exist."""

    create_table_query = """
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            log_line INTEGER,
            incident_time TEXT,
            detected_problem TEXT NOT NULL,
            severity TEXT NOT NULL,
            affected_component TEXT NOT NULL,
            probable_cause TEXT NOT NULL,
            troubleshooting_action TEXT NOT NULL,
            log_message TEXT NOT NULL,
            saved_at TEXT NOT NULL,

            UNIQUE (
                source_name,
                log_line,
                incident_time,
                detected_problem,
                log_message
            )
        )
    """

    create_severity_index = """
        CREATE INDEX IF NOT EXISTS idx_incidents_severity
        ON incidents (severity)
    """

    create_component_index = """
        CREATE INDEX IF NOT EXISTS idx_incidents_component
        ON incidents (affected_component)
    """

    with get_database_connection(database_path) as connection:
        connection.execute(create_table_query)
        connection.execute(create_severity_index)
        connection.execute(create_component_index)
        connection.commit()


def save_incidents_to_database(
    incident_table,
    source_name,
    database_path=DATABASE_PATH
):
    """
    Save detected incidents to SQLite.

    Duplicate incidents are ignored because of the
    UNIQUE database constraint.
    """

    if incident_table.empty:
        return 0

    insert_query = """
        INSERT OR IGNORE INTO incidents (
            source_name,
            log_line,
            incident_time,
            detected_problem,
            severity,
            affected_component,
            probable_cause,
            troubleshooting_action,
            log_message,
            saved_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    saved_at = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    inserted_count = 0

    with get_database_connection(database_path) as connection:
        for _, incident in incident_table.iterrows():
            problem = str(incident["Detected Problem"])
            component = str(incident["Affected Component"])
            log_message = str(incident["Log Message"])

            probable_cause = get_probable_cause(
                problem,
                component,
                log_message
            )

            troubleshooting_action = (
                get_troubleshooting_action(
                    problem,
                    component,
                    log_message
                )
            )

            cursor = connection.execute(
                insert_query,
                (
                    str(source_name),
                    int(incident["Line"]),
                    str(incident["Date and Time"]),
                    problem,
                    str(incident["Severity"]),
                    component,
                    probable_cause,
                    troubleshooting_action,
                    log_message,
                    saved_at
                )
            )

            if cursor.rowcount == 1:
                inserted_count += 1

        connection.commit()

    return inserted_count


def get_incident_history(
    severity=None,
    limit=200,
    database_path=DATABASE_PATH
):
    """Retrieve stored incidents from SQLite."""

    query = """
        SELECT
            id AS "Incident ID",
            source_name AS "Source",
            incident_time AS "Date and Time",
            detected_problem AS "Detected Problem",
            severity AS "Severity",
            affected_component AS "Affected Component",
            probable_cause AS "Probable-Cause Suggestion",
            troubleshooting_action AS "Suggested Action",
            log_message AS "Log Message",
            saved_at AS "Saved At"
        FROM incidents
    """

    parameters = []

    if severity:
        query += """
            WHERE severity = ?
        """

        parameters.append(severity)

    query += """
        ORDER BY id DESC
        LIMIT ?
    """

    parameters.append(int(limit))

    with get_database_connection(database_path) as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=parameters
        )


def get_incident_statistics(database_path=DATABASE_PATH):
    """Calculate incident statistics using an SQL query."""

    query = """
        SELECT
            COUNT(*) AS total_incidents,

            SUM(
                CASE
                    WHEN severity = 'Critical' THEN 1
                    ELSE 0
                END
            ) AS critical_incidents,

            SUM(
                CASE
                    WHEN severity = 'High' THEN 1
                    ELSE 0
                END
            ) AS high_incidents,

            SUM(
                CASE
                    WHEN severity = 'Medium' THEN 1
                    ELSE 0
                END
            ) AS medium_incidents,

            COUNT(
                DISTINCT affected_component
            ) AS affected_components
        FROM incidents
    """

    with get_database_connection(database_path) as connection:
        row = connection.execute(query).fetchone()

    return {
        "total_incidents": row["total_incidents"] or 0,
        "critical_incidents": row["critical_incidents"] or 0,
        "high_incidents": row["high_incidents"] or 0,
        "medium_incidents": row["medium_incidents"] or 0,
        "affected_components": row["affected_components"] or 0
    }