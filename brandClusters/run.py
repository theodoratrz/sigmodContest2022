from typing import Dict, List, Tuple
from collections import defaultdict
import string

USE_C_SEQ_MATHCER = False

if USE_C_SEQ_MATHCER:
    import cdifflib
    SequenceMatcher = cdifflib.CSequenceMatcher

else:
    import difflib
    SequenceMatcher = difflib.SequenceMatcher

import pandas as pd

DUMP_STATS = True

def printBrandStats(brandClusters: Dict[str, List[ Tuple[int, str, List[str]] ]]):
    clusterSizes: List[int] = []
    brandNames: List[str] = []
    
    for k in brandClusters:
        clusterSizes.append(len(brandClusters[k]))
        brandNames.append(k)

    print(pd.DataFrame({
            'Brand': brandNames,
            'Items': clusterSizes
        }, index=None)
    )

def dumpUnknownInstances(instances: Tuple[int, str, List[str]]):
    import csv

    with open('unknown.csv', mode='w') as outFile:
        writer = csv.writer(outFile)
        
        for id, title, _ in instances:
            writer.writerow((id, title))    

SUBMISSION_MODE = False

KNOWN_SEQ_MATCH_THRESHOLD = 0.9
UNKNOWN_SEQ_MATCH_THRESHOLD = 0.9

def saveAndExit(pairs: List[ Tuple[int, int] ]):
    file = "output.csv"
    if SUBMISSION_MODE:
        
        expected_cand_size_X1 = 1000000
        expected_cand_size_X2 = 2000000

        # make sure to include exactly 1000000 pairs for dataset X1 and 2000000 pairs for dataset X2
        if len(pairs) > expected_cand_size_X1:
            pairs = pairs[:expected_cand_size_X1]

        # make sure to include exactly 1000000 pairs for dataset X1 and 2000000 pairs for dataset X2
        if len(pairs) < expected_cand_size_X1:
            pairs.extend([(0, 0)] * (expected_cand_size_X1 - len(pairs)))
        
        pairs.extend([(0,0)]*expected_cand_size_X2)
    else:
        pass
        #pairs.extend([(0,0)]*2)
    
    out = pd.DataFrame(
                pairs,
                columns=[
                    'left_instance_id',
                    'right_instance_id'])

    out.to_csv(file, index=False)
    exit()

def cleanInstance(raw: str):
    raw_low = raw.lower()
    no_punct = raw_low.translate(str.maketrans({ord(c): ' ' for c in string.punctuation}))
    clean_words = no_punct.split()
    clean_words.sort()
    unique_words = set(clean_words)

    return unique_words, ' '.join(set(unique_words))

brandNames = {
    'dell',
    'lenovo',
    'acer',
    'asus',
    'hp',
    'panasonic',
    'sony',
    'samsung',
    'xiaomi',
    'microsoft',
    'huawei',
    'toshiba',
    'apple'
}
UNKNOWN_BRAND = 'unknown family'

familyNames = {
    'elitebook',
    'compaq',
    'folio',
    'pavilion',
    'x1 carbon',
    'inspiron',
    'zenbook',
    'aspire',
    'extensa',
    'surface',
    'yoga',
    'thinkpad'
    'latitude',
    'atom'
}
UNKNOWN_FAMILY = 'unknown brand'

if __name__ == '__main__':
    pairs: List[Tuple[int, int]] = []
    brandClusters: Dict[str, List[ Tuple[int, str, List[str]] ]] = defaultdict(list)

    pd.read_csv("X2.csv")
    X = pd.read_csv("X1.csv")

    for i, row in X.iterrows():
        sortedWords, cleanedTitle = cleanInstance(row['title'])

        instanceBrands = []
        for word in sortedWords:
            if word in brandNames:
                instanceBrands.append(word)
        
        if len(instanceBrands) > 0:
            brand = ' '.join(instanceBrands)
            brandClusters[brand].append((row['id'], cleanedTitle, sortedWords))
        else:
            brandClusters[UNKNOWN_BRAND].append((row['id'], cleanedTitle, sortedWords))

    if DUMP_STATS:
        printBrandStats(brandClusters)
        dumpUnknownInstances(brandClusters[UNKNOWN_BRAND])
    
    # Start from the smallest cluster
    brandClustersKeys = sorted(brandClusters.keys(), key=lambda k: len(brandClusters[k]))
    for brand in brandClustersKeys:
        familyClusters: Dict[str, List[ Tuple[int, str] ]] = defaultdict(list)

        for instanceId, title, words in brandClusters[brand]:
            unkownFamily = True
            for word in words:
                if word in familyNames:
                    familyClusters[word].append((instanceId, title))
                    unkownFamily = False
                    break
            
            if unkownFamily:
                familyClusters[UNKNOWN_FAMILY].append((instanceId, title))
        
        # Maybe save some memory?
        brandClusters[brand] = None
        
        brandThreshold = KNOWN_SEQ_MATCH_THRESHOLD
        if brand == UNKNOWN_BRAND:
            brandThreshold = UNKNOWN_SEQ_MATCH_THRESHOLD

        # Start from the smallest cluster
        familyClustersKeys = sorted(familyClusters.keys(), key=lambda k: len(familyClusters[k]))
        for family in familyClustersKeys:
            for i in range(len(familyClusters[family])):
                i_id, i_title = familyClusters[family][i]
                for j in range(i + 1, len(familyClusters[family])):
                    j_id, j_title = familyClusters[family][j]
                    seqMatch = SequenceMatcher(None, i_title, j_title)

                    if seqMatch.ratio() >= brandThreshold:
                        if i_id < j_id:
                            pairs.append( (i_id, j_id) )
                        else:
                            pairs.append( (j_id, i_id) )

                        if len(pairs) == 1000000:
                            saveAndExit(pairs)
        
    saveAndExit(pairs)
