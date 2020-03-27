import os
from os.path import isfile

import dask.dataframe as dd
from dask.delayed import delayed
from dask.distributed import Client, get_worker
from dask_jobqueue import SLURMCluster

import parse_aminer
import parse_dblp
import parse_semantic_scholar
from database_manager import DatabaseManager

number_of_cores_per_node = 16  # DAS-5 features 2x8 NUMA cores per compute node
reservation_length = "02:00:00"  # 2 hours is more than enough... probably
cluster = SLURMCluster(cores=number_of_cores_per_node, memory="64 GB", processes=number_of_cores_per_node,
                       local_directory="./aip-logs", interface='ib0', walltime=reservation_length)

file_locations = "/var/scratch/atlarge/aip_data"
local_database_location = "/tmp/aip.db"

data_files = []

# Create a list of all the files we want to parse. Skip the compressed sources if they are still lingering around
for path, subdirs, files in os.walk(file_locations):
    for name in files:
        if isfile(os.path.join(path, name)) and not name.endswith(("gz", "zip", "tar")):
            data_files.append(os.path.join(path, name))


def process_file(path):
    if "dblp" in path:
        parse_dblp.parse(path, local_database_location)
    elif "s2-corpus" in path:
        parse_semantic_scholar.parse_semantic_scholar_corpus_file(path, local_database_location)
    elif "aminer" in path:
        parse_aminer.parse_aminer_corpus_file(path, local_database_location)


def copy_database_to_home_folder():
    h = hash(get_worker())  # Use the hash of the node name as database file.
    os.rename(local_database_location, "~/{}.db".format(h))


# Grab 5 execution nodes -> 80 cores
cluster.scale_up(5)
client = Client(cluster)

# Create one task per file.
tasks = list(map(delayed(process_file), data_files))
true_false_array = dd.from_delayed(tasks)
if False not in true_false_array:  # If everything went alright, let all nodes copy their databases to the home folder.
    client.run(copy_database_to_home_folder())
else:
    print("Parsing one of the files went horribly wrong, quitting!")
    exit(-1)

# Now, each of the nodes has a local database file, we will now combine these databases into one.
# We do this process sequentially, because we are not sure yet if SQLite likes it if all nodes do this in parallel.
# TODO: test if we can do this procedure in each node through the copy_database_to_home_folder, would save copying data
database_manager = DatabaseManager()  # This creates an empty aip.db if it doesn't exists.
con3 = database_manager.db  # Reuse the connection

# based on https://stackoverflow.com/a/37138506
for worker in cluster.workers:  # For each worker, copy all the data
    con3.execute("ATTACH '{}.db' as dba".format(hash(worker)))

    con3.execute("BEGIN")
    for row in con3.execute("SELECT * FROM dba.sqlite_master WHERE type='table'"):
        combine = "INSERT INTO " + row[1] + " SELECT * FROM dba." + row[1]
        print(combine)
        con3.execute(combine)
    con3.execute("detach database dba")
    con3.commit()
    # Now, delete the database as it has been copied.
    # os.remove("{}.db".format(hash(worker)))

# Release the nodes
await cluster.scale_down(cluster.workers)
