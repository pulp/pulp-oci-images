#!/usr/bin/env python3

import os
import socket
import sys
import time

from requests.packages.urllib3.util.connection import HAS_IPV6

if __name__ == "__main__":

    postgres_is_alive = False
    family = socket.AF_INET6 if HAS_IPV6  else socket.AF_INET
    s = socket.socket(family, socket.SOCK_STREAM)
    tries = 0
    print("Waiting on postgresql to start...")
    while not postgres_is_alive and tries < 100:
        tries += 1
        pg_port = 5432
        try:
            env_port = os.environ.get("POSTGRES_SERVICE_PORT", "5432")
            pg_port = int(env_port)
        except ValueError:
            pass
        try:
            print("Checking postgres host %s" % os.environ["POSTGRES_SERVICE_HOST"])
            print("Checking postgres port %s" % os.environ["POSTGRES_SERVICE_PORT"])
            s.connect((os.environ["POSTGRES_SERVICE_HOST"], pg_port))
        except socket.error:
            time.sleep(3)
        else:
            postgres_is_alive = True

    if postgres_is_alive:
        print("Postgres started!")
        sys.exit(0)
    else:
        print("Unable to reach postgres on port %s" % os.environ["POSTGRES_SERVICE_PORT"])
        sys.exit(1)
