import asyncio
import datetime
import os
import shutil
import threading
from os.path import isfile

import dask.bag as db
from dask.delayed import delayed
from dask.distributed import Client
from dask_jobqueue import SLURMCluster

import parse_dblp
from parser import parse_aminer, parse_semantic_scholar
from parser.database_manager import DatabaseManager

tmp_folder = '/tmp/sachtmp'
db_files_location = "/home/stalluri/aiptmp/"


def process_file(path):
    print(path)
    if 'local_lock' not in globals():
        globals()['local_lock'] = None

    global local_lock

    ret_value = [False]

    if local_lock is None:
        local_lock = threading.Lock()

    local_lock.acquire()

    # Filename can't start with a number
    h = 'aipdb' + str(
        abs(hash(path)))  # Use the hash of the node name as database file.
    print(h)
    tmp_path = os.path.join(tmp_folder, "{}.db".format(h))
    os.makedirs(tmp_folder, exist_ok=True)
    if "dblp.xml" in path:
        ret_value = [parse_dblp.parse(path, tmp_path)]
    elif "s2-corpus" in path:
        ret_value = [
            parse_semantic_scholar.parse_semantic_scholar_corpus_file(
                path,
                tmp_path)]
    elif "aminer_papers" in path:
        ret_value = [parse_aminer.parse_aminer_corpus_file(path, tmp_path)]

    local_lock.release()
    return ret_value


def copy_database_to_home_folder():
    shutil.move(os.path.join(tmp_folder, "*.db"), db_files_location)


def clear_all_files():
    shutil.rmtree(tmp_folder)


async def run():
    number_of_cores_per_node = 16  # DAS-5 features 2x8
    # NUMA cores per compute node
    reservation_length = "08:00:00"  # 2 hours is more than enough... probably
    cluster = SLURMCluster(cores=number_of_cores_per_node, memory="64 GB",
                           processes=4,
                           scheduler_options={"dashboard_address": ":6868"},
                           local_directory="./aip-logs", interface='ib0',
                           walltime=reservation_length)

    # Grab 5 execution nodes -> 80 cores
    print("Scaling up, getting 5 nodes")
    cluster.scale_up(5)
    client = Client(cluster)

    print("Client is ready, parsing data files...")

    file_locations = "/var/scratch/lvs215/aip_tmp"
    data_files = []

    # Create a list of all the files we want to parse.
    # Skip the compressed sources if they are still lingering around
    for path, subdirs, files in os.walk(file_locations):
        for name in files:
            if isfile(os.path.join(path, name)) and not name.endswith(
                    ("gz", "zip", "tar")):
                data_files.append(os.path.join(path, name))

    client.run(clear_all_files)

    # Create one task per file.
    print(data_files)
    print("Creating and executing tasks...")
    tasks = list(map(delayed(process_file), data_files))
    true_false_array = db.from_delayed(tasks)

    # DEBUG CODE
    # future = client.compute(true_false_array)
    # client.recreate_error_locally(future)

    # Time to compute them!
    start = datetime.datetime.now()
    res = true_false_array.compute()
    end = datetime.datetime.now()
    print(true_false_array)
    print(res)
    print("Tasks ran to completion! Copying databases.")
    if False not in true_false_array:  # If everything went alright, let all
        # nodes copy their databases to the home dir.
        client.run(copy_database_to_home_folder)
        client.run(clear_all_files)
    else:
        print("Parsing one of the files went horribly wrong, quitting!")
        exit(-1)

    print("Beginning assembling of all databases into one!")
    # Now, each of the nodes has a local database file, we will now combine
    # these databases into one. We do this process sequentially, because we
    # are not sure yet if SQLite likes it if all nodes do this in parallel.
    # TODO: test if we can do this procedure in each node through the
    #  copy_database_to_home_folder, would save copying data
    database_manager = DatabaseManager()  # This creates an empty aip.db if
    # it doesn't exists.
    con3 = database_manager.db  # Reuse the connection

    # based on https://stackoverflow.com/a/37138506
    os.makedirs(db_files_location, exist_ok=True)
    for file in [os.path.join(db_files_location, f) for f in
                 os.listdir(db_files_location) if
                 isfile(os.path.join(db_files_location, f)) and f.endswith(
                     ".db")]:
        con3.execute("ATTACH '{}' as dba".format(file))

        con3.execute("BEGIN")
        for row in con3.execute(
                "SELECT * FROM dba.sqlite_master WHERE type='table'"):
            combine = "INSERT INTO " + row[1] + " SELECT * FROM dba." + row[1]
            print(combine)
            con3.execute(combine)
        con3.execute("detach database dba")
        con3.commit()
        # Now, delete the database as it has been copied.
        # os.remove("{}.db".format(hash(worker)))
    print("All done. Releasing all nodes.")
    await cluster.scale_down(cluster.workers)
    print("Nodes released.")
    print(end - start)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()
