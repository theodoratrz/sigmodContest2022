from typing import Dict, List, Tuple
from collections import defaultdict
import string

USE_C_SEQ_MATHCER = False

if USE_C_SEQ_MATHCER:
    from cdifflib import CSequenceMatcher
else:
    from difflib import SequenceMatcher

import pandas as pd

SUBMISSION_MODE = False

SEQ_MATCH_THRESHOLD = 0.925

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
    words = no_punct.split()
    words.sort()

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

UKNOWN_FAMILY = 'unknown'

if __name__ == '__main__':
    pairs: List[Tuple[int, int]] = []
    brandClusters: Dict[str, List[ Tuple[int, str, List[str]] ]] = defaultdict(list)

    pd.read_csv("X2.csv")
    X = pd.read_csv("X1.csv")

    for i, row in X.iterrows():
        sortedWords, cleanedTitle = cleanInstance(row['title'])

        for word in sortedWords:
            if word in brandNames:
                brandClusters[word].append((row['id'], cleanedTitle, sortedWords))
                break
        
    for brand in brandClusters:
        familyClusters: Dict[str, List[ Tuple[int, str] ]] = defaultdict(list)

        for instanceId, title, words in brandClusters[brand]:
            unkownFamily = True
            for word in words:
                if word in familyNames:
                    familyClusters[word].append((instanceId, title))
                    unkownFamily = False
                    break
            
            if unkownFamily:
                familyClusters[UKNOWN_FAMILY].append((instanceId, title))
        
        # Maybe save some memory?
        brandClusters[brand] = None
        
        # Family subcluster
        for family in familyClusters:
            for i, (instanceId, sortedTitle) in enumerate(familyClusters[family]):
                familyClusters[family][i] = (instanceId, sortedTitle)
                
            for i in range(len(familyClusters[family])):
                i_id, i_title = familyClusters[family][i]
                for j in range(i + 1, len(familyClusters[family])):
                    j_id, j_title = familyClusters[family][j]
                    seqMatch = SequenceMatcher(None, i_title, j_title)

                    if seqMatch.ratio() >= SEQ_MATCH_THRESHOLD:
                        if i_id < j_id:
                            pairs.append( (i_id, j_id) )
                            if len(pairs) == 1000000:
                                saveAndExit(pairs)
                        else:
                            pairs.append( (j_id, i_id) )
                            if len(pairs) == 1000000:
                                saveAndExit(pairs)
        
    saveAndExit(pairs)
