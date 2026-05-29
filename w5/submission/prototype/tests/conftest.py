import os
import sys

# put the prototype root on sys.path so tests import the package modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
