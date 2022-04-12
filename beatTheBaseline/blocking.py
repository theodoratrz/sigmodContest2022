from typing import List, Dict, Tuple

from collections import defaultdict
import string
import re

import pandas as pd

trash = [
    r"amazon",
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
trashPattern = re.compile('|'.join(trash))

customPunctuation = string.punctuation.replace(".", "")

def x2_blocking(X: pd.DataFrame) -> List[Tuple[int, int]]:
    return []

def x1_blocking(X: pd.DataFrame) -> List[Tuple[int, int]]:
    """
    This function performs blocking on X1 dataset.
    :param `X`: dataframe
    :return: candidate set of tuple pairs
    """

    attr = 'title'

    # build index from patterns to tuples
    sameSequencePatternToId: Dict[str, List[int]] = defaultdict(list)
    modelPatternToId: Dict[str, List[int]] = defaultdict(list)

    for i, row in X.iterrows():
        id = row['id']
        rawTitle = str(row['title']).lower()
        noTrash = re.sub(trashPattern, '', rawTitle)
        cleanedTitle = noTrash.translate(str.maketrans({ord(c): ' ' for c in customPunctuation}))
        cleanedTitle = re.sub(' +', ' ', cleanedTitle).strip()
        clean_words = cleanedTitle.split()
        clean_words.sort()
        unique_words = {word: None for word in clean_words}.keys()
        sortedTitle = ' '.join(unique_words)

        sameSequencePatternToId[sortedTitle].append(i)

        possibleModels = re.findall("\w+\s\w+\d+", cleanedTitle)  # look for patterns like "thinkpad x1"
        if len(possibleModels) > 0:
            possibleModels = list(sorted(possibleModels))
            possibleModels = [str(m).lower() for m in possibleModels]
            modelPatternToId[" ".join(possibleModels)].append(i)

    # add id pairs that share the same pattern to candidate set
    candidate_pairs_1 = []
    for pattern in sameSequencePatternToId:
        ids = list(sorted(sameSequencePatternToId[pattern]))
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                candidate_pairs_1.append((ids[i], ids[j])) #
    # add id pairs that share the same pattern to candidate set
    candidate_pairs_2 = []
    for pattern in modelPatternToId:
        ids = list(sorted(modelPatternToId[pattern]))
        if len(ids)<1000: #skip patterns that are too common
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    candidate_pairs_2.append((ids[i], ids[j]))

    # remove duplicate pairs and take union
    candidate_pairs = set(candidate_pairs_2)
    candidate_pairs = candidate_pairs.union(set(candidate_pairs_1))
    candidate_pairs = list(candidate_pairs)

    # sort candidate pairs by jaccard similarity.
    # In case we have more than 1000000 pairs (or 2000000 pairs for the second dataset),
    # sort the candidate pairs to put more similar pairs first,
    # so that when we keep only the first 1000000 pairs we are keeping the most likely pairs
    jaccard_similarities = []
    candidate_pairs_real_ids: List[Tuple[int, int]] = []
    for it in candidate_pairs:
        id1, id2 = it

        # get real ids
        real_id1 = X['id'][id1]
        real_id2 = X['id'][id2]
        if real_id1<real_id2: # NOTE: This is to make sure in the final output.csv, for a pair id1 and id2 (assume id1<id2), we only include (id1,id2) but not (id2, id1)
            candidate_pairs_real_ids.append((real_id1, real_id2))
        else:
            candidate_pairs_real_ids.append((real_id2, real_id1))

        # compute jaccard similarity
        name1 = str(X[attr][id1])
        name2 = str(X[attr][id2])
        s1 = set(name1.lower().split())
        s2 = set(name2.lower().split())
        jaccard_similarities.append(len(s1.intersection(s2)) / max(len(s1), len(s2)))
    candidate_pairs_real_ids = [x for _, x in sorted(zip(jaccard_similarities, candidate_pairs_real_ids), reverse=True)]
    return candidate_pairs_real_ids


def save_output(X1_candidate_pairs: List[Tuple[int, int]],
                X2_candidate_pairs: List[Tuple[int, int]],
                submission_mode: bool):
    """
    Save the candidate set for both datasets to a SINGLE file `output.csv`
    """

    if submission_mode:
        expected_cand_size_X1 = 1000000
        expected_cand_size_X2 = 2000000

        # make sure to include exactly 1000000 pairs for dataset X1 and 2000000 pairs for dataset X2
        if len(X1_candidate_pairs) > expected_cand_size_X1:
            X1_candidate_pairs = X1_candidate_pairs[:expected_cand_size_X1]
        if len(X2_candidate_pairs) > expected_cand_size_X2:
            X2_candidate_pairs = X2_candidate_pairs[:expected_cand_size_X2]

        # make sure to include exactly 1000000 pairs for dataset X1 and 2000000 pairs for dataset X2
        if len(X1_candidate_pairs) < expected_cand_size_X1:
            X1_candidate_pairs.extend([(0, 0)] * (expected_cand_size_X1 - len(X1_candidate_pairs)))
        if len(X2_candidate_pairs) < expected_cand_size_X2:
            X2_candidate_pairs.extend([(0, 0)] * (expected_cand_size_X2 - len(X2_candidate_pairs)))

        all_cand_pairs = X1_candidate_pairs + X2_candidate_pairs  # make sure to have the pairs in the first dataset first
    else:
        all_cand_pairs = X1_candidate_pairs + X2_candidate_pairs

    output_df = pd.DataFrame(all_cand_pairs, columns=["left_instance_id", "right_instance_id"])
    # In evaluation, we expect output.csv to include exactly 3000000 tuple pairs.
    # we expect the first 1000000 pairs are for dataset X1, and the remaining pairs are for dataset X2
    output_df.to_csv("output.csv", index=False)


if __name__ == "__main__":
    # read the datasets
    X1 = pd.read_csv("X1.csv")
    X2 = pd.read_csv("X2.csv")

    # perform blocking
    X1_candidate_pairs = x1_blocking(X1)
    X2_candidate_pairs = x2_blocking(X2)

    # save results
    save_output(X1_candidate_pairs, X2_candidate_pairs, submission_mode=False)
