import os

try:
	from local_config import *
except ImportError:
	print "Local settings file not found. Try creating one. There is an example in local_config.py.git"
	exit()
