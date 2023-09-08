from uiautomator2 import Device


class Config(object):
    def __init__(self):
        with open('tmp.txt') as f:
            pkgName, appName, depth = f.readline().split(";")
        self.CLICK_MAX_CNT = 4
        self.sleep_time_sec = 2
        self.device = None
        # self.target_pkg_name = "com.example.myapplication"
        # self.target_pkg_name = "com.alibaba.android.rimet"
        # self.target_pkg_name = "com.ss.android.ugc.aweme" #抖音
        # self.target_pkg_name = "net.csdn.csdnplus"
        # self.target_pkg_name = "com.sina.weibo"
        # self.target_pkg_name = "com.youku.phone"
        self.target_pkg_name = pkgName
        # self.target_pkg_name = "com.ss.android.lark"
        # self.target_pkg_name = "com.cloudy.component"
        # self.target_pkg_name = "com.jingyao.easybike"
        # self.target_pkg_name = "com.cainiao.wireless"
        # self.target_pkg_name = "com.xingin.xhs"
        # self.target_pkg_name = "com.yipiao"
        # self.target_pkg_name = "app.podcast.cosmos"
        # self.target_pkg_name = "com.hunantv.imgo.activity"
        # self.target_pkg_name = "tv.danmaku.bili" #b站
        # self.target_pkg_name = "com.netease.edu.ucmooc" #MOOC
        # self.target_pkg_name = "com.cainiao.wireless"

        self.log_file_name = "./Log/" + self.target_pkg_name + "_1.log"
        self.use_pickle_file_name = "./SavedInstance/com.cainiao.wireless_restart0activity7&screen22&time251.1s.pickle"
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
