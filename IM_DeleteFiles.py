# Import libraries
import sys
import json
import os
import shutil
from datetime import datetime
from datetime import timedelta
from datetime import date
import logging
import IM_Common

if not os.path.isfile(IM_Common.ConfigFileLocation):
    print("Config File: {} not found.".format(
        IM_Common.ConfigFileLocation))
    sys.exit(1)

# Import config file & parameters
with open(IM_Common.ConfigFileLocation, 'rt') as ConfigFile:
    ConfigData = json.load(ConfigFile)

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
logging.info('*** Started Process to Delete Archived Files')

# Check for dependencies
if not os.path.exists(ArchiveDir):
    logger.info(
        'Did not find Archive Directory. Check if directory exists or if path is correct in ConfigFile, then rerun app.')
    sys.exit()

if not os.path.isfile(TrackerDoc):
    logger.info(
        'Did not find Tracker Document. Check if directory exists or if path is correct in ConfigFile, then rerun app.')
    sys.exit()

if not os.path.isfile(LogDoc):
    logger.info(
        'Did not find Log Document. Check if directory exists or if path is correct in ConfigFile, then rerun app.')
    sys.exit()


archived = IM_Common.TinyDB(TrackerDoc)

for archive in list(archived.all()):
    expiry = datetime.strptime(archive['expiry_date'], "%Y-%m-%d")
    if expiry <= datetime.today():
        FileNameToDelete = os.path.join(
            ArchiveDir, archive['original_name'])

        if os.path.isfile(FileNameToDelete):
            try:
                os.remove(FileNameToDelete)
                logger.info('Deleted: ' + FileNameToDelete)
                archived.remove(doc_ids=[archive['doc_id']])
            except Exception as e:
                logger.info(FileNameToDelete + ' could not be deleted')
                continue
