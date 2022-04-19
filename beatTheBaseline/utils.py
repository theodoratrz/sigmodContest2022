import re
import string
from typing import Dict


SUBMISSION_MODE = False

class NamespaceX1:

    punctuation = string.punctuation.replace(".", "")

    trash = [
        r"[a-z]+.com",
        r"[a-z]+.ca",
        r"win(dows)? (xp|7|8.1|8|10)( pro(fessional)?| home premium)? ?((64|32)-bit)?",
        r"com:"
        r"amazon",
        r"alibaba",
        r"\d+ ?[t][b]",
        #r"\d+ ?[g][b]",
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
        r"wholeshale"
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
        r'thinkpad [a-z][0-9]{1,3}[t]?( \w+)? [0-9]{4}', r'thinkpad [a-z][0-9]{1,3}[t]?', 
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
        r'(intel )?(core )?i3( [0-9]{3,4}[q]?[mu])?',
        r'(intel )?(core )?i5( [0-9]{3,4}[q]?[mu])?',
        r'(intel )?(core )?i7( [0-9]{3,4}[q]?[mu])?',
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

    @staticmethod
    def getSimilarityScore(a: str, b: str) -> float:

        a_words = set(a.split())
        b_words = set(b.split())
        if len(a_words) == 0 or len(b_words) == 0:
            return 0.0
        
        common = a_words.intersection(b_words)

        weighted_sum = 0
        for word in common:
            match = re.fullmatch(NamespaceX1.wordPattern, word)
            if match:
                # Character-only word
                if NamespaceX1.brandPattern.fullmatch(match.group()):
                    # Brand
                    weighted_sum += NamespaceX1.BRAND_WEIGHT
                else:
                    weighted_sum += NamespaceX1.WORD_WEIGHT
            elif re.fullmatch(NamespaceX1.numberPattern, word):
                # Number
                weighted_sum += NamespaceX1.NUMBER_WEIGHT
            else:
                # Alphanumeric string
                weighted_sum += NamespaceX1.ALPHANUMERIC_WEIGHT

        return weighted_sum/max(len(a_words), len(b_words))

class NamespaceX2:

    punctuation = re.sub(r'[.-]', '', string.punctuation)

    trash = [
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
        r"flash",
        r"drive",
        r"memory",
        r"tarjeta",
        r"m[eé]mo(ria|ire)",
        r"class[e]? "
    ]
    trashPattern = re.compile('|'.join(trash))

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
        "sd": [r'sd[hx]c', r'(secure.*?digital|digital.*?secure)', r'sd(?!cz)'],
        "usb": [r'ljd', r'usb', r'transmemory', r'hyperx', r'savage', r'cruzer', r'glide', r'fit', r'hx'],
    }
    memTypeLanguagePatterns = {
        "microsd": [r'adapter', r'adaptateur', r'adaptor'],
        "usb": [r'drive']
    }
    # Use these with `re.search` only.
    separatedMicroPattern = r'(^| )micro($| )'
    separatedSdPattern = r'(^| )sd[hx]?c?($| )'

    modelPatterns = {
        "sony": {
            r'(sf|usm)[-]?[0-9]{1,3}': None,
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
            r'dt([a-z]?[0-9])': None
        },
        "sandisk": {
            "ext+": [r'ext.*(\s)?((plus)|(pro)|\+)'],
            "ultra+": [r'ultra.*(\s)?((plus)|(pro)|\+)'],
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
            r"ljd[a-z][0-9]{2}[-\s]?[0-9]{1,3}": None,
        },        
        "transcend": {
            r"ts[0-9]{1,3}": None
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
    
    separatedCapacityPattern = r'(?P<size>[0-9]{1,3}) (?P<unit>[gt]b)'
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

    NO_CAPACITY = 'no_capacity'
    REJECT_SCORE = -1

    @staticmethod
    def getSimilarityScore(a: Dict[str, str], b: Dict[str, str]) -> float:

        a_words = set(a["title"].split())
        b_words = set(b["title"].split())
        if len(a_words) == 0 or len(b_words) == 0:
            return 0.0
        
        common = a_words.intersection(b_words)

        weighted_sum = 0
        hasBonus = False
        for word in common:
            match = re.fullmatch(NamespaceX2.wordPattern, word)
            if match:
                # Character-only word
                if NamespaceX2.brandPattern.fullmatch(match.group()):
                    # Brand
                    weighted_sum += NamespaceX2.BRAND_WEIGHT
                else:
                    weighted_sum += NamespaceX2.WORD_WEIGHT
            elif re.fullmatch(NamespaceX2.numberPattern, word):
                # Number
                weighted_sum += NamespaceX2.NUMBER_WEIGHT
            else:
                # Alphanumeric string
                if re.fullmatch(NamespaceX2.capacityPattern, word):
                    weighted_sum += NamespaceX2.CAPACITY_WEIGHT
                else:
                    if len(word) >= NamespaceX2.ALPHANUMERIC_BONUS_LENGTH:
                        weighted_sum += (NamespaceX2.ALPHANUMERIC_BONUS_WEIGHT * (len(word)/NamespaceX2.ALPHANUMERIC_BONUS_LENGTH))
                        hasBonus = True
                    else:
                        weighted_sum += NamespaceX2.ALPHANUMERIC_WEIGHT
        
        if not hasBonus:
            if a["capacity"] == NamespaceX2.NO_CAPACITY and b["capacity"] == a["capacity"]:
                return NamespaceX2.REJECT_SCORE
        
        return weighted_sum/max(len(a_words), len(b_words))
