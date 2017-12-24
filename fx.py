import numpy as np
import pandas as pd

def read_histdata(histdataPath):
    dataM1 = pd.read_csv(histdataPath, sep=';',
                         names=('Time', 'Open', 'High', 'Low', 'Close', ''),
                         index_col='Time', parse_dates=True)
    return dataM1

def TF_ohlc(df, tf):
    x = df.resample(tf).ohlc()
    O = x['Open']['open']
    H = x['High']['high']
    L = x['Low']['low']
    C = x['Close']['close']
    ret = pd.DataFrame({'Open':O, 'High':H, 'Low':L, 'Close':C},
                        columns=['Open', 'High', 'Low', 'Close'])
    return ret.dropna()

def main():
    histdataPath="histdata/DAT_ASCII_USDJPY_M1_2015.csv"
    TF_ohlc(read_histdata(histdataPath), 'H')


if __name__ == "__main__":
    main()

