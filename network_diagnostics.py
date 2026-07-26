import platform
import socket
import subprocess
import time
from urllib.parse import urlparse


def clean_hostname(hostname):
    """
    Convert inputs such as https://www.google.com/search
    into a simple hostname such as www.google.com.
    """

    hostname = hostname.strip()

    if not hostname:
        return ""

    if "://" not in hostname:
        hostname = "http://" + hostname

    parsed_url = urlparse(hostname)

    return parsed_url.hostname or ""


def resolve_domain(hostname):
    """Resolve a domain name into an IP address."""

    try:
        start_time = time.perf_counter()

        ip_address = socket.gethostbyname(hostname)

        response_time = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        return {
            "success": True,
            "ip_address": ip_address,
            "response_time_ms": response_time,
            "message": "Domain resolved successfully."
        }

    except socket.gaierror:
        return {
            "success": False,
            "ip_address": None,
            "response_time_ms": None,
            "message": "Domain could not be resolved."
        }


def ping_host(hostname, timeout=3):
    """Send one ping request to the given hostname."""

    operating_system = platform.system().lower()

    if operating_system == "windows":
        command = [
            "ping",
            "-n",
            "1",
            "-w",
            str(timeout * 1000),
            hostname
        ]
    else:
        command = [
            "ping",
            "-c",
            "1",
            "-W",
            str(timeout),
            hostname
        ]

    try:
        start_time = time.perf_counter()

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout + 2
        )

        response_time = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        if result.returncode == 0:
            return {
                "success": True,
                "response_time_ms": response_time,
                "message": "Host responded to the ping request."
            }

        return {
            "success": False,
            "response_time_ms": response_time,
            "message": "Host did not respond to the ping request."
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "response_time_ms": None,
            "message": "Ping request timed out."
        }

    except FileNotFoundError:
        return {
            "success": False,
            "response_time_ms": None,
            "message": "Ping command is unavailable on this system."
        }


def check_port(hostname, port, timeout=3):
    """Check whether a TCP port is reachable."""

    try:
        start_time = time.perf_counter()

        with socket.create_connection(
            (hostname, port),
            timeout=timeout
        ):
            response_time = round(
                (time.perf_counter() - start_time) * 1000,
                2
            )

        return {
            "success": True,
            "response_time_ms": response_time,
            "message": f"Port {port} is reachable."
        }

    except socket.timeout:
        return {
            "success": False,
            "response_time_ms": None,
            "message": f"Connection to port {port} timed out."
        }

    except ConnectionRefusedError:
        return {
            "success": False,
            "response_time_ms": None,
            "message": f"Port {port} refused the connection."
        }

    except OSError:
        return {
            "success": False,
            "response_time_ms": None,
            "message": f"Port {port} is not reachable."
        }