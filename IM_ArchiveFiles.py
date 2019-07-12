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
logging.info('*** Started Process to Archive Files')

# Check for dependencies

if not os.path.exists(ArchiveDir):
    logger.info(
        'Did not find Archive Directory. Check if directory exists or if path is correct in ConfigFile, then rerun app.')
    sys.exit()

if not os.path.isfile(TrackerDoc):
    logger.info("{} was not found. Trying to create it.".format(TrackerDoc))
    with open(TrackerDoc, 'w+t') as tfp:
        tfp.write("[]")

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

with open(TrackerDoc, 'rt', newline='') as fp1:
    Files = json.loads(fp1.read())

for current_name, file_data in Files.items():
    if os.path.isfile(current_name):

        TimeToday = date.today()
        TimeDelayDate = TimeToday + timedelta(days=ArchiveDays)
        FileNameNew = os.path.join(ArchiveDir, file_data['OriginalFileName'])

        try:
            shutil.move(current_name, FileNameNew)
        except Exception as e:
            logger.info(current_name + ' could not be archived.')
            print(e)
        else:
            logger.info('Archived: ' + os.path.basename(current_name))

            NewListEntry = Files[current_name]
            NewListEntry['ArchiveDate'] = str(TimeToday)
            NewListEntry['ExpiryDate'] = str(TimeDelayDate)

            with open(TrackerDoc, 'rt') as ReadFile:
                ListEntries = json.loads(ReadFile.read())
                ListEntries[current_name] = NewListEntry
                with open(TrackerDoc, 'w+t') as WriteFile:
                    WriteFile.write(json.dumps(ListEntries, indent=2))
    else:
        logger.info('Did not find: ' + current_name)
        continue
