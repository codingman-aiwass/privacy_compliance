from Memory import Memory
import unittest
from ScreenCompareStrategy import *

class TestMemory(unittest.TestCase):
    def test_case1(self):
        A = Memory()
        B = Memory.get_instance()
        C = Memory()
        D = Memory.get_instance()
        print(A)
        print(B)
        print(C)
        print(D)
        B.similarity_mem[("1", "2")] = (1, 2)
        print(D.similarity_mem)

    def test_case2(self):
        sc = ScreenCompareStrategy(LCSComparator())
        print(Memory.get_instance().get_similarity_mem())
        sc.compare_screen("aa", "ab")
        sc.compare_screen("akk", "kaa")
        print(Memory.get_instance().get_similarity_mem())



if __name__ == "__main__":
    unittest.main()