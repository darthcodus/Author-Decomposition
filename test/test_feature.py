import os
import unittest

from feature import WordFrequency, CharacterNgram


class WordFrequencyTest(unittest.TestCase):
    def setUp(self):
        self.wf = WordFrequency(lang='es')

    def test_build_model(self):
        wf = self.wf
        input_file = '../corpora/spanish_blogs'
        output_file = 'test_wf_model.txt'
        wf.build_model(input_file, output_file)
        self.assertTrue(os.path.isfile(output_file))


class CharacterNgramTest(unittest.TestCase):
    def setUp(self):
        self.nc = CharacterNgram(4, lang='es')

    def test_build_model(self):
        nc = self.nc
        input_path = '../corpora/spanish_blogs'
        output_file = 'test_cn_model.txt'
        nc.build_model(input_path, output_file)
        self.assertTrue(os.path.isfile(output_file))


if __name__ == '__main__':
    unittest.main()
