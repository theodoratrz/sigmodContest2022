from typing import List
import string

THRESHOLD = 0.835
def looksSimilar(words1: List[str], words2: List[str]):
    common = len(set(words1).intersection(set(words2)))
    return ( 2*common / (len(words1) + len(words2)) ) >= THRESHOLD

def cleanInstance(raw: str):
    raw_low = raw.lower()
    no_punct = raw_low.translate(str.maketrans({ord(c): ' ' for c in string.punctuation}))
    words = no_punct.split()
    words.sort()

    return words, ' '.join(words)
