from distutils.core import setup
import py2exe
setup(console=['auto.py'])
#for compiling to exe, first download and install py2exe
#then run this command in windows cmd:
#setup.py install
#after that run
#setup.py py2exe