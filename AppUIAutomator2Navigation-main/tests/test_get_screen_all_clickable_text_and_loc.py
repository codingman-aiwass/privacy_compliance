import sys
sys.path.append("..")
from core_functions import *
from uiautomator2 import Device
import xml.etree.ElementTree as ET
from DeviceHelper import get_screen_all_clickable_text_and_loc

all_text = []
d = Device()
umap = {}
print(get_screen_all_clickable_text_and_loc(d))