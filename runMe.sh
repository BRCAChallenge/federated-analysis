#!/bin/bash

if [ $# -ne 2 ] 
then
	echo "usage: $0 <ensembl-release> <chr-list>"
	echo "example: $0 75 \"['chr13', 'chr17']\"" 
	exit 1
fi

ENSEMBL_RELEASE=$1
CHR_LIST=$2
FDA_PATH=$(pwd)
APP_PATH=${FDA_PATH}/app
CONF_PATH=${FDA_PATH}/config
DATA_PATH=${FDA_PATH}/data
DOCKER_IMAGE_NAME=brcachallenge/federated-analysis

if [ $(uname) == "Darwin" ]
then
	PREV_PERMS=$(stat -f "%OLp" ${DATA_PATH})
else
	PREV_PERMS=$(stat -c "%a" ${DATA_PATH})
fi

chmod 1777 ${DATA_PATH}

docker build -t ${DOCKER_IMAGE_NAME} .

docker run --rm -e PYTHONPATH=/ -e PYTHONIOENCODING=UTF-8 -w /home/myuser --user=1968:games -v ${APP_PATH}:/app:ro -v ${CONF_PATH}:/config -v "${DATA_PATH}":/data:rw ${DOCKER_IMAGE_NAME} /usr/bin/python3 /app/myCooccurrenceFinder.py  $ENSEMBL_RELEASE $CHR_LIST

#docker run --rm -e PYTHONPATH=/ -e PYTHONIOENCODING=UTF-8 -w / --user=`id -u`:`id -g` -v ${APP_PATH}:/app:ro -v ${CONF_PATH}:/config -v "${DATA_PATH}":/data ${DOCKER_IMAGE_NAME} /usr/bin/python3 /app/dataAnalyzer.py /config/conf.json 
#docker run -it --rm --user=1968:1968 -w /home/myuser -v "$(pwd)":/app  -v "${DATA_PATH}":/data:rw --entrypoint /bin/bash  ${DOCKER_IMAGE_NAME}
#docker run -it --rm --user=0:0 -w /home/myuser -v "$(pwd)":/app  -v "${DATA_PATH}":/data:rw --entrypoint /bin/bash  ${DOCKER_IMAGE_NAME}

chmod $PREV_PERMS ${DATA_PATH}
