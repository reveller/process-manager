from base import Plugin
from time import sleep


class collector(Plugin):
    name = "YetAnotherCoolCollector"
    sleepSecs = 1
    def init(self):
        return "I am collector_{0}.init()".format(self.name)

    def run(self, process_number, shared_array):
        cont = 1
        try:
            print "starting thread: ", process_number
            while True:
                print("{0} is doing something and then sleeping for {1} seconds."\
                    .format(self.name, str(self.sleepSecs)))
                sleep(self.sleepSecs)
        except KeyboardInterrupt:
            print "Keyboard interrupt in process: ", process_number
        finally:
            print "cleaning up thread", process_number
        return "I am collector_{0}.run()".format(self.name)

    def shutdown(self):
        return "I am collector_{0}.shutdown()".format(self.name)


