def mid(x,y,z):
    m =z
    if (y<z):
        if (x<y):
            m = y
        elif (x<z):
            m = y
    else:
        if x > y:
            m = y
        elif x>z:
            m = x
    return m
from random import randint
import unittest
class midTestCase(unittest.TestCase):
    iterations = 100
    def test1(self):
        test = [3,3,5]
        self.assertEqual(list(sorted(test))[1],mid(*test))
    def test2(self):
        test = [1,2,3]
        self.assertEqual(list(sorted(test))[1],mid(*test))
    def test3(self):
        test = [3,2,1]
        self.assertEqual(list(sorted(test))[1],mid(*test))
    def test4(self):
        test = [5,5,5]
        self.assertEqual(list(sorted(test))[1],mid(*test))
    def test5(self):
        test = [5,3,4]
        self.assertEqual(list(sorted(test))[1],mid(*test))
    def test6(self):
        test = [2,1,3]
        self.assertEqual(list(sorted(test))[1],mid(*test))
    """def test_random(self):
        self.assertEqual(list(sorted(test))[1],mid(*test))"""
