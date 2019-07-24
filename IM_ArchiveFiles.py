# Import libraries
import sys
import json
import os
import shutil
from datetime import datetime
from datetime import timedelta
from datetime import date
import logging
import argparse
import IM_Common

archive_count = 0


parser = argparse.ArgumentParser()
parser.add_argument(
    'lookup_names', help='NO arguments entered.', type=str)

args = parser.parse_args()

lookup_names = [a.strip() for a in args.lookup_names.split(",")]

if not os.path.isfile(IM_Common.ConfigFileLocation):
    print("Config File: {} not found.".format(
        IM_Common.ConfigFileLocation))
    sys.exit(1)

# Import config file & parameters
with open(IM_Common.ConfigFileLocation, 'rt') as ConfigFile:
    ConfigData = json.load(ConfigFile)

FileDir = ConfigData['FileDir']
ArchiveDir = ConfigData['ArchiveDir']
LogDoc = ConfigData['LogDoc']
TrackerDoc = ConfigData['ArchiveTrackerDoc']
ArchiveDays = int(ConfigData['ArchiveDays'])


# Setup Logger
logging_format = '%(asctime)s - %(message)s'
logging.basicConfig(filename=LogDoc, level=logging.DEBUG,
                    format=logging_format)
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logging.info('***')
logging.info('***')
logging.info('***')
logging.info('*** Started Process to Archive Files')

# Check for dependencies

if not os.path.exists(FileDir):
    logger.info(
        'Did not find Data File Directory. Check if directory exists or if path is correct in ConfigFile, then rerun app.')
    sys.exit()

if not os.path.exists(ArchiveDir):
    logger.info(
        'Did not find Archive Directory. Check if directory exists or if path is correct in ConfigFile, then rerun app.')
    sys.exit()

if not os.path.isfile(TrackerDoc):
    logger.info("{} was not found. Trying to create it.".format(TrackerDoc))
    with open(TrackerDoc, 'w+t') as tfp:
        tfp.write("{}")

    if os.path.isfile(TrackerDoc):
        logger.info('Tracker Document created successfully')
    else:
        logger.info(
            'Did not find Tracker Document. Check if directory exists or if path is correct in ConfigFile, then rerun app.')
        sys.exit()

if not os.path.isfile(LogDoc):
    logger.info(
        'Did not find Log Document. Check if directory exists or if path is correct in ConfigFile, then rerun app.')
    sys.exit()

archived = IM_Common.TinyDB(TrackerDoc)


def name_match(name):
    for search in lookup_names:
        if name.startswith(search):
            return True
    return False


for filename in os.listdir(FileDir):
    if not name_match(filename):
        continue

    file_loc = os.path.join(FileDir, filename)
    if not os.path.isfile(file_loc):
        continue

    destination = os.path.join(ArchiveDir, filename)
    shutil.copy(file_loc, destination)
    archive_count = archive_count + 1

    archived.upsert({
        'archive_date': str(date.today()),
        'expiry_date': str((date.today() + timedelta(days=ArchiveDays))),
        'original_name': os.path.basename(destination)
    }, {"original_name": os.path.basename(destination)})

    logger.debug("{} was archived".format(os.path.basename(destination)))

if archive_count == 0:
    logger.debug("No item was archived!")
else:
    logger.debug("A total of {} items were archived".format(archive_count))
