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

# List Archived Files
ArchivedFiles = []
with open(TrackerDoc, 'rt') as TrackerFile:
    ArchivedFiles = json.loads(TrackerFile.read())

# Check if Archived Files have expired
TimeToday = datetime.now()
KeepArchived = []
DeleteArchived = []
for i, file_data in ArchivedFiles.items():
    ExpDate = datetime.strptime(file_data.get(
        'ExpiryDate', date.today() + timedelta(days=1)), "%Y-%m-%d")
    if ExpDate <= TimeToday:
        DeleteArchived.append(i)
    else:
        KeepArchived.append(i)
        continue

# Delete Files
for j in DeleteArchived:
    FileNameToDelete = os.path.join(
        ArchiveDir, ArchivedFiles[j]['OriginalFileName'])

    if os.path.isfile(FileNameToDelete):
        os.remove(FileNameToDelete)
        logger.info('Deleted: ' + FileNameToDelete)
        del ArchivedFiles[j]
    else:
        logger.info(FileNameToDelete + ' could not be deleted')
        continue

# Update Tracker Document
with open(TrackerDoc, 'w+') as WriteFile:
    WriteFile.write(json.dumps(ArchivedFiles, indent=2))
