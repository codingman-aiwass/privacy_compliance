import threading


class threadWithReturnCode(threading.Thread):
    def __init__(self,script_path):
        threading.Thread.__init__(self,script_path)
        self.script_path = script_path
        self.exit_code = 0
        self.exception = None
        self.exc_traceback = ''

    def my_run(self):
        pass

    def run(self):
        try:
            self.my_run()
        except Exception:
            pass
