import json
import logging
import sys
import numpy as np

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, tuple):
            return list(obj)
        else:
            return super(NpEncoder, self).default(obj)


def main():
    if len(sys.argv) != 5:
        print('out.json batchPerHomoVUS.json batchName filtered-out.json')
        sys.exit(1)

    outFileName = sys.argv[1]
    perBatchFileName = sys.argv[2]
    batchName = sys.argv[3]
    filteredOutFileName = sys.argv[4]

    logger.info('reading data from ' + outFileName)
    with open(outFileName, 'r') as f:
        out = json.load(f)
    f.close()

    logger.info('reading data from ' + perBatchFileName)
    with open(perBatchFileName, 'r') as f:
        bphv = json.load(f)
    f.close()

    excludeList = list()
    for vus in bphv:
        if bphv[vus] == [batchName]:
            excludeList.append(vus)

    for key in excludeList:
        try:
            del out['homozygous vus'][key]
        except Exception as e:
            print('key ' + key + ' not in out.json')
            continue

    with open(filteredOutFileName, 'w') as f:
        json.dump(out, f, cls=NpEncoder)
    f.close()


if __name__ == "__main__":
    main()