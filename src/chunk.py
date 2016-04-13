class Chunker(object):
    # chunk size is in number of sentences
    def __init__(self, debug = False):
        self.debug = False

    def tokenizeIntoSentences(self, text):
        