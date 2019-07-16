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
import argparse

logger = None

DoneList = dict()


def DoRename(config, lookup_names):
    renames_count = 0

    names = lookup_names
    folder = config['FileDir']

    logging.info('***')
    logging.info('***')
    logging.info('***')
    logging.info('*** Started Process to Rename Files')

    for File in sorted(os.listdir(folder), reverse=True):
        original_file = os.path.join(folder, File)
        if not os.path.isfile(original_file):
            continue

        fn, ext = os.path.splitext(File)
        _, ext2 = os.path.splitext(fn)

        for name in names:

            destination = os.path.join(folder, name + ext2 + ext)
            clean_name = os.path.basename(destination)
            if not fn.startswith(name) or fn == name or clean_name in DoneList:
                continue

            if os.path.isfile(destination):
                # Skip existing file
                continue

            logger.info("Renamed {} to {}".format(
                original_file, destination))
            os.rename(original_file, destination)
            renames_count = renames_count + 1
            DoneList[clean_name] = File

    renamed = IM_Common.TinyDB(config['RenameTrackerDoc'])
    for item in DoneList:
        renamed.insert({
            'clean_name': item,
            'original_name': DoneList[item]
        })

    if renames_count == 0:
        logger.debug("No item was renamed!")
    else:
        logger.debug("A total of {} items were renamed".format(renames_count))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'lookup_names', help='List of fileanames to lookup separated by comma (,) without space')
    args = parser.parse_args()

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

    if not os.path.isfile(ArchiveTrackerDoc):
        logger.debug("Creating {}...".format(ArchiveTrackerDoc))
        with open(ArchiveTrackerDoc, 'wt', newline='') as fp:
            fp.write(json.dumps(dict()))

    lookup_names = args.lookup_names.split(',')
    logger.debug("Using lookup names: %s", lookup_names)
    DoRename(config, lookup_names)
