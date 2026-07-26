import os
import time
from datetime import timedelta

import psutil


def get_system_health():
    """Collect the current health information of the computer."""

    cpu_usage = psutil.cpu_percent(interval=0.5)
    ram_usage = psutil.virtual_memory().percent

    disk_path = os.path.abspath(os.sep)
    disk_usage = psutil.disk_usage(disk_path).percent

    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)
    uptime = str(timedelta(seconds=uptime_seconds))

    process_count = len(psutil.pids())

    return {
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage,
        "disk_usage": disk_usage,
        "uptime": uptime,
        "process_count": process_count,
    }


def get_system_warnings(system_data, threshold=80):
    """Generate warnings when CPU, RAM or disk usage crosses the threshold."""

    warnings = []

    if system_data["cpu_usage"] >= threshold:
        warnings.append(
            f"High CPU usage detected: {system_data['cpu_usage']}%"
        )

    if system_data["ram_usage"] >= threshold:
        warnings.append(
            f"High RAM usage detected: {system_data['ram_usage']}%"
        )

    if system_data["disk_usage"] >= threshold:
        warnings.append(
            f"High disk usage detected: {system_data['disk_usage']}%"
        )

    return warnings