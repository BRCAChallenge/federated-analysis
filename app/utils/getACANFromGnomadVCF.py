import pandas as pd
import logging
import argparse
import json
import matplotlib.pyplot as plt
import numpy
from scipy.stats import ks_2samp
import math

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.WARNING)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--vcf', help='vcf input file')
    parser.add_argument('-j', '--json', help='json output file')
    parser.add_argument('-g', '--graph', help='graph output file')
    options = parser.parse_args()
    return options


def main():
    vcfFileName = parse_args().vcf
    outputFileName = parse_args().json
    graphFileName = parse_args().graph


    logger.info('finding variants from ' + vcfFileName)
    vcfDF = pd.read_csv(vcfFileName, delimiter='\t', header=0, dtype=str)
    nontopmedKeys = ['AF-non_topmed-afr', 'AF-non_topmed-amr', 'AF-non_topmed-nfe',
                     'AF-non_topmed-fin', 'AF-non_topmed-eas', 'AF-non_topmed-sas']

    topmedKeys = ['AF-just_topmed-afr', 'AF-just_topmed-amr', 'AF-just_topmed-nfe',
                     'AF-just_topmed-fin', 'AF-just_topmed-eas', 'AF-just_topmed-sas']

    allVariants = getNontopmedAlleleFreqs(vcfDF, nontopmedKeys)

    getTopmedAlleleFreqs(vcfDF, allVariants)

    logger.info('saving ntm allele freqs')
    with open(outputFileName, 'w') as f:
        json.dump(allVariants, f)
    f.close()

    logger.info('plotting allele freqs')
    topmedDict, nontopmedDict = createDicts(allVariants, topmedKeys, nontopmedKeys)
    plotDists(topmedDict, nontopmedDict, topmedKeys, nontopmedKeys, graphFileName)

def getTopmedAlleleFreqs(vcfDF, allVariants):
    ethnicitiesList = ['afr', 'amr', 'eas', 'fin', 'nfe', 'sas']
    # AC-non_topmed-afr, AN-non_topmed-afr, AC-afr, AN-afr
    keys = list()
    for e in ethnicitiesList:
        ntmACKey = 'AC-non_topmed-' + e
        keys.append(ntmACKey)
        ntmANKey = 'AN-non_topmed-' + e
        keys.append(ntmANKey)
        tmACKey = 'AC-' + e
        keys.append(tmACKey)
        tmANKey = 'AN-' + e
        keys.append(tmANKey)


    # get AC and AN for each ethnicity, then calculate AF
    for i in range(len(vcfDF)):
        fields = vcfDF.iloc[i]['INFO'].split(';')
        chrom = vcfDF.iloc[i]['#CHROM'].split('chr')[1]
        pos = vcfDF.iloc[i]['POS']
        ref = vcfDF.iloc[i]['REF']
        alt = vcfDF.iloc[i]['ALT']
        v = "(" + chrom + ", " + pos + ", '" + ref + "', '" + alt + "')"
        for field in fields:
            if '=' in field:
                key = field.split('=')[0]
                if key in keys:
                    value = float(field.split('=')[1])
                    allVariants[v][key] = value

    for v in allVariants:
        for e in ethnicitiesList:
            # get non-topmed ac and an
            ntmACKey = 'AC-non_topmed-' + e
            ntmANKey = 'AN-non_topmed-' + e
            ntmAC = allVariants[v][ntmACKey]
            # odd hack that sometimes AN and/or AC not in VCF for certain variants
            if not ntmANKey in allVariants[v]:
                allVariants[v][afKey] = 0.0
            else:
                ntmAN = allVariants[v][ntmANKey]

                # get topmed ac and an
                tmACKey = 'AC-' + e
                tmANKey = 'AN-' + e
                tmAC = allVariants[v][tmACKey]
                tmAN = allVariants[v][tmANKey]

                # subtract
                ac = tmAC - ntmAC
                an = tmAN - ntmAN
                af = 0.0
                if an != 0:
                    af = float(ac) / float(an)
                afKey = 'AF-just_topmed-' + e
                allVariants[v][afKey] = af


def getNontopmedAlleleFreqs(vcfDF, keys):
    variantsDict = dict()
    # pull AF, AC, and AN and figure out how to deal with this!

    logger.info('getting allele freqs')
    for i in range(len(vcfDF)):
        fields = vcfDF.iloc[i]['INFO'].split(';')
        chrom = vcfDF.iloc[i]['#CHROM'].split('chr')[1]
        pos = vcfDF.iloc[i]['POS']
        ref = vcfDF.iloc[i]['REF']
        alt = vcfDF.iloc[i]['ALT']
        mykey = "(" + chrom + ", " + pos + ", '" + ref + "', '" + alt + "')"
        variantsDict[mykey] = dict()
        for field in fields:
            if '=' in field:
                key = field.split('=')[0]
                if key in keys:
                    value = float(field.split('=')[1])
                    variantsDict[mykey][key] = value

    return variantsDict

def createDicts(variantsDict, topmedKeys, nontopmedKeys):
    # create dict for topmed and non-topmed
    topmedDict = dict()
    nontopmedDict = dict()

    topmedKeys.sort()
    nontopmedKeys.sort()

    for key in topmedKeys:
        topmedDict[key] = list()
    for key in nontopmedKeys:
        nontopmedDict[key] = list()
    variantsNotInTopmedList = list()
    for variant in variantsDict:
        for key in topmedKeys:
            # odd hack that sometimes a variant doesn't have AC and AN for all ethnicities
            if key in variantsDict[variant]:
                topmedDict[key].append(variantsDict[variant][key])
            else:
                variantsNotInTopmedList.append(variant)
        for key in nontopmedKeys:
            if not variant in variantsNotInTopmedList:
                nontopmedDict[key].append(variantsDict[variant][key])
    return topmedDict, nontopmedDict

def plotDists(topmedDict, nontopmedDict, topmedKeys, nontopmedKeys, graphFileName):

    n=len(topmedDict[topmedKeys[0]])

    for i in range(len(topmedKeys)):
        # plot scatter
        tmkey = topmedKeys[i]
        ntmkey = nontopmedKeys[i]

        nontopmedList = nontopmedDict[ntmkey]
        topmedList = topmedDict[tmkey]
        logntmList = list()
        for i in range(len(nontopmedList)):
            if nontopmedList[i] == 0:
                logntmList.append(0.0)
            else:
                logntmList.append(math.log(nontopmedList[i], 10))

        logtmList = list()
        logjusttmList = list()
        for i in range(len(topmedList)):
            if topmedList[i] == 0:
                logtmList.append(0.0)
            else:
                logtmList.append(math.log(topmedList[i], 10))

        lowerBound = min([min(logntmList), min(logtmList)])
        upperBound = max([max(logntmList), max(logtmList)])
        lineNumbers = numpy.arange(lowerBound, upperBound, 0.1)

        # plot all
        print('log ntm list = ' + str(len(logntmList)))
        print('log tm list = ' + str(len(logtmList)))
        print('line numbers list = ' + str(len(lineNumbers)))
        plt.scatter(logntmList, logtmList, marker='.', color='black')
        plt.scatter(lineNumbers, lineNumbers, marker='.', color='red')
        plt.ylabel('log10(topmed AF)', fontsize=18)
        plt.xlabel('log10(nontopmed AF)', fontsize=18)
        plt.title(graphFileName + '_' + tmkey + '_vs_' + ntmkey + '_scatter_' + ' n=' + str(n))
        plt.savefig(graphFileName + '_' + tmkey + '_vs_' + ntmkey + '_scatter_' + '_n=' + str(n) + '.png')
        plt.close()

        # plot PDF
        lowerLimit = min(logntmList + logtmList)
        upperLimit = max(logntmList + logtmList)
        binSize = (upperLimit - lowerLimit) / 10
        plt.xlim(lowerLimit, upperLimit)
        bins = numpy.arange(lowerLimit, upperLimit, binSize)
        plt.hist([logntmList, logtmList], label=['log10(topmed AF)', 'log10(nontopmed AF)'], bins=bins)
        plt.xlabel('log10(AF)')
        plt.ylabel('count')
        plt.title(graphFileName + '_' + tmkey + '_vs_' + ntmkey + 'PDF' + ' n=' + str(n))
        plt.legend(loc="upper right")
        plt.savefig(graphFileName + '_' + tmkey + '_vs_' + ntmkey + '_PDF_' + '_n=' + str(n) + '.png')
        plt.close()


        # run KS test
        ksTest = ks_2samp(topmedList, nontopmedList)
        print('ksTest for ' + tmkey + ' vs ' + ntmkey + ' : ' + str(ksTest))



if __name__ == "__main__":
    main()