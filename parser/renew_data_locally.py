import multiprocessing
import os
import re
import time
from os.path import isfile

from joblib import delayed, Parallel
from tqdm import tqdm

import parse_aminer
import parse_dblp
import parse_mag
import parse_semantic_scholar
from database_manager import DatabaseManager

aip_name = "aip"
file_location = "C:/Users/ktoka/Desktop/raw-data"


def process_file(path, db_file=aip_name):
    if re.match(".*dblp[\w-]+\.xml", path):
        return parse_dblp.parse(path, db_file)
    elif "aminer_papers" in path:
        start = time.time()
        ret = parse_aminer.parse_aminer_corpus_file(path, db_file, logger_disabled=True)
        print("Aminer parse time:", time.time() - start)
        return ret
    elif "mag_papers" in path:
        start = time.time()
        ret = parse_mag.parse_mag_corpus_file(path, db_file, logger_disabled=True)
        print("MAG parse time:", time.time() - start)
        return ret
    elif "s2-corpus" in path:
        return parse_semantic_scholar.parse_semantic_scholar_corpus_file(path, db_file)

    return True  # Nothing that should be done.


def run(file_locations=file_location, db_name=aip_name):
    num_cores = multiprocessing.cpu_count()

    # We are processing dblp first as they have author information and a nice identifier. This is just a preference
    # and the articles can be parsed in no particular order, yet as we do not override an id, the final id in the
    # database will differ based on which entry of the same article gets scanned first.
    dblp_file = None
    other_data_files = []
    semantic_data_files = []

    # Create a list of all the files we want to parse. Skip the compressed sources if they are still lingering around
    for path, subdirs, files in os.walk(file_locations):
        for name in files:
            if isfile(os.path.join(path, name)) and not name.endswith(("zip", "tar")):
                file_path = os.path.join(path, name)
                if re.match("dblp[\w-]+\.xml", name):
                    dblp_file = file_path
                elif re.match("s2-corpus[\w-]+", name):
                    semantic_data_files.append(file_path)
                else:
                    other_data_files.append(file_path)

    # Create one task per file.
    print("Processing DBLP first...")
    if dblp_file is None:
        print("DBLP path is empty")
        exit(-1)

    start = time.time()
    startDBLP = time.time()
    if not process_file(dblp_file, db_file=db_name):
        print("Error during parsing DBLP file {}".format(dblp_file))
        exit(-1)
    print("DBLP parse time:", time.time() - startDBLP)
    # Create one task per file.
    print("Processing other files  ...")

    input_list = tqdm(other_data_files)
    input_list_semantic = tqdm(semantic_data_files)

    processed_list = Parallel(n_jobs=num_cores)(delayed(process_file)(i, db_name) for i in input_list)
    print("Time for parsing all other sources:", time.time() - start)

    semantic_start = time.time()
    processed_list_semantic = Parallel(n_jobs=num_cores)(delayed(process_file)(i, db_name) for i in input_list_semantic)
    print("Time for parsing Semantic sources:", time.time() - semantic_start)

    print("Adding cites data ...")  # Add the cites data after all papers have been added to the db
    cites_time = time.time()
    processed_list_cited = Parallel(n_jobs=num_cores)(delayed(parse_semantic_scholar.add_semantic_scholar_cites_data)(i, db_name) for i in input_list_semantic)
    print("Time for citing all data:", time.time() - cites_time)

    process_time = time.time()
    DatabaseManager(location=db_name).process_data()
    print("Time for processing all data:", time.time() - process_time)

    if False in processed_list or False in processed_list_semantic or False in processed_list_cited:
        print("Parsing one of the files went wrong! Please check output")
        exit(-1)
    else:
        print("Tasks ran to completion!")


if __name__ == '__main__':
    run()
