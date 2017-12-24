from bottle import route, run, template, request, redirect
import sqlite3
import pandas_highcharts.core as ph
from pandas.compat import StringIO
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

def mainaction():
    #histdataPath="histdata/DAT_ASCII_USDJPY_M1_2015.csv"
    #return TF_ohlc(read_histdata(histdataPath), 'H')
    dat = """ts;A;B;C
    2015-01-01 00:00:00;27451873;29956800;113
    2015-01-01 01:00:00;20259882;17906600;76
    2015-01-01 02:00:00;11592256;12311600;48
    2015-01-01 03:00:00;11795562;11750100;50
    2015-01-01 04:00:00;9396718;10203900;43
    2015-01-01 05:00:00;14902826;14341100;53"""
    df = pd.read_csv(pd.compat.StringIO(dat), sep=';', index_col='ts', parse_dates=True)
    return df

@route("/")
def index():
    df=mainaction()
    chart = ph.serialize(df, render_to='my-chart', output_type='json')
    return template("charts.tpl", chart=chart)

index()

if __name__ == "__main__":
    run(host="0.0.0.0",reloader=True,port=9999)
