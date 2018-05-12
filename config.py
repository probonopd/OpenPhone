import os
import configparser # apt install python-configparser

config = configparser.ConfigParser()
config.read_file(open(os.path.dirname(__file__)+'/defaults.cfg'))
config.read([os.path.dirname(__file__)+'/openphone.cfg', os.path.expanduser('~/.openphone.cfg')])

