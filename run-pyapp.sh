#!/bin/bash

set -ex

WORKDIR="./pyapp"
cd $WORKDIR

source ./.env

echo "script to execute python app crawler.py"


VENV="./.venv"
if [ ! -d $VENV ]; then
    echo "creating new virtualenv"
    python -m venv $VENV
    source ./.venv/bin/activate
    pip install -r ./setup/requirements.txt
else
    echo "reusing existing virtualenv"
    source ./.venv/bin/activate
fi

cp ./setup/config.yaml ./config/
# not required for sqlite3
sed -i "s/MYSQL_HOST/$MYSQL_HOST/g" ./config/config.yaml
sed -i "s/MYSQL_PORT/$MYSQL_PORT/g" ./config/config.yaml
sed -i "s/MYSQL_USER/$MYSQL_USER/g" ./config/config.yaml
sed -i "s/MYSQL_PASSWORD/$MYSQL_PASSWORD/g" ./config/config.yaml
sed -i "s/MYSQL_DATABASE/$MYSQL_DATABASE/g" ./config/config.yaml

mkdir -p /var/log/mysql-docker/pyapp

python ./src/crawler.py foo=bar config=./config/config.yaml test=true

deactivate

echo "finished executing python script crawler.py"
