#!/bin/bash
set -euo pipefail

PLUGINS=(
  "pulpcore"
  "pulp_ansible"
  "pulp-certguard"
  "pulp_container"
  "pulp_deb"
  "pulp_file"
  "pulp_maven"
  "pulp_python"
  "pulp_rpm"
)

mkdir -p /pulp_home
cd /pulp_home

for plugin in ${PLUGINS[@]}; do
  if [[ ! -d "./${plugin}" ]]
  then
      git clone https://github.com/pulp/${plugin}.git
  fi
  echo "Installing ${plugin}..."
  pip install -e ./${plugin}
  pip install -r ./${plugin}/doc_requirements.txt
  echo "Building ${plugin} docs ..."
  cd ${plugin}/docs
  PULP_CONTENT_ORIGIN=localhost make PULP_URL="https://pulp.operate-first.cloud" diagrams html
  cd /pulp_home
  mkdir -p /docs/${plugin}/
  cp -r ./${plugin}/docs/_build/* /docs/${plugin}/
done
mkdir -p /usr/local/bin
cp /bin/pulp-content /usr/local/bin/pulp-content
cp /bin/pulpcore-manager /usr/local/bin/pulpcore-manager
cp /bin/pulpcore-worker /usr/local/bin/pulpcore-worker
