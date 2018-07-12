from Backtest.main.Attributes.lib import *
from Backtest.main.Visual.CandlestickChart import CandlestickChart
from Backtest.main.Data.Load import Load


class Attr:

    def __init__(self, df):
        self.df = df

    def add(self, metricName, fields=None, params={}):
        reqFields = self.df[fields] if fields else self.df
        attrList = eval(metricName)(df=reqFields, params=params).run()
        for attrVal in attrList:
            self.df[attrVal[0]] = attrVal[1]
        return self.df


# df = Load('binance').loadOne('BNBBTC_12h', '01/01/2018', timeEnd='01/06/2018')
# df = Attr(
#     Attr(df).add('MA', params={'numPeriods': 50})
# ).add('Bollinger', params={'numPeriods': 50, 'numStd': 1.5})
# CandlestickChart().plot(df, 12*60*60, MA=['ma50'], Bollinger=True)
