#!/usr/bin/env python3

import os
import sys
import requests
import socket

from requests.packages.urllib3.util.connection import HAS_IPV6


def is_api_healthy(path):
    """
    Checks if API is healthy
    """
    address = "[::1]" if HAS_IPV6 else "127.0.0.1"
    url = f"http://{address}:24817{path}"
    print(f"Readiness probe checking {url}")
    response = requests.get(url, allow_redirects=True)
    data = response.json()

    if not data["database_connection"]["connected"]:
        sys.exit(3)

    if os.getenv("REDIS_SERVICE_HOST") and not data["redis_connection"]["connected"]:
        sys.exit(4)

    sys.exit(0)


def is_content_healthy(path):
    """
    Checks if Content is healthy
    """
    address = "[::1]" if HAS_IPV6 else "127.0.0.1"
    url = f"http://{address}:24816{path}"
    print(f"Readiness probe checking {url}")
    response = requests.head(url)
    response.raise_for_status()

    sys.exit(0)

if os.getenv("PULP_API_WORKERS"):
    is_api_healthy(sys.argv[1])

elif os.getenv("PULP_CONTENT_WORKERS"):
    is_content_healthy(sys.argv[1])
