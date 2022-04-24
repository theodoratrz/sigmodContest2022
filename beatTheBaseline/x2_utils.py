from typing import TypedDict
import re
import string


# Might be needed
# from utils import NO_BRAND, NO_MODEL, NO_MEMTYPE, NO_CAPACITY, NO_COLOR

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

class X2Utils:

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

    @staticmethod
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
            match = re.fullmatch(X2Utils.wordPattern, word)
            if match:
                # Character-only word
                if X2Utils.brandPattern.fullmatch(match.group()):
                    # Brand
                    weighted_sum += X2Utils.BRAND_WEIGHT
                else:
                    weighted_sum += X2Utils.WORD_WEIGHT
            elif re.fullmatch(X2Utils.numberPattern, word):
                # Number
                weighted_sum += X2Utils.NUMBER_WEIGHT
            else:
                # Alphanumeric string
                if re.fullmatch(X2Utils.capacityPattern, word):
                    weighted_sum += X2Utils.CAPACITY_WEIGHT
                else:
                    if len(word) >= X2Utils.ALPHANUMERIC_BONUS_LENGTH:
                        weighted_sum += (X2Utils.ALPHANUMERIC_BONUS_WEIGHT * (len(word)/X2Utils.ALPHANUMERIC_BONUS_LENGTH))
                        hasBonus = True
                    else:
                        weighted_sum += X2Utils.ALPHANUMERIC_WEIGHT
        
        #if not hasBonus:
        #    if a["capacity"] == NO_CAPACITY and b["capacity"] == a["capacity"]:
        #        return X2Utils.REJECT_SCORE
        
        return weighted_sum/max(len(a_words), len(b_words))
