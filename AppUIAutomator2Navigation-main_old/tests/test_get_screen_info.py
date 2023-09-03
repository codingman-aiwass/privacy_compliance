import sys 
sys.path.append("..")
from core_functions import *
from uiautomator2 import Device
import xml.etree.ElementTree as ET
from DeviceHelper import *



all_text = []
d = Device()
current_screen = d.app_current()
umap = {}
pkg_name, act_name, all_text = get_screen_info()
print(all_text)