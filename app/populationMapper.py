import pandas as pd
import sys
import json
from collections import defaultdict


def main():
    if len(sys.argv) != 4:
        print('ancestry.tsv cohort.txt outputDir')
        sys.exit(1)

    ancestryFileName = sys.argv[1]
    cohortFileName = sys.argv[2]
    outputDir = sys.argv[3]

    ancestry = pd.read_csv(ancestryFileName, sep='\t')

    cohort = pd.read_csv(cohortFileName, header=None)

    '''Sub_Saharan_Africa      AFR
    Central_and_South_Asia  SAS
    East_Asia       EAS
    Europe  NFE
    Native_America  AMR
    Oceania OTH
    Middle_East     OTH'''

    topmed2gnomAD = dict()
    topmed2gnomAD['Sub_Saharan_Africa'] = 'AFR'
    topmed2gnomAD['Central_and_South_Asia'] = 'SAS'
    topmed2gnomAD['East_Asia'] = 'EAS'
    topmed2gnomAD['Europe'] = 'NFE'
    topmed2gnomAD['Native_America'] = 'AMR'
    topmed2gnomAD['Oceania'] = 'OTH'
    topmed2gnomAD['Middle_East'] = 'OTH'


    populationPerIndividual = defaultdict()
    for individual in cohort[0]:
        row = ancestry.loc[ancestry['individual'] == individual]
        # row = Index(['individual', 'Sub_Saharan_Africa', 'Central_and_South_Asia',
        #       'East_Asia', 'Europe', 'Native_America', 'Oceania', 'Middle_East'],
        #       dtype='object')
        tempPop = None
        tempMax = 0.0
        for pop in row.columns[1:]:
            # pop = 107046    0.7787
            #       Name: Sub_Saharan_Africa, dtype: float64
            try:
                if float(row[pop].values[0]) > tempMax:
                    tempPop = row[pop].name
                    tempMax = row[pop].values[0]
            except Exception as e:
                continue
        populationPerIndividual[individual]['topmedPop'] = (tempPop, tempMax)
        populationPerIndividual[individual]['gnomadPop'] = topmed2gnomAD[tempPop]

    with open(outputDir + '/ancestries.json', 'w') as f:
        json.dump(populationPerIndividual, f)
    f.close()

    '''HGDP	GNOMAD
    Sub_Saharan_Africa	AFR
    Central_and_South_Asia	SAS
    East_Asia	EAS
    Europe	NFE
    Native_America	AMR
    Oceania	OTH
    Middle_East	OTH'''


if __name__ == "__main__":
    main()