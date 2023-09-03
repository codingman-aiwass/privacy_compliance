import sys 
sys.path.append("..")
from core_functions import *
from uiautomator2 import Device
import xml.etree.ElementTree as ET


all_text = []
d = Device()
umap = {}
print(get_screen_all_clickable_text(d))
