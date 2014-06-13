from multiprocessing import Process, Pipe
from multiprocessing.managers import SyncManager
import signal
from time import sleep
import sys
from base import init_plugins

# initializer for SyncManager
def mgr_init():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    print 'initialized manager'

class CollectorProcess():
    def __init__(self, process, collector, parent_p, child_p):
        self.run_function = None
        self.process    = process
        self.collector  = collector
        self.parent_p   = parent_p
        self.child_p    = child_p



if __name__ == '__main__':
    collectors = {}

    manager = SyncManager()
    # explicitly starting the manager, and telling it to ignore the interrupt signal
    manager.start(mgr_init)

    collector_plugins = init_plugins()
    try:
        numCollectors = 0
        for each in collector_plugins:
            numCollectors += 1
            collector = collector_plugins[each].collector()
            parent_p, child_p = Pipe()
            p = Process(target=collector.run, args=(numCollectors, parent_p, child_p))
            p.start()
            collectors[collector.name] = CollectorProcess(p, collector, parent_p, child_p)

        # Send a SAMPLE msg to each collector
        for each in collectors:
            name = collectors[each].collector.name
            msg = "SAMPLE-" + name
            print("Sending {0} to {1}".format(msg, name))
            collectors[each].parent_p.send(msg)

        msg_cnt = 0
        cont = 1
        while cont:
            try:
                for each in collectors:
                    if not collectors[each].parent_p.poll():
                        continue
                    msg = collectors[each].parent_p.recv()
                    if msg is not None:
                        print("Parent recv'd a {0} message from a child".format(msg))
                        msg_cnt += 1
                        if msg_cnt == len(collectors):
                            print("Got one from every child - shutting down")
                            cont = 0
            except:
                print("Error checking pipes")

        # Send a poison pill for each collector in order to signal a terminate
        for each in collectors:
            collectors[each].parent_p.send(None)

        # Wait for the collectors to finish - this will change to a loop for
        # new collector plugins
        try:
            for each in collectors:
                collectors[each].process.join()
        except KeyboardInterrupt:
            print "Keyboard interrupt in main"

    finally:
      # to be safe -- explicitly shutting down the manager
        manager.shutdown()

