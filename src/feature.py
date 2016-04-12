#!/usr/bin/env python3
import glob
from collections import deque

from lib.pycorenlp import StanfordCoreNLP


def count_tokens(tokens):
    assert isinstance(tokens, list)
    model = {}
    for token in tokens:
        assert isinstance(token, str)
        num = model.get(token, 0)
        model[token] = num + 1
    return model


def tokenize_es(texts):
    assert isinstance(texts, str)
    nlp = StanfordCoreNLP('http://25.30.82.122:8011')
    output = nlp.annotate(texts, properties={
        "annotators": "tokenize,ssplit",
        "coref.md.type": "dep",
        "coref.mode": "statistical"
    })

    tokens = []
    for sentence in output['sentences']:
        for token in sentence['tokens']:
            tokens.append(token['word'])
    return tokens


def split_sentences_es(texts):
    assert isinstance(texts, str)
    nlp = StanfordCoreNLP('http://25.30.82.122:8011')
    output = nlp.annotate(texts, properties={
        "annotators": "tokenize,ssplit",
        "coref.md.type": "dep",
        "coref.mode": "statistical"
    })

    sentences = []
    for s in output['sentences']:
        sentence = ''
        for token in s['tokens']:
            sentence += token['word']
        sentences.append(sentence)
    return sentences


def tokenize_other(texts):
    assert isinstance(texts, str)
    return texts.split()


def save_model(model, output_file):
    assert isinstance(model, dict)
    assert isinstance(output_file, str)
    with open(output_file, 'w', encoding='utf-8') as file:
        for word, num in model.items():
            file.write(str.format('{} {}\n', word, num))


class WordFrequency:
    def __init__(self, lang):
        assert isinstance(lang, str)
        self.lang = lang

    def build_model(self, input_path, output_file):
        assert isinstance(input_path, str)
        assert isinstance(output_file, str)
        paths = str.format('{}/*/*', input_path)

        texts = ''
        for file_path in glob.glob(paths):
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    texts += line

        if self.lang == 'es':
            tokens = tokenize_es(texts)
        else:
            tokens = tokenize_other(texts)
        model = count_tokens(tokens)
        save_model(model, output_file)


class NCharacterGram:
    def __init__(self, n, lang='es'):
        assert isinstance(n, int)
        assert isinstance(lang, str)
        if n <= 0:
            raise AssertionError('The parameter should be greater than 0.')
        self.n = n
        self.lang = lang

    def build_model(self, input_path, output_file):
        assert isinstance(input_path, str)
        assert isinstance(output_file, str)
        paths = str.format('{}/*/*', input_path)

        chunks = []
        texts = ''
        for file_path in glob.glob(paths):
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if len(texts) + len(line) >= 1000000:
                        chunks.append(texts)
                        texts = ''
                    texts += line
        chunks.append(texts)

        # Not tokenizing is better to capture stylistic features.
        # if self.lang == 'es':
        #     sentences = split_sentences_es(texts)
        # else:
        #     sentences = [texts]
        ngrams = []
        for chunk in chunks:
            for ngram in self._make_ngram(chunk):
                ngrams.append(ngram)

        model = count_tokens(ngrams)
        print(model)
        save_model(model, output_file)

    def _make_ngram(self, texts):
        assert isinstance(texts, str)
        grams = []
        for i in range(len(texts) - self.n):
            grams.append(texts[i:i + self.n])
        return grams


def main():
    nc = NCharacterGram(4, 'es')
    input_file = '../corpora/spanish_blogs/alejandro nieto gonzalez/Ciertos comportamientos ecológicos puede que no lo sean.txt'
    output_file = 'test_nc_model.txt'
    nc.build_model(input_file, output_file)


if __name__ == '__main__':
    main()
