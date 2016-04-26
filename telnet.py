import telnetlib
import re
import MySQLdb

user_pattern = re.compile(r'(.*3389\s+)(\d+.\d+.\d+.\d+)(:\d+)', re.DOTALL)
db = MySQLdb.connect("localhost", "root", "qwe", "pcmanager")
cursor = db.cursor()
cursor.execute("""select * from pcinfor """)
localdb = cursor.fetchall()
print localdb

def update_db(host, ret_msg):
    if "ESTABLISHED" in ret_msg:
        match = user_pattern.match(ret_msg)
        if match:
            user = match.group(2)
        print "get the user:",user
    elif "timed out" in ret_msg:
        print "time out unreachable"
    else:
        print "not one get in"

    """ update db infor and localdb"""
    cursor = db.cursor()
    cursor.execute("update pcinfor set status='running' where ip='10.69.22.84'")
    db.commit()


def telnet_remote(host):
    password = "btstest"
    user = "upl1-tester"
    print "host:", host
    try:
        tn = telnetlib.Telnet(host, timeout=3)
        #tn.set_debuglevel(2)
        tn.read_until("login:")
        tn.write(user + "\r\n")
        if password:
            tn.read_until("password:")
            tn.write(password + "\r\n")
        tn.read_until("upl1-tester>")
        tn.write("netstat -ano | find \"3389\"\r\n")
        ret_msg = tn.read_until("upl1-tester>")
        print ret_msg
        update_db(host, ret_msg)
        tn.write("exit\r\n")
        tn.close()
    except Exception, e:
        update_db(host, e)
        print e


if __name__ == "__main__":
    telnet_remote("10.69.22.222")