from multiprocessing.dummy import Pool as ThreadPool
from telnet import telnet_remote
import re
import MySQLdb
from Queue import Queue

user_pattern = re.compile(r'(.*3389\s+)(\d+.\d+.\d+.\d+)(:\d+)', re.DOTALL)

class PooledConnection(object):
    def __init__(self, maxconnections):
        self._pool = Queue(maxconnections)
        self.maxconnctions = maxconnections

        try:
            for i in range(maxconnections):
                self.fill_connection(self.create_connection())
        except Exception, e:
            raise e

    def fill_connection(self, conn):
        try:
            self._pool.put(conn)
        except Exception, e:
            raise "fill connection error:",e

    def free_connection(self, conn):
        try:
            self._pool.put(conn)
        except Exception, e:
            raise "free connection error:",e

    def get_connection(self):
        try:
            db_conn = self._pool.get()
            """ maybe connection timeout """
            try:
                db_conn.ping()
            except Exception, e:
                db_conn = MySQLdb.connect("localhost", "root", "qwe", "pcmanager")
                db_conn.ping()
            return db_conn

        except Exception, e:
            raise "get connection error:",e


    def create_connection(self):
        try:
            db_conn = MySQLdb.connect("localhost", "root", "qwe", "pcmanager")
            db_conn.ping()
            return db_conn
        except Exception, e:
            raise "conn target db error", e
            return None

DB_POOL = PooledConnection(10)
LOCALDB = dict()

def localdb_update():
    db_conn = DB_POOL.get_connection()
    db_conn.commit()
    cursor = db_conn.cursor()
    cursor.execute("select ip, status, user from pcinfor ")
    localdb = cursor.fetchall()
    cursor.close()
    print localdb

    for item in localdb:
        LOCALDB[item[0]] = item[1:]
    print LOCALDB
    DB_POOL.free_connection(db_conn)

localdb_update()

def get_user_from_host(host):
    """ get user from host """
    return host[-4:]

def update_db(host, ret_msg):
    user = 'None'
    if "ESTABLISHED" in ret_msg:
        match = user_pattern.match(ret_msg)
        if match:
            user = match.group(2)
        print "get the user:",user[-5:]
        user = user[-5:]
        status = "running"
    elif "timed out" in ret_msg:
        status = "poweroff"
        print "time out unreachable"
    else:
        status = "None"
        print "not one get in"

    if host not in LOCALDB:
        localdb_update()

    if host in LOCALDB and LOCALDB[host][0] != status:
        """ update db infor and localdb"""
        db_conn = DB_POOL.get_connection()
        cursor = db_conn.cursor()
        sql = "update pcinfor set status='%s' where ip='%s'" % (status, host)
        print sql
        cursor.execute(sql)
        cursor.close()
        db_conn.commit()
        DB_POOL.free_connection(db_conn)
        localdb_update()

    if host in LOCALDB  and LOCALDB[host][1] != user:
        """ update db infor and localdb"""
        db_conn = DB_POOL.get_connection()
        cursor = db_conn.cursor()
        sql = "update pcinfor set user='%s' where ip='%s'" % (user, host)
        cursor.execute(sql)
        cursor.close()
        db_conn.commit()
        DB_POOL.free_connection(db_conn)
        localdb_update()

def remote_status_update(host):
    msg = telnet_remote(host)
    update_db(host, msg)

pool = ThreadPool(20)
hosts = ["10.69.22.84", "10.69.22.82", "10.69.22.222"]
result = pool.map(remote_status_update, hosts)
#print "result:", result
pool.close()
pool.join()
