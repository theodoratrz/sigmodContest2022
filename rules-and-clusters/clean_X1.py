import string
import re
import pandas as pd
from collections import defaultdict

customPunctuation = string.punctuation.replace(".", "")

RAM_PATTERN = r'[13]?[268][\s]?[g][b][\s]?((s[d][r][a][m])|(d[d][r]3)|([r][a][m])|(Memory))'

FREQUENCY_PATTERN = r'[123][ .][0-9]?[0-9]?[ ]?[g][h][z]'

brandPatterns = { 
    'dell': r'dell',
    'lenovo': r'lenovo',
    'acer': r'acer',
    'asus': r'asus',
    'hp': r'h(ewlett )?p(ackard)?',
    'panasonic': r'pan(a)?sonic',
    'apple': r'apple',
    'toshiba': r'toshiba',
    'samsung': r'samsung',
    'sony': r'sony'}
brandNames = brandPatterns.keys()
UNKNOWN_BRAND = 'unknown_brand'

cpuBrandCores = {
    'intel': ['i3', 'i5', 'i7', '2 duo', 'celeron', 'pentium', 'centrino', 'xeon'],
    'amd': ['e-series', 'a8', 'radeon', 'athlon', 'turion', 'phenom', 'opteron']
}

amdSpecialCores = {'radeon', 'athlon', 'turion', 'phenom'}
amdSpecialPatterns = {r'[np][0-9]{3}', r'(64[ ]?[x]2)|([n][e][o])'}

cpuBrandModels = {
    'intel': [
        r'[0-9]{4}[q]?[mu]',
        r'[0-9]{3}[q]?[mu]',
        r'[pnt][0-9]{4}',
        r'[0-9]{4}[y]',
        r'[s]?[l][0-9]{4}',
        r'((1st)|(2nd)|(3rd)|([4-9]th))[ ][g]en'
    ],
    'amd': [
        r'([ae][0-9][ ][0-9]{4})',
        r'hd[ ][0-9]{4}'
    ]
}

cpuBrands = cpuBrandCores.keys()

brandModels = {
    'lenovo': [
        r'[0-9]{4}[0-9a-z]{3}(?![0-9a-z])',
        r'[0-9]{4}(?![0-9a-z])'
    ],
    'hp': [
        r'15[ ][a-z][0-9]{3}[a-z]{2}',
        r'810[\s](g2)?',
        r'[0-9]{4}[m]',
        r'((dv)|(nc))[0-9]{4}',
        r'[0-9]{4}dx'
    ],
    'dell': [
        r'1[57][r]?[\s]?([0-9]{4})?[\s]([i])?[0-9]{4}',
        r'[a-z][0-9]{3}[a-z][\s]'
    ],
    'acer': [
        r'[a-z][0-9][ ][0-9]{3}',
        r'as[0-9]{4}',
        r'[0-9]{4}[ ][0-9]{4}'
    ],
    'asus': [
        r'[a-z]{2}[0-9]?[0-9]{2}[a-z]?[a-z]'
    ]
}

families = {
    'hp': [r'elitebook', r'compaq', r'folio', r'pavilion', r'zbook', r'envy'],
    'lenovo': [r'thinkpad x[0-9]{3}[t]?', r' x[0-9]{3}[t]?', r'x1 carbon', r'ideapad', r'flex', r'yoga'],
    'dell': [r'inspiron', r'latitude', r'precision', r'vostro', r'xps'],
    'asus': [r'zenbook', r'vivobook', r'rog', r'chromebook'],
    'acer': [r'aspire', r'extensa' ],
    'panasonic': [r'toughbook'],
    'apple': [],
    'samsung': [],
    'toshiba': [r'satellite', r'portege'],
    'sony': [r'vaio'],
    '0': []
}

trash = [ r"amazon",
                r"alibaba",
                r"com:",
                r"\d+ ?[Tt][Bb]",
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
                r"win(dows)? (xp|7|8.1|8|10)( pro(fessional)?| home premium)? ?((64|32)-bit)?",
                r"notebook",
                r"led",
                r"ips",
                r"processor",
                r"core",
                r"[\(\):&]",
                r"\"",
                r"''",
                r",",
                r"-",
                r" +$",
                r"\|",
                r"e[Bb]ay",
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

def clean_X1(dataset: pd.Dataframe):
    
    idTitle = {}
    for i, row in dataset.iterrows():
        idTitle[row['id']] = row['title']

        # Clean title
        raw_low = row['title'].lower()
        cleanedTitle = raw_low.translate(str.maketrans({ord(c): ' ' for c in customPunctuation}))
        cleanedTitle = re.sub(' +', ' ', cleanedTitle)
        clean_words = cleanedTitle.split()
        clean_words.sort()
        unique_words = set(clean_words)
    
        brand = '0'
        cpu_brand = '0'
        cpu_core = '0'
        cpu_model = '0'
        cpu_frequency = '0'
        ram_capacity = '0'
        name_number = '0'
        name_family = '0'


        brandsFound = []
        for brand in enumerate(brandNames):
            if brand in unique_words:
                brandsFound.append(brand)
        
        if len(brandsFound) == 0:
            brandsFound.append(UNKNOWN_BRAND)
        
        for b in cpuBrands:
            if b in unique_words:
                cpu_brand = b
                for core in cpuBrandCores[cpu_brand]:
                    if core in cleanedTitle:
                        cpu_core = core
                        break
                break
        
        frequency_match = re.search(FREQUENCY_PATTERN, cleanedTitle)
        if frequency_match is not None:
            frequency_match = re.split(r'[ghz]', frequency_match.group())[0].strip().replace(' ', '.')

            # Convert "3(ghz)" to "3.00"
            if len(frequency_match) == 1:
                frequency_match = frequency_match + '.00'
            # Match "3.2(ghz) to 3.20"
            if len(frequency_match) == 3:
                frequency_match = frequency_match + '0'
            # "3.22" is fine

            cpu_frequency = frequency_match
        
        ram_match = re.search(RAM_PATTERN, cleanedTitle)
        if ram_match is not None:
            ram_capacity = ram_match

        matchedModel = None
        if cpu_brand != '0':
            for modelPattern in cpuBrandModels[cpu_brand]:
                matchedModel = re.search(modelPattern, cleanedTitle)
                if matchedModel is not None:
                    cpu_model = matchedModel.group()
                    break
            
            if (cpu_brand == 'amd') and matchedModel is None:
                if cpu_core in amdSpecialCores:
                    for pattern in amdSpecialPatterns:
                        matchedModel = re.search(pattern, cleanedTitle)
                        if matchedModel is not None:
                            cpu_model = matchedModel.group()
                            break
    pass
