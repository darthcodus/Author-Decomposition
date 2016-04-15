#!/usr/bin/env python3
class Chunker(object):
    def __init__(self):
        self.sentences = []
        self.authors = []

    def clear_all(self):
        """
        Deletes all the added sentences.
        """
        self.sentences.clear()
        self.authors.clear()

    def add_sentence(self, author, sentence):
        """
        Add authorship and a corresponding sentence to the chunker.
        :param sentence: a single-sentence text.
        :param author: author name
        """
        assert isinstance(author, str)
        assert isinstance(sentence, str)
        self.sentences.append(sentence)
        self.authors.append(author)

    def fixed_length_chunk(self, chunk_size):
        """
        Separates text into chunks of 'chunk_size' sentences.
        :param chunk_size: the number of sentences in each chunk
        :return: a list of dictionaries containing texts and a author list
        {'text': chunk, 'author': ['a', 'b', 'c']}.
        """
        assert isinstance(chunk_size, int)
        if chunk_size <= 0:
            raise Exception('Invalid chunk size.')

        chunks = []

        for i in range(0, len(self.sentences), chunk_size):
            chunks.append({
                'author': self.authors[i:i + chunk_size],
                'text': ' '.join(self.sentences[i:i + chunk_size])
            })
        return chunks
