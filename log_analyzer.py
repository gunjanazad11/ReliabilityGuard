import re

import pandas as pd


KEYWORD_RULES = {
    "CONNECTION REFUSED": "Critical",
    "FAILED": "High",
    "ERROR": "High",
    "TIMEOUT": "High",
    "WARNING": "Medium"
}

SEVERITY_RANK = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4
}


def load_log_file(source):
    """
    Read a log file from either a file path
    or a Streamlit uploaded file.
    """

    if hasattr(source, "getvalue"):
        file_content = source.getvalue()

        if isinstance(file_content, bytes):
            return file_content.decode("utf-8")

        return str(file_content)

    with open(source, "r", encoding="utf-8") as log_file:
        return log_file.read()


def extract_timestamp(log_line):
    """Extract a timestamp from the beginning of a log line."""

    timestamp_pattern = (
        r"^(\d{4}-\d{2}-\d{2} "
        r"\d{2}:\d{2}:\d{2})"
    )

    match = re.search(timestamp_pattern, log_line)

    if match:
        return match.group(1)

    return "Not available"


def extract_component(log_line):
    """
    Extract a component written inside square brackets.

    Example:
        [DATABASE] becomes DATABASE
    """

    match = re.search(r"\[([A-Za-z0-9 _-]+)\]", log_line)

    if match:
        return match.group(1).strip()

    return "Unknown"


def get_highest_severity(matched_keywords):
    """Return the most serious severity from the matched keywords."""

    severities = [
        KEYWORD_RULES[keyword]
        for keyword in matched_keywords
    ]

    return max(
        severities,
        key=lambda severity: SEVERITY_RANK[severity]
    )


def analyze_log(log_text):
    """
    Analyse log text and return detected incidents,
    keyword counts and an overall summary.
    """

    incidents = []

    keyword_counts = {
        keyword: 0
        for keyword in KEYWORD_RULES
    }

    log_lines = log_text.splitlines()

    for line_number, log_line in enumerate(log_lines, start=1):
        uppercase_line = log_line.upper()

        matched_keywords = [
            keyword
            for keyword in KEYWORD_RULES
            if keyword in uppercase_line
        ]

        if not matched_keywords:
            continue

        for keyword in matched_keywords:
            keyword_counts[keyword] += 1

        severity = get_highest_severity(matched_keywords)

        incidents.append(
            {
                "Line": line_number,
                "Date and Time": extract_timestamp(log_line),
                "Detected Problem": ", ".join(matched_keywords),
                "Severity": severity,
                "Affected Component": extract_component(log_line),
                "Log Message": log_line.strip()
            }
        )

    incident_table = pd.DataFrame(
        incidents,
        columns=[
            "Line",
            "Date and Time",
            "Detected Problem",
            "Severity",
            "Affected Component",
            "Log Message"
        ]
    )

    keyword_table = pd.DataFrame(
        [
            {
                "Indicator": keyword,
                "Occurrences": count
            }
            for keyword, count in keyword_counts.items()
        ]
    )

    detected_matches = sum(keyword_counts.values())

    if incident_table.empty:
        highest_severity = "None"
        status = "HEALTHY"
    else:
        highest_severity = max(
            incident_table["Severity"],
            key=lambda severity: SEVERITY_RANK[severity]
        )
        status = "ATTENTION REQUIRED"

    summary = {
        "total_lines": len(log_lines),
        "flagged_lines": len(incident_table),
        "indicator_matches": detected_matches,
        "highest_severity": highest_severity,
        "status": status
    }

    return incident_table, keyword_table, summary