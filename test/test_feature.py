import os
import unittest

from corenlp import StanfordCoreNLP
from feature import Feature


class FeatureTest(unittest.TestCase):
    def setUp(self):
        nlp = StanfordCoreNLP('http://25.30.82.122:8011')
        self.wf = Feature(nlp)

    def test_build_model(self):
        wf = self.wf
        input_file = '../corpora/spanish_blogs'
        wf.build_model(
            input_file,
            'test_word_model.txt',
            'test_char_model.txt',
            'test_pos_model.txt',
            'test_bipos_model.txt'
        )
        self.assertTrue(os.path.isfile('test_word_model.txt'))
        self.assertTrue(os.path.isfile('test_char_model.txt'))
        self.assertTrue(os.path.isfile('test_pos_model.txt'))
        self.assertTrue(os.path.isfile('test_bipos_model.txt'))


if __name__ == '__main__':
    unittest.main()
