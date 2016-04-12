#!/usr/bin/env python3
import argparse
import glob

from corenlp import StanfordCoreNLP


def count_tokens(tokens):
    assert isinstance(tokens, list)
    model = {}
    for token in tokens:
        assert isinstance(token, str)
        num = model.get(token, 0)
        model[token] = num + 1
    return model


def save_model(model, output_file):
    assert isinstance(model, dict)
    assert isinstance(output_file, str)
    with open(output_file, 'w', encoding='utf-8') as file:
        for word, num in model.items():
            file.write(str.format('{} {}\n', word, num))


class WordFrequency:
    def __init__(self, lang='es'):
        assert isinstance(lang, str)
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
                    if len(texts) + len(line) >= 80000:
                        chunks.append(texts)
                        texts = ''
                    texts += line
        chunks.append(texts)

        tokens = []
        if self.lang == 'es':
            for chunk in chunks:
                nlp = StanfordCoreNLP('http://25.30.82.122:8011')
                tokens.extend(nlp.tokenize_es(chunk))
        else:
            tokens = texts.split()
        model = count_tokens(tokens)
        save_model(model, output_file)


class CharacterNgram:
    def __init__(self, n=4, lang='es'):
        assert isinstance(n, int)
        assert isinstance(lang, str)
        if n <= 0:
            raise AssertionError('The parameter should be greater than 0.')
        self.n = n
        self.lang = lang

    def build_model(self, input_path, output_file):
        """
        # Not tokenizing is better to capture stylistic features.
        """
        assert isinstance(input_path, str)
        assert isinstance(output_file, str)
        paths = str.format('{}/*/*', input_path)
        texts = ''

        for file_path in glob.glob(paths):
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    texts += line.replace('\n', ' ')

        ngrams = []
        for ngram in self._make_ngram(texts):
            ngrams.append(ngram)

        model = count_tokens(ngrams)
        save_model(model, output_file)

    def _make_ngram(self, texts):
        assert isinstance(texts, str)
        grams = []
        for i in range(len(texts) - self.n):
            grams.append(texts[i:i + self.n])
        return grams


def main():
    parser = argparse.ArgumentParser(description='This generates feature metadata.')
    parser.add_argument('-t', metavar='<../corpora>', dest='input_path', help='Paths to folder containing texts', required=True)
    parser.add_argument('-wf', metavar='<output_wf.txt>', dest='wf_file', help='Word frequency output file', required=True)
    parser.add_argument('-cn', metavar='<output_cn.txt>', dest='cn_file', help='Character 4-gram output file', required=True)
    args = parser.parse_args()

    input_path = args.input_path
    wf_file = args.wf_file
    cn_file = args.cn_file

    wf = WordFrequency(lang='es')
    cn = CharacterNgram(4, lang='es')
    wf.build_model(input_path, wf_file)
    cn.build_model(input_path, cn_file)


if __name__ == '__main__':
    main()
