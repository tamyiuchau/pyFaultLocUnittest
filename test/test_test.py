import unittest

class SimpleTestCase(unittest.TestCase):
    def setUp(self):
        pass

class ListTestCase(SimpleTestCase):
    def runTest(self):
        self.assertEqual(list(range(3)),
                         [0,1,2])

class NotTestCase(SimpleTestCase):
    def runTest(self):
        self.assertEqual(False,
                         True)
