import os
import re
import os
import json
from uuid import uuid4

ConfigFileLocation = 'C:\\PYtests\\IMtool\\IM_FileArchiveTool\\IM_config.json'


class TinyDB(object):
    def __init__(self, loc):
        self.loc = os.path.expanduser(loc)
        self.load(self.loc)

    def _gen_id(self):
        if len(self.db) == 0:
            return 1

        return max([int(k) for k in self.db.keys()]) + 1

    def remove(self, doc_ids=[]):
        for id in doc_ids:
            self.delete(str(id))

    def upsert(self, data, query):
        updated = False
        for k, v in self.db.items():
            found = True
            for k1, v1 in query.items():
                if not v[k1] == v1:
                    found = False
                    break

            if found:
                updated = True
                self._set(k, data)
                break

        if not updated:
            self._set(self._gen_id(), data)

    def load(self, loc):
        if(os.path.exists(loc)):
            self._load()
        else:
            self.db = {}

        return True

    def insert(self, data):
        self._set(self._gen_id(), data)

    def _load(self):
        self.db = json.load(open(self.loc, 'r'))

    def dumpdb(self):
        try:
            json.dump(self.db, open(self.loc, 'w+'), indent=2)
            return True
        except:
            return False

    def all(self):
        for k, v in self.db.items():
            v['doc_id'] = k
            yield v

    def _set(self, key, value):
        try:
            self.db[str(key)] = value
            self.dumpdb()
        except Exception as e:
            print("[X] Error Saving Values to Database : " + str(e))
            return False

    # def get(self, key):
    # 	try:
    # 		return self.db[str(key)]
    # 	except KeyError:
    # 		print("No Value Can Be Found for "+ str(key))
    # 		return False

    def get(self, key):
        try:
            obj = self.db
            tokens = key.split(".")
            for tok in tokens:
                if type(obj) != dict:
                    raise KeyError()
                obj = obj[tok]
            return obj
        except KeyError:
            print("No Value Can Be Found for " + str(key))

    def delete(self, key):
        if not key in self.db:
            return False
        del self.db[key]
        self.dumpdb()
        return True

    def resetdb(self):
        self.db = {}
        self.dumpdb()
        return True
