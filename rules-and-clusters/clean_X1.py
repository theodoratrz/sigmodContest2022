import string
import re
import pandas as pd
from collections import defaultdict

customPunctuation = string.punctuation.replace(".", "")

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

cpu_brands = ['intel', 'amd']

intel_cores = [' i3', ' i5', ' i7', '2 duo', 'celeron', 'pentium', 'centrino', 'xeon']
amd_cores = ['e-series', 'a8', 'radeon', 'athlon', 'turion', 'phenom', 'opteron']

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
        
        for b in cpu_brands:
            if b in unique_words:
                cpu_brand = b
                break

        
        frequency_match = re.search(r'[123][ .][0-9]?[0-9]?[ ]?[Gg][Hh][Zz]', cleanedTitle)

    pass