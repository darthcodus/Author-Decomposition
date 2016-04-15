#!/usr/bin/env python3
import glob
import unittest
from chunk import Chunker

from corenlp import StanfordCoreNLP


class ChunkerTest(unittest.TestCase):
    def setUp(self):
        self.nlp = StanfordCoreNLP('http://192.241.215.92:8011')
        self.chunker = Chunker()

    def test_fixed_length_chunk(self):
        text_list = []
        texts = ''

        authors = ['alejandro_nieto_gonzalez', 'aurelio_jimenez', 'javier_j_navarro']
        for author in authors:
            input_path = '../corpora/spanish_blogs/' + author + '/*'
            for file_path in glob.glob(input_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        if len(texts) + len(line) >= 90000:
                            text_list.append(texts)
                            texts = ''
                        texts += line
            text_list.append(texts)

            for texts in text_list:
                for s in self.nlp.split_sentences(texts):
                    self.chunker.add_sentence(author, s)

            text_list.clear()
            texts = ''

        chunks = self.chunker.fixed_length_chunk(3)
        with open('test_chunk_test.txt', 'w', encoding='utf-8') as file:
            for chunk in chunks:
                file.write(str.format('{}\n{}\n\n', chunk['author'], chunk['text']))


if __name__ == '__main__':
    unittest.main()
