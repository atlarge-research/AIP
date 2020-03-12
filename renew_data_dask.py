import os
from os.path import isfile

import dask.dataframe as dd
from dask.delayed import delayed
from dask.distributed import Client, get_worker
from dask_jobqueue import SLURMCluster

import parse_aminer
import parse_dblp
import parse_semantic_scholar

cluster = SLURMCluster(cores=16, memory="64 GB", processes=16, local_directory="./aip-logs", interface='ib0',
                       walltime='02:00:00')

file_locations = "/var/scratch/atlarge/aip_data"
local_database_location = "/tmp/aip.db"

data_files = []

for path, subdirs, files in os.walk(file_locations):
    for name in files:
        if isfile(os.path.join(path, name)):
            data_files.append(os.path.join(path, name))


def process_file(path):
    if "dblp" in path:
        parse_dblp.parse(path, local_database_location)
    elif "s2-corpus" in path:
        parse_semantic_scholar.parse_semantic_scholar_corpus_file(path, local_database_location)
    elif "aminer" in path:
        parse_aminer.parse_aminer_corpus_file(path, local_database_location)


def copy_database_to_home_folder():
    h = hash(get_worker())
    os.rename(local_database_location, "~/{}.db".format(h))

cluster.scale_up(5)
client = Client(cluster)
tasks = list(map(delayed(process_file), data_files))
true_false_array = dd.from_delayed(tasks)
if False not in true_false_array:
    client.run(copy_database_to_home_folder())
else:
    print("Parsing one of the files went horribly wrong, quitting!")
    exit(-1)

import sqlite3
con3 = sqlite3.connect("aip.db")

# based on https://stackoverflow.com/a/37138506
for worker in cluster.workers:
    con3.execute("ATTACH '{}.db' as dba".format(hash(worker)))

    con3.execute("BEGIN")
    for row in con3.execute("SELECT * FROM dba.sqlite_master WHERE type='table'"):
        combine = "INSERT INTO " + row[1] + " SELECT * FROM dba." + row[1]
        print(combine)
        con3.execute(combine)
    con3.execute("detach database dba")
    con3.commit()

# Release the nodes
await cluster.scale_down(cluster.workers)
