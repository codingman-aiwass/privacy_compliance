import unittest
from Utils.DrawGraphUtils import *

class MyTestCase(unittest.TestCase):
    def test_something(self):

        package = "com.alibaba.android.rimet-20230830-173908"
        DrawGraphUtils.draw_callgraph(package)

if __name__ == '__main__':

    unittest.main()
