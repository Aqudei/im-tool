#!/bin/python3
import argparse
import json
import time
import os
import logging
import re
import IM_Common
import sys
import json

DoneList = dict()


def DoRename(config):

    names = config['FileNamesToRename']
    folder = config['FileDir']

    logging.info('***')
    logging.info('***')
    logging.info('***')
    logging.info('*** Started Process to Rename Files')

    logger.debug("Processing folder'{}'...".format(folder))
    for File in sorted(os.listdir(folder)):
        original = os.path.join(folder, File)
        logger.debug("Processing file'{}'...".format(original))
        if not os.path.isfile(original):

            logger.debug(
                "{} is not a file or does not exist. Skipping...".format(original))
            continue

        fn, ext = os.path.splitext(File)
        _, ext2 = os.path.splitext(fn)

        for name in names:

            destination = os.path.join(folder, name + ext2 + ext)
            if not fn.startswith(name) or fn == name or File in DoneList:
                continue

            if os.path.isfile(destination):
                os.remove(destination)

            logger.info("Renamed {} to {}".format(
                original, destination))
            os.rename(original, destination)
            DoneList[File] = {
                "CleanName": os.path.basename(destination)}

    with open(ArchiveTrackerDoc, 'wt', newline='') as fp:
        fp.write(json.dumps(DoneList, indent=2))


if not os.path.isfile(IM_Common.ConfigFileLocation):
    print("Cannot find configuration file {}".format(
        IM_Common.ConfigFileLocation))
    sys.exit()

with open(IM_Common.ConfigFileLocation, 'rt') as fp:
    config = json.load(fp)

ArchiveTrackerDoc = config['ArchiveTrackerDoc']

# Setup Logger
loggingFormat = '%(asctime)s - %(message)s'
logging.basicConfig(filename=config['LogDoc'], level=logging.DEBUG,
                    format=loggingFormat)

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

if not "FileNamesToRename" in config:
    logger.debug(
        "Please add 'FileNamesToRename' key in your configuration so I will know what files to be rename.")
    sys.exit()

if not os.path.isfile(ArchiveTrackerDoc):
    logger.debug("Creating {}...".format(ArchiveTrackerDoc))
    with open(ArchiveTrackerDoc, 'wt', newline='') as fp:
        fp.write(json.dumps(dict()))

with open(ArchiveTrackerDoc, 'rt', newline='') as fp:
    DoneList = json.loads(fp.read())

DoRename(config)
