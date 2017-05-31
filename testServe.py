import sys
from time import sleep, time
import multiprocessing
import xsig

secUpdate = 5

mgr = multiprocessing.Manager()
dictionary = mgr.dict()
serverLocal = multiprocessing.Process(target=xsig.startServe, args=(60001, dictionary))

if __name__ == '__main__':
    ## multiprocessing server
    serverLocal.start()
    while True:
        secStartLoop = time()
#        print ( 'still ticking, {0}'.format(time()))
        if len(dictionary):
            print (dictionary)
        while time() - secStartLoop < secUpdate:
            sleep(0.1)
        
