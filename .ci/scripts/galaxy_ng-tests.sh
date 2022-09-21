#!/usr/bin/env bash
set -euo pipefail

SERVER="localhost"
WEB_PORT="8080"

pip3 install "ansible<2.13.2"

BASE_ADDR="http://$SERVER:$WEB_PORT"
echo $BASE_ADDR
echo "Base Address: $BASE_ADDR"
REPOS=( "published" "staging" "rejected" "community" "rh-certified" )
REPO_RESULTS=()

echo "Waiting ..."
sleep 10

TOKEN=$(curl --location --request POST "$BASE_ADDR/api/galaxy/v3/auth/token/" --header 'Authorization: Basic YWRtaW46cGFzc3dvcmQ=' --silent | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
echo $TOKEN

echo "Testing ..."

for repo in "${REPOS[@]}"
do
	# echo $repo
    COLLECTION_URL="$BASE_ADDR/api/galaxy/content/$repo/v3/collections/"
    # echo $COLLECTION_URL
    HTTP_CODE=$(curl --location --write-out "%{http_code}\n" -H "Authorization:Token $TOKEN" $COLLECTION_URL --silent --output /dev/null)
    # echo $HTTP_CODE
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
