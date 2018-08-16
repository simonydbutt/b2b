from Pipeline_.main.Finance.AnalyseOpenTrades import AnalyseOpenTrades
import Settings
import yaml
from tinydb import TinyDB


class OpenClosePosition:

    def __init__(self, stratName, baseStratName, fees=0.001, dbPath='Pipeline_/DB',):
        self.fees = fees
        with open('%s/%s/Capital.yml' % (Settings.BASE_PATH, dbPath)) as capitalFile:
            self.capitalDict = yaml.load(capitalFile)
        with open('%s/%s/Configs/%s/%s.yml' % (Settings.BASE_PATH, dbPath, baseStratName, stratName)) as configFile:
            self.configFile = yaml.load(configFile)
        self.transLogDB = TinyDB('%s/%s/PerformanceLogs/%s/TransactionLog.ujson' %
                                 (Settings.BASE_PATH, dbPath, baseStratName))

    def openPosition(self, openDict):
        self.capitalDict['liquidCurrent'] -= openDict['capAllocated']
        self.capitalDict['percentAllocated'] = 100*round(1 - self.capitalDict['liquidCurrent']/self.capitalDict['paperCurrent'], 2)

    def closePosition(self, tradeDict):
        fees = self.fees if type(self.fees) != dict else self.fees[tradeDict['Exchange']]
        tradeDict['realPnL'] = tradeDict['capitalAllocated']*((1 - fees)*tradeDict['closePrice'] -
                                                              (1 + fees)*tradeDict['openPrice'])
        tradeDict['percentPnL'] = tradeDict['closePrice'] / tradeDict['openPrice'] - 1
        self.transLogDB.insert(tradeDict)
        self.capitalDict['liquidCurrent'] += (tradeDict['amountHeld'] / tradeDict['closePrice'])*(1-fees)
        self.capitalDict['paperPnL'] = float(self.capitalDict['paperCurrent'] / self.capitalDict['initialCapital'])
        pStats = self.configFile['performance']
        self.configFile['performance']['percentPnL'] = (pStats['percentPnL']*pStats['numTrades'] +
                                                        tradeDict['percentPnL']) / (pStats['percentPnL'] + 1)
        self.configFile['performance']['maxGain'] = max(pStats['maxGain'], tradeDict['percentPnL'])
        self.configFile['performance']['maxLoss'] = min(pStats['maxLoss'], tradeDict['percentPnL'])
        self.configFile['performance']['numTrades'] += 1
        isWin = 1 if tradeDict['percentPnL'] > 0 else 0
        self.configFile['performance']['winLoss'] = (pStats['winLoss'] * pStats['numTrades'] + isWin) / \
                                                    (pStats['numTrades'] + 1)

    def add2Books(self):
        AOT = AnalyseOpenTrades()
        self.capitalDict['percentAllocated'] = float(AOT.allocated(liquidCurrent=self.capitalDict['liquidCurrent']))
        self.capitalDict['paperCurrent'] = float(self.capitalDict['liquidCurrent'] + AOT.paperValue())
        with open('%s/Pipeline_/DB/Capital.yml' % Settings.BASE_PATH, 'w') as capFile:
            yaml.dump(self.capitalDict, capFile)