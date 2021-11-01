#!/bin/bash


ANNO_FILE=/private/groups/patenlab/jcasalet/TOPMED_WORKDIR/DATA/F8/GT40/13/freeze8_sample_annot_2020-07-07.txt
CHROM=13
GENE=BRCA2
P2=0.001
VCF_FILENAME=/private/groups/patenlab/jcasalet/TOPMED_WORKDIR/DATA/F8/GT40/13/f8_chr13_brca2_gruhmb_age.vcf
SAVE_FILES=True
GNOMAD_FILE=/private/groups/patenlab/jcasalet/federated-analysis/data/gnomad_genome_31_sites_chr13_brca2.vcf
VARIANT_PATHOGENICITY_FILE=/private/groups/patenlab/jcasalet/federated-analysis/data/clinvar.vcf
PYTHON_SCRIPT=/private/groups/patenlab/jcasalet/federated-analysis/app/cooccurrence/cooccurrenceFinder.py
PATHOLOGY_FILE=/private/groups/patenlab/jcasalet/federated-analysis/examples/BRCA2/data/brca2-pathology.tsv

miniwdl cromwell /private/groups/patenlab/jcasalet/WDL/myVusCooccur.wdl \
PYTHON_SCRIPT=${PYTHON_SCRIPT} \
VCF_FILE=$VCF_FILENAME \
ANNO_FILE=${ANNO_FILE} \
VARIANT_PATHOGENICITY_FILE=$VARIANT_PATHOGENICITY_FILE \
OUTPUT_FILENAME=${GENE}-cooccurrences.json \
ALL_FILENAME=${GENE}-all.json \
VPI_FILENAME=${GENE}-vpi.json \
IPV_FILENAME=${GENE}-ipv.json \
TOUT_FILENAME=${GENE}-tout.json \
HG_VERSION=38 \
ENSEMBL_RELEASE=99 \
PHASED=True \
P2=$P2 \
CHROM=$CHROM \
GENE=$GENE \
NUM_CORES=$(grep -c processor /proc/cpuinfo) \
SAVE_FILES=$SAVE_FILES \
GNOMAD_FILE=$GNOMAD_FILE \
PATHOLOGY_FILE=$PATHOLOGY_FILE \
-c /private/groups/patenlab/jcasalet/WDL/cromwell.local.conf 
