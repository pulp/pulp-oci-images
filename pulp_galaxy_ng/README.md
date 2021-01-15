# Galaxy

For loading the initial data:
```bash
$ DATA_FIXTURE_URL="https://raw.githubusercontent.com/ansible/galaxy_ng/master/dev/automation-hub/initial_data.json"
$ curl $DATA_FIXTURE_URL | <docker | podman> exec -i pulp bash -c "cat > /tmp/initial_data.json"
$ <docker | podman> exec pulp bash -c "/usr/local/bin/pulpcore-manager loaddata /tmp/initial_data.json"
```
