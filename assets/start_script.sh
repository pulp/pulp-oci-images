#!/bin/bash
debuginfod -R /var/lib/pulp -Z=cat $1 & /init
