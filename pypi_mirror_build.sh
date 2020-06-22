#!/bin/sh

set -eux

# Poll a Pulp task until it is finished.
wait_until_task_finished() {
    echo "Polling the task until it has reached a final state."
    local task_url=$1
    while true
    do
        local response="$(http --auth admin:password $task_url)"
        local state="$(echo "${response}" | jq -r .state)"
        case "${state}" in
            failed|canceled)
                echo "Task in final state: ${state}"
                exit 1
                ;;
            completed)
                echo "${task_url} complete."
                break
                ;;
            *)
                echo "Still waiting..."
                sleep 1
                ;;
        esac
    done
}

BASE_URL="http://localhost:8080"

buildah bud -f pypi_mirror/Containerfile -t pulp-ci-pypi-mirror-stage .

podman run --detach --publish 8080:80 --device /dev/fuse --name pulp-ci-pypi-mirror --volume ./settings:/etc/pulp pulp-ci-pypi-mirror-stage

_success=0
for i in $(seq 10); do
  sleep 5
  http "${BASE_URL}/pulp/api/v3/status/" || continue
  echo Success!
  _success=1
  break
done
[ $_success = 1 ]

podman exec pulp-ci-pypi-mirror bash -c 'pulpcore-manager reset-admin-password --password password'

REPO=$(http --auth admin:password POST "${BASE_URL}/pulp/api/v3/repositories/python/python/" name=pulp_ci_pypi_mirror | jq -r '.pulp_href')

REMOTE=$(http --auth admin:password POST "${BASE_URL}/pulp/api/v3/remotes/python/python/" name=pulp_ci_pypi_mirror url="https://pypi.org/" includes:=@./pypi_mirror/requirements.json | jq -r '.pulp_href')

TASK_URL=$(http --auth admin:password POST "${BASE_URL}${REPO}sync/" remote="${REMOTE}" mirror=False | jq -r '.task')
wait_until_task_finished "${BASE_URL}${TASK_URL}"
VERSION=$(http --auth admin:password "${BASE_URL}${TASK_URL}" | jq -r '.created_resources | first')

TASK_URL=$(http --auth admin:password POST "${BASE_URL}/pulp/api/v3/publications/python/pypi/" repository_version="${VERSION}" | jq -r '.task')
wait_until_task_finished "${BASE_URL}${TASK_URL}"
PUBLICATION=$(http --auth admin:password "${BASE_URL}${TASK_URL}" | jq -r '.created_resources | first')

TASK_URL=$(http --auth admin:password POST "${BASE_URL}/pulp/api/v3/distributions/python/pypi/" name=pulp_ci_pypi_mirror base_path=pypi publication="${PUBLICATION}" | jq -r '.task')
wait_until_task_finished "${BASE_URL}${TASK_URL}"
DISTRIBUTION=$(http --auth admin:password "${BASE_URL}${TASK_URL}" | jq -r '.created_resources | first')
echo "${DISTRIBUTION}"

podman stop pulp-ci-pypi-mirror

podman commit pulp-ci-pypi-mirror pulp-ci-pypi-mirror:latest

podman rm pulp-ci-pypi-mirror
