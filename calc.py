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
   
if __name__ == "__main__":
    class argstr:
        conn = psycopg2.connect("host=postgres port=5432 dbname=fxdb user="+os.environ["postgres_user"])
        conn_calc = psycopg2.connect("host=postgres port=5432 dbname=calcdb user="+os.environ["postgres_user"])
        cur =  conn.cursor()
        cur_calc =  conn_calc.cursor()

    wma_write(argstr, "onem")
