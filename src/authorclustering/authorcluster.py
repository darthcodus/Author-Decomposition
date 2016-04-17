import nltk

from sklearn import cluster
from sklearn import metrics

class AuthorCluster:
    def __init__(self, verbose = False):
        self.Verbose = verbose
        self.MostCommonWords = []

    def generateFeatureVector(self, chunk):
        vec = [x in chunk for x in self.MostCommonWords]
        return vec

    # TODO: reduce calls to corenlp API
    def cluster(self, text, chunkSize, numClusters):
        """
        Splits text into chunks of size 'chunkSize' and clusters those chunks into
        'numClusters' number of clusters.
        :param text: input text object.
        :return: a list of lists of sentences belonging to each cluster
        """

        fdist = nltk.FreqDist(text.getTextTokenizedByWord())
        for wordfreqpair in fdist.most_common(500): # TODO: too high for the size of our texts?
            word = wordfreqpair[0]
            # freq = wordfreqpair[1]
            self.MostCommonWords.append(word)

        featurizeVectorList = []
        chunkIds, chunks = text.fixed_length_chunk(chunkSize)
        for chunk in chunks:
            featurizeVectorList.append(self.generateFeatureVector(chunk))

        print('Chunk Ids: ', chunkIds)
        print('Chunks: ', chunks)
        km = cluster.KMeans(n_clusters=numClusters, init='k-means++', max_iter=100, n_init=1, verbose=self.Verbose)
        labels = km.fit_predict(featurizeVectorList)
        ret = [None] * numClusters

        print('Labels: ', labels)
        for i, label in enumerate(labels):
            if ret[label] is None:
                ret[label] = []
            ret[label] += chunkIds[i]
        return ret
