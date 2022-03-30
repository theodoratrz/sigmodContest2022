import os
import gc
import random
import joblib

import numpy as np
import pandas as pd
from randomForestPredict import predict

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

pd.read_csv("./X2.csv")
gc.collect()

classifier = joblib.load("./classifier.txt")
classifier.verbose = 0

if os.getenv('RANDOM_FOREST_DEV_MODE'):
    x1_results = predict("./X1.csv", classifier, batchMaxSize=25000, verbose=True)
    output_df = pd.DataFrame(x1_results, columns=["left_instance_id", "right_instance_id"])
    output_df.to_csv("output.csv", index=False)
else:
    expected_cand_size_X1 = 1000000
    expected_cand_size_X2 = 2000000
    x1_results = predict("./X1.csv", classifier, batchMaxSize=50000, verbose=False)

    # make sure to include exactly 1000000 pairs for dataset X1 and 2000000 pairs for dataset X2
    X2_candidate_pairs = [(0, 0)] * expected_cand_size_X2

    all_cand_pairs = x1_results + X2_candidate_pairs  # make sure to have the pairs in the first dataset first
    output_df = pd.DataFrame(all_cand_pairs, columns=["left_instance_id", "right_instance_id"])
    # In evaluation, we expect output.csv to include exactly 3000000 tuple pairs.
    # we expect the first 1000000 pairs are for dataset X1, and the remaining pairs are for dataset X2
    output_df.to_csv("output.csv", index=False)
