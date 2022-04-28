SUBMISSION_MODE = False
TARGET_DATASET = '2'
IGNORE_DATASET = '1'


NO_BRAND = 'no_brand'
NO_MODEL = 'no_model'
NO_CODE = 'no_code'
NO_TYPE = 'no_type'
NO_CPU = 'no_cpu'
NO_RAM = 'no_ram'
NO_MEMTYPE = 'no_memtype'
NO_COLOR = 'no_color'
NO_CAPACITY = 'no_capacity'

def jaccardSimilarity(a: str, b: str) -> float:
    a_words = set(a.split())
    b_words = set(b.split())
    if len(a_words) == 0 or len(b_words) == 0:
        return 0.0
    
    common = a_words.intersection(b_words)
    return len(common)/max(len(a_words), len(b_words))
