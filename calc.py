import numpy as np

def wma_write(cur, conn, TABLEname):
    cur.execute("SELECT timestamp, high, low, close FROM "+TABLEname+" ORDER BY timestamp DESC LIMIT 3")
    DESC_lists=cur.fetchall()
    np.array(DESC_lists)

    for DESC_list in DESC_lists:
        DESC_list

    
   
if __name__ == "__main__":
    conn = psycopg2.connect("host=postgres port=5432 dbname=fxdb user="+os.environ["postgres_user"])
    cur =  conn.cursor()
