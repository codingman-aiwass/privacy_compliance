import threading, time
from queue import Queue
import sys
import frida
import re
from Config import *

lock = threading.Lock()

class Producer(threading.Thread):
    def __init__(self, t_name, queue):
        threading.Thread.__init__(self, name=t_name)
        self.data = queue

    def is_http(self, test_str):
        pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        # 使用re模块进行匹配
        matches = re.findall(pattern, test_str)
        return matches

    def on_message(self, message, data):
        with lock:
            res = self.is_http(str(message))
            if res:
                print()
                print("*" * 50 + f"Producer{self.name}" + "*" * 50)
                print(res)
                print("*" * 50 + f"Producer{self.name}" + "*" * 50)
                print()
                self.data.put(res)
                # print("%s: %s is producing %d to the queue!" % (time.ctime(), self.name, message))

    def run(self):
        device = frida.get_usb_device()
        # 启动`demo02`这个app
        print(device)
        appName = Config.get_instance().app_name
        pid = device.attach(appName)
        # 加载s1.js脚本
        # with open("./hook_rpc.js") as f:
        with open("./FridaLibs/hook_rpc.js") as f:
            script = pid.create_script(f.read())
        script.on('message', self.on_message)
        script.load()
        sys.stdin.read()
        print("%s: %s finished!" % (time.ctime(), self.name))