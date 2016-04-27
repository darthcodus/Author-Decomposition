#!/usr/bin/env python3
import argparse
import logging
from collections import Counter
from multiprocessing.pool import Pool

import numpy
from sklearn import metrics

from sklearn.cluster import SpectralClustering, KMeans

from sklearn.feature_selection import VarianceThreshold
from sklearn.metrics.pairwise import cosine_similarity, pairwise_distances

from authorclustering.corenlp import StanfordCoreNLP
from authorclustering.multi_author_text import Text


class Corpus:
    def __init__(self):
        self.paragraphs = []
        self.sentences = []

    def add_file(self, file_path):
        assert isinstance(file_path, str)
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                self.paragraphs.append(line)

        with Pool() as pool:
            results = pool.map(Corpus._split_sentences, self.paragraphs)
            for sentences in results:
                assert isinstance(sentences, list)
                self.sentences.extend(sentences)

    @staticmethod
    def _split_sentences(text):
        assert isinstance(text, str)
        nlp = StanfordCoreNLP('http://localhost:8011')
        return nlp.split_sentences(text)


class Chunk:
    def __init__(self):
        self.sentences = []

    def append_sentences(self, author, sentences):
        assert isinstance(author, str)
        assert isinstance(sentences, list)
        for sentence in sentences:
            self.sentences.append({'author': author, 'text': sentence})

    def generate(self, size):
        assert isinstance(size, int)
        if size <= 0:
            raise Exception('Invalid chunk size less than 0.')

        chunks = []
        authors = []
        texts = ''
        for i, sentence in enumerate(self.sentences, start=1):
            assert isinstance(sentence, dict)
            if size == 1:
                authors.clear()
                authors.append(sentence['author'])
                texts = sentence['text']
                chunks.append({'author': list(authors), 'text': texts})
            elif i % size == 0 and size != 1:
                chunks.append({'author': list(authors), 'text': texts})
                authors.clear()
                texts = ''
            else:
                authors.append(sentence['author'])
                texts += sentence['text'] + ' '
        chunks.append({'author': list(authors), 'text': texts})
        return chunks


class Feature:
    def __init__(self):
        self.words = set()
        self.word_bigrams = set()
        self.char_ngrams = set()
        self.postags = set()
        self.postag_bigrams = set()
        self.postag_trigrams = set()
        self.postag_fourgrams = set()

    def load(self, word_path=None, word_bigram_path=None, char_ngram_path=None,
             postag_path=None, postag_bigram_path=None,
             postag_trigram_path=None, postag_fourgram_path=None):
        if word_path is not None:
            assert isinstance(word_path, str)
            with open(word_path, 'r', encoding='utf=8') as file:
                for line in file:
                    elements = line.split()
                    assert len(elements) == 2
                    self.words.add(elements[0])

        if word_bigram_path is not None:
            assert isinstance(word_bigram_path, str)
            with open(word_bigram_path, 'r', encoding='utf=8') as file:
                for line in file:
                    elements = line.split()
                    assert len(elements) == 3
                    key = str.format('{} {}', elements[0], elements[1])
                    self.word_bigrams.add(key)

        if char_ngram_path is not None:
            assert isinstance(char_ngram_path, str)
            with open(char_ngram_path, 'r', encoding='utf=8') as file:
                for line in file:
                    self.char_ngrams.add(line[:4])

        if postag_path is not None:
            assert isinstance(postag_path, str)
            with open(postag_path, 'r', encoding='utf=8') as file:
                for line in file:
                    elements = line.split()
                    assert len(elements) == 2
                    self.postags.add(elements[0])

        if postag_bigram_path is not None:
            assert isinstance(postag_bigram_path, str)
            with open(postag_bigram_path, 'r', encoding='utf=8') as file:
                for line in file:
                    elements = line.split()
                    assert len(elements) == 3
                    key = str.format('{} {}', elements[0], elements[1])
                    self.postag_bigrams.add(key)

        if postag_trigram_path is not None:
            assert isinstance(postag_trigram_path, str)
            with open(postag_trigram_path, 'r', encoding='utf=8') as file:
                for line in file:
                    elements = line.split()
                    assert len(elements) == 4
                    key = str.format('{} {} {}', elements[0], elements[1], elements[2])
                    self.postag_trigrams.add(key)

        if postag_fourgram_path is not None:
            assert isinstance(postag_fourgram_path, str)
            with open(postag_fourgram_path, 'r', encoding='utf=8') as file:
                for line in file:
                    elements = line.split()
                    assert len(elements) == 5
                    key = str.format('{} {} {} {}', elements[0], elements[1], elements[2], elements[3])
                    self.postag_fourgrams.add(key)

    def vectorize(self, chunks, features):
        assert isinstance(chunks, list)
        assert isinstance(features, str)

        parsed_words = {}
        parsed_postags = {}
        with Pool() as pool:
            results = pool.map(Feature._parallel_parse, chunks)
            for i, (words, postags) in enumerate(results):
                parsed_words[i] = words
                parsed_postags[i] = postags

        words = self.words if 'w' in features else None
        word_bigrams = self.word_bigrams if 'W' in features else None
        char_ngrams = self.char_ngrams if 'c' in features else None
        postags = self.postags if 'p' in features else None
        postag_bigrams = self.postag_bigrams if 'P' in features else None
        postag_trigrams = self.postag_trigrams if 'T' in features else None
        postag_fourgrams = None

        vectors = []
        with Pool() as pool:
            args = []
            for i, chunk in enumerate(chunks):
                args.append((chunk, tuple(parsed_words.get(i)), tuple(parsed_postags.get(i)),
                             words, char_ngrams, postags, postag_bigrams,
                             word_bigrams, postag_trigrams, postag_fourgrams))
            results = pool.starmap(Feature._parallel_vectorize, args)
            vectors.extend(results)
        return vectors

    @staticmethod
    def _parallel_parse(chunk):
        assert isinstance(chunk, str)
        nlp = StanfordCoreNLP('http://localhost:8011')
        words, postags = nlp.parse(chunk)
        return words, postags

    @staticmethod
    def _parallel_vectorize(chunk, words, postags, ref_words=None, ref_char_grams=None,
                            ref_postags=None, ref_postag_bigrams=None, ref_word_bigrams=None,
                            ref_postag_trigram=None, ref_postag_fourgram=None):
        assert isinstance(chunk, str)
        assert isinstance(words, tuple)
        assert isinstance(postags, tuple)
        assert isinstance(ref_words, set) or ref_words is None
        assert isinstance(ref_char_grams, set) or ref_char_grams is None
        assert isinstance(ref_postags, set) or ref_postags is None
        assert isinstance(ref_postag_bigrams, set) or ref_postag_bigrams is None
        assert isinstance(ref_word_bigrams, set) or ref_word_bigrams is None
        assert isinstance(ref_postag_trigram, set) or ref_postag_trigram is None
        assert isinstance(ref_postag_fourgram, set) or ref_postag_fourgram is None

        vector = []

        if ref_words is not None:
            word_counter = Counter(words)
            vector.extend([x in word_counter for x in ref_words])

        if ref_char_grams is not None:
            char_grams = Feature._make_ngram(chunk, 4)
            vector.extend([x in char_grams for x in ref_char_grams])

        if ref_postags is not None:
            tag_counter = Counter(postags)
            vector.extend([x in tag_counter for x in ref_postags])

        if ref_postag_bigrams is not None:
            postag_bigrams = set()
            for pair in Feature._make_ngram(postags, 2):
                postag_bigrams.add(str.format('{} {}', pair[0], pair[1]))
            vector.extend([x in postag_bigrams for x in ref_postag_bigrams])

        if ref_word_bigrams is not None:
            word_bigrams = set()
            for pair in Feature._make_ngram(words, 2):
                word_bigrams.add(str.format('{} {}', pair[0], pair[1]))
            vector.extend([x in word_bigrams for x in ref_word_bigrams])

        if ref_postag_trigram is not None:
            postag_trigrams = set()
            for pair in Feature._make_ngram(postags, 3):
                postag_trigrams.add(str.format('{} {} {}', pair[0], pair[1], pair[2]))
            vector.extend([x in postag_trigrams for x in ref_postag_trigram])

        if ref_postag_fourgram is not None:
            postag_fourgrams = set()
            for pair in Feature._make_ngram(words, 4):
                postag_fourgrams.add(str.format('{} {} {} {}', pair[0], pair[1], pair[2], pair[3]))
            vector.extend([x in postag_fourgrams for x in ref_postag_fourgram])

        return vector

    @staticmethod
    def _make_ngram(iterable, size):
        grams = set()
        for i in range(len(iterable) - size + 1):
            grams.add(iterable[i:i + size])
        return grams

    @staticmethod
    def remove_features(vectors):
        assert isinstance(vectors, list)
        num = len(vectors[0])
        for v in vectors:
            assert num == len(v)
        sel = VarianceThreshold(.9 * (1 - .9))
        return sel.fit_transform(vectors)


class Evaluation:
    @staticmethod
    def purity(labels, chunks):
        assert isinstance(chunks, list)

        result_text = '\n'
        result_text += str.format('Num of labels: {}\n', len(labels))
        result_text += str.format('Num of chunks: {}\n', len(chunks))

        chunk_majorities = []
        for chunk in chunks:
            author = Counter(chunk['author']).most_common(1)[0][0]
            chunk_majorities.append(author)

        clusters = {}
        for i, label in enumerate(labels):
            majors = clusters.get(label, list())
            majors.append(chunk_majorities[i])
            clusters[label] = majors

        sum_majority = 0
        for key in clusters.keys():
            counter = Counter(clusters[key])
            major_author, sub_purity = counter.most_common(1)[0]
            sum_majority += sub_purity
            result_text += str.format(
                'Cluster id {} major author: {}, purity: {}\n',
                key, major_author, sub_purity / len(clusters[key])
            )

        total_purity = (1 / len(labels)) * sum_majority
        result_text += str.format('Overall purity: {}\n', total_purity)
        return result_text

    @staticmethod
    def silhouette_coefficient(vectors, labels):
        coefficient = metrics.silhouette_score(vectors, labels, metric='euclidean')
        return str.format('\nSilhouette Coefficient: {}\n', coefficient)

    @staticmethod
    def average_cosine_distance(vectors, labels):
        assert len(vectors) == len(labels)

        labeled_vectors = {}
        for vector, label in zip(vectors, labels):
            vector_list = labeled_vectors.get(label, list())
            vector_list.append(vector)
            labeled_vectors[label] = vector_list

        result_text = '\n'
        overall_avg = 0
        num_label = 0

        for label in labeled_vectors.keys():
            vector_list = labeled_vectors.get(label)
            distances = pairwise_distances(numpy.array(vector_list), metric='cosine', n_jobs=12)

            dumps = []
            for i in range(len(distances)):
                for j in range(i):
                    dumps.append(distances[i][j])

            mean = numpy.mean(dumps)
            overall_avg += mean
            num_label += 1
            result_text += str.format(
                'Cluster id {} average cosine distance: {}\n', label, mean)

        result_text += str.format(
            'Overall average cosine distance: {}\n', overall_avg / num_label)
        return result_text

    @staticmethod
    def cosine_similarity(vectors, labels):
        """
        DO NOT USE, NOT DONE YET
        """
        assert len(vectors) == len(labels)

        labeled_vectors = {}
        for vector, label in zip(vectors, labels):
            vector_list = labeled_vectors.get(label, list())
            vector_list.append(vector)
            labeled_vectors[label] = vector_list

        result_text = '\n'
        overall_min = 0
        num_label = 0

        for label in labeled_vectors.keys():
            vector_list = labeled_vectors.get(label)
            similarity = cosine_similarity(numpy.array(vector_list))
            distances = pairwise_distances(numpy.array(vector_list), metric='cosine', n_jobs=12)
            for i in range(len(distances)):
                distances[i][i] = float('Inf')

            min_distances = []
            for i, distance in enumerate(distances):
                min_distance = float('Inf')
                for j, d in enumerate(distance):
                    min_distance = min(min_distance, d)
                min_distances.append(min_distance)

            num_label += 1
            overall_min += numpy.mean(min_distances)
            result_text += str.format(
                'Cluster id {} cosine similarity: {}\n', label, numpy.mean(min_distances))

        result_text += str.format(
            'Overall cosine similarity: {}\n', overall_min / num_label)
        return result_text


class CommandLineParser:
    @staticmethod
    def parse():
        feature_help = 'w:Word frequency, ' \
                       'W:Word bigram, ' \
                       'c:Character 4-gram, ' \
                       'p:POS tag, ' \
                       'P:POS tag bigram, ' \
                       'T:POS tag trigram'
        metavar = 'wWcpPT'
        parser = argparse.ArgumentParser()
        parser.add_argument('features', metavar=metavar, nargs='?', help=feature_help)
        parser.add_argument('-s', metavar='20', dest='chunk_size', type=int, required=True)
        parser.add_argument('-c', metavar='3', dest='n_clusters', type=int, required=True)
        args = parser.parse_args()
        features = args.features
        chunk_size = args.chunk_size
        n_clusters = args.n_clusters

        if not any([f in metavar for f in features]):
            parser.print_help()
            exit()
        return features, chunk_size, n_clusters


def main():
    formatter = logging.Formatter('%(asctime)s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    features, chunk_size, n_clusters = CommandLineParser.parse()

    path_prefix = '../models/spanish_blogs2/interspersed_20_40/'
    logger.info('Loading text file.')
    corpus = Text.loadFromFile(path_prefix + '20_40.pickle')
    assert isinstance(corpus, Text)

    logger.info('Chunking.')
    chunk = Chunk()
    ids, sentences = corpus.fixed_length_chunk(chunk_size)
    num_sentences = {}

    for id, sentence in zip(ids, sentences):
        assert isinstance(id, list)
        assert isinstance(sentence, list)

        for i, s in zip(id, sentence):
            author = corpus.getAuthorForSentenceIndex(i)
            chunk.append_sentences(author, [s])
            n = num_sentences.get(author, 0)
            num_sentences[author] = n + 1

    for author, num in num_sentences.items():
        logger.info(str.format('{} sentences: {}', author, num))

    chunks = chunk.generate(chunk_size)
    logger.info(str.format('Number of chunks: {}, chunk size: {}', len(chunks), chunk_size))

    logger.info('Loading features.')
    feature = Feature()
    word_path = path_prefix + 'output_word.txt'
    word_bigram_path = path_prefix + 'output_biword.txt'
    char_ngram_path = path_prefix + 'output_char.txt'
    postag_path = path_prefix + 'output_pos.txt'
    postag_bigram_path = path_prefix + 'output_bipos.txt'
    postag_trigram_path = path_prefix + 'output_tripos.txt'
    postag_fourgram_path = path_prefix + 'output_4pos.txt'
    feature.load(word_path=word_path, word_bigram_path=word_bigram_path,
                 char_ngram_path=char_ngram_path, postag_path=postag_path,
                 postag_bigram_path=postag_bigram_path, postag_trigram_path=postag_trigram_path,
                 postag_fourgram_path=postag_fourgram_path)

    logger.info('Vectorizing.')
    trans_chunks = []
    for chunk in chunks:
        trans_chunks.append(chunk['text'])
    vectors = feature.vectorize(trans_chunks, features)
    logger.info(str.format('Number of features: {}', len(vectors[0])))

    logger.info('Removing features.')
    vectors = feature.remove_features(vectors)
    logger.info(str.format('Number of features: {}', len(vectors[0])))

    logger.info('Clustering.')
    n_neighbors = int(len(chunks) / n_clusters - (n_clusters * 0.1))
    clustering = SpectralClustering(n_clusters=n_clusters,
                                    affinity='nearest_neighbors',
                                    n_neighbors=n_neighbors)

    # cosines = pairwise_distances(numpy.array(vectors))
    labels = clustering.fit_predict(vectors)

    logger.info('Evaluating.')
    evaluation = Evaluation()
    purity = evaluation.purity(labels, chunks)
    logger.info(str.format('==RESULT=='))
    logger.info(str.format('{}', purity))

    # min_distance = evaluation.average_cosine_distance(vectors, labels)
    # logger.info(str.format('{}', min_distance))
    # coefficient = evaluation.silhouette_coefficient(vectors, labels)
    # logger.info(str.format('Silhouette Coefficient: {}', coefficient))

    logger.info('Done.')


if __name__ == '__main__':
    main()
