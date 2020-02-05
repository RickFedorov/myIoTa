import client
import threading

from logs.logger import get_my_logger
logger = get_my_logger(__name__)

def myIota(name):
    m = client.IOTA()
    m.run()


try:
    x = threading.Thread(target=myIota, args=(1,))
    x.start()
except:
    logger.exception("Client exception!")

