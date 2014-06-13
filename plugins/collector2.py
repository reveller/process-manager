from base import Plugin
from time import sleep

class collector(Plugin):
    name = "SomeWayCoolCoolector"
    sleepSecs = 20
    def init(self):
        return "I am {0}.init()".format(self.name)

    def run(self, process_number, parent_p, child_p):
        cont = 1
        try:
            print "starting thread: ", process_number
            while True:
                try:
                    msg = child_p.recv()
                    if msg is None:
                        print("{0} is exiting".format(self.name))
                        break
                    print("{0} recv'd a {1} message from the parent".format(self.name, msg))
                except EOFError:
                    print("{0} hit an EOFError".format(self.name))
                    break
                print("{0} is doing something and then sleeping for {1} seconds."\
                    .format(self.name, str(self.sleepSecs)))
                sleep(self.sleepSecs)
        except KeyboardInterrupt:
            print "Keyboard interrupt in process: ", process_number
        finally:
            print "cleaning up thread", process_number
        return "I am {0}.run()".format(self.name)

    def shutdown(self):
        return "I am {0}.shutdown()".format(self.name)


