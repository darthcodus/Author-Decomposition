from chunk import Chunker
from constants import Language
import nltk
from corenlp import StanfordCoreNLP

from sklearn import cluster
from sklearn import metrics

def AuthorCluster(object):
    def __init__(self, verbose = False, lang):
        self.Chunker = Chunker(verbose)
        self.Verbose = verbose
        self.Language = lang # TODO: needed? ignored for now. Assuming corenlp does the right thing for the langs we need.
        self.MostCommonWords = []

    def generateFeatureVector(self, chunk):
        vec = [x in chunk for x in self.MostCommonWords]
        return vec

    # TODO: reduce calls to corenlp API
    def cluster(self, text, chunkSize, numClusters):
        """
        Splits text into chunks of size 'chunkSize' and clusters those chunks into
        'numClusters' number of clusters.
        :param text: input text.
        :return: a tuple(list of sentences after tokenizing text, a list of lists of sentences belonging to each cluster)
        """
        #if self.Language not in [Language.Arabic, Language.English, Language.Spanish]:
        #    raise Exception("Not implemented for language", self.Language)
        cnlp = StanfordCoreNLP()
        fdist = nltk.FreqDist(cnlp.parse(text)[0])
        # TODO: the english tokenizer at least also includes punctuation, filter?
        for wordfreqpair in fdist.most_common(500): # TODO: too high for the size of our texts?
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
            for sentence in cnlp.split_sentences(chunks[i]):
                ret[label].append(sentencenum)
                sentencenum += 1
        return (cnlp.split_sentences(text), ret)
