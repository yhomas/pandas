"""
Demonstrates streaming feature in OANDA open api

To execute, run the following command:

python streaming.py [options]

To show heartbeat, replace [options] by -b or --displayHeartBeat
"""

import requests
import json
import os
import psycopg2
import re
import datetime

from optparse import OptionParser

def connect_to_stream():

    """
    Environment                 Description 
    fxTrade (Live)              The live (real money) environment 
    fxTrade Practice (Demo)     The demo (simulated money) environment 
    """
    domainDict = { 'live' : 'stream-fxtrade.oanda.com',
               'demo' : 'stream-fxpractice.oanda.com' }

    # Replace the following variables with your personal values 
    environment = "demo" # Replace this 'live' if you wish to connect to the live environment 
    domain = domainDict[environment] 
    access_token = os.environ["access_token"]
    account_id = os.environ["account_id"]
    instruments = 'USD_JPY' 

    try:
        s = requests.Session()
        url = "https://" + domain + "/v1/prices"
        headers = {'Authorization' : 'Bearer ' + access_token,
                   # 'X-Accept-Datetime-Format' : 'unix'
                  }
        params = {'instruments' : instruments, 'accountId' : account_id}
        req = requests.Request('GET', url, headers = headers, params = params)
        pre = req.prepare()
        resp = s.send(pre, stream = True, verify = True)
        return resp
    except Exception as e:
        s.close()
        print("Caught exception when connecting to stream\n" + str(e)) 



def UpdateDB(DBname, StartTime, cur, conn, rate, split_num, match_time, msg, MorH):
    cur.execute("SELECT MAX(timestamp) FROM "+DBname)
    DBLastTimestamp=cur.fetchone()[0]

    if DBLastTimestamp == None:
        cur.execute("INSERT INTO "+DBname+" VALUES(1,%s,%s,%s,%s,%s,%s)", (StartTime, msg["tick"]["instrument"], rate, rate ,rate, rate,))
    else:
        if MorH == "M":
            LastTimeStamp = int(DBLastTimestamp.minute)

        elif MorH == "H":
            LastTimeStamp = int(DBLastTimestamp.hour)

        if LastTimeStamp != (int(match_time) // split_num)*split_num:
            cur.execute("INSERT INTO "+DBname+" VALUES((SELECT MAX(id)+1 from "+DBname+"),%s,%s,%s,%s,%s,%s)", (StartTime, msg["tick"]["instrument"], rate, rate ,rate, rate,))
            conn.commit()

        else:
            cur.execute("SELECT open,high,low,close FROM "+DBname+" WHERE timestamp IN (SELECT MAX(timestamp) FROM "+DBname+")")
            ohlc=cur.fetchone()

            if ohlc[1] < rate:
                cur.execute("UPDATE "+DBname+" SET high = %s WHERE timestamp IN (SELECT MAX(timestamp) FROM "+DBname+")", (rate,))

            if ohlc[2] > rate:
                cur.execute("UPDATE "+DBname+" SET low = %s WHERE timestamp IN (SELECT MAX(timestamp) FROM "+DBname+")", (rate,))
                
            cur.execute("UPDATE "+DBname+" SET close = %s WHERE timestamp IN (SELECT MAX(timestamp) FROM "+DBname+")", (rate,))
            conn.commit()

def demo(displayHeartbeat):
    response = connect_to_stream()
    if response.status_code != 200:
        print(response.text)
        return

    conn = psycopg2.connect("host=postgres port=5432 dbname=fxdb user="+os.environ["postgres_user"])
    cur =  conn.cursor()
    r_extract_min = re.compile(":\d{2}:")
    r_extract_hour = re.compile("T\d{2}:")
    r_extract_digit = re.compile("\d{2}")

    for line in response.iter_lines(1):
        if line:
            try:
                line = line.decode('utf-8')
                msg = json.loads(line)

            except Exception as e:
                print("Caught exception when converting message into json\n" + str(e))
                return

            if "instrument" in msg or "tick" in msg or displayHeartbeat:
                #cur.execute("INSERT INTO tick VALUES((SELECT MAX(id)+1 FROM tick),%s,%s,%s,%s)",(msg["tick"]["time"], msg["tick"]["instrument"], msg["tick"]["bid"], msg["tick"]["ask"],))
                #conn.commit()
                
                rate=msg["tick"]["bid"]

                # exam) 2018-01-30T09:44:49.976256Z
                match_min_obj = r_extract_min.search(msg["tick"]["time"])
                match_hour_obj = r_extract_hour.search(msg["tick"]["time"])
                
                match_min = r_extract_digit.search(match_min_obj.group(0)).group(0)
                match_hour = r_extract_digit.search(match_hour_obj.group(0)).group(0)


                oneMStartTime = re.sub(":\d{2}\.\d{6}Z", ":00.000000Z", msg["tick"]["time"])

                twoMStartTime = re.sub("\d{2}:\d{2}\.\d{6}Z", str((int(match_min) // 2)*2)+":00.000000Z", msg["tick"]["time"])
                threeMStartTime = re.sub("\d{2}:\d{2}\.\d{6}Z", str((int(match_min) // 3)*3)+":00.000000Z", msg["tick"]["time"])
                fiveMStartTime = re.sub("\d{2}:\d{2}\.\d{6}Z", str((int(match_min) // 5)*5)+":00.000000Z", msg["tick"]["time"])
                tenMStartTime = re.sub("\d{2}:\d{2}\.\d{6}Z", str((int(match_min) // 10)*10)+":00.000000Z", msg["tick"]["time"])
                fifteenMStartTime = re.sub("\d{2}:\d{2}\.\d{6}Z", str((int(match_min) // 15)*15)+":00.000000Z", msg["tick"]["time"])
                thirtyMStartTime = re.sub("\d{2}:\d{2}\.\d{6}Z", str((int(match_min) // 30)*30)+":00.000000Z", msg["tick"]["time"])
                oneHStartTime = re.sub("\d{2}:\d{2}:\d{2}\.\d{6}Z", str((int(match_hour) // 1)*1)+":00:00.000000Z", msg["tick"]["time"])
                fourHStartTime = re.sub("\d{2}:\d{2}:\d{2}\.\d{6}Z", str((int(match_hour) // 4)*4)+":00:00.000000Z", msg["tick"]["time"])
                eightHStartTime = re.sub("\d{2}:\d{2}:\d{2}\.\d{6}Z", str((int(match_hour) // 8)*8)+":00:00.000000Z", msg["tick"]["time"])
                UpdateDB("onem", oneMStartTime, cur, conn, rate, 1, match_min, msg, "M")
                UpdateDB("twom", twoMStartTime, cur, conn, rate, 2, match_min, msg, "M")
                UpdateDB("fivem", fiveMStartTime, cur, conn, rate, 5, match_min, msg, "M")
                UpdateDB("tenm", tenMStartTime, cur, conn, rate, 10, match_min, msg, "M")
                UpdateDB("fifteenm", fifteenMStartTime, cur, conn, rate, 15, match_min, msg, "M")
                UpdateDB("thirtym", thirtyMStartTime, cur, conn, rate, 30, match_min, msg, "M")
                UpdateDB("oneH", oneHStartTime, cur, conn, rate, 1, match_hour, msg, "H")
                UpdateDB("fourH", fourHStartTime, cur, conn, rate, 4, match_hour, msg, "H")
                UpdateDB("eightH", eightHStartTime, cur, conn, rate, 8, match_hour, msg, "H")


def main():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-b", "--displayHeartBeat", dest = "verbose", action = "store_true", 
                        help = "Display HeartBeat in streaming data")
    displayHeartbeat = False

    (options, args) = parser.parse_args()
    if len(args) > 1:
        parser.error("incorrect number of arguments")
    if options.verbose:
        displayHeartbeat = True
    demo(displayHeartbeat)


if __name__ == "__main__":
    main()
