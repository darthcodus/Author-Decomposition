#!/usr/bin/env python3
import glob
import os
import nosetest

from authorclustering.corenlp import StanfordCoreNLP


class StanfordCoreNLPTest(nosetest.TestCase):
    def setUp(self):
        self.nlp = StanfordCoreNLP('http://192.241.215.92:8011')

    def test_split_sentences(self):
        chunks = []
        texts = ''

        input_path = '../corpora/spanish_blogs/*/*'
        for file_path in glob.glob(input_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if len(texts) + len(line) >= 90000:
                        chunks.append(texts)
                        texts = ''
                    texts += line
        chunks.append(texts)

        sentences = []
        for chunk in chunks:
            sentences.extend(self.nlp.split_sentences(chunk))

        with open('test_split_sentences.txt', 'w', encoding='utf-8') as file:
            for s in sentences:
                file.write(s + '\n')
        self.assertTrue(os.path.isfile('test_split_sentences.txt'))


if __name__ == '__main__':
    nosetest.main()
