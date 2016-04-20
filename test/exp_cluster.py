#!/usr/bin/env python3
import copy
import logging
from collections import Counter
from multiprocessing.pool import Pool
from sklearn.cluster import SpectralClustering

from sklearn.feature_selection import VarianceThreshold

from authorclustering.corenlp import StanfordCoreNLP


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

    def simple_concat(self, size):
        assert isinstance(size, int)
        if size <= 0:
            raise Exception('Invalid chunk size less than 0.')

        chunks = []
        authors = []
        texts = ''
        for i, sentence in enumerate(self.sentences, start=1):
            assert isinstance(sentence, dict)
            if i % size == 0:
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
        self.words = {}
        self.char_ngrams = {}
        self.postags = {}
        self.postag_bigrams = {}

    def load(self, word_path, char_ngram_path, postag_path, postag_bigram_path):
        assert isinstance(word_path, str)
        assert isinstance(char_ngram_path, str)
        assert isinstance(postag_path, str)
        assert isinstance(postag_bigram_path, str)

        with open(word_path, 'r', encoding='utf=8') as file:
            for line in file:
                elements = line.split()
                assert len(elements) == 2
                self.words[elements[0]] = int(elements[1])

        with open(char_ngram_path, 'r', encoding='utf=8') as file:
            for line in file:
                self.char_ngrams[line[:4]] = int(line[5:])

        with open(postag_path, 'r', encoding='utf=8') as file:
            for line in file:
                elements = line.split()
                assert len(elements) == 2
                self.postags[elements[0]] = int(elements[1])

        with open(postag_bigram_path, 'r', encoding='utf=8') as file:
            for line in file:
                elements = line.split()
                assert len(elements) == 3
                self.postag_bigrams[(elements[0], elements[1])] = int(elements[2])

    def vectorize(self, chunks):
        assert isinstance(chunks, list)
        vectors = []
        with Pool() as pool:
            args = []
            for chunk in chunks:
                args.append((list(self.words.keys()), chunk))
            returns = pool.starmap(Feature._parallel_vectorize, args)
            for r in returns:
                vectors.append(r)
        return vectors

    @staticmethod
    def _parallel_vectorize(ref_words, chunk):
        assert isinstance(ref_words, list)
        assert isinstance(chunk, str)
        nlp = StanfordCoreNLP('http://localhost:8011')
        words, postags = nlp.parse(chunk)
        counter = Counter(words)
        return [counter[x] for x in ref_words]

    @staticmethod
    def remove_features(vectors):
        assert isinstance(vectors, list)
        sel = VarianceThreshold(.8 * (1 - .8))
        return sel.fit_transform(vectors)


class Evaluation:
    @staticmethod
    def purity(labels, chunks):
        assert isinstance(chunks, list)

        print(str.format('Num of labels: {}', len(labels)))
        print(str.format('Num of chunks: {}', len(chunks)))

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
            print(str.format(
                'Cluster id {} major author: {}, purity: {}',
                key, major_author, sub_purity / len(clusters[key]))
            )

        total_purity = (1 / len(labels)) * sum_majority
        print(str.format('Total purity: {}', total_purity))
        return total_purity


def main():
    formatter = logging.Formatter('%(asctime)s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info('Loading corpus 1.')
    corpus1 = Corpus()
    corpus1.add_file('../models/spanish_blogs2/alejandro-nieto-gonzalez.txt')
    logger.info(str.format('Corpus 1 sentences: {}', len(corpus1.sentences)))

    logger.info('Loading corpus 2.')
    corpus2 = Corpus()
    corpus2.add_file('../models/spanish_blogs2/aurelio-jimenez.txt')
    logger.info(str.format('Corpus 2 sentences: {}', len(corpus2.sentences)))

    logger.info('Loading corpus 3.')
    corpus3 = Corpus()
    corpus3.add_file('../models/spanish_blogs2/javier-j-navarro.txt')
    logger.info(str.format('Corpus 3 sentences: {}', len(corpus3.sentences)))

    logger.info('Chunking.')
    chunk = Chunk()
    chunk.append_sentences('alejandro-nieto-gonzalez', corpus1.sentences)
    chunk.append_sentences('aurelio-jimenez', corpus2.sentences)
    chunk.append_sentences('javier-j-navarro', corpus3.sentences)
    chunks = chunk.simple_concat(10)
    logger.info(str.format('Number of chunks: {}', len(chunks)))

    logger.info('Loading features.')
    feature = Feature()
    word_path = '../models/spanish_blogs2/output_word.txt'
    char_ngram_path = '../models/spanish_blogs2/output_char.txt'
    postag_path = '../models/spanish_blogs2/output_pos.txt'
    postag_bigram_path = '../models/spanish_blogs2/output_bipos.txt'
    feature.load(word_path, char_ngram_path, postag_path, postag_bigram_path)

    logger.info('Vectorizing.')
    trans_chunks = []
    for chunk in chunks:
        trans_chunks.append(chunk['text'])
    vectors = feature.vectorize(trans_chunks)

    logger.info('Removing features.')
    vectors = feature.remove_features(vectors)

    logger.info('Clustering.')
    clustering = SpectralClustering(n_clusters=3)
    labels = clustering.fit_predict(vectors)

    logger.info('Evaluating.')
    evaluation = Evaluation()
    evaluation.purity(labels, chunks)

    logger.info('Done.')


if __name__ == '__main__':
    main()
