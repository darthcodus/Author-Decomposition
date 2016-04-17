from authorclustering.constants import Language
import nltk

class Tokenizer(object):
    def __init__(self, lang):
        if lang is not Language.English:
            raise Exception("Not implemented for language", lang)
        self.Language = lang

    def tokenizeIntoWords(self, text):
        if self.Language is Language.English:
            return nltk.tokenize.word_tokenize(text)

    def tokenizeIntoSentences(self, text):
        raise NotImplemented()
        # if self.Language is Language.English:
