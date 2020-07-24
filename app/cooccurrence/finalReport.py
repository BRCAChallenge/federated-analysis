import json
import sys
import pandas as pd
import logging

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def main():
	if len(sys.argv) != 6:
		print('ipv-f.json in.txt not.txt sites.tsv output.tsv')
		sys.exit(1)


	ipvFileName = sys.argv[1]
	logger.info('reading data from ' + ipvFileName)
	with open(ipvFileName, 'r') as f:
		ipvDict = json.load(f)
	f.close()

	inFileName = sys.argv[2]
	logger.info('reading data from ' + inFileName)
	f = open(inFileName, 'r')
	inList = f.readlines() 
	f.close()
	inList = [x.strip() for x in inList]

	outFileName = sys.argv[3]
	logger.info('reading data from ' + outFileName)
	f = open(outFileName, 'r')
	outList = f.readlines() 
	f.close()
	outList = [x.strip() for x in outList]

	sitesFileName = sys.argv[4]
	logger.info('reading data from ' + sitesFileName)
	f = open(sitesFileName, 'r')
	sitesDF = pd.read_csv(sitesFileName, header=0, sep='\t')
	f.close()

	outputFileName = sys.argv[5]


	allVariants = ipvDict.keys()
	variantsDict = dict()
	#print('variant\tclass\tpopFreq\tcohortFreq\taa\tAa\tAA\thomozygousSample\tinGnomad')
	for v in allVariants:
		vClass = ipvDict[v]['class']
		vPopFreq = '%.4f'%(ipvDict[v]['maxFreq'])
		vCohortFreq = '%.4f'%(ipvDict[v]['cohortFreq'])

		if len(ipvDict[v]['homozygous individuals']) == 0:
			homoSample = "None"
		else:
			homoSample = ipvDict[v]['homozygous individuals'][0]
		v = v.replace(' ', '')	
		v = v.replace("'", "")
		if v in inList:
			vIn = 'True'
		elif v in outList:
			vIn = 'False'
		else:
			print('neither in in nor out?')
			vIn = 'False'
		#print(v + '\t' + vClass + '\t' + vPopFreq + '\t' + vCohortFreq + \
		# '\t' + aa + '\t' + Aa + '\t' + AA + '\t' + homoSample + '\t' + vIn)
		variantsDict[v] = dict()
		variantsDict[v]['homo_alt'] = str(ipvDict[v]['aa'])
		variantsDict[v]['hetero'] = str(ipvDict[v]['Aa'])
		variantsDict[v]['homo_ref'] = str(ipvDict[v]['AA'])
		variantsDict[v]['Z'] = str(ipvDict[v]['Z'])
		variantsDict[v]['F'] = str(ipvDict[v]['F'])
		variantsDict['chisquare'] = str(ipvDict[v]['chisquare'])
		variantsDict[v]['class'] = vClass
		variantsDict[v]['popFreq'] = vPopFreq
		variantsDict[v]['cohortFreq'] = vCohortFreq
		variantsDict[v]['homozygousSample'] = homoSample
		variantsDict[v]['inGnomad'] = vIn

	variantsDF = pd.DataFrame.from_dict(variantsDict)
	variantsDF = variantsDF.transpose()
	variantsDF['variant'] = variantsDF.index
	variantsDF.to_csv('/tmp/brcaDF.tsv', sep='\t', index=True)

	variantsWithInfoDF = addInfo(variantsDF, sitesDF)

	logger.info('writing output to ' + outputFileName)
	variantsWithInfoDF.to_csv(outputFileName, sep='\t', index=False)


def addInfo(variantsDF, sitesDF):


	variants = list(variantsDF['variant'])
	brca_dict = dict()
	for index, row in sitesDF.iterrows():
		var = str((str(row['#CHROM']).split('chr')[1], row['POS'], row['REF'], row['ALT']))
		var = var.replace("'", "").replace(" ", "")
		if var in variants:
			brca_dict[var] = row['INFO']

	info_df = pd.DataFrame(brca_dict.items())
	info_df.columns = ['variant', 'INFO']


	finalDF = pd.merge(variantsDF, info_df, on='variant', how='left')


	# now iterate through the INFO column and pull out each var=val pair
	# we'll make new cols based on these pairs

	infoDict = dict()
	for i in range(len(finalDF.index)):
		infoDict[i] = dict()
		infoPairs = finalDF.iloc[i]['INFO'].split('|')[0].split(';')
		for pair in infoPairs:
			vv = pair.split('=')
			infoDict[i][vv[0]] = vv[1]


	infoDF = pd.DataFrame.from_dict(infoDict).transpose()

	finalDF['FIBC_I'] = infoDF['FIBC_I']
	finalDF['HWEAF_p'] = infoDF['HWEAF_P']
	finalDF['HWE_SLP_I'] = infoDF['HWE_SLP_I']
	finalDF['HWE_SLP_P'] = infoDF['HWE_SLP_P']
	finalDF['AC'] = infoDF['AC']
	finalDF['AF'] = infoDF['AF']
	finalDF['AN'] = infoDF['AN']

	finalDF = finalDF.drop(columns=['INFO'])

	return finalDF
		
	
if __name__ == "__main__":
    main()


