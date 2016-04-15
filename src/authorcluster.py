from chunk import Chunker
from constants import Language
import nltk
from word_tokenizer import WordTokenizer

def AuthorCluster(object):
    def __init__(self, verbose = False, lang):
        self.Chunker = Chunker(verbose)
        self.Verbose = verbose
        self.Language = lang
        self.MostCommonWords = []

    def generateFeatureVector(self, chunk):
        vec = [x in chunk for x in self.MostCommonWords]
        return vec

    # [ 0'sen1', 1'sen2', 3'sen3' ]
    # RET: [ [0], [1, 3] ] - > len = numClusters
    def cluster(self, text, chunkSize, numClusters):
        wt = WordTokenizer(self.Language)
        fdist = nltk.FreqDist(wt)
        # TODO: the english tokenizer at least also includes punctuation, filter?
        for wordfreqpair in fdist.most_common(500): # TODO: too high for the size of our texts?s
            word = wordfreqpair[0]
            # freq = wordfreqpair[1]
            self.MostCommonWords.append(word)

        chunks = self.Chunker.chunk(text, chunkSize)
        for chunk in chunks:
            fv = self.generateFeatureVector(chunk)

