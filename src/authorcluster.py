from chunk import Chunker
from constants import Language
import nltk
from tokenizer import Tokenizer

from sklearn import cluster
from sklearn import metrics

def AuthorCluster(object):
    def __init__(self, verbose = False, lang):
        self.Chunker = Chunker(verbose)
        self.Verbose = verbose
        self.Language = lang
        self.MostCommonWords = []

    def generateFeatureVector(self, chunk):
        vec = [x in chunk for x in self.MostCommonWords]
        return vec

    # Input: text tokenized into sentences [ 0'sen1', 1'sen2', 3'sen3' ]
    # RET: [ [0], [1, 3] ] - > len = numClusters
    def cluster(self, text, chunkSize, numClusters):
        tokenizer = Tokenizer(self.Language)
        fdist = nltk.FreqDist(tokenizer.tokenizeIntoWords(text))
        # TODO: the english tokenizer at least also includes punctuation, filter?
        for wordfreqpair in fdist.most_common(500): # TODO: too high for the size of our texts?s
            word = wordfreqpair[0]
            # freq = wordfreqpair[1]
            self.MostCommonWords.append(word)

        featurizeVectorList = []
        chunks = self.Chunker.chunk(text, chunkSize)
        for chunk in chunks:
            featurizeVectorList.append(self.generateFeatureVector(chunk))

        km = cluster.KMeans(n_clusters=numClusters, init='k-means++', max_iter=100, n_init=1, verbose=self.Verbose)
        labels = km.fit_predict(featurizeVectorList)
        ret = [[]] * numClusters
        sentencenum = 0
        for i, label in enumerate(labels):
            for sentence in tokenizer.tokenizeIntoSentences(chunks[i]):
                ret[label].append(sentencenum)
                sentencenum += 1
        return ret
