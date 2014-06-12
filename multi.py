from multiprocessing import Process
from multiprocessing.managers import SyncManager
import signal
from time import sleep
import sys
from base import init_plugins

# initializer for SyncManager
def mgr_init():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    print 'initialized manager'

def f(process_number, shared_array):
    try:
        print "starting thread: ", process_number
        while True:
            shared_array.append(process_number)
            sleep(3)
    except KeyboardInterrupt:
        print "Keyboard interrupt in process: ", process_number
    finally:
        print "cleaning up thread", process_number


if __name__ == '__main__':

    init_plugins()
    sys.exit(0)

    processes = []

  # now using SyncManager vs a Manager
    manager = SyncManager()

    print type(manager), manager.__dict__

    # explicitly starting the manager, and telling it to ignore the interrupt signal
    manager.start(mgr_init)
    #manager.start()
    try:
        shared_array = manager.list()

        for i in xrange(4):
            p = Process(target=f, args=(i, shared_array))
            p.start()
            processes.append(p)

        try:
            for process in processes:
                process.join()
        except KeyboardInterrupt:
            print "Keyboard interrupt in main"

        for item in shared_array:
            # we still have access to it!  Yay!
            print item
    finally:
      # to be safe -- explicitly shutting down the manager
        manager.shutdown()

