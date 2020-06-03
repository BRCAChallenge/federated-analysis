import sys
import json
import logging
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd



logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def main():
    if len(sys.argv) != 5:
        print('13 13-vpi.json genotypeCounts.json outputDir')
        sys.exit(1)

    chrom = sys.argv[1]
    vpiFileName = sys.argv[2]
    gtFileName = sys.argv[3]
    outputDir = sys.argv[4]

    with open(vpiFileName, 'r') as f:
        vpiDict = json.load(f)
    f.close()

    freqDict, ratioArray = getFrequenciesAndRatios(vpiDict)
    with open(outputDir + '/' + chrom + '-rpi.json', 'w') as f:
        json.dump(freqDict, f)
    f.close()

    #colorBinPlot(ratioArray, outputDir, chrom + '-fpi.png', chrom)

    with open(gtFileName, 'r') as f:
        genotypeCounts = json.load(f)
    f.close()
    plotGenotypeCounts(genotypeCounts, False, outputDir)


    '''ratioList = list()
    for i in ratios:
        ratioList.append(ratios[i][2])'''
    binList = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    benignList = list()
    pathogenicList = list()
    vusList = list()
    for individual in freqDict:
        homo = freqDict[individual]['homoBSum']
        het = freqDict[individual]['hetBSum']
        if homo + het == 0:
            pass
        else:
            benignList.append(float(homo)/float(homo + het))

        homo = freqDict[individual]['homoPSum']
        het = freqDict[individual]['hetPSum']
        if homo + het == 0:
            pass
        else:
            pathogenicList.append(float(homo) / float(homo + het))

        homo = freqDict[individual]['homoVSum']
        het = freqDict[individual]['hetVSum']
        if homo + het == 0:
            pass
        else:
            vusList.append(float(homo) / float(homo + het))

    #binPlot(benignList, 10, "benign homozygosity density", "number of individuals", float, 3, binList, outputDir, chrom + '-benign-hrpi.png')
    #binPlot(pathogenicList, 10, "pathogenic homozygosity density", "number of individuals", float, 3, binList, outputDir, chrom + '-pathogenic-hrpi.png')
    #binPlot(vusList, 10, "vus homozygosity density", "number of individuals", float, 3, binList, outputDir, chrom + '-vus-hrpi.png')

    plt.hist([benignList, pathogenicList, vusList], binList, stacked = True, alpha=0.5, color=['green', 'red', 'blue'], label=['benign', 'pathogenic', 'vus'])
    #plt.hist(pathogenicList, binList, stacked=True, alpha=0.5, label='pathogenic')
    #plt.hist(vusList, binList, stacked=True, alpha=0.5, label='vus')
    plt.xlabel('homozygosity ratio')
    plt.ylabel('number of individuals')
    plt.title('ratios for chr ' + chrom)
    plt.xticks(np.arange(0.0, 1.1, 0.1))
    plt.legend(loc='upper right')
    plt.savefig(outputDir + '/' + chrom + '-rpi.png')

    #homoVHet(ratios, outputDir, chrom + '-homovhet.png')

def plotGenotypeCounts(genotypeCounts, rare, outputDir):
    homoCounts = [0 if genotypeCounts['benign']['homo'] == 0 else genotypeCounts['benign']['homo'],
                 0 if genotypeCounts['pathogenic']['homo'] == 0 else genotypeCounts['pathogenic']['homo'],
                 0 if genotypeCounts['vus']['homo'] == 0 else genotypeCounts['vus']['homo']]
    heteroCounts = [0 if genotypeCounts['benign']['hetero'] == 0 else genotypeCounts['benign']['hetero'],
                 0 if genotypeCounts['pathogenic']['hetero'] == 0 else genotypeCounts['pathogenic']['hetero'],
                 0 if genotypeCounts['vus']['hetero'] == 0 else genotypeCounts['vus']['hetero']]


    # plot bar graph
    '''labels = ['benign', 'pathogenic', 'vus']
    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots()
    ax.bar(x - width/2, homoCounts, width, label = 'homozygous')
    ax.bar(x + width/2, heteroCounts, width, label = 'heterozygous')
    ax.set_ylabel('log10(counts)')
    ax.set_title('count per zygosity per classification')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc='upper center')
    fig.tight_layout()
    #plt.ylim(0, 7)
    plt.show()'''

    # plot pie chart
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    plt.rcParams['font.size'] = 10
    fig1, ax1 = plt.subplots()

    if rare:
        labels = ['Homo VUS',  'Hetero VUS']
        colors = ['green', 'brown']
        sizes = [genotypeCounts['vus']['homo'], genotypeCounts['vus']['hetero']]
        explode = (0, 0)
        ax1.pie(sizes, explode=explode, colors=colors, labels=labels, shadow=False, startangle=90)

    else:
        labels = ['Homo benign', 'Homo path', 'Homo VUS', 'Hetero benign', 'Hetero path', 'Hetero VUS']
        sizes = [genotypeCounts['benign']['homo'], genotypeCounts['pathogenic']['homo'],
                    genotypeCounts['vus']['homo'], genotypeCounts['benign']['hetero'],
                    genotypeCounts['pathogenic']['hetero'], genotypeCounts['vus']['hetero']]
        colors = ['red', 'yellow', 'green', 'orange', 'blue', 'brown']
        explode = (0.1, 0.1, 0.1, 0, 0, 0)
        #ax1.pie(sizes, explode=explode, labels=labels, colors = colors, autopct='%1.3f%%', shadow=False, startangle=90)
        patches, texts = ax1.pie(sizes, explode=explode, colors = colors, shadow=False, startangle=90)
    plt.legend(patches, labels, fontsize=8)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    #plt.show()
    plt.savefig(outputDir + '/genotypeCounts.png')



def getFrequenciesAndRatios(vpiDict):
    frequencyDict = dict()
    ratioArray = np.zeros((len(vpiDict), 3))
    print('num individuals = ' + str(len(vpiDict)))
    counter = 0
    for i in vpiDict:
        homoBSum = 0
        homoPSum = 0
        homoVSum = 0
        hetBSum = 0
        hetPSum = 0
        hetVSum = 0
        for b in vpiDict[i]['benign']:
            if b[1] == "3":
                homoBSum += 1
            elif b[1] == '1' or b[1] == '2':
                hetBSum += 1
        for p in vpiDict[i]['pathogenic']:
            if p[1] == "3":
                homoPSum += 1
            elif p[1] == '1' or p[1] == '2':
                hetPSum += 1
        for v in vpiDict[i]['vus']:
            if v[1] == "3":
                homoVSum += 1
            elif v[1] == '1' or v[1] == '2':
                hetVSum += 1

        frequencyDict[i] = {'homoBSum': homoBSum, 'hetBSum': hetBSum,
                        'homoPSum': homoPSum, 'hetPSum': hetPSum,
                        'homoVSum': homoVSum, 'hetVSum': hetVSum }
        if homoBSum + hetBSum == 0:
            #ratioArray[counter][0] = 0
            pass
        else:
            ratioArray[counter][0] = homoBSum / (homoBSum + hetBSum)
        if homoPSum + hetPSum == 0:
            #ratioArray[counter][1] = 0
            pass
        else:
            ratioArray[counter][1] = homoPSum / (homoPSum + hetPSum)
        if homoVSum + hetVSum == 0:
            #ratioArray[counter][2] = 0
            pass
        else:
            ratioArray[counter][2] = homoVSum / (homoVSum + hetVSum)

        counter += 1

    return frequencyDict, ratioArray

def homoVHet(ratios, outputDir, imageName):
    plt.style.use('seaborn-whitegrid')
    homoList = list()
    hetList = list()
    for i in ratios:
        homoList.append(ratios[i][0])
        hetList.append(ratios[i][1])
    fig = plt.figure()
    plt.xlabel('homozygosity frequency')
    plt.ylabel('heterozygosity frequency')
    plt.scatter(homoList, hetList, s=10, color='black')
    plt.savefig(outputDir + '/' + imageName)


def colorBinPlot(freqArray, outputDir, imageName, chrom):
    import matplotlib.ticker as ticker

    n_bins = 10

    fig = plt.figure()
    colors = ['green', 'red', 'blue']
    plt.hist(freqArray, n_bins, density=False, histtype='bar', stacked=False, color=colors, label=['benign', 'pathogenic', 'vus'])
    plt.legend(prop={'size': 10})
    plt.xlabel('homozygosity ratio')
    plt.ylabel('number of individuals')
    plt.title('ratios for chr ' + chrom)
    plt.xticks(np.arange(0.0, 1.1, 0.1))


    plt.savefig(outputDir + '/' + imageName)


def binPlot(theList, binSize, xlabel, ylabel, dtype, sigDigs, binList, outputDir, imageName):
    customBinList = False
    if binList is None:
        sizeOfRange = 0.5 * (min(theList) + max(theList))
        try:
            binList = np.arange(min(theList), max(theList), round((1/binSize) * sizeOfRange, sigDigs) , dtype=dtype)
        except Exception as e:
            logger.error('error in binPlot np.arange(): ' + str(e))
            return
    else:
        customBinList = True
    bins = list()

    for element in theList:
        for i in range(len(binList) - 1):
            lhs = binList[i]
            rhs = binList[i + 1]
            if element >= lhs and element <= rhs:
                if customBinList:
                    bins.append(rhs)
                else:
                    bins.append(dtype(round(0.5 * (lhs + rhs), sigDigs)))
                break

    binMax = binList[len(binList)-1]
    listMax = max(theList)
    for element in theList:
        if element > binMax:
            bins.append(dtype(round(listMax, sigDigs)))



    df_bins = pd.DataFrame({xlabel: bins})
    if (len(df_bins) != 0):
        df_bins.groupby(xlabel, as_index=False).size().plot(kind='bar')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        #plt.xlim(start, end)
        #plt.ylim(ymin, ymax)
        #plt.show()
        plt.savefig(outputDir + '/' + imageName)


if __name__ == "__main__":
    main()