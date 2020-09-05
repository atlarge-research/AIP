import os
from os.path import isfile

import multiprocessing
from joblib import Parallel, delayed
from tqdm import tqdm

import parse_aminer
import parse_dblp
import parse_semantic_scholar


def process_file(path, db_file="aip.db"):
    if "dblp.xml" in path:
        return parse_dblp.parse(path, db_file)
    elif "s2-corpus" in path:
        return parse_semantic_scholar.parse_semantic_scholar_corpus_file(path, db_file)
    elif "aminer_papers" in path:
        return parse_aminer.parse_aminer_corpus_file(path, db_file, logger_disabled=True)

    return True  # Nothing that should be done.


def run():
    num_cores = multiprocessing.cpu_count()
    file_locations = "D:/raw-vanue-data-csur-survey/ss-2019-11-01"
    # We are processing dblp first as they have author information and a nice identifier. This is just a preference
    # and the articles can be parsed in no particular order, yet as we do not override an id, the final id in the
    # database will differ based on which entry of the same article gets scanned first.
    dblp_file = None
    other_data_files = []

    # Create a list of all the files we want to parse. Skip the compressed sources if they are still lingering around
    for path, subdirs, files in os.walk(file_locations):
        for name in files:
            if isfile(os.path.join(path, name)) and not name.endswith(("zip", "tar")):
                file_path = os.path.join(path, name)
                if "dblp.xml" in path:
                    dblp_file = file_path
                else:
                    other_data_files.append(file_path)

    # Create one task per file.
    print("Processing DBLP first...")
    if dblp_file is None or not process_file(dblp_file):
        print("Error during parsing DBLP file {}".format(dblp_file))
        exit(-1)

    # Create one task per file.
    input_list = tqdm(other_data_files)
    processed_list = Parallel(n_jobs=num_cores)(delayed(process_file)(input_list))
    if False in processed_list:
        print("Parsing one of the files went wrong! Please check output")
        exit(-1)
    else:
        print("Tasks ran to completion!")


if __name__ == '__main__':
    run()
