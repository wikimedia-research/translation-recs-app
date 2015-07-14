import pymysql
import pandas as pd
import os


# mysql -us52262 -peolaiheiheeviish -hlabsdb1001.eqiad.wmnet

def mysql_to_pandas(dicts):
    dmaster = {}
    for d in dicts:
        for k in d.keys():
            if k not in dmaster:
                dmaster[k] = []
            
            dmaster[k].append(d[k]) 
    return pd.DataFrame(dmaster)

def query_through_tunnel(port,cnf_path, query, params):
    conn = pymysql.connect(host="127.0.0.1", port=port, read_default_file=cnf_path)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return mysql_to_pandas(rows)

def query_db(query, params):
    return query_through_tunnel(8001, "~/.stat3.cnf", query, params)