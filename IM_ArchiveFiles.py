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
from tinydb import TinyDB, Query

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


db = TinyDB(TrackerDoc, indent=2)
renamed = db.table("renamed")
archived = db.table("archived")

for r in sorted(renamed.all(), key=lambda x: x.doc_id, reverse=True):
    file_loc = os.path.join(FileDir, r['clean_name'])
    if os.path.isfile(file_loc):
        destination = os.path.join(ArchiveDir, r['original_name'])
        shutil.move(file_loc, destination)

        ArchiveFileQuery = Query()
        archived.upsert({
            'archive_date': str(date.today()),
            'expiry_date': str((date.today() + timedelta(days=ArchiveDays))),
            'original_name': os.path.basename(destination)
        }, ArchiveFileQuery.original_name == os.path.basename(destination))

        logger.debug("{} was archived".format(os.path.basename(destination)))
        renamed.remove(doc_ids=[r.doc_id])

# for original, file_data in Files.items():
#     if file_data.get('ArchiveDate'):
#         continue

#     RenamedFile = os.path.join(FileDir, file_data['CleanName'])
#     if os.path.isfile(RenamedFile):

#         TimeToday = date.today()
#         TimeDelayDate = TimeToday + timedelta(days=ArchiveDays)
#         FileNameNew = os.path.join(ArchiveDir, original)

#         try:
#             shutil.move(RenamedFile, FileNameNew)
#         except Exception as e:
#             logger.info(original + ' could not be archived.')
#             print(e)
#         else:
#             logger.info('Archived: ' + os.path.basename(original))

#             NewListEntry = Files[original]
#             NewListEntry['ArchiveDate'] = str(TimeToday)
#             NewListEntry['ExpiryDate'] = str(TimeDelayDate)

#             with open(TrackerDoc, 'rt') as ReadFile:
#                 ListEntries = json.loads(ReadFile.read())
#                 ListEntries[original] = NewListEntry
#                 with open(TrackerDoc, 'w+t') as WriteFile:
#                     WriteFile.write(json.dumps(ListEntries, indent=2))
#     else:
#         logger.info('Did not find: ' + RenamedFile)
#         continue
