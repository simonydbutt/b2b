from Backtest.main.Utils.TimeUtil import TimeUtil
import pandas as pd
from pymongo import MongoClient, ASCENDING


class Load:

    def __init__(self, dbName):
        self.TU = TimeUtil()
        self.db = MongoClient('localhost', 27017)[dbName]

    def listAssets(self, contains=''):
        return [col for col in self.db.list_collection_names() if contains in col]

    def loadOne(self, col, timeStart, timeEnd=None, limit=100, paramList=None):
        """
            timeStart in format:
                -> TS
                -> 'dd/mm/yyyy'
        """
        timeStart = self.TU.getTS(timeStart, timeFormat='%d/%m/%Y') if type(timeStart) == str else timeStart
        timeEnd = self.TU.getTS(timeEnd, timeFormat='%d/%m/%Y') if type(timeEnd) == str else timeEnd
        paramDict = {} if not paramList else {val: 1 for val in paramList}
        if timeEnd:
            data = list(self.db[col].find(
                {
                    'TS': {
                        '$gte': timeStart,
                        '$lte': timeEnd
                    }
                },
                {
                    **paramDict,
                    '_id': 0
                }
            ).sort('TS', ASCENDING))
        else:
            data = list(self.db[col].find(
                {
                    'TS': {
                        '$gte': timeStart
                    }
                },
                {
                    **paramDict,
                    '_id': 0
                }
            ).sort('TS', ASCENDING).limit(limit))
        key = list(self.db[col].find_one({}, {'_id': 0}).keys()) if not paramList else paramList
        return pd.DataFrame(data, columns=key)