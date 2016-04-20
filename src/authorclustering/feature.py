#!/usr/bin/env python3
import argparse
import glob
import logging
from copy import deepcopy
from multiprocessing.pool import Pool

from .corenlp import StanfordCoreNLP


class Feature:
    def __init__(self, nlp, num_gram=4):
        assert isinstance(nlp, StanfordCoreNLP)
        assert isinstance(num_gram, int)
        self.nlp = nlp
        self.num_gram = num_gram

        formatter = logging.Formatter('%(asctime)s %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)

    def build_model(self, input_dir, word_path=None, char_ngram_path=None,
                    postag_path=None, bipostag_path=None):
        assert isinstance(input_dir, str)
        assert isinstance(word_path, str) or word_path is None
        assert isinstance(char_ngram_path, str) or char_ngram_path is None
        assert isinstance(postag_path, str) or postag_path is None
        assert isinstance(bipostag_path, str) or bipostag_path is None

        input_paths = str.format('{}/*/*', input_dir)
        chunks = []
        paragraphs = []
        texts = ''

        self.logger.info('Loading corpora...')

        for file_path in glob.glob(input_paths):
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    paragraphs.append(line)
                    if len(texts) + len(line) >= 100000:
                        chunks.append(texts)
                        texts = ''
                    texts += line
        chunks.append(texts)

        words = []
        chars = []
        postags = []
        bipostag = []

        self.logger.info('Parsing...')

        with Pool() as pool:
            args = []
            for chunk in chunks:
                args.append((deepcopy(self.nlp), chunk))

            results = pool.starmap(Feature._multi_run, args)
            for result in results:
                words.extend(result[0])
                postags.extend(result[1])

        for para in paragraphs:
            g = self._make_ngram(para, self.num_gram)
            chars.extend(g)

        for pair in self._make_ngram(postags, 2):
            bipostag.append(str.format('{} {}', pair[0], pair[1]))

        self.logger.info('Counting...')

        word_model = self.count_tokens(words)
        char_model = self.count_tokens(chars)
        postag_model = self.count_tokens(postags)
        bigram_model = self.count_tokens(bipostag)

        if word_path is not None:
            self.save_model(word_model, word_path)
            self.logger.info('Exported word frequency model to files.')

        if char_ngram_path is not None:
            self.save_model(char_model, char_ngram_path)
            self.logger.info('Exported character n-gram model to files.')

        if postag_path is not None:
            self.save_model(postag_model, postag_path)
            self.logger.info('Exported POS tag model to files.')

        if bipostag_path is not None:
            self.save_model(bigram_model, bipostag_path)
            self.logger.info('Exported POS tag bigram model to files.')

    @staticmethod
    def _make_ngram(iterable, size):
        grams = []
        for i in range(len(iterable) - size):
            grams.append(iterable[i:i + size])
        return grams

    @staticmethod
    def count_tokens(tokens):
        assert isinstance(tokens, list)
        model = {}
        for token in tokens:
            assert isinstance(token, str)
            num = model.get(token, 0)
            model[token] = num + 1
        return model

    @staticmethod
    def save_model(model, output_file):
        assert isinstance(model, dict)
        assert isinstance(output_file, str)
        with open(output_file, 'w', encoding='utf-8') as file:
            for word, num in model.items():
                file.write(str.format('{} {}\n', word, num))

    @staticmethod
    def _multi_run(nlp, texts):
        assert isinstance(nlp, StanfordCoreNLP)
        assert isinstance(texts, str)
        words, postags = nlp.parse(texts)
        return words, postags


def main():
    parser = argparse.ArgumentParser(description='This generates feature metadata.')
    parser.add_argument('-t', metavar='<../corpora/spanish_blogs2>', dest='input_path', help='Paths to folder containing texts', required=True)
    parser.add_argument('-url', metavar='<192.241.215.92>', dest='url', help='CoreNLP server URL', required=False)
    parser.add_argument('-word', metavar='<output_word.txt>', dest='word_file', help='Word frequency output file', required=False)
    parser.add_argument('-char', metavar='<output_char.txt>', dest='char_file', help='Character 4-gram output file', required=False)
    parser.add_argument('-pos', metavar='<output_pos.txt>', dest='pos_file', help='Character 4-gram output file', required=False)
    parser.add_argument('-bipos', metavar='<output_bipos.txt>', dest='bipos_file', help='Character 4-gram output file', required=False)
    args = parser.parse_args()

    input_path = args.input_path
    word_file = args.word_file
    char_file = args.char_file
    pos_file = args.pos_file
    bipos_file = args.bipos_file
    url = '192.241.215.92'
    if args.url is not None:
        url = args.url
    nlp = StanfordCoreNLP(str.format('http://{}:8011', url))
    wf = Feature(nlp)
    wf.build_model(input_path, word_file, char_file, pos_file, bipos_file)


if __name__ == '__main__':
    main()
