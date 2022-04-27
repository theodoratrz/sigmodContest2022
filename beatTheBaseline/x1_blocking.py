# *Not standard*
from frozendict import frozendict

from typing import List, Dict, Tuple, TypedDict
from collections import defaultdict
import re
import string

from utils import NO_BRAND, NO_CPU, NO_MODEL, NO_RAM, jaccardSimilarity

class X1Instance(TypedDict):
    id: int
    title: str
    brand: str
    model: str
    cpu: str
    ram: str

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

brandModels = {
    'lenovo': [
        r'thinkpad [a-z][0-9]{1,3}[t]?( \w+)?( \w+)? [0-9]{4}',
        r'thinkpad [a-z][0-9]{1,3}[t]?', 
        r'[a-z][0-9]{1,3}[t]?( \w+)?( [0-9]{4})?',
        r'x1 carbon',
        r'thinkpad',
        r'ideapad',
        r'flex',
        r'yoga',
    ]
}
models = [
    r'thinkpad [a-z][0-9]{1,3}[te]?( \w+)?( \w+)? [0-9]{4}',
    r'thinkpad [a-z][0-9]{1,3}[te]?', 
    r'elitebook (folio )?[0-9]{4}[a-z]?',
    r'aspire [a-z][0-9] (\w+|\d+) (\w+|\d+)[ $]',
    r'[a-z][0-9]{1,3}[te]?( \w+)?( [0-9]{4})?', 
    
    r'x1 carbon', r'thinkpad', r'ideapad', r'flex', r'yoga',
    
    r'elitebook', r'compaq', r'folio', r'pavilion', r'zbook', r'envy',

    r'inspiron', r'latitude', r'precision', r'vostro', r'xps',
    r'zenbook', r'vivobook', r'rog', r'chromebook',
    r'aspire', r'extensa',
    r'toughbook',
    r'satellite', r'portege',
    r'vaio'
]
modelPattern = re.compile('|'.join(models))

cpus = [
    # intel
    r'(^| )i[357]( [0-9]{3,4}[q]?(lm|[mu]))',
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

ramCapacityPattern = r'(2|4|8|16|32)[ ]?gb'

numberPattern = r'[0-9]+(\.[0-9]+)?'
NUMBER_WEIGHT = 0.15
wordPattern = r'(?=\D)[\w]+'
WORD_WEIGHT = 0.2
BRAND_WEIGHT = 0.5
ALPHANUMERIC_WEIGHT = 1

SOLVED_PAIR_SCORE = float(10.1)
REJECTED_PAIR_SCORE = float(-10.1)

def getSimilarityScore(a: X1Instance, b: X1Instance) -> float:

    if a['cpu'] == b['cpu'] and a['model'] == b['model'] and a['model'] != NO_MODEL:
        if a['brand'] == 'lenovo' and len(a['model']) >= 8:
            if a['cpu'] != NO_CPU and len(a['cpu']) >= 5:
                return SOLVED_PAIR_SCORE
        elif a['brand'] == 'hp' and len(a['model']) >= 9:
            if a['cpu'] != NO_CPU and len(a['cpu']) >= 5:
                return SOLVED_PAIR_SCORE
        elif a['brand'] == 'acer' and len(a['model']) >= 6:
            if a['cpu'] != NO_CPU and len(a['cpu']) >= 5:
                return SOLVED_PAIR_SCORE
        
        # Both have different RAM or different CPU, reject.
    #     return REJECTED_PAIR_SCORE
    # elif a['brand'] == 'acer' and a['model'] == b['model'] and len(a['model']) >= 6:
    #     if a['cpu'] != NO_CPU and b['cpu'] != NO_CPU and a['cpu'] != b['cpu']:
    #         return REJECTED_PAIR_SCORE
    #     elif a['ram'] != NO_RAM and b['ram'] != NO_RAM and a['ram'] != b['ram']:
    #         return REJECTED_PAIR_SCORE
    #     if a['cpu'] == b['cpu'] or a['ram'] == b['ram']:
    #         return SOLVED_PAIR_SCORE

    a_words = set(a['title'].split())
    b_words = set(b['title'].split())
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

def acer_preprocessing(rawTitle: str, model: str) -> Tuple[str, str]:
    newModel = model
    ram = NO_RAM

    match = re.search(r'[a-z][0-9]-(\w+|\d+)-(\w+|\d+)[ $]', rawTitle)
    if match:
        match = re.match(r'[a-z][0-9]-(\w+|\d+)', match.group())
        if match:
            newModel = match.group()
    
    match = re.search(ramCapacityPattern, rawTitle)
    if match:
        ram = re.search(r'[0-9]+', match.group()).group()
    
    return newModel , ram

def hp_preprocessing(title: str, model: str) -> Tuple[str, str]:
    newModel = re.sub(r'(elitebook|folio|elitebook folio)', r'ebf', model)
    ram = NO_RAM
    match = re.search(ramCapacityPattern, title)
    if match:
        ram = re.search(r'[0-9]+', match.group()).group()
    
    return re.sub(' +', ' ', newModel).strip(), ram

def lenovo_processing(title: str, model: str) -> Tuple[str, str]:

    newModel = re.sub(r'(touch|thinkpad)', '', model)
    newModel = re.sub(r'3435[a-z0-9]{3}', r'3435', newModel)
    newModel = re.sub(r'tablet 3435', r'2320', newModel)
    newModel = re.sub(r'x230[t]? 3435', r'x230 2320', newModel)
    #newModel = model.replace('tablet 3435', '2320')\
    #                .replace('x230t 3435', 'x230 2320')

    newModel = re.sub(r'(4291|4287)', r'4290', newModel)
    newModel = re.sub(r'2339', r'2338', newModel)
    
    if re.search(r'x[0-9]{3}e', newModel):
        match = re.search(r'e-[0-9]{3}', title)
        if match:
            newModel = newModel + ' ' + match.group()

    ram = NO_RAM
    match = re.search(ramCapacityPattern, title)
    if match:
        ram = re.search(r'[0-9]+', match.group()).group()

    return re.sub(' +', ' ', newModel).strip(), ram

def x1_blocking(csv_reader, id_col: str, title_col: str, save_scores=False) -> List[Tuple[int, int]]:
    """
    This function performs blocking on X1 dataset.
    :param `X`: dataframe
    :return: candidate set of tuple pairs
    """

    sameSequencePatterns: Dict[str, List[ X1Instance ]] = defaultdict(list)
    modelPatterns: Dict[str, List[ X1Instance ]] = defaultdict(list)

    for i, row in enumerate(csv_reader):
        instanceId = int(row[id_col])
        rawTitle = str(row[title_col]).lower()

        noTrash = re.sub(trashPattern, '', rawTitle)
        cleanedTitle = noTrash.translate(str.maketrans({ord(c): ' ' for c in customPunctuation}))
        cleanedTitle = re.sub(' +', ' ', cleanedTitle).strip()

        clean_words = cleanedTitle.split()
        clean_words.sort()
        unique_words = {word: None for word in clean_words}.keys()
        sortedTitle = ' '.join(unique_words)
        
        brands = []
        for brand in brandPatterns:
            match = re.search(brand, sortedTitle)
            if match:
                brands.append(match.group())
        brand = ' & '.join(brands) if len(brands) else NO_BRAND
        
        #model = modelPattern.search(cleanedTitle)
        #if not model:
        #    model = NO_MODEL
        #else:
        #    model = model.group()
        model = NO_MODEL
        for m in models:
            match = re.search(m, cleanedTitle)
            if match:
                model = match.group()
                break

        ram = NO_RAM
        if brand == 'lenovo':
            model, ram = lenovo_processing(rawTitle, model)
        elif brand == 'hp':
            model, ram = hp_preprocessing(rawTitle, model)
        elif brand == 'acer':
            model, ram = acer_preprocessing(rawTitle, model)

        cpu = NO_CPU
        for pattern in cpus:
            match = re.search(pattern, cleanedTitle)
            if match:
                cpu = match.group().strip()
                break

        #instance = (instanceId, cleanedTitle)
        instance: X1Instance = frozendict({
            'id': instanceId,
            'title': cleanedTitle,
            'brand': brand,
            'model': model,
            'cpu': cpu,
            'ram': ram
        })

        if brand == 'lenovo' and model != NO_MODEL and len(model) >= 8:
            pattern = " || ".join((brand, model, cpu, ram))
            modelPatterns[pattern].append(instance)
        elif brand == 'hp' and model != NO_MODEL and len(model) >=9:
            #pattern = " || ".join((brand, model, cpu, ram))
            pattern = " || ".join((brand, model))
            modelPatterns[pattern].append(instance)
        elif brand == 'acer' and model != NO_MODEL and len(model) >= 6:
            pattern = " || ".join((brand, model))
            #pattern = " || ".join((brand, model, cpu, ram))
            modelPatterns[pattern].append(instance)
        elif model != NO_MODEL and cpu != NO_CPU:
            pattern = " || ".join((brand, model, cpu, ram))
            modelPatterns[pattern].append(instance)        

        sameSequencePatterns[sortedTitle].append(instance)

    # add id pairs that share the same pattern to candidate set
    candidate_pairs_1: List[Tuple[X1Instance, X1Instance]] = []
    for pattern in sameSequencePatterns:
        instances = sameSequencePatterns[pattern]
        for i in range(len(instances)):
            for j in range(i + 1, len(instances)):
                candidate_pairs_1.append((instances[i], instances[j])) #
    # add pairs that share the same pattern to candidate set
    candidate_pairs_2: List[Tuple[X1Instance, X1Instance]] = []
    for pattern in modelPatterns:
        instances = modelPatterns[pattern]
        if len(instances)<500: #skip patterns that are too common
            for i in range(len(instances)):
                for j in range(i + 1, len(instances)):
                    candidate_pairs_2.append((instances[i], instances[j]))

    # remove duplicate pairs and take union
    candidate_pairs_1 = set(candidate_pairs_1)
    candidate_pairs_2 = set(candidate_pairs_2)
    candidate_pairs: List[Tuple[X1Instance, X1Instance]] = list(candidate_pairs_2.union(candidate_pairs_1))

    # sort candidate pairs by jaccard similarity.
    # In case we have more than 1000000 pairs (or 2000000 pairs for the second dataset),
    # sort the candidate pairs to put more similar pairs first,
    # so that when we keep only the first 1000000 pairs we are keeping the most likely pairs
    jaccard_similarities = []
    candidate_pairs_real_ids: List[Tuple[int, int]] = []
    for pair in candidate_pairs:
        #(id1, name1), (id2, name2) = pair
        instance1, instance2 = pair

        if instance1['id'] < instance2['id']: # NOTE: This is to make sure in the final output.csv, for a pair id1 and id2 (assume id1<id2), we only include (id1,id2) but not (id2, id1)
            candidate_pairs_real_ids.append((instance1['id'], instance2['id']))
        else:
            candidate_pairs_real_ids.append((instance2['id'], instance1['id']))

        score = getSimilarityScore(instance1, instance2)
        if score > REJECTED_PAIR_SCORE:
            jaccard_similarities.append(score)

    if save_scores:
        candidate_pairs_real_ids = [(pair[0], pair[1], score) for pair, score in sorted(zip(candidate_pairs_real_ids, jaccard_similarities), key=lambda t: t[1], reverse=True)]
    else:
        candidate_pairs_real_ids = [x for _, x in sorted(zip(jaccard_similarities, candidate_pairs_real_ids), reverse=True)]
    return candidate_pairs_real_ids
