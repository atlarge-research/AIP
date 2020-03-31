import os
from os.path import isfile


import parse_aminer
import parse_dblp
import parse_semantic_scholar


def process_file(path, db_file="aip.db"):
    if "dblp.xml" in path:
        return parse_dblp.parse(path, db_file)
    elif "s2-corpus" in path:
        return parse_semantic_scholar.parse_semantic_scholar_corpus_file(path, db_file)
    elif "aminer_papers" in path:
        return parse_aminer.parse_aminer_corpus_file(path, db_file)

    return True  # Nothing that should be done.


def run():
    file_locations = "C:/Users/L/Downloads/aip-raw-traces"
    data_files = []

    # Create a list of all the files we want to parse. Skip the compressed sources if they are still lingering around
    for path, subdirs, files in os.walk(file_locations):
        for name in files:
            if isfile(os.path.join(path, name)) and not name.endswith(("gz", "zip", "tar")):
                data_files.append(os.path.join(path, name))

    # Create one task per file.
    print("Creating and executing tasks...")
    for file in data_files:
        if not process_file(file):
            print("Parsing one of the files went horribly wrong, quitting!")
            exit(-1)

    print("Tasks ran to completion!")


if __name__ == '__main__':
    run()
