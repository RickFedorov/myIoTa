import client
import threading


def myIota(name):
    m = client.IOTA()
    m.run()


x = threading.Thread(target=myIota, args=(1,))
x.start()

