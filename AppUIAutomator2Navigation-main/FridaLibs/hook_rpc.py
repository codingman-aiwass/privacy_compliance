import sys
import frida


def on_message(message, data):
    print(message)


device = frida.get_usb_device()
# 启动`demo02`这个app
print(device)
pid = device.attach("淘宝")
# 加载s1.js脚本
with open("hook_rpc.js") as f:
    script = pid.create_script(f.read())
script.on('message', on_message)
script.load()
sys.stdin.read()
# command = ""
# while 1 == 1:
#     print("*"*100)
#     command = input("Enter command:\n1: Exit\n2: Call secret function\nchoice:")
#     if command == "1":
#         break
#     elif command == "2": #在这里调用
#         script.exports.callsecretfunction()
