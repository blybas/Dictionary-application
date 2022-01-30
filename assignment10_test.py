"""
Blythe Bassart
CS3B Assignment 10, Online Dictionary
November 29, 2021
"""

import copy
import unittest

from assignment10 import *


class TestCase(unittest.TestCase):

    def setUp(self):
        self.oxford_dict = OxfordDictionary()
        self.dictionary = Dictionary()
        self.first_search = self.dictionary.search("ace")
        self.second_search = self.dictionary.search("ace")

    def test_time_func_pow(self):
        result, duration = time_func(pow, 2, 128)
        self.assertTrue(result == 340282366920938463463374607431768211456
                        and duration<1)

    def test_time_func_print(self):
        result, duration = time_func(print, "hello", "world", sep="\n")
        self.assertTrue(duration<1)

    def test_OxfordDictionary_no_example(self):
        result = self.oxford_dict.search("python")
        self.assertTrue(isinstance(result, DictionaryEntry))

    def test_OxfordDictionary_example(self):
        result = self.oxford_dict.search("foothill")
        self.assertTrue(isinstance(result, DictionaryEntry))

    def test_OxfordDictionary_example(self):
        with self.assertRaises(KeyError):
            self.oxford_dict.search("optimisitic")

    def test_Dictionary_search_source(self):
        res1 = self.first_search
        res2 = self.second_search
        self.assertTrue(res1[1] == DictionarySource.OXFORD_ONLINE and
                        res2[1] == DictionarySource.CACHE)

    def test_Dictionary_search_time(self):
        res1 = self.first_search
        res2 = self.second_search
        self.assertTrue(res1[2] > res2[2])




if __name__ == '__main__':
    unittest.main()