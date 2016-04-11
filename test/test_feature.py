import os
import unittest

from src.feature import WordFrequency


class WordFrequencyTest(unittest.TestCase):
    def setUp(self):
        self.wf = WordFrequency(lang='es')

    def test_build_model(self):
        wf = self.wf
        input_file = '../corpora/spanish_blogs/alejandro nieto gonzalez/Ciertos comportamientos ecológicos puede que no lo sean.txt'
        output_file = 'test_wq_model.txt'
        wf.build_model(input_file, output_file)
        self.assertTrue(os.path.isfile(output_file))


if __name__ == '__main__':
    unittest.main()
