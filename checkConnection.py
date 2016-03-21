import psycopg2
try:
    conn = psycopg2.connect("host=localhost dbname=facultyRank")
    conn.close();
except psycopg2.OperationalError, ex:
    print("Connection failed: {0}".format(ex));
