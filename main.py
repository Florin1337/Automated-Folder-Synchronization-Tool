import os
import shutil
import hashlib
import logging
import schedule
import time
import sys

def folder_synchronization(source_folder, replica_folder, log_file):
    # get md5 hash of existing file
    def get_md5(file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    # get md5 hash of existing file or None
    def file_exist_md5(file_path):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[logging.FileHandler(log_file), logging.StreamHandler()])
        if os.path.exists(file_path):
            return get_md5(file_path)
        return None

    # removing from the replica folder the files that don't exist in the source folder
    for filename in os.listdir(replica_folder):
        replica_file = os.path.join(replica_folder, filename)
        if filename not in os.listdir(source_folder):
            os.remove(replica_file)
            logging.info(f"Removed replica file: {replica_file}")
            print(f"Removed replica file: {replica_file}")

    # synchronization of the files between source and replica
    for filename in os.listdir(source_folder):
        source_file = os.path.join(source_folder, filename)
        replica_file = os.path.join(replica_folder, filename)
        source_file_md5 = get_md5(source_file)
        replica_file_md5 = file_exist_md5(replica_file)

        # if the file doesn't exist in the replica folder then copy it from the source folder
        if replica_file_md5 is None:
            shutil.copy(source_file, replica_file)
            logging.info(f"Created a new replica file: {replica_file}")
            print(f"Created a new replica file: {replica_file}")
        # if the file exists in both folders check hash md5 and if it's different we replace the replica file with source file
        elif source_file_md5 != replica_file_md5:
            shutil.copy(source_file, replica_file)
            logging.info(f"Modified the replica file: {replica_file}")
            print(f"Modified the replica file: {replica_file}")

    # check if there are files in the replica folder that don't exist in the source folder and remove them
    for filename in os.listdir(replica_folder):
        source_file = os.path.join(source_folder, filename)
        replica_file = os.path.join(replica_folder, filename)

        if not os.path.exists(source_file):
            os.remove(replica_file)
            logging.info(f"Removed replica file: {replica_file}")
            print(f"Removed replica file: {replica_file}")

# check if the correct number of command-line arguments is provided
if len(sys.argv) != 5:
    print("Please input a command in the following format: ")
    print("python main.py <source_folder_path> <replica_folder_path> <log_file_path> <sync_interval_seconds>")
    sys.exit(1)
else:
    print("Starting file synchronization of the specified folders.")

# extraction of needed values from command line arguments
source_folder = sys.argv[1]
replica_folder = sys.argv[2]
log_file = sys.argv[3]
sync_interval_seconds = int(sys.argv[4])

# scheduling the synchronization to run periodically
schedule.every(sync_interval_seconds).seconds.do(folder_synchronization, source_folder, replica_folder, log_file)

# infinite loop to run the scheduled tasks
while True:
    schedule.run_pending()
    time.sleep(1)

# example of command-line arguments when running the program
# python main.py "C:\Users\bocse\Desktop\Source" "C:\Users\bocse\Desktop\Replica" "C:\Users\bocse\Desktop\Changelogs\changelog.log" 5