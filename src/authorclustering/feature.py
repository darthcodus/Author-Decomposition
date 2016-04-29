#!/usr/bin/env python3
import argparse
import glob
import logging
import os
from multiprocessing.pool import Pool

from .corenlp import StanfordCoreNLP


class Feature:
    """
    This class generates feature metadata out of corpora.
    """

    def __init__(self, url, num_gram=4):
        """
        Initializes with the CoreNLP server URL and the number n for character n-grams.
        :param url: A URL to the CoreNLP server.
        :param num_gram: A number n for character n-gram.
        """
        assert isinstance(url, str)
        assert isinstance(num_gram, int)
        self.url = url
        self.num_gram = num_gram

        formatter = logging.Formatter('%(asctime)s %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)

    def build_model(self, input_path, word_path=None, biword_path=None,
                    triword_path=None, char_ngram_path=None, pos_path=None,
                    bipos_path=None, tripos_path=None, fourpos_path=None):
        """
        Builds feature metadata and saves to files.
        :param input_path: A path to a directory containing corpora.
        :param word_path: An output file path for word frequency metadata.
        :param biword_path: An output file path for word bigram metadata.
        :param triword_path: An output file path for word trigram metadata.
        :param char_ngram_path: An output file path for character n-gram metadata.
        :param pos_path: An output file path for POS tag metadata.
        :param bipos_path: An output file path for POS tag bigram metadata.
        :param tripos_path: An output file path for POS tag trigram metadata.
        :param fourpos_path: An output file path for POS tag 4-gram metadata.
        :return: None.
        """
        assert isinstance(input_path, str)
        assert isinstance(word_path, str) or word_path is None
        assert isinstance(biword_path, str) or biword_path is None
        assert isinstance(triword_path, str) or triword_path is None
        assert isinstance(char_ngram_path, str) or char_ngram_path is None
        assert isinstance(pos_path, str) or pos_path is None
        assert isinstance(bipos_path, str) or bipos_path is None
        assert isinstance(tripos_path, str) or tripos_path is None
        assert isinstance(fourpos_path, str) or fourpos_path is None

        chunks = []
        paragraphs = []
        self.logger.info('Loading corpora...')

        if os.path.isdir(input_path):
            texts = ''
            input_paths = str.format('{}/*/*', input_path)

            for file_path in glob.glob(input_paths):
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        paragraphs.append(line)
                        if len(texts) + len(line) >= 100000:
                            chunks.append(texts)
                            texts = ''
                        texts += line
            chunks.append(texts)
        elif os.path.isfile(input_path):
            with open(input_path, 'r', encoding='utf-8') as file:
                for line in file:
                    paragraphs.append(line)
                    chunks.append(line)
        else:
            raise Exception(str.format('{} is not a directory nor a file.', input_path))

        words = []
        biwords = []
        triwords = []
        chars = []
        postags = []
        bipostag = []
        tripostag = []
        fourpostag = []

        self.logger.info('Parsing...')

        with Pool() as pool:
            args = []
            for chunk in chunks:
                args.append((self.url, chunk))

            results = pool.starmap(Feature._multi_run, args)
            for result in results:
                words.extend(result[0])
                postags.extend(result[1])

        for pair in self._make_ngram(words, 2):
            biwords.append(str.format('{} {}', pair[0], pair[1]))

        for pair in self._make_ngram(words, 3):
            triwords.append(str.format('{} {} {}', pair[0], pair[1], pair[2]))

        for para in paragraphs:
            g = self._make_ngram(para, self.num_gram)
            chars.extend(g)

        for pair in self._make_ngram(postags, 2):
            bipostag.append(str.format('{} {}', pair[0], pair[1]))

        for pair in self._make_ngram(postags, 3):
            tripostag.append(str.format('{} {} {}', pair[0], pair[1], pair[2]))

        for pair in self._make_ngram(postags, 4):
            fourpostag.append(str.format('{} {} {} {}', pair[0], pair[1], pair[2], pair[3]))

        self.logger.info('Counting...')

        word_model = self.count_tokens(words)
        biword_model = self.count_tokens(biwords)
        triwords_model = self.count_tokens(triwords)
        char_model = self.count_tokens(chars)
        postag_model = self.count_tokens(postags)
        bigram_model = self.count_tokens(bipostag)
        tripos_model = self.count_tokens(tripostag)
        fourpos_model = self.count_tokens(fourpostag)

        if word_path is not None:
            self.save_model(word_model, word_path)
            self.logger.info('Exported word frequency model to files.')

        if biword_path is not None:
            self.save_model(biword_model, biword_path)
            self.logger.info('Exported word bigram model to files.')

        if triword_path is not None:
            self.save_model(triwords_model, triword_path)
            self.logger.info('Exported word trigram model to files.')

        if char_ngram_path is not None:
            self.save_model(char_model, char_ngram_path)
            self.logger.info('Exported character n-gram model to files.')

        if pos_path is not None:
            self.save_model(postag_model, pos_path)
            self.logger.info('Exported POS tag model to files.')

        if bipos_path is not None:
            self.save_model(bigram_model, bipos_path)
            self.logger.info('Exported POS tag bigram model to files.')

        if tripos_path is not None:
            self.save_model(tripos_model, tripos_path)
            self.logger.info('Exported POS tag trigram model to files.')

        if fourpos_path is not None:
            self.save_model(fourpos_model, fourpos_path)
            self.logger.info('Exported POS tag 4gram model to files.')

    @staticmethod
    def _make_ngram(iterable, size):
        """
        Generates n-grams out of iterable objects, such as strings or lists.
        :param iterable: An iterable object.
        :param size: A constant number of n to make n-gram.
        :return: A set of generated n-grams out of the iterable object.
        """
        grams = []
        for i in range(len(iterable) - size + 1):
            grams.append(iterable[i:i + size])
        return grams

    @staticmethod
    def count_tokens(tokens):
        """
        Counts all the given tokens and returns a dictionary containing
        the token and its count.
        :param tokens: A list of tokens.
        :return: A dictionary containing the token as a key and its count as a value.
        """
        assert isinstance(tokens, list)
        model = {}
        for token in tokens:
            assert isinstance(token, str)
            num = model.get(token, 0)
            model[token] = num + 1
        return model

    @staticmethod
    def save_model(model, output_file):
        """
        Saves the given model to the file.
        :param model: A dictionary generated by the function build_model().
        :param output_file: A path to the output file you want to save to.
        :return: None.
        """
        assert isinstance(model, dict)
        assert isinstance(output_file, str)
        with open(output_file, 'w', encoding='utf-8') as file:
            for word, num in model.items():
                file.write(str.format('{} {}\n', word, num))

    @staticmethod
    def _multi_run(url, text):
        """
        This function is internally used for RESTful API calls to
        the CoreNLP server in parallel.
        :param url: A URL to the CoreNLP server.
        :param text: A text to be processed.
        :return: A tuple containing a list of words and a list of POS tags.
        """
        assert isinstance(url, str)
        assert isinstance(text, str)
        nlp = StanfordCoreNLP(str.format('http://{}:8011', url))
        words, postags = nlp.parse(text)
        return words, postags


def main():
    parser = argparse.ArgumentParser(description='This generates feature metadata.')
    parser.add_argument('-t', metavar='<../corpora/spanish_blogs2>', dest='input_path', help='Paths to a file or a folder containing texts', required=True)
    parser.add_argument('-url', metavar='<192.241.215.92>', dest='url', help='CoreNLP server URL', required=False)
    parser.add_argument('-word', metavar='<output_word.txt>', dest='word_file', help='Word frequency output file', required=False)
    parser.add_argument('-biword', metavar='<output_biword.txt>', dest='biword_file', help='Word bigram output file', required=False)
    parser.add_argument('-triword', metavar='<output_triword.txt>', dest='triword_file', help='Word trigram output file', required=False)
    parser.add_argument('-char', metavar='<output_char.txt>', dest='char_file', help='Character 4-gram output file', required=False)
    parser.add_argument('-pos', metavar='<output_pos.txt>', dest='pos_file', help='POS tag output file', required=False)
    parser.add_argument('-bipos', metavar='<output_bipos.txt>', dest='bipos_file', help='POS tag bigram output file', required=False)
    parser.add_argument('-tripos', metavar='<output_tripos.txt>', dest='tripos_file', help='POS tag trigram output file', required=False)
    parser.add_argument('-4pos', metavar='<output_4pos.txt>', dest='fourpos_file', help='POS tag 4gram output file', required=False)
    args = parser.parse_args()

    input_path = args.input_path
    word_file = args.word_file
    biword_file = args.biword_file
    triword_file = args.triword_file
    char_file = args.char_file
    pos_file = args.pos_file
    bipos_file = args.bipos_file
    tripos_file = args.tripos_file
    fourpos_file = args.fourpos_file

    url = '192.241.215.92'
    if args.url is not None:
        url = args.url

    wf = Feature(url)
    wf.build_model(input_path=input_path,
                   word_path=word_file,
                   biword_path=biword_file,
                   triword_path=triword_file,
                   char_ngram_path=char_file,
                   pos_path=pos_file,
                   bipos_path=bipos_file,
                   tripos_path=tripos_file,
                   fourpos_path=fourpos_file)


if __name__ == '__main__':
    main()
