import os
import unittest

from src.feature import WordFrequency, NCharacterGram


# class WordFrequencyTest(unittest.TestCase):
#     def setUp(self):
#         self.wf = WordFrequency(lang='es')
#
#     def test_build_model(self):
#         wf = self.wf
#         input_file = '../corpora/spanish_blogs'
#         output_file = 'test_wq_model.txt'
#         wf.build_model(input_file, output_file)
#         self.assertTrue(os.path.isfile(output_file))


class NCharacterGramTest(unittest.TestCase):
    def setUp(self):
        self.nc = NCharacterGram(4, lang='es')

    def test_build_model(self):
        nc = self.nc
        input_path = '../corpora/spanish_blogs'
        output_file = 'test_nc_model.txt'
        nc.build_model(input_path, output_file)
        self.assertTrue(os.path.isfile(output_file))


if __name__ == '__main__':
    unittest.main()
