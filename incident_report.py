from datetime import datetime
from pathlib import Path

import pandas as pd


def get_probable_cause(problem, component, log_message):
    """
    Suggest a probable cause based on detected keywords.

    These are rule-based suggestions, not confirmed root causes.
    """

    combined_text = (
        f"{problem} {component} {log_message}"
    ).upper()

    if "CONNECTION REFUSED" in combined_text:
        return (
            "The destination service may not be running, may not "
            "be listening on the requested port, or a firewall may "
            "be rejecting the connection."
        )

    if "TIMEOUT" in combined_text:
        return (
            "The service may be responding slowly because of network "
            "latency, system overload, packet loss or an unavailable "
            "dependent service."
        )

    if "DATABASE" in combined_text:
        return (
            "The database service may be unavailable, overloaded or "
            "using an invalid connection configuration."
        )

    if "DISK" in combined_text:
        return (
            "Disk usage may be high because of accumulated logs, "
            "temporary files, application data or insufficient storage."
        )

    if "CPU" in combined_text:
        return (
            "A process or workload may be consuming unusually high "
            "CPU resources."
        )

    if "MEMORY" in combined_text or "RAM" in combined_text:
        return (
            "One or more processes may be consuming excessive memory, "
            "or the system may not have enough available RAM."
        )

    if "AUTH" in combined_text:
        return (
            "The authentication service may be unavailable, or the "
            "request may contain invalid or expired credentials."
        )

    if "MARKET_FEED" in combined_text:
        return (
            "The simulated market-data source may be unavailable, "
            "delayed or unable to deliver records."
        )

    if "FAILED" in combined_text:
        return (
            "The operation did not complete successfully. A dependent "
            "service, invalid configuration or unavailable resource "
            "may have caused the failure."
        )

    if "ERROR" in combined_text:
        return (
            "An application or service error occurred and requires "
            "further inspection of nearby log entries."
        )

    if "WARNING" in combined_text:
        return (
            "A monitored value may have crossed its configured limit "
            "or the system may be approaching an unhealthy state."
        )

    return (
        "The available log entry does not provide enough information "
        "to identify a specific probable cause."
    )


def get_troubleshooting_action(problem, component, log_message):
    """Suggest a suitable troubleshooting action."""

    combined_text = (
        f"{problem} {component} {log_message}"
    ).upper()

    if "CONNECTION REFUSED" in combined_text:
        return (
            "Verify the hostname and port, confirm that the destination "
            "service is running, and inspect firewall rules."
        )

    if "TIMEOUT" in combined_text:
        return (
            "Check network connectivity and latency, inspect service "
            "load, retry the request and review dependent services."
        )

    if "DATABASE" in combined_text:
        return (
            "Check whether the database service is running, verify the "
            "connection string and credentials, and inspect database logs."
        )

    if "DISK" in combined_text:
        return (
            "Check disk usage, remove unnecessary temporary files, "
            "archive old logs and confirm that sufficient storage remains."
        )

    if "CPU" in combined_text:
        return (
            "Open the process monitor, identify high-CPU processes and "
            "inspect the workload before restarting or stopping anything."
        )

    if "MEMORY" in combined_text or "RAM" in combined_text:
        return (
            "Identify memory-intensive processes, check for memory leaks "
            "and restart only the affected service when appropriate."
        )

    if "AUTH" in combined_text:
        return (
            "Verify credentials or tokens, check the authentication "
            "service status and inspect related authentication logs."
        )

    if "MARKET_FEED" in combined_text:
        return (
            "Check the market-feed connection, validate the configured "
            "endpoint and confirm that new data is being received."
        )

    if "FAILED" in combined_text or "ERROR" in combined_text:
        return (
            "Review the surrounding log entries, reproduce the operation "
            "if safe, and verify all dependent services and configurations."
        )

    if "WARNING" in combined_text:
        return (
            "Review the affected metric, compare it with its configured "
            "threshold and continue monitoring for further changes."
        )

    return (
        "Collect additional logs and system metrics before performing "
        "further troubleshooting."
    )


def generate_incident_report(
    incident_table,
    source_name="Unknown log source"
):
    """Create a plain-text incident report."""

    generated_time = datetime.now().astimezone().strftime(
        "%Y-%m-%d %H:%M:%S %Z"
    )

    report_lines = [
        "=" * 72,
        "RELIABILITYGUARD INCIDENT REPORT",
        "=" * 72,
        f"Report generated: {generated_time}",
        f"Log source: {source_name}",
        "",
        "Important note:",
        (
            "This report contains rule-based probable-cause suggestions. "
            "It does not perform automatic or confirmed root-cause detection."
        ),
        "",
        f"Total detected incidents: {len(incident_table)}",
        "=" * 72,
        ""
    ]

    if incident_table.empty:
        report_lines.extend(
            [
                "No configured failure or warning indicators were detected.",
                "",
                "Overall Status: HEALTHY"
            ]
        )

        return "\n".join(report_lines)

    for incident_number, (_, incident) in enumerate(
        incident_table.iterrows(),
        start=1
    ):
        problem = str(incident["Detected Problem"])
        component = str(incident["Affected Component"])
        log_message = str(incident["Log Message"])

        probable_cause = get_probable_cause(
            problem,
            component,
            log_message
        )

        troubleshooting_action = get_troubleshooting_action(
            problem,
            component,
            log_message
        )

        report_lines.extend(
            [
                f"INCIDENT {incident_number}",
                "-" * 72,
                f"Date and time: {incident['Date and Time']}",
                f"Detected problem: {problem}",
                f"Severity: {incident['Severity']}",
                f"Affected component: {component}",
                f"Log line: {incident['Line']}",
                "",
                "Original log message:",
                log_message,
                "",
                "Probable-cause suggestion:",
                probable_cause,
                "",
                "Suggested troubleshooting action:",
                troubleshooting_action,
                "",
                "=" * 72,
                ""
            ]
        )

    report_lines.extend(
        [
            "Overall Status: ATTENTION REQUIRED",
            "",
            "End of report"
        ]
    )

    return "\n".join(report_lines)


def save_incident_report(
    report_text,
    output_path="reports/sample_incident_report.txt"
):
    """Save the generated report as a text file."""

    report_path = Path(output_path)

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    report_path.write_text(
        report_text,
        encoding="utf-8"
    )

    return str(report_path)