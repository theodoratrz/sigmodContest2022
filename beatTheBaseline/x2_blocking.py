# *Not standard*
from frozendict import frozendict

from typing import Iterable, List, Dict, Tuple, TypedDict
from collections import defaultdict
import re
import csv
import string

from utils import NO_BRAND, NO_MODEL, NO_MEMTYPE, NO_TYPE, NO_CAPACITY, NO_COLOR, jaccardSimilarity


class X2Instance(TypedDict):
    id: int
    title: str
    brand: str
    memType: str
    model: str
    type: str
    capacity: str
    color: str
    solved: bool

customPunctuation = string.punctuation.replace('.', '').replace('-', '').replace('+', '')

trashPhrases = [
    r"[a-z]+(\.com|\.ca|\.es|\.de|\.fr)",
    r"com:",
    r"amazon",
    r"clé",
    r"tesco",
    r"mediamarkt",
    r"alibaba",
    r"vology",
    r"downgrade",
    r"brand new",
    r"china",
    r"buy",
    r"famous",
    r"australia",
    r"(online in )?egypt",
    r"online",
    r"accessories",
    r"wholeshale",
    r"ebay",
    r"best",
    r"kids",
    r"general",
    r"cheap",
    r"with",
    r"great",
    r"product",
    r"quality",
    #r"flash",
    r"memory",
    r"tarjeta",
    r"m[eé]mo(ria|ire)",
    r"class[e]? "
]
trashPattern = re.compile('|'.join(trashPhrases))

brandPatterns = [
    r"sony",
    r"toshiba",
    r"kingston",
    r"sandisk",
    r"intenso",
    r"lexar",
    r"transcend",
    r"samsung",
    r"pny"
]
brandPattern = re.compile('|'.join(brandPatterns))

memTypePatterns = {
    "sim": [r'lte'],
    "ssd": [r'ssd'],
    "xqd": [r'xqd'],
    "microsd": [r'micro[- ]?sd[hx]?c?', ],
    "sd": [r'sd[hx]c', r'(secure.*?digital|digital.*?secure)', r'sd(?!cz)', r'exceria'],
    "usb": [r'ljd', r'usb', r'transmemory', r'hyperx', r'savage', r'cruzer', r'glide', r'fit', r'flash', r'hx'],
}
memTypeExtra = {
    "microsd": [r'adapter', r'adaptateur', r'adaptor'],
    "usb": [r'drive']
}
# Use these with `re.search` only.
separatedMicroPattern = r'(^| )micro($| )'
separatedSdPattern = r'(^| )sd[hx]?c?($| )'

modelPatterns = {
    "sony": {
        r'(sf|usm)[-]?[0-9a-z]{1,6}': None,
        r'serie[s]': None,
        "sony_microsd": [r'ux', r'uy', r'sr'],
        "sony_sd": [r'uf'],
        "sony_usb": [r'usm']
    },
    "toshiba": {
        r'[mnu][0-9]{3}': None,
        "xpro": [r'exceria( |.*)pro'],
        "xhigh": [r'exceria( |.*)high'],
        "xplus": [r'exceria( |.*)plus'],
        "x": [r'exceria']
    },
    "kingston": {
        r'dt([a-z]?[0-9])': None,
        "hyperx": [r'hx', r'hyperx'],
        r"savage": None,
        r"ultimate": None,
        "dt": r'data[ ]?traveler'
    },
    "sandisk": {
        "ext+": [r'ext.*(\s)?((plus)|(pro)|\+)'],
        "ultra+": [r'ultra.*(\s)?((plus)|(pro)|(performance)|\+)'],
        "ultra": [r'ultra', r'dual', r'double connect.*'],
        "ext": [r'ext(reme)'],
        r'glide': None,
        r'blade': None,
        r'fit': None
    },
    "intenso": {
        r'[0-9]{7}': None,
        r'(high\s)?[a-z]+\s(?=line)': None,
        r"basic": None,
        r"rainbow": None,
        r"high speed": None,
        r"speed": None,
        r"premium": None,
        r"alu": None,
        r"business": None,
        r"micro": None,
        r"imobile": None,
        r"cmobile": None,
        r"mini": None,
        r"ultra": None,
        r"slim": None,
        r"flash": None,
        r"mobile": None
    },
    "lexar": {
        #r"ljd[\w]+": None,
        r'jumpdrive [a-z][0-9]{2}[a-z]?': None,
        r"ljd[a-z][0-9]{2}[-\s]?[0-9]{1,3}": None,
        "1400x": [r'([0-9]{4}x|x[0-9]{4})']
    },        
    "transcend": {
        r"ts[0-9]{1,3}": None,
        "transcend_sd": [r'sd[hx]c', r'(secure.*?digital|digital.*?secure)', r'sd(?!cz)'],
        "transcend_usb": [r'usb', r'flash'],
    },        
    "samsung": {
        # patterns missing
        r"galaxy [ajs][0-9]{1,2}( (plus|ultra))?": None,
        r"galaxy note[ ]?[0-9]{1,2}( (plus|ultra))?": None,
    },
    "pny": {
        "att 3": [r'att.*?[3]'],
        "att 4": [r'att.*?[4]']
    },
    #r"lsd[\w]+": [],
    #r"thn[\w]+": [],
}

intensoIdToModel = {
    "3502450": "rainbow",
    "3502460": "rainbow",
    "3502470": "rainbow",
    "3502480": "rainbow",
    "3502490": "rainbow",
    "3502491": "rainbow",
    "3503460": "basic",
    "3503470": "basic",
    "3503480": "basic",
    "3503490": "basic",
    "3533470": "speed",
    "3533480": "speed",
    "3533490": "speed",
    "3533491": "speed",
    "3533492": "speed",
    "3534460": "premium",
    "3534470": "premium",
    "3534480": "premium",
    "3534490": "premium",
    "3534491": "premium",
    "3521451": "alu",
    "3521452": "alu",
    "3521462": "alu",
    "3521471": "alu",
    "3521472": "alu",
    "3521481": "alu",
    "3521482": "alu",
    "3521480": "alu",
    "3521491": "alu",
    "3521492": "alu",
    "3511460": "business",
    "3511470": "business",
    "3511480": "business",
    "3511490": "business",
    "3500450": "micro",
    "3500460": "micro",
    "3500470": "micro",
    "3500480": "micro",
    "3523460": "mobile",
    "3523470": "mobile",
    "3523480": "mobile",
    "3524460": "mini",
    "3524470": "mini",
    "3524480": "mini",
    "3531470": "ultra",
    "3531480": "ultra",
    "3531490": "ultra",
    "3531491": "ultra",
    "3531492": "ultra",
    "3531493": "ultra",
    "3532460": "slim",
    "3532470": "slim",
    "3532480": "slim",
    "3532490": "slim",
    "3532491": "slim",
    "3537490": "highspeed",
    "3537491": "highspeed",
    "3537492": "highspeed",
    "3535580": "imobile",
    "3535590": "imobile",
    "3536470": "cmobile",
    "3536480": "cmobile",
    "3536490": "cmobile",
    "3538480": "flash",
    "3538490": "flash",
    "3538491": "flash"
}

colors = [
    'midnight black',
    'prism white',
    'prism black',
    'prism green',
    'prism blue',
    'canary yellow',
    'flamingo pink',
    'cardinal red',
    'smoke blue',
    'deep blue',
    'coral orange',
    'black sky',
    'gold sand',
    'blue mist and peach cloud',
    'orchid gray',
    'metallic copper',
    'lavender purple',
    'ocean blue',
    'pure white',
    'alpine white',
    'copper',
    'red',
    'black',
    'blue',
    'white',
    'silver',
    'gold',
    'violet',
    'purple',
    'brown',
    'orange',
    'coral',
    'pink'
]
#modelPattern = re.compile('|'.join(models))

@staticmethod
def unifyCapacities(s: str):
    separatedCapacity = r'(?P<size>[0-9]{1,3}) (?P<unit>[gt]b)'

    return re.sub(separatedCapacity, r'\g<size>\g<unit>', s)

separatedCapacityPattern = r'(?P<size>[0-9]{1,3}) (?P<unit>[gt][bo])'
unifiedCapacityPattern = r'\g<size>\g<unit>'
capacityPattern = r'[0-9]{1,3}[gt][bo]'
# Use these with `re.search` only.
capacityUnitPattern = r'(^| )g[bo]($| )'
capacitySizesPattern = r'(^| )(4|8|16|32|64|128|256|512)($| )'

numberPattern = r'[0-9]+(\.[0-9]+)?'
NUMBER_WEIGHT = 0.1
wordPattern = r'(?=\D)[\w]+'
WORD_WEIGHT = 0.2
BRAND_WEIGHT = 0.6
CAPACITY_WEIGHT = 0.4
ALPHANUMERIC_WEIGHT = 0.75
ALPHANUMERIC_BONUS_WEIGHT = 1.25
ALPHANUMERIC_BONUS_LENGTH = 4

REJECT_SCORE = -1
SOLVED_PAIR_SCORE = float(10.1)

def getSimilarityScore(a: X2Instance, b: X2Instance) -> float:

    #if a["solved"] and b["solved"]:
    #    return X2Utils.SOLVED_PAIR_SCORE

    a_words = set(a["title"].split())
    b_words = set(b["title"].split())
    if len(a_words) == 0 or len(b_words) == 0:
        return 0.0
    
    common = a_words.intersection(b_words)

    weighted_sum = 0
    hasBonus = False
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
            if re.fullmatch(capacityPattern, word):
                weighted_sum += CAPACITY_WEIGHT
            else:
                if len(word) >= ALPHANUMERIC_BONUS_LENGTH:
                    weighted_sum += (ALPHANUMERIC_BONUS_WEIGHT * (len(word)/ALPHANUMERIC_BONUS_LENGTH))
                    hasBonus = True
                else:
                    weighted_sum += ALPHANUMERIC_WEIGHT
    
    #if not hasBonus:
    #    if a["capacity"] == NO_CAPACITY and b["capacity"] == a["capacity"]:
    #        return REJECT_SCORE
    
    return weighted_sum/max(len(a_words), len(b_words))


def findBrands(title: str, brandColumn: str):
    brands = []
    for brand in brandPatterns:
        match = re.search(brand, title)
        if match:
            brands.append(match.group())
    if len(brands):
        brand = ' & '.join(brands)
    else:
        match = re.fullmatch(brandPattern, str(brandColumn).lower())
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

        score = jaccardSimilarity(instance1['title'], instance2['title'])
        #score = getSimilarityScore(instance1, instance2)
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
    for mem in memTypePatterns:
        if memType == NO_MEMTYPE:
            for pattern in memTypePatterns[mem]:
                if re.search(pattern, cleanedTitle):
                    memType = mem
                    break
        else:    
            break
    for mem in memTypeExtra:
        if memType == NO_MEMTYPE:
            for pattern in memTypeExtra[mem]:
                if re.search(pattern, cleanedTitle):
                    memType = mem
                    break
        else:
            break

    capacity = re.search(capacityPattern, cleanedTitle)
    if not capacity:
        # The capacity is probably separated (and shuffled)
        unitMatch = re.search(capacityUnitPattern, sortedTitle)
        if unitMatch:
            sizeMatch = re.search(capacitySizesPattern, sortedTitle)
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
        for pattern in modelPatterns['intenso']:
            match = re.search(pattern, cleanedTitle)
            if match:
                model = match.group()
                break

        if model in intensoIdToModel.keys():
            model = intensoIdToModel[model]
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
                for key in modelPatterns[b]:
                    if model == NO_MODEL:
                        if modelPatterns[b][key] is None:
                            # key is a regex
                            match = re.search(key, cleanedTitle)
                            if match:
                                model = match.group()
                                break
                        else:
                            # key is model category
                            for pattern in modelPatterns[b][key]:
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
        for c in colors:
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