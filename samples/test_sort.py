from .bubblesort import bubblesort as bubble_sort
from .insertionsort import insertion_sort
from .mergesort import merge_sort
from .selectionsort import selection_sort
import random

import unittest
class SortTestCase(unittest.TestCase):
    algorithm = staticmethod(lambda x: sorted(x))
    iterations = 100
    size = 100
    def test_random(self):
        for _ in range(self.iterations):
            l2 = []
            for ith in range(self.size):
                l2.append(random.getrandbits(64))
            self.assertEqual(list(sorted(l2)),self.algorithm(l2))
            #self.assertEqual(True,False)
    def test_randomShuffle(self):
        for _ in range(self.iterations):#iterations
            l1 = list(range(self.size))
            l2 = list(range(self.size))
            random.shuffle(l2)
            self.assertEqual(l1,self.algorithm(l2))
    def test_reversed(self):
        l1 = list(range(self.size))
        l2 = list(reversed(range(self.size)))
        self.assertEqual(l1,self.algorithm(l2))
class BubbleTestCase(SortTestCase):
    algorithm = staticmethod(bubble_sort)
class InsertionTestCase(SortTestCase):
    algorithm = staticmethod(insertion_sort)
class MergeTestCase(SortTestCase):
    algorithm = staticmethod(merge_sort)
class SelectionTestCase(SortTestCase):
    algorithm = staticmethod(selection_sort)
