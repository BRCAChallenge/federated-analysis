#!/bin/bash

FDA_PATH=$(pwd)
APP_PATH=${FDA_PATH}/app
CONF_PATH=${FDA_PATH}/config
DATA_PATH=${FDA_PATH}/data
COOCCUR_DOCKER_IMAGE_NAME=brcachallenge/federated-analysis:cooccurrence
PATHOLOGY_DOCKER_IMAGE_NAME=brcachallenge/federated-analysis:pathology

if [ $# -eq 0 ]
then
	echo "usage: $0 <vcf-file> analyze"
	echo "OR"
	echo "$0 <input-vcf-filename> <hg-version> <ensembl-version> <chromosome-of-interest> <phased-boolean> <gene-of-interest> <brca-vars-filename>" 
	echo "example: $0 /data/breastcancer.vcf 37 75 13 False BRCA2 /data/brca-variants.tsv" 
	exit 1
	

elif [ $# -eq 1 -a $1 == 'analyze' ]
then
	docker build -t ${PATHOLOGY_DOCKER_IMAGE_NAME} - < docker/pathology/Dockerfile
	docker run --rm -e PYTHONPATH=/ -e PYTHONIOENCODING=UTF-8 -w / --user=`id -u`:`id -g` -v ${APP_PATH}/pathology:/app:ro -v ${CONF_PATH}:/config -v "${DATA_PATH}":/data ${PATHOLOGY_DOCKER_IMAGE_NAME} /usr/bin/python3 /app/dataAnalyzer.py /config/conf.json 
	exit 0

elif [ $# -eq 3 -a $1 == 'intersect' ]
then
	CHROM=$2
	OUT_FILENAME=/data/${CHROM}-out.json
	IPV_FILENAME=/data/${CHROM}-ipv.json
	PATHOLOGY_FILENAME=/data/$3
	OUTPUT_FILENAME=/data/${CHROM}-intersection.json

	docker build -t ${COOCCUR_DOCKER_IMAGE_NAME} - < docker/cooccurrence/Dockerfile
	docker run --rm -e PYTHONPATH=/ -e PYTHONIOENCODING=UTF-8 -w / --user=`id -u`:`id -g` -v ${APP_PATH}/intersection:/app:ro -v "${DATA_PATH}":/data ${COOCCUR_DOCKER_IMAGE_NAME} /usr/bin/python3 /app/getPathologyPerCooccurrence.py $OUT_FILENAME $IPV_FILENAME $PATHOLOGY_FILENAME $OUTPUT_FILENAME
	exit 0


elif [ $# -eq 7 ]
then

	VCF_FILE=/data/$1
	HG_VERSION=$2
	ENSEMBL_RELEASE=$3
	CHROM=$4
	PHASED=$5
	GENE=$6
	PATHOLOGY_FILE=/data/$7
        BRCA_VARS=/data/brca-variants.tsv
	IPV_FILE=/data/${CHROM}-ipv.json
	VPI_FILE=/data/${CHROM}-vpi.json
	ALL_FILE=/data/${CHROM}-all.json
	OUTPUT_FILE=/data/${CHROM}-out.json

	docker build -t ${COOCCUR_DOCKER_IMAGE_NAME} - < docker/cooccurrence/Dockerfile

	docker run --rm -e PYTHONPATH=/ -e PYTHONIOENCODING=UTF-8 --user=`id -u`:`id -g` -v ${APP_PATH}/cooccurrence:/app:ro -v ${CONF_PATH}:/config -v "${DATA_PATH}":/data:rw ${COOCCUR_DOCKER_IMAGE_NAME} /usr/bin/python3 /app/cooccurrenceFinder_nontopmed.py --vcf $VCF_FILE --out $OUTPUT_FILE --h $HG_VERSION --e $ENSEMBL_RELEASE --c $CHROM --g $GENE --p $PHASED --b $BRCA_VARS --vpi $VPI_FILE --ipv $IPV_FILE --all $ALL_FILE --pf $PATHOLOGY_FILE

else
	echo "wrong usage"
	exit 1
fi
