import getpass
import sys
import telnetlib

HOST = "10.69.22.84"
password = "btstest"
user = "upl1-tester"
tn = telnetlib.Telnet(HOST)
#tn.set_debuglevel(2)
tn.read_until("login:")
tn.write(user + "\r\n")
if password:
    tn.read_until("password:")
    tn.write(password + "\r\n")
tn.read_until("upl1-tester>")
tn.write("netstat -ano | find \"3389\"\r\n")
print tn.read_until("upl1-tester>")
tn.write("exit\r\n")
tn.close()
