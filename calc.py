import numpy as np
import psycopg2
import os

def wma_write(argstr, TABLEname):
    argstr.cur.execute("SELECT timestamp, high, low, close FROM "+TABLEname+" ORDER BY timestamp DESC LIMIT 3")
    DESC_lists=argstr.cur.fetchall()
    array=np.array(DESC_lists)
    if len(array) < 3:
        return

    wma_timestamp=array[0][0]
    wma_value=(((array[0][1]+array[0][2]+array[0][3]*2)/4)*3+((array[1][1]+array[1][2]+array[1][3]*2)/4)*2+((array[2][1]+array[2][2]+array[2][3]*2)/4)*1)/(3+2+1)

    argstr.cur_calc.execute("INSERT INTO "+TABLEname+"_wma(timestamp, value) VALUES(%s,%s)",(wma_timestamp,wma_value,))
    argstr.conn_calc.commit()

def wma_dow(argstr, TABLEname):
    argstr.cur_calc.execute("SELECT timestamp, value FROM "+TABLEname+"_wma ORDER BY timestamp DESC LIMIT 3")
    DESC_lists=argstr.cur_calc.fetchall()
    if len(DESC_lists) < 3:
        return

    if DESC_lists[0][1] < DESC_lists[1][1] and DESC_lists[1][1] > DESC_lists[2][1]:
        argstr.cur_calc.execute("UPDATE "+TABLEname+"_wma SET state='mountain' WHERE timestamp = '"+str(DESC_lists[1][0])+"'")
        argstr.cur_calc.execute("SELECT timestamp, value FROM "+TABLEname+"_wma WHERE state = 'valley' OR state = 'plain' ORDER BY timestamp DESC LIMIT 1")
        DESC_lists_f=argstr.cur_calc.fetchall()
        if len(DESC_lists_f) == 0:
            return

        eliot_length = DESC_lists_f[0][1] - DESC_lists[1][1]
        argstr.cur_calc.execute("UPDATE "+TABLEname+"_wma SET eliot_length= "+str(eliot_length)+" WHERE timestamp = '"+str(DESC_lists[1][0])+"'")

    elif DESC_lists[0][1] > DESC_lists[1][1] and DESC_lists[1][1] < DESC_lists[2][1]:
        argstr.cur_calc.execute("UPDATE "+TABLEname+"_wma SET state='valley' WHERE timestamp = '"+str(DESC_lists[1][0])+"'")
        argstr.cur_calc.execute("SELECT timestamp, value FROM "+TABLEname+"_wma WHERE state = 'mountain' OR state = 'plain' ORDER BY timestamp DESC LIMIT 1")
        DESC_lists_f=argstr.cur_calc.fetchall()
        if len(DESC_lists_f) == 0:
            return

        eliot_length = DESC_lists_f[0][1] - DESC_lists[1][1]
        argstr.cur_calc.execute("UPDATE "+TABLEname+"_wma SET eliot_length= "+str(eliot_length)+" WHERE timestamp = '"+str(DESC_lists[1][0])+"'")

    elif DESC_lists[0][1] < DESC_lists[1][1] and DESC_lists[1][1] < DESC_lists[2][1]:
        argstr.cur_calc.execute("UPDATE "+TABLEname+"_wma SET state='downhill' WHERE timestamp = '"+str(DESC_lists[1][0])+"'")

    elif DESC_lists[0][1] > DESC_lists[1][1] and DESC_lists[1][1] > DESC_lists[2][1]:
        argstr.cur_calc.execute("UPDATE "+TABLEname+"_wma SET state='ascent' WHERE timestamp = '"+str(DESC_lists[1][0])+"'")

    elif DESC_lists[0][1] == DESC_lists[1][1]:
        argstr.cur_calc.execute("UPDATE "+TABLEname+"_wma SET state='plain' WHERE timestamp = '"+str(DESC_lists[1][0])+"' OR timestamp = '"+str(DESC_lists[0][0])+"'")


if __name__ == "__main__":
    class argstr:
        conn = psycopg2.connect("host=postgres port=5432 dbname=fxdb user="+os.environ["postgres_user"])
        conn_calc = psycopg2.connect("host=postgres port=5432 dbname=calcdb user="+os.environ["postgres_user"])
        cur =  conn.cursor()
        cur_calc =  conn_calc.cursor()

    wma_write(argstr, "onem")
