import numpy as np
import pandas as pd

FILES = [
    'COSMIC_v3.4_SBS_GRCh38.txt',
    'COSMIC_v3.3.1_SBS_GRCh38.txt',
    'COSMIC_v3.2_SBS_GRCh38.txt',
    'COSMIC_v3.1_SBS_GRCh38.txt',
    'COSMIC_v3_SBS_GRCh38.txt',
    'COSMIC_v2_SBS_GRCh38.txt',
    'COSMIC_v1_SBS_GRCh38.txt',

    'COSMIC_v3.4_SBS_GRCh37.txt',
    'COSMIC_v3.3.1_SBS_GRCh37.txt',
    'COSMIC_v3.2_SBS_GRCh37.txt',
    'COSMIC_v3.1_SBS_GRCh37.txt',
    'COSMIC_v3_SBS_GRCh37.txt',
    'COSMIC_v2_SBS_GRCh37.txt',
    'COSMIC_v1_SBS_GRCh37.txt'
]

DEFAULT_SIGNATURES = 'COSMIC_v3.4_SBS_GRCh38.txt'


linkage_methods = ['single', 'complete', 'average', 'ward']

DEFAULT_LINKAGE_METHOD = 'complete'

def normalize(data):
    return (data - np.nanmin(data)) / (np.nanmax(data) - np.nanmin(data))

def calculate_rmse(x, y):
    x_normalized = normalize(x)
    y_normalized = normalize(y)
    return np.sqrt(np.nanmean((x_normalized - y_normalized) ** 2))

def calculate_cosine(x, y):
    return 1-np.dot(x, y) / (np.sqrt(np.dot(x, x)) * np.sqrt(np.dot(y, y)))

def reprint(data, epsilon=10e-4):
    # Extracting mutation categories and their probabilities
    mutation_types = data.index
    signatures = data.columns[0:]

    # Initialize a dictionary to store the RePrint probabilities for each signature
    reprint_probabilities = {signature: {} for signature in signatures}

    # Iterate over each signature
    for signature in signatures:
        # Extract the probabilities for the current signature
        signature_probs = data[signature].values + epsilon

        # Iterate over each mutation type
        for idx, mutation in enumerate(mutation_types):
            # Split the mutation type to extract NL, X, Y, NR
            NL = mutation[0]
            NR = mutation[6]
            X, Y = mutation[2], mutation[4]

            # Compute the denominator: sum of probabilities for Z != X
            denominator = np.sum([signature_probs[j] for j in range(len(mutation_types))
                                  if mutation_types[j].startswith(f"{NL}[{X}>") and mutation_types[j].endswith(f"]{NR}")
                                  and mutation_types[j][4] != X])

            # Compute the RePrint probability for the current mutation
            reprint_prob = signature_probs[idx] / denominator if denominator != 0 else 0

            # Store the RePrint probability
            reprint_probabilities[signature][mutation] = reprint_prob

    # Convert the reprint_probabilities dictionary to a DataFrame for better readability
    reprint_df = pd.DataFrame(reprint_probabilities)
    return reprint_df

import base64
import io
def parse_signatures(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    if 'txt' in filename:
        return pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep='\t')
    if 'csv' in filename:
        return pd.read_csv(io.StringIO(decoded.decode('utf-8')), index_col=[0, 1], sep=',')
