import os
import sys

collectors = []

class Plugin(object):
  pass

def init_plugins():
  '''simple plugin initializer
  '''
  find_plugins()
  register_plugins()

def find_plugins():
  '''find all files in the plugin directory and imports them'''
  plugin_dir = os.path.dirname(os.path.realpath(__file__))
  plugin_files = [x[:-3] for x in os.listdir(plugin_dir) if x.endswith(".py")]
  sys.path.insert(0, plugin_dir)
  for plugin in plugin_files:
      print("Importing {0}".format(plugin))
      mod = __import__(plugin)

def register_plugins():
  '''Register all class based plugins.

     Uses the fact that a class knows about all of its subclasses
     to automatically initialize the relevant plugins
  '''
  print Plugin.__subclasses__()
  for plugin in Plugin.__subclasses__():
      print("Registering {0}".format(plugin))
      collectors.append(plugin)

