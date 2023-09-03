import sys 
sys.path.append("..")
from ScreenCompareStrategy import *


str1 = "   旧设备扫码验证支付宝验证发送短信验证人工申诉 联系客服"
str2 = "   旧设备扫码验证支付宝验证发送短信验证人工申诉 联系客服"
ab = ScreenCompareStrategy(EditDistanceComparator())
res, ratio = ab.compare_screen(str1, str2)
print(f"The result is {res} and {ratio}")

str3 = "mycccc"
str4 = "mycccabc"
res, ratio = ab.compare_screen(str3, str4)
print(f"The result is {res} and {ratio}")