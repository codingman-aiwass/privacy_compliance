import sys 
sys.path.append("..")
from core_functions import *
from uiautomator2 import Device
import xml.etree.ElementTree as ET

d = Device()

top = get_top_activity(d)
cur = get_current_activity(d)
print(top)
print(cur)
print(cur in top)