#!/usr/bin/env python3

import os
import sys
import requests

from requests.packages.urllib3.util.connection import HAS_IPV6


def is_api_healthy(path):
    """
    Checks if API is healthy
    """
    address = "[::1]" if HAS_IPV6 else "127.0.0.1"
    url = f"http://{address}:24817{path}"
    print(f"Readiness probe: checking {url}")
    response = requests.get(url, allow_redirects=True)
    data = response.json()

    if not data["database_connection"]["connected"]:
        print("Readiness probe: database issue")
        sys.exit(3)

    if os.getenv("REDIS_SERVICE_HOST") and not data["redis_connection"]["connected"]:
        print("Readiness probe: cache issue")
        sys.exit(4)

    print("Readiness probe: ready!")
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

    print("Readiness probe: ready!")
    sys.exit(0)


"""
Get container type based on entrypoint.
Our entrypoint script is "exec'ing" (so no new process being created) the gunicorn process with the name of pulp "entity" (pulp-api, pulp-content, pulp-worker, pulp-resource-manager). Because of that, container's PID 1 will always be something like:
```
gunicorn: master \[pulp-{content,api,worker,resource-manager}\]
```
"""
def pulp_type():
    f = open("/proc/1/cmdline", "r")
    p_type = f.readline().split(" ")[2].strip("\x00")
    f.close()
    return p_type

if pulp_type() == "[pulp-api]":
    is_api_healthy(sys.argv[1])

elif pulp_type() == "[pulp-content]":
    is_content_healthy(sys.argv[1])
