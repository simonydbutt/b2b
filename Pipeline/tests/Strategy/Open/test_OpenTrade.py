from Pipeline.main.Strategy.Open.OpenTrade import OpenTrade
from Pipeline.tests.CreateCleanDir import CreateCleanDir
from pymongo import MongoClient
import Settings
import yaml


dbPath = 'Pipeline/resources/testOPStrat'
compPath = '%s/%s' % (Settings.BASE_PATH, dbPath)
CCD = CreateCleanDir(filePathList=[dbPath])
client = MongoClient('localhost', 27017)


def before():
    CCD.create()
    client.drop_database('testOPStrat')
    configParams = {
        'enter': {'bolStd': 2, 'granularity': 43200, 'name': 'CheapVol', 'periodsMA': 5, 'periodsVolLong': 5,
                  'periodsVolShort': 5, 'volCoef': 1.5},
        'stratName': 'testStrat',
        'positionSize': {'name': 'Basic', 'percent': 0.05}
    }
    with open('%s/config.yml' % compPath, 'w') as configFile:
        yaml.dump(configParams, configFile)
    baseCapFile = {'initialCapital': 10,'liquidCurrent': 10, 'paperCurrent': 10,'paperPnL': 0, 'percentAllocated': 10}
    with open('%s/capital.yml' % compPath, 'w') as capFile:
        yaml.dump(baseCapFile, capFile)
    OT = OpenTrade(stratName='testOPStrat')
    OT.open(assetVals=('ETHBTC', 'Binance', 0.7))
    return baseCapFile, compPath, OT


def after():
    client.drop_database('testOpenPosStrat')
    CCD.clean()


def test_open():
    baseCapFile, dbPath, OT = before()
    entry = list(client['testOPStrat']['currentPositions'].find({'assetName': 'ETHBTC'}))
    assert len(entry) == 1
    for i in ['assetName', 'openPrice', 'currentPrice', 'periods', 'positionSize', 'paperSize', 'TSOpen', 'exchange']:
        assert i in list(entry[0])
    after()


def test_updateBooks():
    baseCapFile, dbPath, OT = before()
    OT.updateBooks()
    with open('%s/capital.yml' % dbPath) as capFile:
        currentCap = yaml.load(capFile)

    assert currentCap['paperCurrent'] == 10 * (1 - 0.05*0.001)
    assert currentCap['liquidCurrent'] == 9.5
    assert currentCap['percentAllocated'] == 0.05
    assert currentCap['paperPnL'] == 1


if __name__ == '__main__':
    test_updateBooks()
    test_open()
