from multiprocessing import Process, Pipe
from multiprocessing.managers import SyncManager
import signal
from time import sleep
import sys
import re
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
        self.running    = True

def number_running(collector_dict):
    run_cnt = 0
    for each in collector_dict:
        if collector_dict[each].running:
            run_cnt += 1
    return run_cnt


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
            collectors[collector.name].running = True

        # Send a SAMPLE msg to each collector
        for each in collectors:
            name = collectors[each].collector.name
            msg = "SAMPLE-" + name
            print("Sending {0} to {1}".format(msg, name))
            collectors[each].parent_p.send(msg)

        stop_cnt = 0
        cont = 1
        while cont:
            try:
                for each in collectors:
                    # while there are msgs in the pipe from this collector
                    #   read and process them
                    #   (this could get ugly is a collector streams msgs
                    #   faster than the parent can process them [like
                    #   httpd access logs].  need to do something to prevent
                    #   spamming the pipe and not letting others have a turn)
                    # once the pipe has cleared once for each collector,
                    #   sleep for a second to give th rest of the system a
                    #   chance
                    while collectors[each].parent_p.poll():
                        msg = collectors[each].parent_p.recv()
                        m = re.search('(.+)-(.+)', msg)
                        msg_type = m.group(1)
                        msg_from = m.group(2)
                        if msg_type == "STOPPED":
                            print("{0} message recv'd from {1}".format(msg, msg_from))
                            collectors[msg_from].running = False
                            if number_running(collectors) == 0:
                                print("No one is running - shutting down - I wouldn't really do this for realsies")
                                cont = 0
                        elif msg_type is not None:
                            print("Parent recv'd a {0} message from {1} - {2}".format(msg_type, msg_from, msg))
                sleep(1)
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

