import asyncio
import os
import shutil
from os.path import isfile

import dask
import dask.dataframe as dd
from dask.delayed import delayed
from dask.distributed import Client
from dask_jobqueue import SLURMCluster
import numpy as np

import parse_aminer
import parse_dblp
import parse_semantic_scholar
from database_manager import DatabaseManager

@dask.delayed
def process_file(path):
    h = hash(path)  # Use the hash of the node name as database file.
    tmp_path = os.path.join("/tmp/aiptmp/{}.db".format(h))
    os.makedirs("/tmp/aiptmp", exist_ok=True)
    if "dblp.xml" in path:
        parse_dblp.parse(path, tmp_path)
    elif "s2-corpus" in path:
        parse_semantic_scholar.parse_semantic_scholar_corpus_file(path, tmp_path)
    elif "aminer_papers" in path:
        parse_aminer.parse_aminer_corpus_file(path, tmp_path)


def copy_database_to_home_folder():
    shutil.move("/tmp/aiptmp/*.db", "/home/lvs215/aiptmp/")


async def run():
    number_of_cores_per_node = 16  # DAS-5 features 2x8 NUMA cores per compute node
    reservation_length = "02:00:00"  # 2 hours is more than enough... probably
    cluster = SLURMCluster(cores=number_of_cores_per_node, memory="64 GB", processes=number_of_cores_per_node,
                           local_directory="./aip-logs", interface='ib0', walltime=reservation_length)

    # Grab 5 execution nodes -> 80 cores
    print("Scaling up, getting 5 nodes")
    cluster.scale_up(5)
    client = Client(cluster)

    try:

        print("Client is ready, parsing data files...")

        file_locations = "/var/scratch/lvs215/aip_tmp"
        data_files = []

        # Create a list of all the files we want to parse. Skip the compressed sources if they are still lingering around
        for path, subdirs, files in os.walk(file_locations):
            for name in files:
                if isfile(os.path.join(path, name)) and not name.endswith(("gz", "zip", "tar")):
                    data_files.append(os.path.join(path, name))

        # Create one task per file.
        print(data_files)
        print("Creating and executing tasks...")
        tasks = list(map(delayed(process_file), data_files))
        true_false_array = dd.from_delayed(tasks, meta={
            "success": np.bool,
        })
        print("Tasks ran to completion! Copying databases.")
        if False not in true_false_array:  # If everything went alright, let all nodes copy their databases to the home dir.
            client.run(copy_database_to_home_folder())
        else:
            print("Parsing one of the files went horribly wrong, quitting!")
            exit(-1)

        print("Beginning assembling of all databases into one!")
        # Now, each of the nodes has a local database file, we will now combine these databases into one.
        # We do this process sequentially, because we are not sure yet if SQLite likes it if all nodes do this in parallel.
        # TODO: test if we can do this procedure in each node through the copy_database_to_home_folder, would save copying data
        database_manager = DatabaseManager()  # This creates an empty aip.db if it doesn't exists.
        con3 = database_manager.db  # Reuse the connection

        # based on https://stackoverflow.com/a/37138506
        db_files_location = "/home/lvs215/aiptmp/"
        os.makedirs(db_files_location, exist_ok=True)
        for file in [os.path.join(db_files_location, f) for f in os.listdir(db_files_location) if
                     isfile(os.path.join(db_files_location, f)) and f.endswith(".db")]:
            con3.execute("ATTACH '{}' as dba".format(file))

            con3.execute("BEGIN")
            for row in con3.execute("SELECT * FROM dba.sqlite_master WHERE type='table'"):
                combine = "INSERT INTO " + row[1] + " SELECT * FROM dba." + row[1]
                print(combine)
                con3.execute(combine)
            con3.execute("detach database dba")
            con3.commit()
            # Now, delete the database as it has been copied.
            # os.remove("{}.db".format(hash(worker)))
        print("All done. Releasing all nodes.")
    except Exception as e:
        print(e)
    finally:
        # Release the nodes
        await cluster.scale_down(cluster.workers)
        print("Nodes released.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()
