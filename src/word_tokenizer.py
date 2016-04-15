from constants import Language
import nltk

class WordTokenizer(object):
    def __init__(self, lang):
        if lang is not Language.English:
            raise Exception("Not implemented for language", lang)
        self.Language = lang

    def tokenize(self, text):
        if self.Language is Language.English:
            return nltk.tokenize.word_tokenize(text)
