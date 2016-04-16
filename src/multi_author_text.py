class Text(object):
    def __init__(self, paragraphs = False):
        self.Paragraphs = []
        self.Sentences = []
        self.AuthorIds = []
        self.Authors = []
        return

    def _get_authorid(self, author):
        idx = len(self.Authors)
        if author in self.Authors:
            idx = self.Authors.index(author)
        else:
            self.Authors.append(author)
        return idx

    def getText(self):
        return ' '.join(self.Sentences)

    def getTextTokenizedBySentence(self):
        return self.Sentences

    # def add_untokenized_sentences(self, author, sentences):
    def add_sentences(self, author, sentences):
        idx = self._get_authorid(author)
        for sentence in sentences:
            self.Sentences.append(sentence)
            self.AuthorIds.append(idx)

    def add_sentence(self, author, sentence):
        self.add_sentences(author, [sentence])

    def getAuthorForSentenceIndex(self, sentenceIdx):
        return self.Authors[self.AuthorIds[sentenceIdx]]

    def getAuthorIndexForSentence(self, sentenceIdx):
        return self.AuthorIds[sentenceIdx]

    def getAuthorForAuthorIndex(self, authorIdx):
        return self.Authors[authorIdx]

    def writeToFile(self, fname):
        with open(fname, 'wb') as f:
            import pickle
            pickle.dump(self, f)

    @staticmethod
    def loadFromFile(fname):
        with open(fname, 'rb') as f:
            import pickle
            return pickle.load(f)
