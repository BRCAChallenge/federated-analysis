import allel
import sys
import numpy as np
from collections import defaultdict
import json
import pandas as pd
import logging

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def main():
    if len(sys.argv) != 3:
        print('vcf-file-name output-file')
        sys.exit(1)
    vcfFileName = sys.argv[1]
    outputFile = sys.argv[2]

    logger.debug('reading ' + vcfFileName)
    vcf = allel.read_vcf(vcfFileName, fields=['samples', 'calldata/GT', 'variants/ALT', 'variants/CHROM',
            'variants/FILTER_PASS', 'variants/ID', 'variants/POS', 'variants/QUAL','variants/REF', 'variants/INFO'])

    logger.debug('reading data into genotype array')
    genoArray = allel.GenotypeArray(vcf['calldata/GT'])

    '''logger.debug('counting allele frequencies')
    alleleFrequency = genoArray.count_alleles().to_frequencies()

    logger.debug('calculating expected heterozygosity')
    expectedHeterozygosity = allel.heterozygosity_expected(alleleFrequency, ploidy=2)
    #print('expected: ' + str(expectedHeterozygosity))

    logger.debug('calculating observed heterozygosity')
    observedHeterozygosity = allel.heterozygosity_observed(genoArray)
    #print('observed: ' + str(observedHeterozygosity))

    logger.debug('calculating inbreeding coefficient')
    inbreedingCoefficient = allel.inbreeding_coefficient(genoArray)
    #print('ibc: ' + str(inbreedingCoefficient))

    logger.debug('calculating delta heterozygosity')
    diff = list()
    for i in range(len(expectedHeterozygosity)):
        diff.append(expectedHeterozygosity[i] - observedHeterozygosity[i])'''

    logger.debug('finding runs of homozygosity')
    numVariants = len(genoArray)
    numSamples = len(vcf['samples'])
    posArray = np.asarray([i for i in range(numVariants)])
    isAccessible = np.asarray([True for i in range(numVariants)])
    runsOfHomozygosity = dict()
    for i in range(numSamples):
        genoVector = genoArray[:,i]
        roh = allel.roh_mhmm(genoVector, posArray, is_accessible=isAccessible)
        print('roh = ' + str(roh))
        if not roh[0].empty:
            runsOfHomozygosity[i] = dict()
            runsOfHomozygosity[i]['confidence'] = float(roh[1])
            for j in range(len(roh[0])):
                runsOfHomozygosity[i][j] = dict()
                runsOfHomozygosity[i][j]['start'] = int(roh[0].iloc[j]['start'])
                runsOfHomozygosity[i][j]['stop'] = int(roh[0].iloc[j]['stop'])
                runsOfHomozygosity[i][j]['is_marginal'] = bool(roh[0].iloc[j]['is_marginal'])

    '''logger.debug('saving ibc.txt')
    np.savetxt(outputDir + '/ibc.txt', inbreedingCoefficient)

    logger.debug('saving zygosityDelta.txt')
    with open(outputDir + '/zygosityDelta.txt', 'w') as f:
        for item in diff:
            f.write("%s\n" % item)
    f.close()'''

    logger.debug('writing to ' + outputFile)
    #roh = json.dumps(runsOfHomozygosity)
    with open(outputFile, 'w') as f:
        json.dump(runsOfHomozygosity, f)
    f.close()


if __name__ == "__main__":
    main()