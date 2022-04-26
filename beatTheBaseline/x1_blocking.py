from typing import List, Dict, Tuple
from collections import defaultdict
import re
import string

from utils import NO_BRAND, NO_CPU, NO_MODEL, jaccardSimilarity


customPunctuation = string.punctuation.replace(".", "")

trash = [
    r"[a-z]+\.com",
    r"[a-z]+\.ca",
    r"win(dows)? (xp|7|8.1|8|10)( pro(fessional)?| home premium)? ?((64|32)-bit)?",
    r"com:",
    r"amazon",
    r"alibaba",
    r"\d+ ?[t][b]",
    r"hdd",
    r"ssd",
    r"vology",
    r"downgrade",
    r"brand new",
    r"laptops",
    r"laptop",
    r"pc",
    r"computers",
    r"china",
    r"buy",
    r"famous",
    r"australia",
    r"accessories",
    r"wireless lan",
    r"wifi",
    r"wholeshale",
    r"notebook",
    r"led",
    r"ips",
    r"processor",
    r"core",
    r"e[b]ay",
    r"webcam",
    r"best",
    r"and",
    r"kids",
    r"bit",
    r"win",
    r"com",
    r"general",
    r"linux",
    r"cheap",
    r"inch",
    r"with",
    r"great",
    r"product",
    r"dvdrw",
    r"quality"
]
trashPattern = re.compile('|'.join(trash))

brandPatterns = [
    r'dell',
    r'lenovo',
    r'acer',
    r'asus',
    r'h(ewlett )?p(ackard)?',
    r'pan(a)?sonic',
    r'apple',
    r'toshiba',
    r'samsung',
    r'sony'
]
brandPattern = re.compile('|'.join(brandPatterns))

models = [
    r'elitebook', r'compaq', r'folio', r'pavilion', r'zbook', r'envy',
    r'thinkpad [a-z][0-9]{1,3}[t]?( \w+)?( \w+)? [0-9]{4}', r'thinkpad [a-z][0-9]{1,3}[t]?', 
    r'[a-z][0-9]{1,3}[t]?( \w+)?( [0-9]{4})?', r'x1 carbon', r'thinkpad', r'ideapad', r'flex', r'yoga',

    r'inspiron', r'latitude', r'precision', r'vostro', r'xps',
    r'zenbook', r'vivobook', r'rog', r'chromebook',
    r'aspire', r'extensa',
    r'toughbook',
    r'satellite', r'portege',
    r'vaio',
]
modelPattern = re.compile('|'.join(models))

cpus = [
    # intel
    #r'(intel )?(core )?i[357]( [0-9]{3,4}[q]?[mu])?',
    r'(^| )i[357]( [0-9]{3,4}[q]?[mu])',
    #r'(^| )i5( [0-9]{3,4}[q]?[mu])',
    #r'(^| )i7( [0-9]{3,4}[q]?[mu])',
    r'(^| )i[357]',
    r'(intel )?(core )?2 duo',
    r'(intel )?celeron', r'(intel )?pentium', r'(intel )?centrino', r'(intel )?xeon',
    r'[0-9]{3,4}[q]?[mu]', r'[pnt][0-9]{4}', r'[0-9]{4}[y]', r'[s]?[l][0-9]{4}', r'((1st)|(2nd)|(3rd)|([4-9]th))[ ][g]en',

    # amd
    r'([ae][0-9][ ][0-9]{4})',
    r'hd[ ][0-9]{4}'
]
cpuModelPattern = re.compile('|'.join(cpus))
cpuBrandPattern = re.compile(r'intel|amd')

numberPattern = r'[0-9]+(\.[0-9]+)?'
NUMBER_WEIGHT = 0.15
wordPattern = r'(?=\D)[\w]+'
WORD_WEIGHT = 0.2
BRAND_WEIGHT = 0.5
ALPHANUMERIC_WEIGHT = 1

def getSimilarityScore(a: str, b: str) -> float:

    a_words = set(a.split())
    b_words = set(b.split())
    if len(a_words) == 0 or len(b_words) == 0:
        return 0.0
    
    common = a_words.intersection(b_words)

    weighted_sum = 0
    for word in common:
        match = re.fullmatch(wordPattern, word)
        if match:
            # Character-only word
            if brandPattern.fullmatch(match.group()):
                # Brand
                weighted_sum += BRAND_WEIGHT
            else:
                weighted_sum += WORD_WEIGHT
        elif re.fullmatch(numberPattern, word):
            # Number
            weighted_sum += NUMBER_WEIGHT
        else:
            # Alphanumeric string
            weighted_sum += ALPHANUMERIC_WEIGHT

    return weighted_sum/max(len(a_words), len(b_words))

def lenovo_blocking(title: str) -> str:
    lenovoNumber = ''
    match = re.search(r'[0-9]{4}[0-9a-z]{3}(?![0-9a-z])', title)
    if not match:
        match = re.search(r'[0-9]{4}(?![0-9a-z])')
    if match:
        lenovoNumber = match.group().replace('-', '')[:4]
    pass

def lenovo_processing(model: str) -> str:
    newModel = model.replace('touch', '')\
                    .replace('tablet 3435', '2320')\
                    .replace('tablet 3435', '2320')\
                    .replace('x230t 3435', 'x230 2320')\
                    .replace('thinkpad', '')

    newModel = re.sub(r'4291', r'4290', newModel)
    return re.sub(' +', ' ', newModel).strip()

def x1_blocking(csv_reader, id_col: str, title_col: str, save_scores=False) -> List[Tuple[int, int]]:
    """
    This function performs blocking on X1 dataset.
    :param `X`: dataframe
    :return: candidate set of tuple pairs
    """

    sameSequencePatterns: Dict[str, List[ Tuple[int, str] ]] = defaultdict(list)
    modelPatterns: Dict[str, List[ Tuple[int, str] ]] = defaultdict(list)

    for i, row in enumerate(csv_reader):
        id = int(row[id_col])
        rawTitle = str(row[title_col]).lower()

        noTrash = re.sub(trashPattern, '', rawTitle)
        cleanedTitle = noTrash.translate(str.maketrans({ord(c): ' ' for c in customPunctuation}))
        cleanedTitle = re.sub(' +', ' ', cleanedTitle).strip()

        clean_words = cleanedTitle.split()
        clean_words.sort()
        unique_words = {word: None for word in clean_words}.keys()
        sortedTitle = ' '.join(unique_words)

        instance = (id, cleanedTitle)

        sameSequencePatterns[sortedTitle].append(instance)
        
        brands = []
        for brand in brandPatterns:
            match = re.search(brand, sortedTitle)
            if match:
                brands.append(match.group())
        brand = ' & '.join(brands) if len(brands) else NO_BRAND
        
        model = modelPattern.search(cleanedTitle)
        if not model:
            model = NO_MODEL
        else:
            model = model.group()

        if brand == 'lenovo':
            model = lenovo_processing(model)

        cpu = NO_CPU
        for pattern in cpus:
            match = re.search(pattern, cleanedTitle)
            if match:
                cpu = match.group().strip()
                break

        if model != NO_MODEL and cpu != NO_CPU:
            pattern = " || ".join((brand, model, cpu))
            modelPatterns[pattern].append(instance)
        #elif brand == 'lenovo':
        #    pass

    # add id pairs that share the same pattern to candidate set
    candidate_pairs_1 = []
    for pattern in sameSequencePatterns:
        instances = sameSequencePatterns[pattern]
        for i in range(len(instances)):
            for j in range(i + 1, len(instances)):
                candidate_pairs_1.append((instances[i], instances[j])) #
    # add pairs that share the same pattern to candidate set
    candidate_pairs_2 = []
    for pattern in modelPatterns:
        instances = modelPatterns[pattern]
        if len(instances)<500: #skip patterns that are too common
            for i in range(len(instances)):
                for j in range(i + 1, len(instances)):
                    candidate_pairs_2.append((instances[i], instances[j]))

    # remove duplicate pairs and take union
    candidate_pairs_1 = set(candidate_pairs_1)
    candidate_pairs_2 = set(candidate_pairs_2)
    candidate_pairs = list(candidate_pairs_2.union(candidate_pairs_1))

    # sort candidate pairs by jaccard similarity.
    # In case we have more than 1000000 pairs (or 2000000 pairs for the second dataset),
    # sort the candidate pairs to put more similar pairs first,
    # so that when we keep only the first 1000000 pairs we are keeping the most likely pairs
    jaccard_similarities = []
    candidate_pairs_real_ids: List[Tuple[int, int]] = []
    for pair in candidate_pairs:
        (id1, name1), (id2, name2) = pair

        if id1 < id2: # NOTE: This is to make sure in the final output.csv, for a pair id1 and id2 (assume id1<id2), we only include (id1,id2) but not (id2, id1)
            candidate_pairs_real_ids.append((id1, id2))
        else:
            candidate_pairs_real_ids.append((id2, id1))

        # compute jaccard similarity
        jaccard_similarities.append(getSimilarityScore(name1, name2))
        #jaccard_similarities.append(jaccardSimilarity(name1, name2))

    if save_scores:
        candidate_pairs_real_ids = [(pair[0], pair[1], score) for pair, score in sorted(zip(candidate_pairs_real_ids, jaccard_similarities), key=lambda t: t[1], reverse=True)]
    else:
        candidate_pairs_real_ids = [x for _, x in sorted(zip(jaccard_similarities, candidate_pairs_real_ids), reverse=True)]
    return candidate_pairs_real_ids
