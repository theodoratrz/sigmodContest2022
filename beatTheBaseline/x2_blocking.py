# *Not standard*
from frozendict import frozendict

from typing import Iterable, List, Dict, Tuple
from collections import defaultdict
import re
import csv
import string

from utils import NO_BRAND, NO_MODEL, NO_MEMTYPE, NO_CAPACITY, NO_COLOR
from x2_utils import X2Instance, X2Utils


def findBrands(title: str, brandColumn: str):
    brands = []
    for brand in X2Utils.brandPatterns:
        match = re.search(brand, title)
        if match:
            brands.append(match.group())
    if len(brands):
        brand = ' & '.join(brands)
    else:
        match = re.fullmatch(X2Utils.brandPattern, str(brandColumn).lower())
        if match:
            brand = match.group()
        else:
            brand = NO_BRAND

    return brand, brands


def findPairs(candidate_pairs: Iterable[Tuple[X2Instance, X2Instance]], save_scores = False):

    jaccard_similarities: List[float] = []
    candidate_pairs_real_ids: List[Tuple[int, int]] = []

    for pair in candidate_pairs:
        instance1, instance2 = pair
        
        if instance1["id"] < instance2["id"]: # NOTE: This is to make sure in the final output.csv, for a pair id1 and id2 (assume id1<id2), we only include (id1,id2) but not (id2, id1)
            candidate_pairs_real_ids.append((instance1["id"], instance2["id"]))
        else:
            candidate_pairs_real_ids.append((instance2["id"], instance1["id"]))

        score = X2Utils.getSimilarityScore(instance1, instance2)
        #if score != REJECT_SCORE:
        #    jaccard_similarities.append(score)
        jaccard_similarities.append(score)

    # sort candidate pairs by similarity score.
    # In case we have more than 2000000 pairs,
    # sort the candidate pairs to put more similar pairs first,
    # so that when we keep only the first 2000000 pairs we are keeping the most likely pairs
    if save_scores:
        candidate_pairs_real_ids = [(pair[0], pair[1], score) for pair, score in sorted(zip(candidate_pairs_real_ids, jaccard_similarities), key=lambda t: t[1], reverse=True)]
    else:
        candidate_pairs_real_ids = [x for _, x in sorted(zip(jaccard_similarities, candidate_pairs_real_ids), reverse=True)]
    return candidate_pairs_real_ids

# TODO: use brand-specific logic
def createInstanceInfo(instanceId: int, cleanedTitle: str, sortedTitle: str, brand: str, brands: List[str]) -> X2Instance:
    # Try to classify a mem type
        memType = NO_MEMTYPE
        for mem in X2Utils.memTypePatterns:
            if memType == NO_MEMTYPE:
                for pattern in X2Utils.memTypePatterns[mem]:
                    if re.search(pattern, cleanedTitle):
                        memType = mem
                        break
            else:    
                break
        for mem in X2Utils.memTypeExtra:
            if memType == NO_MEMTYPE:
                for pattern in X2Utils.memTypeExtra[mem]:
                    if re.search(pattern, cleanedTitle):
                        memType = mem
                        break
            else:
                break

        model = NO_MODEL
        for b in brands:
            if model == NO_MODEL:
                for key in X2Utils.modelPatterns[b]:
                    if model == NO_MODEL:
                        if X2Utils.modelPatterns[b][key] is None:
                            # key is a regex
                            match = re.search(key, cleanedTitle)
                            if match:
                                model = match.group()
                                break
                        else:
                            # key is model category
                            for pattern in X2Utils.modelPatterns[b][key]:
                                match = re.search(pattern, cleanedTitle)
                                if match:
                                    model = key
                                    break
                    else:
                        break
            else:
                break

        capacity = re.search(X2Utils.capacityPattern, cleanedTitle)
        if not capacity:
            # The capacity is probably separated (and shuffled)
            unitMatch = re.search(X2Utils.capacityUnitPattern, sortedTitle)
            if unitMatch:
                sizeMatch = re.search(X2Utils.capacitySizesPattern, sortedTitle)
                if sizeMatch:
                    capacity = sizeMatch.group().strip() + unitMatch.group().strip()
                    capacity = capacity.replace('o','b')
            if not capacity:
                capacity = NO_CAPACITY
        else:
            capacity = capacity.group().replace('o','b')

        color = NO_COLOR
        if 'galaxy' in model:
            # convert "note9" to "note 9"
            model = re.sub(r'(?P<note>note)(?P<series>\S)', r'\g<note> \g<series>', model)
            # find color
            for c in X2Utils.colors:
                if c in cleanedTitle:
                    color = c
                    break

        return frozendict({
            "id": instanceId,
            "title": cleanedTitle,
            "brand": brand,
            "memType": memType,
            "model": model,
            "capacity": capacity,
            "color": color
        })

def assignToCluster(
    instance: X2Instance,
    sortedTitle: str,
    sameSequenceClusters: Dict[str, List[X2Instance]],
    smartClusters: Dict[str, List[X2Instance]]):

    # TODO: Replace with brand-specific logic
    sameSequenceClusters[sortedTitle].append(instance)
    if instance["brand"] != NO_BRAND and instance["memType"] != NO_MEMTYPE and instance["capacity"] != NO_CAPACITY and instance["model"] != NO_MODEL:
        pattern = " || ".join((instance["brand"], instance["memType"], instance["model"], instance["capacity"], instance["color"]))
        smartClusters[pattern].append(instance)
    #else:
    #    sameSequenceClusters[sortedTitle].append(instance)

def x2_blocking(csv_reader: csv.DictReader, id_col: str, title_col: str, brand_col: str, save_scores=False) -> List[Tuple[int, int]]:
    """
    Perform blocking on X2 dataset.
    Returns a candidate set of tuple pairs.
    """

    customPunctuation = X2Utils.customPunctuation
    trashPattern = X2Utils.trashPattern
    separatedCapacityPattern = X2Utils.separatedCapacityPattern
    unifiedCapacityPattern = X2Utils.unifiedCapacityPattern    

    sameSequenceClusters: Dict[str, List[X2Instance]] = defaultdict(list)
    smartClusters: Dict[str, List[X2Instance]] = defaultdict(list)

    for i, row in enumerate(csv_reader):
        instanceId = int(row[id_col])
        rawTitle = str(row[title_col]).lower()

        rawTitle = re.sub(separatedCapacityPattern, unifiedCapacityPattern, rawTitle)

        noTrash = re.sub(trashPattern, '', rawTitle)
        cleanedTitle = noTrash.translate(str.maketrans({ord(c): ' ' for c in customPunctuation}))
        cleanedTitle = re.sub(' +', ' ', cleanedTitle).strip()

        clean_words = cleanedTitle.split()
        clean_words.sort()
        unique_words = {word: None for word in clean_words if word not in string.punctuation}.keys()
        sortedTitle = ' '.join(unique_words)

        brand, brands = findBrands(sortedTitle, row[brand_col])
        if brand == NO_BRAND:
            continue

        instance = createInstanceInfo(instanceId, cleanedTitle, sortedTitle, brand, brands)

        assignToCluster(instance, sortedTitle, sameSequenceClusters, smartClusters)

    # add id pairs that share the same pattern to candidate set
    candidate_pairs_1 = []
    for pattern in sameSequenceClusters:
        instances = sameSequenceClusters[pattern]
        for i in range(len(instances)):
            for j in range(i + 1, len(instances)):
                candidate_pairs_1.append((instances[i], instances[j])) #
    # add pairs that share the same pattern to candidate set
    candidate_pairs_2 = []
    for pattern in smartClusters:
        instances = smartClusters[pattern]
        if len(instances)<1000: #skip patterns that are too common
            for i in range(len(instances)):
                for j in range(i + 1, len(instances)):
                    candidate_pairs_2.append((instances[i], instances[j]))

    # remove duplicate pairs and take union
    candidate_pairs_1 = set(candidate_pairs_1)
    candidate_pairs_2 = set(candidate_pairs_2)
    candidate_pairs = list(candidate_pairs_2.union(candidate_pairs_1))
    
    return findPairs(candidate_pairs, save_scores=save_scores)
