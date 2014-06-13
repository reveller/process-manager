import os
import sys
import abc

collectors = {}

class Plugin(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def init(self):
        return

    @abc.abstractmethod
    def run(self, process_number, shared_array):
        return

    @abc.abstractmethod
    def shutdown(self):
        return


def init_plugins():
    '''simple plugin initializer
    '''
    find_plugins()
    #register_plugins()
    dump_plugins()

def find_plugins():
    '''find all files in the plugin directory and imports them'''
    root_dir = os.path.dirname(os.path.realpath(__file__))
    plugin_dir = root_dir + '/plugins/'
    print("Reading plugins from {0}".format(plugin_dir))
    plugin_files = [x[:-3] for x in os.listdir(plugin_dir) if x.endswith(".py")]
    sys.path.insert(0, plugin_dir)

    for plugin in plugin_files:
        if plugin == '__init__':
            continue
        print("Importing for {0}".format(plugin))
        plugin_class = plugin + ".collector"
        try:
            mod = __import__(plugin)
            name = mod.collector.name
            collectors[name] = mod
        except:
            print("Error importing {0}".format(plugin))

def dump_plugins():
    for sc in Plugin.__subclasses__():
        print sc.__name__

    for each in collectors:
        f = collectors[each].collector()
        #print("{0}:{1}".format(each, collectors[each].collector.init()))
        print("{0}:{1}".format(each, f.init()))

#def register_plugins():
#  '''Register all class based plugins.
#
#     Uses the fact that a class knows about all of its subclasses
#     to automatically initialize the relevant plugins
#  '''
#  print Plugin.__subclasses__()
#  for plugin in Plugin.__subclasses__():
#      print("Registering {0}".format(plugin))
#      collectors.append(plugin)

if __name__ == '__main__':

    init_plugins()
