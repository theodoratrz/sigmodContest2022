from typing import Dict, List, Tuple
from collections import defaultdict
from difflib import SequenceMatcher
import string

import pandas as pd

SUBMISSION_MODE = True

SEQ_MATCH_THRESHOLD = 0.9

def saveAndExit(pairs):
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
        pairs.extend([(0,0)]*2)
    
    out = pd.DataFrame(
                pairs,
                columns=[
                    'left_instance_id',
                    'right_instance_id'])

    out.to_csv(file, index=False)

def cleanInstance(raw: str):
    raw_low = raw.lower()
    no_punct = raw_low.translate(str.maketrans({ord(c): ' ' for c in string.punctuation}))
    words = no_punct.split()
    #words.sort()

    return words, ' '.join(words)

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
    'huawei'
}

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
    'yoga'
}

pairs: List[Tuple[int, int]] = []

brandClusters: Dict[str, List[ Tuple[int, str] ]] = defaultdict(list)

if __name__ == '__main__':
    pd.read_csv("X2.csv")
    X = pd.read_csv("X1.csv")

    for i, row in X.iterrows():
        words, cleaned = cleanInstance(row['title'])

        for word in words:
            if word in brandNames:
                brandClusters[word].append((row['id'], cleaned))
                break
        
    for brand in brandClusters:
        familyClusters: Dict[str, List[ Tuple[int, str] ]] = defaultdict(list)

        for instanceId, title in brandClusters[brand]:
            words = title.split()
            for word in words:
                if word in familyNames:
                    familyClusters[word].append((instanceId, title))
                    break
        
        # Family subcluster
        for family in familyClusters:
            for i, (instanceId, title) in enumerate(familyClusters[family]):
                sortedTitleList = title.split()
                sortedTitleList.sort()
                sortedTitle = ' '.join(sortedTitleList)

                familyClusters[family][i] = (instanceId, sortedTitle)
                
            for i in range(len(familyClusters[family])):
                i_id, i_title = familyClusters[family][i]
                for j in range(i + 1, len(familyClusters[family])):
                    j_id, j_title = familyClusters[family][j]
                    seqMatch = SequenceMatcher(None, i_title, j_title)

                    if seqMatch.ratio() >= SEQ_MATCH_THRESHOLD:
                        if i_id < j_id:
                            pairs.append( (i_id, j_id) )
                        else:
                            pairs.append( (j_id, i_id) )
        
    saveAndExit(pairs)
