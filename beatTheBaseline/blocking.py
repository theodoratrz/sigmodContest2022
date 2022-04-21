from typing import List, Dict, Tuple
from collections import defaultdict
import re
import csv

import pandas as pd

from utils import *
from x2_blocking import x2_blocking


def x1_blocking(csv_reader, id_col: str, title_col: str, save_scores=False) -> List[Tuple[int, int]]:
    """
    This function performs blocking on X1 dataset.
    :param `X`: dataframe
    :return: candidate set of tuple pairs
    """

    customPunctuation = NamespaceX1.punctuation
    trashPattern = NamespaceX1.trashPattern
    brandPatterns = NamespaceX1.brandPatterns
    modelPattern = NamespaceX1.modelPattern
    cpuModelPattern = NamespaceX1.cpuModelPattern

    sameSequencePatterns: Dict[str, List[ Tuple[int, str] ]] = defaultdict(list)
    modelPatterns: Dict[str, List[ Tuple[int, str] ]] = defaultdict(list)

    for i, row in enumerate(csv_reader):
        id = int(row[id_col])
        rawTitle = str(row[title_col]).lower()

        noTrash = re.sub(trashPattern, '', rawTitle)
        cleanedTitle = noTrash.translate(str.maketrans({ord(c): ' ' for c in customPunctuation}))
        cleanedTitle = re.sub(' +', ' ', cleanedTitle).strip()

        clean_words = cleanedTitle.split()
        clean_words.sort()
        unique_words = {word: None for word in clean_words}.keys()
        sortedTitle = ' '.join(unique_words)

        #instance = (id, cleanedTitle)
        instance = (id, rawTitle)

        sameSequencePatterns[sortedTitle].append(instance)

        brands = []
        for brand in brandPatterns:
            match = re.search(brand, sortedTitle)
            if match:
                brands.append(match.group())
        brand = ' & '.join(brands) if len(brands) else NO_BRAND
        
        model = modelPattern.search(cleanedTitle)
        if not model:
            model = NO_MODEL
        else:
            model = model.group()

        cpu = cpuModelPattern.search(cleanedTitle)
        if not cpu:
            cpu = NO_CPU
        else:
            cpu = cpu.group()

        if model != NO_MODEL and cpu != NO_CPU:
            pattern = " || ".join((brand, model, cpu))
            modelPatterns[pattern].append(instance)

    # add id pairs that share the same pattern to candidate set
    candidate_pairs_1 = []
    for pattern in sameSequencePatterns:
        instances = sameSequencePatterns[pattern]
        for i in range(len(instances)):
            for j in range(i + 1, len(instances)):
                candidate_pairs_1.append((instances[i], instances[j])) #
    # add pairs that share the same pattern to candidate set
    candidate_pairs_2 = []
    for pattern in modelPatterns:
        instances = modelPatterns[pattern]
        if len(instances)<500: #skip patterns that are too common
            for i in range(len(instances)):
                for j in range(i + 1, len(instances)):
                    candidate_pairs_2.append((instances[i], instances[j]))

    # remove duplicate pairs and take union
    candidate_pairs_1 = set(candidate_pairs_1)
    candidate_pairs_2 = set(candidate_pairs_2)
    candidate_pairs = list(candidate_pairs_2.union(candidate_pairs_1))

    # sort candidate pairs by jaccard similarity.
    # In case we have more than 1000000 pairs,
    # sort the candidate pairs to put more similar pairs first,
    # so that when we keep only the first 1000000 pairs we are keeping the most likely pairs
    jaccard_similarities = []
    candidate_pairs_real_ids: List[Tuple[int, int]] = []
    for pair in candidate_pairs:
        (id1, name1), (id2, name2) = pair

        if id1 < id2: # NOTE: This is to make sure in the final output.csv, for a pair id1 and id2 (assume id1<id2), we only include (id1,id2) but not (id2, id1)
            candidate_pairs_real_ids.append((id1, id2))
        else:
            candidate_pairs_real_ids.append((id2, id1))

        # compute jaccard similarity
        jaccard_similarities.append(NamespaceX1.getSimilarityScore(name1, name2))

    if save_scores:
        candidate_pairs_real_ids = [(pair[0], pair[1], score) for pair, score in sorted(zip(candidate_pairs_real_ids, jaccard_similarities), key=lambda t: t[1], reverse=True)]
    else:
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
        output_df = pd.DataFrame(all_cand_pairs, columns=["left_instance_id", "right_instance_id"])
    else:
        all_cand_pairs = X1_candidate_pairs + X2_candidate_pairs
        output_df = pd.DataFrame(all_cand_pairs, columns=["left_instance_id", "right_instance_id", "score"])
    
    # In evaluation, we expect output.csv to include exactly 3000000 tuple pairs.
    # we expect the first 1000000 pairs are for dataset X1, and the remaining pairs are for dataset X2
    output_df.to_csv("output.csv", index=False)


if __name__ == "__main__":

    with open('X1.csv') as x1_file:
        x1_reader = csv.DictReader(x1_file)
        #X1_candidate_pairs = x1_blocking(x1_reader, id_col='id', title_col='title', save_scores=(not SUBMISSION_MODE))
        X1_candidate_pairs = []
    with open('X2.csv') as x2_file:
        x2_reader = csv.DictReader(x2_file)
        X2_candidate_pairs = x2_blocking(x2_reader, id_col='id', title_col='name', brand_col='brand', save_scores=(not SUBMISSION_MODE))
        #X2_candidate_pairs = []

    save_output(X1_candidate_pairs, X2_candidate_pairs, submission_mode=SUBMISSION_MODE)
