import sys
import json

def main():
    if len(sys.argv) != 3:
        print('vpi.json output-dir')
        sys.exit(1)
    vpiFileName = sys.argv[1]
    outputDir = sys.argv[2]

    with open(vpiFileName, 'r') as f:
        vpiDict = json.load(f)
    f.close()

    homozygousCount = 0
    heterozygousCount = 0
    for individual in vpiDict:
        print('type = ' + str(type(individual['benign'])))
        print(individual['benign'])
        for b in individual['benign']:
            if b[1] == '3':
                homozygousCount += 1
            else:
                heterozygousCount += 1

        for v in individual['vus']:
            if v[1] == '3':
                homozygousCount += 1
            else:
                heterozygousCount += 1

        for p in individual['pathogenic']:
            if p[1] == '3':
                homozygousCount += 1
            else:
                heterozygousCount += 1

        print('individual: ' + str(individual) + ',homo: ' + str(homozygousCount) + ',hetero:' + str(heterozygousCount))
if __name__ == "__main__":
    main()