#!/usr/bin/env python3
import logging
from collections import Counter
from multiprocessing.pool import Pool
from sklearn.cluster import SpectralClustering, KMeans

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

    def vectorize(self, chunks):
        assert isinstance(chunks, list)
        parsed_words = {}
        parsed_postags = {}
        with Pool() as pool:
            results = pool.map(Feature._parallel_parse, chunks)
            for i, (words, postags) in enumerate(results):
                parsed_words[i] = words
                parsed_postags[i] = postags

        vectors = []
        with Pool() as pool:
            args = []
            for i, chunk in enumerate(chunks):
                # args.append((chunk, tuple(parsed_words.get(i)), tuple(parsed_postags.get(i)),
                #              self.words, self.char_ngrams, self.postags, self.postag_bigrams,
                #              self.word_bigrams, self.postag_trigrams, self.postag_fourgrams))

                args.append((chunk, tuple(parsed_words.get(i)), tuple(parsed_postags.get(i)),
                             self.words, self.char_ngrams, None, None,
                             self.word_bigrams, self.postag_trigrams, None))
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

        result_text = ''
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
        result_text += str.format('Total purity: {}\n', total_purity)
        return result_text


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
    logger.info(str.format('Corpus 1, sentences: {}', len(corpus1.sentences)))

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

    del corpus1, corpus2, corpus3

    chunk_size = 20
    chunks = chunk.simple_concat(chunk_size)
    logger.info(str.format('Number of chunks: {}, chunk size: {}', len(chunks), chunk_size))

    logger.info('Loading features.')
    feature = Feature()
    word_path = '../models/spanish_blogs2/output_word.txt'
    word_bigram_path = '../models/spanish_blogs2/output_biword.txt'
    char_ngram_path = '../models/spanish_blogs2/output_char.txt'
    postag_path = '../models/spanish_blogs2/output_pos.txt'
    postag_bigram_path = '../models/spanish_blogs2/output_bipos.txt'
    postag_trigram_path = '../models/spanish_blogs2/output_tripos.txt'
    postag_fourgram_path = '../models/spanish_blogs2/output_4pos.txt'
    feature.load(word_path=word_path, word_bigram_path=word_bigram_path,
                 char_ngram_path=char_ngram_path, postag_path=postag_path,
                 postag_bigram_path=postag_bigram_path, postag_trigram_path=postag_trigram_path,
                 postag_fourgram_path=postag_fourgram_path)

    logger.info('Vectorizing.')
    trans_chunks = []
    for chunk in chunks:
        trans_chunks.append(chunk['text'])
    vectors = feature.vectorize(trans_chunks)
    logger.info(str.format('Number of features: {}', len(vectors[0])))

    logger.info('Removing features.')
    vectors = feature.remove_features(vectors)
    logger.info(str.format('Number of features: {}', len(vectors[0])))

    logger.info('Clustering.')
    n_clusters = 3
    n_neighbors = int(len(chunks) / n_clusters - (n_clusters * 0.1))
    clustering = SpectralClustering(n_clusters=n_clusters,
                                    affinity='nearest_neighbors',
                                    n_neighbors=n_neighbors)
    labels = clustering.fit_predict(vectors)

    logger.info('Evaluating.')
    evaluation = Evaluation()
    result = evaluation.purity(labels, chunks)
    logger.info(str.format('==RESULT==\n{}', result))

    logger.info('Done.')


if __name__ == '__main__':
    main()
