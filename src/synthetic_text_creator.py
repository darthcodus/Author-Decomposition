#!/usr/bin/python3

import os
import pickle
from authorclustering.multi_author_text import Text

from authorclustering.corenlp import StanfordCoreNLP

class TextMerger(object):
    def __init__(self, debug = False):
        self.debug = debug
        self.texts = []

    def addText(self, author, text):
        newText = {}
        self.texts.append(newText)
        newText['author'] = author
        newText['text'] = text

    def textsByAuthor(self, author):
        return list(filter(lambda x: x['author'].lower() == author.lower(), self.texts))

    def generateText(self, lower, upper):
        scnlp = StanfordCoreNLP()
        text = Text()
        textFile = ""
        metaFile = ""
        # lower and upper ignored for now, just randomly concatenates texts
        if lower is not 0 or upper is not 0:
            raise Exception('Not implemented sentence wise chunking')
        import random
        done = [False] * len(self.texts)
        curtext = -1
        while any(x is False for x in done):
            curtext = random.randint(0, len(self.texts) - 1)
            if done[curtext]:
                continue
            newText = self.texts[curtext]['text']
            newAuthor = self.texts[curtext]['author']
            print(textFile)
            print(newText)
            metaFile += '%d,,, %d,,, %s\n' % (len(textFile), len(textFile) + len(newText) - 1, newAuthor)
            textFile += newText
            text.add_sentences(newAuthor, scnlp.split_sentences(newText))
            done[curtext] = True
        return textFile, metaFile, text

        """
        for text in self.texts:
            text['ptr'] = 0
        temp = filter(lambda x: x['ptr'] < len(x['text']), self.texts)
        while any(x['ptr'] < len(x['text']) for x in temp):
            for text in temp:
                chunksize = -1
                if lower is 0:
                    chunksize = len(text['text'])
                else:
                    import random
                    chunksize = random.randint(lower, upper)
                lines = 0
                while(lines < chunksize and text['ptr'] < len(text['text']):
                if x['ptr'] >= <?>:
                    temp = filter(lambda x: x['ptr'] < len(x['text']), self.texts)
        return None, None #TODO
        """

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--texts', help='paths to folder containing texts', required=True)
    parser.add_argument('-c', '--chunk', help='number of sentences per chunk, as -c <size> or -c <lower> <upper> for random values between a range, or 0 to simply randomly join the texts', required=True, nargs = '*')
    parser.add_argument('-oth', '--hrtxt', help='output human-readable text file', required=False)
    parser.add_argument('-omh', '--hrmeta', help='output human-readable metadata file', required=False)
    parser.add_argument('-opick', '--pickletext', help='output file for pickled Text object', required=True)
    args = parser.parse_args()

    tm = TextMerger()
    for subdir, dirs, files in os.walk(args.texts):
        if not files:
            print("\tSkipping: %s" % subdir)
            continue
        print("\t%s" % subdir)
        author = os.path.split(subdir)[-1]
        print('\n\nAuthor: ', author)
        for f in files:
            print('Text: ', f)
            if f.lower() == '.DS_Store'.lower():
                print('Ignoring %s' % f)
                continue

            with open(os.path.join(subdir, f), encoding='utf-8') as fin:
                contents = ''.join(fin.readlines())
                tm.addText(author, contents)
                # print(author, '\n', contents)
        print(tm.texts)
        print("\t\tRead %d texts for author." % len(tm.textsByAuthor(author)))

    if len(args.chunk) == 1:
        textFile, metaFile, text = tm.generateText(int(args.chunk[0]), int(args.chunk[0]))
    else:
        textFile, metaFile, text = tm.generateText(int(args.chunk[0]), int(args.chunk[1]))

    if args.hrtxt is not None:
        with open(args.hrtxt, 'wt') as f:
            f.write(textFile)

    if args.hrmeta is not None:
        with open(args.hrmeta, 'wt') as f:
            f.write(metaFile)

    text.writeToFile(args.pickletext)

main()
