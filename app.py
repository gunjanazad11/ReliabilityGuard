import pandas as pd
import streamlit as st

from data_validator import load_market_data, validate_market_data
from log_analyzer import analyze_log, load_log_file
from incident_report import (
    generate_incident_report,
    save_incident_report
)
from network_diagnostics import (
    check_port,
    clean_hostname,
    ping_host,
    resolve_domain
)
from system_monitor import get_system_health, get_system_warnings
from database import (
    get_incident_history,
    get_incident_statistics,
    initialize_database,
    save_incidents_to_database
)

st.set_page_config(
    page_title="ReliabilityGuard",
    page_icon="🛡️",
    layout="wide"
)

initialize_database()

st.title("🛡️ ReliabilityGuard")
st.subheader("Market Data and System Health Monitor")

st.write(
    """
    ReliabilityGuard monitors computer health, performs network diagnostics,
    validates financial data, analyses logs and generates probable-cause
    troubleshooting suggestions.
    """
)

(
    overview_tab,
    system_tab,
    network_tab,
    data_tab,
    log_tab,
    history_tab
) = st.tabs(
    [
        "🏠 Overview",
        "💻 System Health",
        "🌐 Network Diagnostics",
        "📈 Market Data Validation",
        "📋 Log Analysis",
        "🗄️ Incident History"
    ]
)

# ---------------------------------------------------------
# OVERVIEW TAB
# ---------------------------------------------------------

with overview_tab:
    st.header("Reliability Overview")

    st.write(
        """
        This dashboard combines live computer-health monitoring,
        network diagnostics, market-data validation, log analysis
        and SQLite-based incident tracking.
        """
    )

    overview_health = get_system_health()

    overview_warnings = get_system_warnings(
        overview_health,
        threshold=80
    )

    overview_statistics = get_incident_statistics()

    # -----------------------------------------------------
    # LIVE SYSTEM METRICS
    # -----------------------------------------------------

    st.subheader("Live System Snapshot")

    metric_column1, metric_column2, metric_column3 = st.columns(3)

    with metric_column1:
        st.metric(
            "CPU Usage",
            f"{overview_health['cpu_usage']}%"
        )

    with metric_column2:
        st.metric(
            "RAM Usage",
            f"{overview_health['ram_usage']}%"
        )

    with metric_column3:
        st.metric(
            "Disk Usage",
            f"{overview_health['disk_usage']}%"
        )

    metric_column4, metric_column5 = st.columns(2)

    with metric_column4:
        st.metric(
            "System Uptime",
            overview_health["uptime"]
        )

    with metric_column5:
        st.metric(
            "Running Processes",
            overview_health["process_count"]
        )

    if overview_warnings:
        st.warning(
            "One or more live system metrics have crossed "
            "the 80% overview threshold."
        )

        for warning in overview_warnings:
            st.write(f"• {warning}")

    else:
        st.success(
            "Live CPU, RAM and disk usage are currently "
            "below the 80% overview threshold."
        )

    st.divider()

    # -----------------------------------------------------
    # DATABASE INCIDENT SUMMARY
    # -----------------------------------------------------

    st.subheader("Stored Incident Summary")

    incident_column1, incident_column2, incident_column3 = st.columns(3)
    incident_column4, incident_column5 = st.columns(2)

    with incident_column1:
        st.metric(
            "Total Incidents",
            overview_statistics["total_incidents"]
        )

    with incident_column2:
        st.metric(
            "Critical Incidents",
            overview_statistics["critical_incidents"]
        )

    with incident_column3:
        st.metric(
            "High Incidents",
            overview_statistics["high_incidents"]
        )

    with incident_column4:
        st.metric(
            "Medium Incidents",
            overview_statistics["medium_incidents"]
        )

    with incident_column5:
        st.metric(
            "Affected Components",
            overview_statistics["affected_components"]
        )

    if overview_statistics["critical_incidents"] > 0:
        st.error(
            "The SQLite incident history contains one or more "
            "critical incidents. These are historical records "
            "and do not automatically mean the system is currently down."
        )

    elif overview_statistics["total_incidents"] > 0:
        st.warning(
            "Stored incident history is available for investigation."
        )

    else:
        st.info(
            "No incidents have been stored in the SQLite database yet."
        )

    st.divider()

    # -----------------------------------------------------
    # SEVERITY CHART
    # -----------------------------------------------------

    st.subheader("Incident Distribution by Severity")

    severity_chart_data = pd.DataFrame(
        {
            "Severity": [
                "Critical",
                "High",
                "Medium"
            ],
            "Incident Count": [
                overview_statistics["critical_incidents"],
                overview_statistics["high_incidents"],
                overview_statistics["medium_incidents"]
            ]
        }
    )

    severity_chart_data = severity_chart_data.set_index(
        "Severity"
    )

    st.bar_chart(
        severity_chart_data
    )

    st.caption(
        "The chart uses incidents currently stored in "
        "data/reliabilityguard.db."
    )

    st.divider()

    # -----------------------------------------------------
    # RECENT INCIDENTS
    # -----------------------------------------------------

    st.subheader("Most Recently Stored Incidents")

    recent_incidents = get_incident_history(
        severity=None,
        limit=5
    )

    if recent_incidents.empty:
        st.info(
            "No recent incidents are available. Analyse a log "
            "file and save the detected incidents first."
        )

    else:
        recent_columns = [
            "Incident ID",
            "Date and Time",
            "Detected Problem",
            "Severity",
            "Affected Component",
            "Source"
        ]

        st.dataframe(
            recent_incidents[recent_columns],
            width="stretch",
            hide_index=True
        )

    st.divider()

    # -----------------------------------------------------
    # PROJECT MODULES
    # -----------------------------------------------------

    st.subheader("ReliabilityGuard Modules")

    module_column1, module_column2 = st.columns(2)

    with module_column1:
        st.markdown(
            """
            **System Health**

            Monitors CPU, RAM, disk, uptime and running processes.

            **Network Diagnostics**

            Tests DNS resolution, ping response and TCP port reachability.

            **Market Data Validation**

            Detects missing, duplicate, invalid, stale and abnormal records.
            """
        )

    with module_column2:
        st.markdown(
            """
            **Log Analysis**

            Detects warnings, errors, failures, timeouts and refused connections.

            **Incident Reporting**

            Generates probable-cause suggestions and troubleshooting actions.

            **SQLite Incident History**

            Stores and retrieves previous incidents using relational queries.
            """
        )

    if st.button(
        "Refresh Overview",
        key="refresh_overview_button"
    ):
        st.rerun()


# ---------------------------------------------------------
# SYSTEM HEALTH TAB
# ---------------------------------------------------------

with system_tab:
    st.header("System Health Monitor")

    threshold = st.slider(
        "Warning threshold",
        min_value=50,
        max_value=100,
        value=80,
        step=5,
        help=(
            "A warning appears when CPU, RAM or disk usage "
            "reaches this percentage."
        )
    )

    system_data = get_system_health()
    warnings = get_system_warnings(system_data, threshold)

    column1, column2, column3 = st.columns(3)

    with column1:
        st.metric(
            label="CPU Usage",
            value=f"{system_data['cpu_usage']}%"
        )

    with column2:
        st.metric(
            label="RAM Usage",
            value=f"{system_data['ram_usage']}%"
        )

    with column3:
        st.metric(
            label="Disk Usage",
            value=f"{system_data['disk_usage']}%"
        )

    column4, column5 = st.columns(2)

    with column4:
        st.metric(
            label="System Uptime",
            value=system_data["uptime"]
        )

    with column5:
        st.metric(
            label="Running Processes",
            value=system_data["process_count"]
        )

    st.divider()
    st.subheader("System Status")

    if warnings:
        for warning in warnings:
            st.warning(warning)
    else:
        st.success(
            f"System is healthy. CPU, RAM and disk usage "
            f"are below {threshold}%."
        )

    if st.button("🔄 Refresh System Data"):
        st.rerun()


# ---------------------------------------------------------
# NETWORK DIAGNOSTICS TAB
# ---------------------------------------------------------

with network_tab:
    st.header("Network Diagnostics")

    st.write(
        """
        Enter a hostname and port to test DNS resolution,
        ping connectivity and port reachability.
        """
    )

    hostname_input = st.text_input(
        "Hostname or website",
        value="google.com",
        placeholder="Example: google.com"
    )

    port = st.number_input(
        "Port number",
        min_value=1,
        max_value=65535,
        value=443,
        step=1
    )

    st.caption(
        "Tip: Use port 443 for HTTPS websites and port 80 for HTTP websites."
    )

    if st.button("Run Network Diagnostics", type="primary"):
        hostname = clean_hostname(hostname_input)

        if not hostname:
            st.error("Please enter a valid hostname.")

        else:
            st.info(f"Testing: {hostname}:{port}")

            with st.spinner("Running network checks..."):
                dns_result = resolve_domain(hostname)
                ping_result = ping_host(hostname)
                port_result = check_port(hostname, int(port))

            st.divider()
            st.subheader("Diagnostic Results")

            dns_column, ping_column, port_column = st.columns(3)

            # DNS result
            with dns_column:
                st.markdown("### DNS Resolution")

                if dns_result["success"]:
                    st.success("Successful")
                    st.write(
                        f"**IP address:** "
                        f"{dns_result['ip_address']}"
                    )
                    st.write(
                        f"**Response time:** "
                        f"{dns_result['response_time_ms']} ms"
                    )
                else:
                    st.error("Failed")
                    st.write(dns_result["message"])

            # Ping result
            with ping_column:
                st.markdown("### Ping Test")

                if ping_result["success"]:
                    st.success("Successful")
                    st.write(ping_result["message"])
                    st.write(
                        f"**Approximate time:** "
                        f"{ping_result['response_time_ms']} ms"
                    )
                else:
                    st.error("Failed")
                    st.write(ping_result["message"])

                    if ping_result["response_time_ms"] is not None:
                        st.write(
                            f"**Attempt duration:** "
                            f"{ping_result['response_time_ms']} ms"
                        )

            # Port result
            with port_column:
                st.markdown("### Port Check")

                if port_result["success"]:
                    st.success("Reachable")
                    st.write(port_result["message"])
                    st.write(
                        f"**Connection time:** "
                        f"{port_result['response_time_ms']} ms"
                    )
                else:
                    st.error("Not reachable")
                    st.write(port_result["message"])

            st.divider()

            successful_checks = sum(
                [
                    dns_result["success"],
                    ping_result["success"],
                    port_result["success"]
                ]
            )

            if successful_checks == 3:
                st.success(
                    "All network diagnostic checks completed successfully."
                )

            elif successful_checks >= 1:
                st.warning(
                    f"{successful_checks} out of 3 network checks succeeded. "
                    "Review the failed checks."
                )

            else:
                st.error(
                    "All network checks failed. Verify the hostname, "
                    "internet connection and firewall settings."
                )

# ---------------------------------------------------------
# MARKET DATA VALIDATION TAB
# ---------------------------------------------------------

with data_tab:
    st.header("Financial Market Data Validation")

    st.write(
        """
        ReliabilityGuard checks simulated market data for
        missing information, duplicate records, invalid values,
        stale timestamps and abnormal price changes.
        """
    )

    uploaded_file = st.file_uploader(
        "Upload a market-data CSV",
        type=["csv"],
        help=(
            "Leave this empty to use the sample file stored "
            "inside the data folder."
        )
    )

    if uploaded_file is None:
        data_source = "data/market_data.csv"
        st.info(
            "Using the sample file: data/market_data.csv"
        )
    else:
        data_source = uploaded_file
        st.success(
            f"Uploaded file: {uploaded_file.name}"
        )

    try:
        market_data = load_market_data(data_source)

    except FileNotFoundError:
        st.error(
            "The sample CSV was not found. Check that "
            "data/market_data.csv exists."
        )
        market_data = None

    except pd.errors.EmptyDataError:
        st.error("The selected CSV file is empty.")
        market_data = None

    except pd.errors.ParserError:
        st.error(
            "The CSV structure is invalid and could not be read."
        )
        market_data = None

    except UnicodeDecodeError:
        st.error(
            "The CSV encoding could not be read. Save the file "
            "using UTF-8 encoding."
        )
        market_data = None

    if market_data is not None:
        st.subheader("Input Data")

        st.dataframe(
            market_data,
            width="stretch",
            hide_index=True
        )

        settings_column1, settings_column2 = st.columns(2)

        with settings_column1:
            stale_minutes = st.slider(
                "Stale timestamp limit",
                min_value=1,
                max_value=120,
                value=15,
                step=1,
                help=(
                    "Records older than this limit compared "
                    "with the latest timestamp are marked stale."
                )
            )

        with settings_column2:
            price_change_threshold = st.slider(
                "Abnormal price-change threshold",
                min_value=1,
                max_value=100,
                value=20,
                step=1,
                help=(
                    "Price changes above this percentage are "
                    "marked as potentially abnormal."
                )
            )

        if st.button(
            "Validate Market Data",
            type="primary"
        ):
            with st.spinner("Validating market data..."):
                (
                    normalized_data,
                    validation_issues,
                    validation_summary
                ) = validate_market_data(
                    market_data,
                    stale_minutes=stale_minutes,
                    price_change_threshold=(
                        price_change_threshold
                    )
                )

            st.divider()
            st.subheader("Validation Summary")

            summary_column1, summary_column2 = st.columns(2)
            summary_column3, summary_column4 = st.columns(2)

            with summary_column1:
                st.metric(
                    "Rows Checked",
                    validation_summary["rows_checked"]
                )

            with summary_column2:
                st.metric(
                    "Problems Found",
                    validation_summary["issues_found"]
                )

            with summary_column3:
                st.metric(
                    "Affected Rows",
                    validation_summary["rows_with_issues"]
                )

            with summary_column4:
                st.metric(
                    "Validation Status",
                    validation_summary["status"]
                )

            st.divider()

            if validation_issues.empty:
                st.success(
                    "The market data passed all validation checks."
                )

            else:
                st.warning(
                    f"ReliabilityGuard detected "
                    f"{len(validation_issues)} validation problems."
                )

                st.subheader("Detected Problems")

                st.dataframe(
                    validation_issues,
                    width="stretch",
                    hide_index=True
                )

                issues_csv = validation_issues.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    label="Download Validation Results",
                    data=issues_csv,
                    file_name="market_data_validation_results.csv",
                    mime="text/csv"
                )

            with st.expander(
                "View normalized data"
            ):
                st.caption(
                    "Invalid timestamps and numeric values "
                    "appear as missing values in this view."
                )

                st.dataframe(
                    normalized_data,
                    width="stretch",
                    hide_index=True
                )

# ---------------------------------------------------------
# LOG ANALYSIS TAB
# ---------------------------------------------------------

with log_tab:
    st.header("System Log Analysis")

    st.write(
        """
        ReliabilityGuard scans system logs for important
        failure indicators and highlights entries that may
        require investigation.
        """
    )

    uploaded_log = st.file_uploader(
        "Upload a log file",
        type=["log", "txt"],
        key="log_file_uploader",
        help=(
            "Leave this empty to analyse the sample log file "
            "stored inside the logs folder."
        )
    )

    if uploaded_log is None:
        log_source = "logs/sample_system.log"

        st.info(
            "Using the sample file: logs/sample_system.log"
        )
    else:
        log_source = uploaded_log

        st.success(
            f"Uploaded file: {uploaded_log.name}"
        )

    try:
        log_text = load_log_file(log_source)

    except FileNotFoundError:
        st.error(
            "The sample log file was not found. Check that "
            "logs/sample_system.log exists."
        )
        log_text = None

    except UnicodeDecodeError:
        st.error(
            "The log file could not be decoded. Save it using "
            "UTF-8 encoding and try again."
        )
        log_text = None

    except OSError as error:
        st.error(
            f"The log file could not be opened: {error}"
        )
        log_text = None

    if log_text is not None:
        with st.expander("View original log file"):
            st.code(log_text, language="text")

        if "log_analysis_results" not in st.session_state:
            st.session_state["log_analysis_results"] = None

        if st.button(
            "Analyse Log File",
            type="primary"
        ):
            with st.spinner("Scanning log entries..."):
                (
                    detected_incidents,
                    keyword_summary,
                    log_summary
                ) = analyze_log(log_text)

                if uploaded_log is None:
                    source_name = "logs/sample_system.log"
                else:
                    source_name = uploaded_log.name

                incident_report_text = generate_incident_report(
                    detected_incidents,
                    source_name=source_name
                )

                saved_report_path = save_incident_report(
                    incident_report_text,
                    "reports/sample_incident_report.txt"
                )

                st.session_state["log_analysis_results"] = {
                    "incidents": detected_incidents,
                    "keywords": keyword_summary,
                    "summary": log_summary,
                    "report": incident_report_text,
                    "report_path": saved_report_path,
                    "source_name": source_name
                }

        analysis_results = st.session_state[
            "log_analysis_results"
        ]

        if analysis_results is not None:
            detected_incidents = analysis_results["incidents"]
            keyword_summary = analysis_results["keywords"]
            log_summary = analysis_results["summary"]
            incident_report_text = analysis_results["report"]
            source_name = analysis_results["source_name"]

            st.divider()
            st.subheader("Log Analysis Summary")

            summary_column1, summary_column2 = st.columns(2)
            summary_column3, summary_column4 = st.columns(2)

            with summary_column1:
                st.metric(
                    "Total Log Lines",
                    log_summary["total_lines"]
                )

            with summary_column2:
                st.metric(
                    "Flagged Lines",
                    log_summary["flagged_lines"]
                )

            with summary_column3:
                st.metric(
                    "Indicator Matches",
                    log_summary["indicator_matches"]
                )

            with summary_column4:
                st.metric(
                    "Highest Severity",
                    log_summary["highest_severity"]
                )

            if detected_incidents.empty:
                st.success(
                    "No configured warning or failure indicators "
                    "were detected in the log file."
                )

            else:
                if log_summary["highest_severity"] == "Critical":
                    st.error(
                        "Critical log entries were detected. "
                        "Review the affected components."
                    )
                else:
                    st.warning(
                        "The log file contains entries that "
                        "require investigation."
                    )

                st.subheader("Detected Log Problems")

                st.dataframe(
                    detected_incidents,
                    width="stretch",
                    hide_index=True
                )

                incident_csv = detected_incidents.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    label="Download Log Analysis CSV",
                    data=incident_csv,
                    file_name="log_analysis_results.csv",
                    mime="text/csv"
                )

            st.subheader("Indicator Counts")

            st.dataframe(
                keyword_summary,
                width="stretch",
                hide_index=True
            )

            st.divider()
            st.subheader("Incident Report")

            st.info(
                "The report provides probable-cause suggestions, "
                "not confirmed automatic root-cause detection."
            )

            with st.expander(
                "Preview Incident Report",
                expanded=True
            ):
                st.code(
                    incident_report_text,
                    language="text"
                )

            st.download_button(
                label="Download Incident Report",
                data=incident_report_text,
                file_name="sample_incident_report.txt",
                mime="text/plain"
            )

            st.success(
                "A copy of the report was also saved to "
                "reports/sample_incident_report.txt"
            )
            st.divider()
            st.subheader("SQLite Incident Storage")

            if detected_incidents.empty:
                st.info(
                    "There are no detected incidents to save."
                )

            else:
                st.write(
                    """
                    Store these incidents in the local SQLite
                    database for historical analysis.
                    """
                )

                if st.button(
                    "Save Incidents to Database",
                    type="secondary",
                    key="save_incidents_database_button"
                ):
                    inserted_count = save_incidents_to_database(
                        detected_incidents,
                        source_name
                    )

                    if inserted_count > 0:
                        st.success(
                            f"{inserted_count} new incident(s) "
                            f"were saved to SQLite."
                        )

                    else:
                        st.info(
                            "These incidents are already stored. "
                            "No duplicate rows were added."
                        )

# ---------------------------------------------------------
# INCIDENT HISTORY TAB
# ---------------------------------------------------------

with history_tab:
    st.header("SQLite Incident History")

    st.write(
        """
        This section retrieves previously saved incidents from
        the local relational database. You can filter incidents
        by severity and download the stored history.
        """
    )

    statistics = get_incident_statistics()

    metric_column1, metric_column2, metric_column3 = st.columns(3)
    metric_column4, metric_column5 = st.columns(2)

    with metric_column1:
        st.metric(
            "Total Incidents",
            statistics["total_incidents"]
        )

    with metric_column2:
        st.metric(
            "Critical",
            statistics["critical_incidents"]
        )

    with metric_column3:
        st.metric(
            "High",
            statistics["high_incidents"]
        )

    with metric_column4:
        st.metric(
            "Medium",
            statistics["medium_incidents"]
        )

    with metric_column5:
        st.metric(
            "Affected Components",
            statistics["affected_components"]
        )

    st.divider()

    filter_column, limit_column = st.columns(2)

    with filter_column:
        selected_severity = st.selectbox(
            "Filter by severity",
            [
                "All",
                "Critical",
                "High",
                "Medium",
                "Low"
            ]
        )

    with limit_column:
        history_limit = st.number_input(
            "Maximum rows to display",
            min_value=1,
            max_value=1000,
            value=200,
            step=10
        )

    severity_filter = (
        None
        if selected_severity == "All"
        else selected_severity
    )

    incident_history = get_incident_history(
        severity=severity_filter,
        limit=int(history_limit)
    )

    st.subheader("Stored Incident Records")

    if incident_history.empty:
        st.info(
            "No incidents are currently stored for this filter. "
            "Analyse a log file and save its incidents first."
        )

    else:
        st.dataframe(
            incident_history,
            width="stretch",
            hide_index=True
        )

        history_csv = incident_history.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Incident History",
            data=history_csv,
            file_name="sqlite_incident_history.csv",
            mime="text/csv"
        )

    if st.button(
        "Refresh Incident History",
        key="refresh_incident_history"
    ):
        st.rerun()

    st.caption(
        "Database file: data/reliabilityguard.db"
    )