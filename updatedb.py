from multiprocessing.dummy import Pool as ThreadPool
from telnet import telnet_remote

pool = ThreadPool(20)
hosts = ["10.69.22.84", "10.69.22.82", "10.69.22.222"]
result = pool.map(telnet_remote, hosts)
#print "result:", result
pool.close()
pool.join()
