from typing import List, Tuple
import csv

import pandas as pd

from utils import SUBMISSION_MODE, TARGET_DATASET
from x1_blocking import x1_blocking
from x2_blocking import x2_blocking


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
        if SUBMISSION_MODE or TARGET_DATASET == '1':
            X1_candidate_pairs = x1_blocking(x1_reader, id_col='id', title_col='title', save_scores=(not SUBMISSION_MODE))
        else:
            X1_candidate_pairs = []
    with open('X2.csv') as x2_file:
        x2_reader = csv.DictReader(x2_file)
        if SUBMISSION_MODE or TARGET_DATASET == '2':
            X2_candidate_pairs = x2_blocking(x2_reader, id_col='id', title_col='name', brand_col='brand', save_scores=(not SUBMISSION_MODE))
        else:
            X2_candidate_pairs = []

    save_output(X1_candidate_pairs, X2_candidate_pairs, submission_mode=SUBMISSION_MODE)
