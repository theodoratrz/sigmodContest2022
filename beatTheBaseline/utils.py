import re
import string


SUBMISSION_MODE = True

NO_BRAND = 'no_brand'
NO_MODEL = 'no_model'
NO_CPU = 'no_cpu'
NO_MEMTYPE = 'no_memtype'
NO_COLOR = 'no_color'
NO_CAPACITY = 'no_capacity'

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
