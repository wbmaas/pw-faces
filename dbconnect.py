import MySQLdb


def connection():
    conn = MySQLdb.connect(host='localhost', user='root', passwd='root', db='password')
    c = conn.cursor()
    return c, conn
