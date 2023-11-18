import threading
from AppUIAutomator2Navigation.run import main

class threadWithReturnCode(threading.Thread):
    def __init__(self,pkgName,appName,depth,test_time):
        threading.Thread.__init__(self)
        self.exit_code = 0
        self.exception = None
        self.exc_traceback = ''
        self.pkgName = pkgName
        self.appName = appName
        self.depth = depth
        self.test_time = test_time

    # TODO 这里定义错误类型

    def my_run(self):
        main(self.pkgName,self.appName,self.depth,self.test_time)

    def run(self):
        try:
            self.my_run()
        # TODO 这里根据不同的错误类型返回不同的错误代码
        except Exception:
            pass
