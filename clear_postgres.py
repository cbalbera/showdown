import psycopg2
import sys
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s -  %(levelname)s-  %(message)s')
logging.debug('Start of clear')
logging.disable(logging.CRITICAL)

db_name = "postgres" #input("What is your database name?")
#print("try/except")
try: db_pwd = sys.argv[1]
except: db_pwd = input("What is your database password?")
showdown_connection = psycopg2.connect(f"dbname={db_name} user=postgres host=/tmp password={db_pwd}")
showdown_cursor = showdown_connection.cursor()

positive_responses = ["Y","y","YES","Yes","yes",True]

def clear(curs,conn):
    curs.execute("DROP TABLE pitcher_stats;")
    curs.execute("DROP TABLE hitter_stats;")
    conn.commit()

    return

if len(sys.argv) < 3: 
    pass
elif sys.argv[2] in positive_responses:
    clear(showdown_cursor,showdown_connection)
    quit()

"""if truly necessary:
This will clear all locks on all tables.

curs.execute(SELECT pg_terminate_backend(pid))
conn.commit()
"""