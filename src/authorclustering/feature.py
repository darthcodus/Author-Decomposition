#!/usr/bin/env python3
import argparse
import glob
import logging

from authorclustering.corenlp import StanfordCoreNLP


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

    def build_model(self, input_dir,
                    word_path, char_ngram_path, postag_path, bipostag_path):
        assert isinstance(input_dir, str)
        assert isinstance(word_path, str)
        assert isinstance(char_ngram_path, str)
        assert isinstance(postag_path, str)
        assert isinstance(bipostag_path, str)

        input_paths = str.format('{}/*/*', input_dir)
        chunks = []
        sentences = []
        texts = ''

        self.logger.info('Loading corpora...')

        for file_path in glob.glob(input_paths):
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    sentences.append(line)
                    if len(texts) + len(line) >= 90000:
                        chunks.append(texts)
                        texts = ''
                    texts += line
        chunks.append(texts)

        words = []
        chars = []
        postags = []
        bipostag = []

        self.logger.info('Parsing...')

        for chunk in chunks:
            w, p = self.nlp.parse(chunk)
            words.extend(w)
            postags.extend(p)

        for sentence in sentences:
            g = self._make_ngram(sentence, self.num_gram)
            chars.extend(g)

        for pair in self._make_ngram(postags, 2):
            bipostag.append(str.format('{} {}', pair[0], pair[1]))

        self.logger.info('Counting...')

        word_model = self.count_tokens(words)
        char_model = self.count_tokens(chars)
        postag_model = self.count_tokens(postags)
        bigram_model = self.count_tokens(bipostag)

        self.save_model(word_model, word_path)
        self.save_model(char_model, char_ngram_path)
        self.save_model(postag_model, postag_path)
        self.save_model(bigram_model, bipostag_path)

        self.logger.info('Saved to files.')

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


def main():
    parser = argparse.ArgumentParser(description='This generates feature metadata.')
    parser.add_argument('-t', metavar='<../corpora>', dest='input_path', help='Paths to folder containing texts', required=True)
    parser.add_argument('-word', metavar='<output_word.txt>', dest='word_file', help='Word frequency output file', required=True)
    parser.add_argument('-char', metavar='<output_char.txt>', dest='char_file', help='Character 4-gram output file', required=True)
    parser.add_argument('-pos', metavar='<output_pos.txt>', dest='pos_file', help='Character 4-gram output file', required=True)
    parser.add_argument('-bipos', metavar='<output_bipos.txt>', dest='bipos_file', help='Character 4-gram output file', required=True)
    args = parser.parse_args()

    input_path = args.input_path
    word_file = args.word_file
    char_file = args.char_file
    pos_file = args.pos_file
    bipos_file = args.bipos_file

    nlp = StanfordCoreNLP()
    wf = Feature(nlp)
    wf.build_model(input_path, word_file, char_file, pos_file, bipos_file)


if __name__ == '__main__':
    main()
