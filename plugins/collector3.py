from base import Plugin
from time import sleep

class collector(Plugin):
    name = "YetAnotherCoolCollector"
    sleep_secs = 11
    loop_counter = 3
    def init(self):
        return "I am {0}.init()".format(self.name)

    def run(self, process_number, parent_p, child_p):
        # set sleep counter to 0 so it will trigger the first do_something
        # immediately
        sleep_counter = 0
        cont = 1
        try:
            print "starting thread: ", process_number
            while True:
                try:
                    if child_p.poll():
                        msg = child_p.recv()
                        if msg is None:
                            print("{0} is exiting".format(self.name))
                            break
                        print("{0} recv'd a {1} message from the parent".format(self.name, msg))
                        print("Sending {0} to parent".format("RECVD-" + msg))
                        self.send_to_parent(child_p, "RECVD-" + msg)
                except EOFError:
                    print("{0} hit an EOFError from child pipe recv".format(self.name))
                    break
                # Track the sleep counter
                # if sleep counter is still positive
                #   sleep for one second
                #   decrement the counter
                # else (counter has reached 0)
                #   time to do somethinng
                #   reset sleep counter
                if sleep_counter:
                    print("{0} is sleeping {1}/{2}".format(self.name, str(sleep_counter), str(self.sleep_secs)))
                    sleep(1)
                    sleep_counter -= 1
                else:
                    print("{0} is doing something because sleep counter {1}".format(self.name, str(sleep_counter)))
                    self._do_something()
                    sleep_counter = self.sleep_secs

                    # Keep track of some artificial number of loops so we know when
                    # to signal back to the parent
                    if self.loop_counter <= 0:
                        break
        except KeyboardInterrupt:
            print("Keyboard interrupt in {0} process".format(self.name))
        finally:
            print("Cleaning up {0} process".format(self.name))
            self.send_to_parent(child_p, "STOPPED-" + self.name)
        return "I am {0}.run()".format(self.name)

    def shutdown(self):
        return "I am {0}.shutdown()".format(self.name)


    def _do_something(self):
        print("{0} is doing something - loop counter {1}"\
            .format(self.name, self.loop_counter))
        self.loop_counter -= 1

    def send_to_parent(self, conn, msg):
        # Send a RECV message nack to parent to indicate that we recv'd
        # something
        try:
            conn.send(msg)
        except EOFError:
            print("{0} hit an EOFError from pipe send".format(self.name))

