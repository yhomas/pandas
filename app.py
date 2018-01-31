from bottle import route, run, template, request, redirect
import sqlite3
import pandas_highcharts.core as ph
from pandas.compat import StringIO
import numpy as np
import pandas as pd
import os
import psycopg2

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
    histdataPath="histdata/DAT_ASCII_USDJPY_M1_2015.csv"
    return TF_ohlc(read_histdata(histdataPath), 'H')

@route("/")
def index():
    df=mainaction()
    chart = ph.serialize(df, chart_type="stock", title="chart", render_to='my-chart', output_type='json', grid=True)
    return template("charts.tpl", chart=chart)

@route("/getchartdata")
def getchartdata():
    conn = psycopg2.connect("host=postgres port=5432 dbname=fxdb user="+os.environ["postgres_user"])
    cur =  conn.cursor()
    
    DBname="onem"
    cur.execute("SELECT timestamp,open,high,low,close FROM "+DBname+" WHERE timestamp IN (SELECT MAX(timestamp) FROM "+DBname+")")
    ohlc=cur.fetchone()
    input_ohlc="["+str(ohlc[0])+","+str(ohlc[1])+","+str(ohlc[2])+","+str(ohlc[3])+","+str(ohlc[4])+"]"

    return template(input_ohlc)

if __name__ == "__main__":
    run(host="0.0.0.0",reloader=True,port=9999)
