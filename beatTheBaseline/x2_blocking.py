# *Not standard*
from frozendict import frozendict

from typing import Iterable, List, Dict, Tuple
from collections import defaultdict
import re
import csv
import string

from utils import NO_BRAND, NO_MODEL, NO_MEMTYPE, NO_TYPE, NO_CAPACITY, NO_COLOR
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
            return brand, [brand]
        else:
            if re.search(r'tos-[umn][0-9]{3}', title):
                return 'toshiba', ['toshiba']
            else:
                return NO_BRAND, []

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

    model = NO_MODEL
    brandType = NO_TYPE

    # Sony logic
    if brand == 'sony':            
        if memType == NO_MEMTYPE:
            if 'ux' in cleanedTitle or 'uy' in cleanedTitle or 'sr' in cleanedTitle:
                memType = 'microsd'
            elif 'uf' in cleanedTitle:
                memType = 'sd'
            elif 'usm' in cleanedTitle or capacity == '1tb':
                memType = 'usb'
            pass
        
        match = re.search(r'(sf|usm)[-]?[0-9a-z]{1,6}', cleanedTitle)
        if match:
            model = match.group().replace('-', '').replace('g', '')
            if capacity == NO_CAPACITY:
                capacity_match = re.search(r'[0-9]+', cleanedTitle)
                if capacity_match:
                    capacity = capacity_match.group() + 'gb'
            for c in range(ord('0'), ord('9')):
                model = model.replace(chr(c), '')
            if 'sf' in model and memType == NO_MEMTYPE:
                memType = 'sd'
            model = model.replace('sf', '').replace('usm', '')
        elif memType in ('usb', 'sd'):
            if 'machqx' in cleanedTitle:
                model = 'qx'
            elif 'type-c' in cleanedTitle or 'type c' in cleanedTitle:
                model = 'ca'
            match = re.search(
                r'(serie[s]?[\s-]?[a-z]{1,2}[\s])|([\s][a-z]{1,2}[\-]?serie[s]?)', cleanedTitle)
            
            if match is not None:
                model = match.group().replace(
                    ' ',
                    '').replace(
                    '-',
                    '').replace(
                    'g',
                    '')
                model = model.replace('series', '').replace('serie', '')
    elif brand == 'sandisk':
        match = re.search(r'ext.*(\s)?((plus)|(pro)|\+)', cleanedTitle)
        if match:
            model = 'ext+'
        else:
            match = re.search(r'ext(reme)?', cleanedTitle)
            if match:
                model = 'ext'
            else:
                for p in (r'fit', r'glide', r'blade'):
                    match = re.search(p, cleanedTitle)
                    if match:
                        model = match.group()
                        break
                if match is None:
                    match = re.search(
                        r'ultra(\s)?((plus)|(pro)|\+|(performance)|(android))', cleanedTitle)
                    if match:
                        model = 'ultra+'
                    elif re.search(r'(ultra|dual)', cleanedTitle):
                        model = 'ultra'
        if 'accessoires montres' in cleanedTitle:
            if 'extreme' in cleanedTitle:
                memType = 'microsd'
                model = 'ultra+'
            elif 'ext pro' in cleanedTitle:
                memType = 'microsd'
                model = 'ext+'
        if 'adapter' in cleanedTitle or 'adaptateur' in cleanedTitle:
            memType = 'microsd'
        if memType == NO_MEMTYPE:
            if 'drive' in cleanedTitle:
                memType = 'usb'
            elif 'cruzer' in cleanedTitle:
                memType = 'usb'
            elif model in ('glide', 'fit'):
                memType = 'usb'
    elif brand == 'lexar':
        match = re.search(
            r'((jd)|[\s])[a-wy-z][0-9]{2}[a-z]?', cleanedTitle)
        if match is None:
            match = re.search(r'[\s][0-9]+x(?![a-z0-9])', cleanedTitle)
        if match is None:
            match = re.search(r'(([\s][x])|(beu))[0-9]+', cleanedTitle)
        if match is not None:
            model = match.group().strip() \
                .replace('x', '').replace('l', '').replace('j', '').replace('d', '') \
                .replace('b', '').replace('e', '').replace('u', '')
    elif brand == 'intenso':
        for pattern in X2Utils.modelPatterns['intenso']:
            match = re.search(pattern, cleanedTitle)
            if match:
                model = match.group()
                break

        if model in X2Utils.intensoIdToModel.keys():
            model = X2Utils.intensoIdToModel[model]
    elif brand == 'kingston':
        if memType == NO_MEMTYPE:
            if 'savage' in cleanedTitle or 'hx' in cleanedTitle or 'hyperx' in cleanedTitle:
                memType = 'usb'
            elif 'ultimate' in cleanedTitle:
                memType = 'sd'
        if re.search(r'(dt[a-z]?[0-9]|data[ ]?t?travel?ler)', cleanedTitle):
            model = 'data traveler'
            type_model = re.search(r'(g[234]|gen[ ]?[234])', cleanedTitle)
            if type_model:
                brandType = type_model.group()[-1:]
        else:
            type_model = re.search(r'[\s](g[234]|gen[ ]?[234])[\s]', cleanedTitle)
            if type_model:
                brandType = type_model.group().strip()[-1:]
                model = 'data traveler'
        if model == 'data traveler' and memType == NO_MEMTYPE:
            memType = 'usb'
    elif brand == 'toshiba':
        match = re.search(r'[mnu][0-9]{3}', cleanedTitle)
        if match:
            model = match.group()
            if memType == NO_MEMTYPE and len(model) > 0:
                c = model[0]
                for char, mem in (('u', 'usb'), ('n', 'sd'), ('m', 'microsd')):
                    if c == char:
                        memType = mem
                        break
        if memType == 'usb' and model == NO_MODEL and re.search(r'(ex[\s-]?ii|osus)', cleanedTitle):
            model = 'ex'
        if memType == NO_MEMTYPE and ('transmemory' in cleanedTitle):
            memType = 'usb'
        if memType != 'usb':
            match = re.search(r'exceria[ ]?(high|pro|plus)?', cleanedTitle)
            if match:
                brandType = match.group().replace(' ', '').replace('exceria', 'x')
            if memType == NO_MEMTYPE:
                if brandType == 'xpro':
                    memType = 'sd'
                elif brandType == 'xhigh':
                    memType = 'microsd'
        elif model == NO_MODEL and (('hayaqa' in cleanedTitle) or ('hayabusa' in cleanedTitle)):
            model = 'u202'
        if memType == 'sd' and model == NO_MODEL:
            if re.search(r'silber', cleanedTitle):
                model = 'n401'
            elif brandType == NO_TYPE:
                if re.search(r'sd[hx]c uhs clas[se] 3 memor(y|(ia)) ((card)|(flash))', cleanedTitle):
                    brandType = 'xpro'
                elif ('uhs-ii' in cleanedTitle) and ('carte mémoire flash' in cleanedTitle):
                    brandType = 'xpro'
        elif memType != 'usb':
            # speed pattern (30[ ]?mb/s)
            match = re.search(r'[1-9][0-9]{1,2}[\s]?m[bo]/s', cleanedTitle)
            if match:
                speed = re.search(r'[0-9]{2,3}', match.group())
                if speed:
                    speed = speed.group()
                    if (speed == '260' or speed == '270') and brandType == NO_TYPE:
                        brandType = 'xpro'
                    elif speed == '90' and brandType == 'x' and model == NO_MODEL:
                        model = 'n302'
    else:
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

    color = NO_COLOR
    if 'galaxy' in model:
        # convert "note9" to "note 9"
        model = re.sub(r'(?P<note>note)(?P<series>\S)', r'\g<note> \g<series>', model)
        # find color
        for c in X2Utils.colors:
            if c in cleanedTitle:
                color = c
                break

    return {
        "id": instanceId,
        "title": cleanedTitle,
        "brand": brand,
        "memType": memType,
        "model": model,
        "type": brandType,
        "capacity": capacity,
        "color": color,
        "solved": False
    }

def assignToCluster(
    instance: X2Instance,
    sortedTitle: str,
    sameSequenceClusters: Dict[str, List[X2Instance]],
    smartClusters: Dict[str, List[X2Instance]]):

    if instance['brand'] == 'sony':
        if (instance['memType'] in ('ssd', 'microsd') or instance['capacity'] == '1tb') and instance['capacity'] != NO_CAPACITY:
            pattern = " || ".join((instance['brand'], instance['capacity'], instance['memType']))
        elif instance['memType'] != NO_MEMTYPE and instance['capacity'] != NO_CAPACITY and instance['model'] != NO_MODEL:
            pattern = " || ".join((instance['brand'], instance['capacity'], instance['memType'], instance['model']))
        else:
            instance['solved'] = False
            sameSequenceClusters[sortedTitle].append(frozendict(instance))
            return
        
        instance['solved'] = True
        smartClusters[pattern].append(frozendict(instance))
    elif instance['brand'] == 'sandisk_':
        if instance['memType'] != NO_MEMTYPE and instance['capacity'] != NO_CAPACITY:
            pattern = " || ".join((instance['brand'], instance['capacity'], instance['memType'], instance['model']))
        else:
            instance['solved'] = False
            sameSequenceClusters[sortedTitle].append(frozendict(instance))
            return
        
        instance['solved'] = True
        smartClusters[pattern].append(frozendict(instance))
    elif instance['brand'] == 'lexar':
        if instance['memType'] != NO_MEMTYPE and instance['capacity'] != NO_CAPACITY and instance['model'] != NO_MODEL:
            pattern = " || ".join((instance['brand'], instance['capacity'], instance['memType'], instance['model']))
        else:
            instance['solved'] = False
            sameSequenceClusters[sortedTitle].append(frozendict(instance))
            return
        
        instance['solved'] = True
        smartClusters[pattern].append(frozendict(instance))
    elif instance['brand'] == 'intenso':
        if instance['capacity'] != NO_CAPACITY and instance['model'] != NO_MODEL:
            pattern = " || ".join((instance['brand'], instance['capacity'], instance['model']))
        else:
            instance['solved'] = False
            sameSequenceClusters[sortedTitle].append(frozendict(instance))
            return
        
        instance['solved'] = True
        smartClusters[pattern].append(frozendict(instance))
    elif instance['brand'] == 'kingston':
        if instance['memType'] != NO_MEMTYPE and instance['capacity'] != NO_CAPACITY:
            pattern = " || ".join((instance['brand'], instance['capacity'], instance['memType']))
        else:
            instance['solved'] = False
            sameSequenceClusters[sortedTitle].append(frozendict(instance))
            return
        
        instance['solved'] = True
        smartClusters[pattern].append(frozendict(instance))
    elif instance['brand'] == 'toshiba':
        if instance['capacity'] != NO_CAPACITY and instance['memType'] != NO_MEMTYPE and instance['model'] != NO_MODEL:
            pattern = " || ".join((instance['brand'], instance['capacity'], instance['model'], instance['memType']))
        elif instance['capacity'] != NO_CAPACITY and instance['memType'] != NO_MEMTYPE and instance['type'] != NO_TYPE:
            pattern = " || ".join((instance['brand'], instance['capacity'], instance['type'], instance['memType']))
        else:
            instance['solved'] = False
            sameSequenceClusters[sortedTitle].append(frozendict(instance))
            return
        
        instance['solved'] = True
        smartClusters[pattern].append(frozendict(instance))
    elif instance['brand'] == 'transcend':
        if instance['capacity'] != NO_CAPACITY and instance['memType'] != NO_MEMTYPE:
            pattern = " || ".join((instance['brand'], instance['capacity'], instance['memType']))
        else:
            instance['solved'] = False
            sameSequenceClusters[sortedTitle].append(frozendict(instance))
            return
        
        instance['solved'] = True
        smartClusters[pattern].append(frozendict(instance))
    else:
        # TODO: Replace with brand-specific logic
        #instance['solved'] = False
        #sameSequenceClusters[sortedTitle].append(frozendict(instance))
        if instance['brand'] != NO_BRAND and instance['memType'] != NO_MEMTYPE and instance['capacity'] != NO_CAPACITY and instance['model'] != NO_MODEL:
            pattern = " || ".join((instance['brand'], instance['memType'], instance['model'], instance['capacity'], instance['color']))
            instance['solved'] = True
            smartClusters[pattern].append(frozendict(instance))
        else:
            instance['solved'] = False
            sameSequenceClusters[sortedTitle].append(frozendict(instance))

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
        if len(instances)<2000: #skip patterns that are too common
            for i in range(len(instances)):
                for j in range(i + 1, len(instances)):
                    candidate_pairs_2.append((instances[i], instances[j]))

    # remove duplicate pairs and take union
    candidate_pairs_1 = set(candidate_pairs_1)
    candidate_pairs_2 = set(candidate_pairs_2)
    candidate_pairs = list(candidate_pairs_2.union(candidate_pairs_1))
    #
    # candidate_pairs = candidate_pairs_1 + candidate_pairs_2
    
    return findPairs(candidate_pairs, save_scores=save_scores)
