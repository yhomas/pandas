from bottle import route, template, run, request, redirect, static_file, auth_basic
import sqlite3
import pandas_highcharts.core as ph
from pandas.compat import StringIO
import numpy as np
import pandas as pd
import os
import psycopg2
from datetime import datetime

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


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@route('/tmpl/<filename>')
def css_dir(filename):
    return static_file(filename, root=BASE_DIR+"/tmpl")

@route('/tmpl/css/<filename>')
def css_dir(filename):
    return static_file(filename, root=BASE_DIR+"/tmpl/css")

@route('/tmpl/js/<filename>')
def css_dir(filename):
    return static_file(filename, root=BASE_DIR+"/tmpl/js")

@route('/tmpl/tmpl/<filename>')
def css_dir(filename):
    return static_file(filename, root=BASE_DIR+"/tmpl/fonts")

@route('/tmpl/fonts/codropsicons/<filename>')
def css_dir(filename):
    return static_file(filename, root=BASE_DIR+"/tmpl/fonts/codropsicons/")

@route('/tmpl/fonts/ecoicons/<filename>')
def css_dir(filename):
    return static_file(filename, root=BASE_DIR+"/tmpl/fonts/ecoicons/")

@route("/")
def index():
    df=mainaction()
    chart = ph.serialize(df, chart_type="stock", title="chart", render_to='my-chart', output_type='json', grid=True)
    return template("tmpl/charts.tpl", chart=chart)

@route("/getchartdata")
def getchartdata():
    conn = psycopg2.connect("host=postgres port=5432 dbname=fxdb user="+os.environ["postgres_user"])
    cur =  conn.cursor()
    
    DBname="onem"
    cur.execute("SELECT timestamp,open,high,low,close FROM "+DBname+" WHERE timestamp IN (SELECT MAX(timestamp) FROM "+DBname+")")
    ohlc=list(cur.fetchone())
    date_obj=datetime.strptime(str(ohlc[0]), '%Y-%m-%d %H:%M:%S')
    ohlc[0]=str(date_obj.timestamp()).split(".")[0]+"000"
    input_ohlc='{"time":'+str(ohlc[0])+',"o":'+str(ohlc[1])+',"h":'+str(ohlc[2])+',"l":'+str(ohlc[3])+',"c":'+str(ohlc[4])+'}'

    return input_ohlc

def init_input_ohlc(ohlc):
    date_obj=datetime.strptime(str(ohlc[0]), '%Y-%m-%d %H:%M:%S')
    new_timestamp=str(date_obj.timestamp()).split(".")[0]+"000"
    #new_input_ohlc='{"time":'+str(new_timestamp)+',"o":'+str(ohlc[1])+',"h":'+str(ohlc[2])+',"l":'+str(ohlc[3])+',"c":'+str(ohlc[4])+'}'
    new_input_ohlc=[int(new_timestamp), float(ohlc[1]), float(ohlc[2]), float(ohlc[3]), float(ohlc[4])]

    return new_input_ohlc

@route("/getchartpastdata")
def getchartpastdata():
    conn = psycopg2.connect("host=postgres port=5432 dbname=fxdb_bt user="+os.environ["postgres_user"])
    cur =  conn.cursor()

    DBname="onem"
    cur.execute("SELECT timestamp,open,high,low,close FROM "+DBname+" ORDER BY timestamp DESC LIMIT 2000")
    ohlcs=cur.fetchall()
    ohlcs_list='{"ohlclist":'+str(list(map(init_input_ohlc,ohlcs))[::-1])+'}'
    #ohlcs_list=str(list(map(init_input_ohlc,ohlcs)))

    return ohlcs_list


if __name__ == "__main__":
    run(host="0.0.0.0",reloader=True,port=9999)
