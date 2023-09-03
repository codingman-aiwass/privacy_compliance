import os.path

from uiautomator2 import Device
from datetime import datetime


# "com.taobao.taobao"
# "com.autonavi.minimap" # 高德
# "com.ss.android.ugc.aweme" #抖音
# "net.csdn.csdnplus"
# "com.sina.weibo"
# "com.youku.phone"
# "cn.damai"
# "com.ss.android.lark"
# "com.cloudy.component"
# "com.jingyao.easybike"
# "com.cainiao.wireless"
# "com.xingin.xhs"
# "com.yipiao"
# "app.podcast.cosmos"
# "com.hunantv.imgo.activity"
# "tv.danmaku.bili" #b站
# "com.netease.edu.ucmooc" #MOOC
# "com.cainiao.wireless" #菜鸟
# "com.taobao.taobao" #淘宝
# "com.taobao.mobile.dipei"#口碑
# "com.taobao.trip"#飞猪旅行
# "com.youku.phone"#优酷
# "com.eg.android.AlipayGphone"#支付宝
# "com.xiaomi.smarthome" #米家
# "me.ele" #饿了么
# "com.alibaba.wireless.lstretailer" # 阿里零售通
# "com.alibaba.cloudmail" # 阿里邮箱
# ”com.taobao.aliAuction“  #阿里拍卖
# "com.alibaba.aliyun" # 阿里云
# "com.alicloud.databox" # 阿里云盘
# "com.wudaokou.hippo" # 盒马
# "com.moji.mjweather" # 墨迹天气
# "com.alibaba.android.rimet" #钉钉

class Config(object):
    def __init__(self):

        # with open('tmp.txt') as f:
        #     pkgName = f.readline()
        # self.target_pkg_name = pkgName
        # self.target_pkg_name = "com.alibaba.android.rimet"  # 应用包名
        # self.app_name = "钉钉"  # 应用名
        self.target_pkg_name = 'com.youku.phone'
        self.app_name = '优酷'

        self.test_time = 600  # 配置测试的时间,以秒为单位
        self.sleep_time_sec = 1  # 配置点击之后睡眠的时间
        self.maxDepth = 5  # 配置点击的最大深度
        self.isDrawAppCallGraph = False  # 配置是否绘制App界面跳转图

        self.CLICK_MAX_CNT = 4
        self.device = None
        self.screen_similarity_threshold = 0.9  # 配置界面与界面之间相似度多少表示同一界面, 默认90%/0.9

        self.root_path = "collectData"
        self.start_time = datetime.now().strftime("%Y%m%d-%H%M%S")

        # self.use_pickle_file_name = "./SavedInstance/com.eg.android.AlipayGphone_restart0activity28&screen78&time3601.86s.pickle"
        self.is_saved_start = False

    def __new__(cls, *args, **kwargs):
        if not hasattr(Config, "_instance"):
            Config._instance = object.__new__(cls)
        return Config._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if not hasattr(Config, '_instance'):
            Config._instance = Config(*args, **kwargs)
        return Config._instance

    def get_target_pkg_name(self):
        return self.target_pkg_name

    def get_CLICK_MAX_CNT(self):
        return self.CLICK_MAX_CNT

    def get_sleep_time_sec(self):
        return self.sleep_time_sec

    def get_log_file_name(self):
        return self.log_file_name

    def get_pickle_file_name(self):
        return self.use_pickle_file_name

    def set_device(self, device):
        self.device = device

    def get_device(self):
        if self.device is None:
            self.set_device(Device())
        return self.device

    def get_CollectDataName(self):
        return self.target_pkg_name + "-" + self.start_time

    def get_collectDataPath(self):
        pkg_path = self.target_pkg_name + "-" + self.start_time
        return os.path.join(self.root_path, pkg_path)
