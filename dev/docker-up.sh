#!/bin/bash
FILE=$1

if [[ $# -ne 1 ]]; then
    echo "You must include an argument, e.g., 'docker-compose-w-db.yml', 'docker-compose.yml', etc."
    exit 2
fi

#rm -rf dist/ build/ ds_infra.egg-info/
# modified one line of code below so that /dist won't be removed (it's needed in Dockerfile. If removed, an error will occur: 'ERROR [stage-0  3/10] COPY dist /dist')
rm -rf dev/dist
rm -rf build/ ds_infra.egg-info/
python3 -m ensurepip --upgrade
python3 setup.py sdist bdist_wheel
docker system prune -f --volumes
docker-compose -f $FILE up --build
