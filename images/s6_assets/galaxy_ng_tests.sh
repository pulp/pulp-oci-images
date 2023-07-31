#!/usr/bin/env bash
set -euo pipefail

SERVER="localhost"
WEB_PORT="8080"
scheme=${1:-http}

pip3 install "ansible<2.13.2"

BASE_ADDR="$scheme://$SERVER:$WEB_PORT"
echo "Base Address: $BASE_ADDR"
REPOS=( "published" "staging" "rejected" "community" "rh-certified" )
REPO_RESULTS=()

echo "Waiting ..."
sleep 10

TOKEN=$(curl --insecure --location --request POST "$BASE_ADDR/api/galaxy/v3/auth/token/" --header 'Authorization: Basic YWRtaW46cGFzc3dvcmQ=' --silent | jq -r .token)
echo $TOKEN

echo "Testing ..."

for repo in "${REPOS[@]}"
do
	  echo "Testing $repo"
    COLLECTION_URL="$BASE_ADDR/api/galaxy/v3/plugin/ansible/content/$repo/collections/"
    echo "Trying $COLLECTION_URL"
    HTTP_CODE=$(curl --insecure --location --write-out "%{http_code}\n" -H "Authorization:Token $TOKEN" $COLLECTION_URL --silent --output /dev/null)
    echo "Returned $HTTP_CODE"
    REPO_RESULTS+=($HTTP_CODE)
done

GALAXY_INIT_RESULT=0
ITER=0
for code in "${REPO_RESULTS[@]}"
do
    echo "${REPOS[$ITER]} $code"
    ITER=$((ITER + 1))
    if [[ $code != 200 ]]; then
        GALAXY_INIT_RESULT=$ITER
    fi
done

exit $GALAXY_INIT_RESULT
