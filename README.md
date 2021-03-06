# Summary 

HIPAA requires that medical records be kept private, yet scientists need this data in order to conduct their research.  So instead of sharing data, hospitals and clinics can run software on that data and share the summarized, aggregated, anonymized results with the interested scientists.  In this way, people's privacy is protected, and science can move forward on important research.

This software repository contains scripts that achieve the above goal.  

# Cooccurrence analysis
Run the following steps to find variants of uncertain significance (VUS) in a VCF file that co-occur with known pathogenic variants in the BRCA Exchange database.

## Prepare for co-occurrence 
To prepare for a co-occurrence analysis, perform the following steps:

1. Clone this github repository to your local system where the VCF file resides.

```console
$ git clone https://github.com/BRCAChallenge/federated-analysis
```

2. Put a copy of the VCF file in the federated-analysis/data directory.

```console
$ cp <your-vcf-file> federated-analysis/data
```

3. Make sure the VCF file has read permissions for the world.

```console
$ chmod a+r federated-analysis/data/<your-vcf-file>
```
4. Put a copy of the pathology report in the federated-analysis/data directory.

```console
$ cp <your-pathology-report> federated-analysis/data
```

5. Make sure the pathology report has read permissions for the world.

```console
$ chmod a+r federated-analysis/data/<your-pathology-report>
```
 

## Run co-occurrence analysis container from command line
To run the co-occurrence analysis, perform the following steps:

1. Change directory to the top-level directory of the repository.

```console
$ cd federated-analysis/
```

2. Run the runMe_nontopmed.sh script as follows:

```console
$ ./runMe_nontopmed.sh BreastCancer.shuffle.vcf 37 75 13 False BRCA2 shuffle.tsv

$ ./runMe_nontopmed.sh BreastCancer.shuffle.vcf 37 75 17 False BRCA1 shuffle.tsv
```

where:
* BreastCancer.shuffle.vcf is the name of the VCF file in the federated-analysis/data directory

* 38 is the version of the human genome for the coordinates in the VCF file (37 is also supported)

* 99 is the build of ensembl for retrieving gene names for the coordinates (use 75 for hg37)

* 13 (or 17) is the chromosome to filter in the VCF file

* True is a boolean value for whether the VCF data is phased (True) or not (False)

* BRCA2 (or BRCA1) is the name of the gene of interest on the chromosome of interest

* shuffle.tsv is the name of the pathology report located in the federated-analysis/data directory

3. This will generate a report in federated-analysis/data called `13-out.json` (and `17-out.json`) which contains a list of VUS, each in the following format:

```json
"(13, 32911164, 'T', 'A')": {
            "likelihood data": {
                "p1": 0.0015891032917139615,
                "p2": 0.001,
                "n": 25,
                "k": 1,
                "likelihood": 0.6382577479687377
            },
            "allele frequencies": {
                "maxPop": null,
                "maxPopFreq": 0.0,
                "minPop": null,
                "minPopFreq": 0.0,
                "cohortFreq": 0.0008107669855683476
            },
            "pathogenic variants": [
                [
                    13,
                    32911297,
                    "TAAAC",
                    "T"
                ]
            ],
            "RARE": true

```

5. This will create 2 JSON files called `13-intersection.json` and `17-intersection.json` in the federated-analysis/data directory which intersect the pathology report with the co-occurrence results.

6. This will also create some ancillary files in the federated-analysis/data directory called `13-all.json` and `17-all.json` .


# Pathology statistics

Additionally, this software allows users to run a Docker container which has the necessary code to perform basic statistical analysis and validity checking.  There's a configuration file that the cooperating owner of the data must fill out in conjunction with the scientist to define the fields of interest in the data set.  
There are three Python modules in this repository: one which performs default analysis (dataAnalyzer.py), one that performs custom analysis (customDataAnalyzer.py), and one that creates a table (supplementaryTable4.py).  

The default data analysis outputs the following information:
1. data file name 
2. data file header present?
3. data file field delimiter
4. total records read from data file
5. for each field of interest
    - name of field
    - type of field (numerical, categorical, or free-form)
    - total counts for each value
    - for numerical data, the min, max, mean, and median values
6. bad values (those that don't conform to the type)
7. missing values (fields that are not populated)

Note that the default data analysis is generic -- it's completely devoid of any application or context.  If the scientist wishes to perform specific analyses on the data, then they must implement the custom data analyzer.  The custom data analyzer is provided an object that encapsulates all the default data analysis.  The custom code can then perform application-specific analyses on the data. 


In order to use this solution, perform the following steps.

1. Change directory to the top-level directory of the repository.

```console
cd federated-analysis/
```

2. Edit the config/conf.json file to reflect the metadata regarding the data file (file name, header line, field delimiter) as well as the correct fields of interest.

```console
vi config/conf.json
```

3. Run the runMe_nontopmed.sh script as follows:

```console
$ ./runMe_nontopmed.sh analyze
```

4. This will generate a report that is printed to standard output containing records such as the following:

```json

============================================
total records read from data file: 7051
============================================
column: ER / type: categorical
{
    "fieldCount": {
        "NA": 2200,
        "Negative": 1313,
        "Positive": 3538
    }
}

...
```

This output will also contain any custom reporting you add to the script.



# Software unit testing 

To run the unit tests, perform the following steps:

1. change directory to the top-level directory of the repository

```console
cd federated-analysis/
```

2. run the following command:

```console
python -m unittest tests.test_dataAnalyzer
```

# Run co-occurrence analysis container from WDL
Define the environment variables for the workflow, such as the following example shows:
```
PYTHON_SCRIPT=/home/jcasalet/src/cooccurrenceFinder.py
VCF_FILE=/data/chr13_brca2.vcf 
BRCA_FILE=/data/brca-variants.tsv 
OUTPUT_FILENAME=13-out.json 
HG_VERSION=38 
ENSEMBL_RELEASE=99 
PHASED=True 
SAVE_VARS=True 
CHROM=13 
GENE=BRCA2 
NUM_CORES=16
INDIVIDUALS_FILENAME=13-vpi.json
VARIANTS_FILENAME=13-ipv.json
```

Then run the WDL workflow using the values of the environment variables defined above.

