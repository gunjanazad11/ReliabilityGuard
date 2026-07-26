# ReliabilityGuard

## Market Data and System Health Monitor

ReliabilityGuard is a Python and Streamlit-based reliability-monitoring application that combines computer-health monitoring, network diagnostics, simulated financial-data validation, system-log analysis, probable-cause suggestions, incident reporting and SQLite-based incident history.

The project demonstrates concepts relevant to financial-data platforms and site-reliability engineering, including data quality, Python programming, relational databases, operating-system monitoring, networking fundamentals, troubleshooting and service reliability.

> ReliabilityGuard provides rule-based probable-cause suggestions. It does not claim to perform confirmed or automatic root-cause detection.

---

## Dashboard Screenshots

### Reliability Overview

![ReliabilityGuard Overview](screenshots/01_overview.png)

### System Health Monitoring

![System Health](screenshots/02_system_health.png)

### Network Diagnostics

![Network Diagnostics](screenshots/03_network_diagnostics.png)

### Market Data Validation

![Market Data Validation](screenshots/04_market_data_validation.png)

### Log Analysis & Incident Report

![Log Analysis](screenshots/05_log_analysis_&_incident_report.png)


### SQLite Incident History

![Incident History](screenshots/06_incident_history.png)

### Automated Tests

![Pytest Results](screenshots/07_pytest_results.png)
 
---

## Project Motivation

Financial and infrastructure platforms depend on accurate data, healthy systems and reliable network services.

A financial-data error such as a missing price, duplicate record, stale timestamp or invalid volume can affect downstream processing and analysis. Similarly, high resource usage, service timeouts, unavailable ports and connection failures can reduce platform reliability.

ReliabilityGuard brings these checks into one beginner-friendly monitoring dashboard.

---

## Key Features

### System Health Monitoring

* CPU usage monitoring
* RAM usage monitoring
* Disk usage monitoring
* System uptime
* Running-process count
* Configurable warning threshold
* Manual metric refresh

### Network Diagnostics

* Hostname cleaning and validation
* Domain-to-IP resolution
* Ping connectivity testing
* TCP port-reachability testing
* Approximate response-time measurement
* Clear success and failure messages

### Financial Market-Data Validation

ReliabilityGuard validates CSV files containing:

```text
timestamp, symbol, price, volume
```

The validator detects:

* Missing values
* Missing required columns
* Duplicate rows
* Negative prices
* Zero or negative volume
* Incorrect data types
* Invalid timestamps
* Stale timestamps
* Sudden abnormal price changes

### Log Analysis

The log analyzer scans `.log` and `.txt` files for:

* `ERROR`
* `WARNING`
* `FAILED`
* `TIMEOUT`
* `CONNECTION REFUSED`

For every flagged log entry, the application extracts:

* Log line number
* Date and time
* Detected indicator
* Severity
* Affected component
* Original log message

### Incident Reporting

ReliabilityGuard generates a downloadable incident report containing:

* Date and time
* Detected problem
* Severity
* Affected component
* Original log message
* Probable-cause suggestion
* Suggested troubleshooting action

### SQLite Incident History

Detected incidents can be stored in a local SQLite database.

The database functionality includes:

* Relational incident table
* Primary key
* Unique constraint
* Duplicate prevention
* Parameterized SQL inserts
* Severity filtering
* Incident statistics
* Recent-incident display
* CSV export

### Automated Testing

Pytest tests verify:

* Valid market data passes validation
* Missing columns are detected
* Duplicate records are detected
* Negative prices are detected
* Invalid volumes are detected
* Stale timestamps are detected
* Abnormal price changes are detected

---

## Technology Stack

| Area                 | Technology         |
| -------------------- | ------------------ |
| Programming language | Python             |
| Dashboard            | Streamlit          |
| Data processing      | pandas             |
| System monitoring    | psutil             |
| Networking           | socket, subprocess |
| Database             | SQLite             |
| Testing              | pytest             |
| Version control      | Git and GitHub     |

---

## Project Structure

```text
ReliabilityGuard/
│
├── app.py
├── system_monitor.py
├── network_diagnostics.py
├── data_validator.py
├── log_analyzer.py
├── incident_report.py
├── database.py
│
├── data/
│   └── market_data.csv
│
├── logs/
│   └── sample_system.log
│
├── reports/
│   └── sample_incident_report.txt
│
├── tests/
│   └── test_data_validator.py
│
├── screenshots/
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Module Explanation

### `app.py`

Contains the Streamlit user interface and connects all project modules.

### `system_monitor.py`

Uses `psutil` to collect CPU, RAM, disk, uptime and process information.

### `network_diagnostics.py`

Performs DNS resolution, ping checks and TCP port-reachability tests.

### `data_validator.py`

Reads and validates simulated financial market data using pandas.

### `log_analyzer.py`

Scans system logs for configured warning and failure indicators.

### `incident_report.py`

Generates probable-cause suggestions, troubleshooting actions and text incident reports.

### `database.py`

Creates and manages the SQLite incident-history database.

### `tests/test_data_validator.py`

Contains automated Pytest tests for financial-data validation rules.

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd ReliabilityGuard
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux or macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

## Running the Application

Run:

```bash
python -m streamlit run app.py
```

Open the URL displayed in the terminal, normally:

```text
http://localhost:8501
```

---

## Running Automated Tests

Run:

```bash
python -m pytest -v
```

Expected result:

```text
7 passed
```

---

## Dashboard Modules

The Streamlit dashboard contains:

1. Overview
2. System Health
3. Network Diagnostics
4. Market Data Validation
5. Log Analysis
6. Incident History

---

## Sample Market-Data Format

```csv
timestamp,symbol,price,volume
2026-07-26 08:00:00,AAPL,190.50,1200
2026-07-26 08:01:00,MSFT,430.25,900
```

The included sample CSV deliberately contains invalid records to demonstrate the validator.

---

## Example Network Test

```text
Hostname: google.com
Port: 443
```

ReliabilityGuard performs:

* DNS resolution
* Ping test
* TCP port check
* Approximate response-time measurement

A failed ping does not necessarily mean that a website is unavailable because some servers block ping traffic while still accepting web connections.

---

## Example Incident

```text
Detected problem: CONNECTION REFUSED, ERROR
Severity: Critical
Affected component: NETWORK
```

Example probable-cause suggestion:

```text
The destination service may not be running, may not be listening
on the requested port, or a firewall may be rejecting the connection.
```

Example troubleshooting action:

```text
Verify the hostname and port, confirm that the destination service
is running, and inspect firewall rules.
```

---

## Data Reliability Approach

ReliabilityGuard follows a rule-based validation approach:

1. Verify the required CSV structure.
2. Detect missing and duplicate records.
3. Convert timestamps and numeric values safely.
4. detect invalid prices and volumes.
5. Compare timestamps to identify stale records.
6. Compare each symbol’s price with its previous valid price.
7. Record all detected problems in a structured table.

Abnormal price-change detection is a configurable data-quality rule. It does not classify a transaction as fraudulent.

---

## Database Design

The SQLite database stores:

* Incident ID
* Source log
* Log line number
* Incident timestamp
* Detected problem
* Severity
* Affected component
* Probable-cause suggestion
* Suggested troubleshooting action
* Original log message
* Database save time

A unique database constraint prevents the same incident from being stored repeatedly.

---

## Limitations

* Market data is simulated and does not use a live financial-data API.
* Ping availability depends on operating-system and firewall permissions.
* Some servers intentionally block ping requests.
* Approximate response times are diagnostic measurements, not professional network benchmarks.
* Log analysis uses configurable keyword rules rather than machine learning.
* Probable-cause suggestions are not confirmed root causes.
* System metrics represent the computer on which Streamlit is running.
* SQLite is suitable for this local project but would need to be replaced or scaled for a large distributed platform.

---

## Future Enhancements

* Live financial-data API integration
* Email or Slack incident alerts
* Historical system-health charts
* Continuous background monitoring
* Configurable log-analysis rules
* PostgreSQL or MySQL support
* User authentication
* Docker deployment
* REST API for external monitoring tools
* Machine-learning-based anomaly detection
* Exportable PDF incident reports
* Service dependency mapping
* Incident acknowledgement and resolution status

