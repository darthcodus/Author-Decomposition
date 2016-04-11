#!/usr/bin/env python3
from lib.pycorenlp import StanfordCoreNLP


class WordFrequency:
    def __init__(self, lang):
        assert isinstance(lang, str)
        self.lang = lang

    def build_model(self, input_file, output_file):
        assert isinstance(input_file, str)
        assert isinstance(output_file, str)
        texts = ''
        with open(input_file, 'r', encoding='utf-8') as file:
            for line in file:
                texts += line

        tokens = []
        if self.lang == 'es':
            tokens = self._tokenize_es(texts)
        model = self._count_words(tokens)
        self._write_file(model, output_file)

    @staticmethod
    def _tokenize_es(texts):
        assert isinstance(texts, str)
        nlp = StanfordCoreNLP('http://25.30.82.122:8011')
        output = nlp.annotate(texts, properties={
            "annotators": "tokenize,ssplit",
            "coref.md.type": "dep",
            "coref.mode": "statistical"
        })
        print(output['sentences'][0]['tokens'][1]['word'])

        tokens = []
        for sentence in output['sentences']:
            for token in sentence['tokens']:
                tokens.append(token['word'])
        return tokens

    @staticmethod
    def _count_words(tokens):
        assert isinstance(tokens, list)
        model = {}
        for token in tokens:
            assert isinstance(token, str)
            num = model.get(token, 0)
            model[token] = num + 1
        return model

    @staticmethod
    def _write_file(model, output_file):
        assert isinstance(model, dict)
        assert isinstance(output_file, str)
        with open(output_file, 'w', encoding='utf-8') as file:
            for word, num in model.items():
                file.write(str.format('{} {}\n', word, num))


class NCharacterGram:
    def __init__(self):
        pass


def main():
    pass


if __name__ == '__main__':
    main()
