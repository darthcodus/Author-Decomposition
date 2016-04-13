class Chunker(object):
    # chunk size is in number of sentences
    def __init__(self, debug = False):
        self.debug = False

    # return a list of sentences
    def tokenizeIntoSentences(self, text):
        raise Exception("Not implemented")

    # separate text into chunks of 'chunkSize' sentences, return a list containing lists of sentences belonging to that chunk
    def chunk(self, text, chunkSize):
        raise Exception("Not implemented")
