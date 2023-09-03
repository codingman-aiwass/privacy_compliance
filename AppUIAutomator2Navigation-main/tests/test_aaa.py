from uiautomator2 import Device

d = Device()
# d(text = "关闭").click()
# print(d(text = "分享"))
print(d(text = "关闭"))
if d(className = "android.webkit.WebView").exists() == False:
    print("?")
else:
    print(d(className = "android.webkit.WebView"))

