from tinydb import TinyDB
import Settings
import logging
import yaml
import os


class Build:

    """
        __Requirements__

        enterParams*
            - name
            - granularity

        exitParams*
            - name
            - granularity

        positionSizeParams*
            - name

        assetSelectionParams*
            - name
            - exchangeList
            - baseAsset

        * Indiv requirements are noted at top of class
    """

    def __init__(self, dbName, stratName, initialCapital, positionSizeParams, enterParams, assetSelectionParams,
                 exitParams, loggingParams={'console': logging.WARNING, 'terminal': logging.INFO}):
        self.compPath = '%s/Pipeline/DB/%s/%s' % (Settings.BASE_PATH, dbName, stratName)
        if os.path.exists(self.compPath):
            print('Strat already exists. Print Y to overwrite')
            if input() == 'Y':
                self.buildStrat(stratName=stratName, assetSelectionParams=assetSelectionParams,
                                positionSizeParams=positionSizeParams, enterParams=enterParams, exitParams=exitParams,
                                loggingParams=loggingParams, initialCapital=initialCapital)
        else:
            self.buildStrat(stratName=stratName, assetSelectionParams=assetSelectionParams,
                            positionSizeParams=positionSizeParams, enterParams=enterParams, exitParams=exitParams,
                            loggingParams=loggingParams, initialCapital=initialCapital)

    def buildStrat(self, stratName, assetSelectionParams, positionSizeParams,
                   enterParams, exitParams, loggingParams, initialCapital):
        configDict = {
            'stratName': stratName, 'assetSelection': assetSelectionParams,
            'positionSize': positionSizeParams, 'enter': enterParams, 'exit': exitParams,
            'logging': loggingParams
        }
        for path in (self.compPath, '%s/CodeLogs' % self.compPath, '%s/TransactionLogs' % self.compPath):
            os.mkdir(path) if not os.path.isdir(path) else None
        with open('%s/config.yml' % self.compPath, 'w') as configFile:
            yaml.dump(configDict, configFile)
        with open('%s/capital.yml' % self.compPath, 'w') as capFile:
            yaml.dump(
                {
                    'initialCapital': initialCapital,
                    'liquidCurrent': initialCapital,
                    'paperCurrent': initialCapital,
                    'paperPnL': 0,
                    'percentAllocated': 0
                },
                capFile
            )
        TinyDB('%s/currentPositions.ujson' % self.compPath)


# # Test
# Build(
#     stratName='CheapVol_ProfitRun',
#     dbName='disco',
#     initialCapital=10,
#     positionSizeParams={
#         'name': 'Basic',
#         'percent': 0.05},
#     assetSelectionParams={
#         'name': 'All',
#         'exchangeList': ['Binance'],
#         'baseAsset': BTC
#     },
#     enterParams={
#         'name': 'CheapVol',
#         'granularity': 43200,
#         'periodsVolLong': 100,
#         'periodsVolShort': 5,
#         'periodsMA': 100,
#         'volCoef': 1.5,
#         'bolStd': 2
#     },
#     exitParams={
#         'name': 'ProfitRun',
#         'granularity': 7200,
#         'periodsVolLong': 50,
#         'periodsVolShort': 5,
#         'periodsMA': 50,
#         'volCoef': 1,
#         'bolStd': 2
#     }
# )