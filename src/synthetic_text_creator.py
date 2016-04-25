#!/usr/bin/python3

import os
import pickle
from authorclustering.multi_author_text import Text

from authorclustering.corenlp import StanfordCoreNLP

class TextMerger(object):
    def __init__(self, verbose = False):
        self.Verbose = verbose
        self.texts = {}

    def addText(self, author, text):
        failcount = 0
        scnlp = StanfordCoreNLP()
        if author not in self.texts:
            self.texts[author] = []
        if True:
            print('Text: %s' % text)
            self.texts[author].extend(scnlp.split_sentences(text))
        if True:
            failcount += 1
            print('Failure #%d' % failcount)
            print('Failed for the given text by author %s' % author)

    def generateText(self, lower, upper):
        text = Text(verbose=self.Verbose)
        textFile = ""
        metaFile = ""
        # lower and upper ignored for now, just randomly concatenates texts
        import random
        auths = list(self.texts.keys())
        ptrs = [0] * len(auths)
        curtext = -1
        print("Generating text...")
        while any(x < len(self.texts[auths[i]]) for i, x in enumerate(ptrs)):
            curauth_idx = random.randint(0, len(auths) - 1)
            curauth = auths[curauth_idx]
            runlength = random.randint(lower, upper)
            if ptrs[curauth_idx] >= len(self.texts[auths[curauth_idx]]):
                continue

            startptr = ptrs[curauth_idx]
            endptr = min(len(self.texts[curauth]), startptr + runlength)
            ptrs[curauth_idx] = endptr
            print("At author: %s, runlength: %d" % (curauth, endptr - startptr))

            new_text_sentences = self.texts[curauth][startptr:endptr]
            #print(new_text_sentences[0])
            #assert False
            new_text = ' '.join(new_text_sentences)
            text.add_sentences(curauth, new_text_sentences)
            metaFile += '%d,,, %d,,, %s\n' % (len(textFile), len(textFile) + len(new_text) - 1, curauth)
            textFile += new_text

        return textFile, metaFile, text

    def writeToFile(self, fname):
        with open(fname, 'wb') as f:
            import pickle
            pickle.dump(self, f)

    @staticmethod
    def loadFromFile(fname, verbose = False):
        with open(fname, 'rb') as f:
            import pickle
            textgen = pickle.load(f)
            textgen.Verbose = verbose
            return textgen

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--texts', help='paths to folder containing texts', required=True)
    parser.add_argument('-c', '--chunk', help='number of sentences per chunk, as -c <size> or -c <lower> <upper> for random values between a range', required=True, nargs = '*')
    parser.add_argument('-oth', '--hrtxt', help='output human-readable text file', required=False)
    parser.add_argument('-omh', '--hrmeta', help='output human-readable metadata file', required=False)
    parser.add_argument('-opick', '--pickletext', help='output file for pickled Text object', required=True)
    parser.add_argument('-ogenpick', '--generatorpickle', help='output file for pickled text generator', required=False)
    args = parser.parse_args()

    tm = None
    if args.generatorpickle and os.path.exists(args.generatorpickle):
        tm = TextMerger.loadFromFile(args.generatorpickle, verbose = True)
    else:
        tm = TextMerger(verbose=True)
        for subdir, dirs, files in os.walk(args.texts):
            if not files:
                print("\tSkipping: %s" % subdir)
                continue
            print("\t%s" % subdir)
            author = os.path.split(subdir)[-1]
            print('\n\nAuthor: ', author)
            count = 0
            for f in files:
                # print('Text: ', f)
                if f.lower() == '.DS_Store'.lower():
                    print('Ignoring %s' % f)
                    continue

                with open(os.path.join(subdir, f), encoding='utf-8') as fin:
                    contents = ''.join(fin.readlines())
                    if contents.strip():
                        tm.addText(author, contents)
                        count += 1
                    else:
                        print("Skipping empty file: ", os.path.join(subdir, f))
                    # print(author, '\n', contents)
            #print(tm.texts)
            print("\t\tRead %d texts for author." % count)

        if(args.generatorpickle):
            tm.writeToFile(args.generatorpickle)

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

    print("Parsing sentences...")
    text.cacheWords()
    print("Done parsing sentences...")
    text.writeToFile(args.pickletext)

main()
