import os
import pickle

class TextMerger(object):
    def __init__(self, debug = False):
        self.debug = debug
        self.texts = []

    def addText(self, author, text):
        text = {}
        self.texts.append(text)
        text['author'] = author
        text['text'] = text

    def textsByAuthor(self, author):
        return filter(lambda x: x['author'].lower() is author.lower(), self.texts)

    def generateText(self, lower, upper):
        textFile = ""
        metaFile = ""
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

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--texts', help='paths to folder containing texts', required=True)
    parser.add_argument('-c', '--chunk', help='number of sentences per chunk, as -c <size> or -c <lower> <upper> for random values between a range, or 0 to simply randomly join the texts', required=True, nargs = '*')
    parser.add_argument('-ot', '--outputtextfile', help='output binary (pickle) file containing text', required=True)
    parser.add_argument('-om', '--outputmetafile', help='output binary file containing metadata', required=True)
    parser.add_argument('-oth', '--hrtxt', help='output human-readable text file', required=False)
    parser.add_argument('-omh', '--hrmeta', help='output human-readable metadata file', required=False)
    args = parser.parse_args()

    tm = TextMerger()
    for subdir, dirs, files in os.walk(args.texts):
        if not files:
            print("\tSkipping: %s" % subdir)
            continue
        print("\t%s" % subdir)
        author = os.path.split(subdir)[-1]
        print('Author: ', author)
        for f in files:
            print('Text: ', file)
            with open(os.path.join(subdir, f), encoding='utf-8') as fin:
                contents = fin.readlines()
                tm.addText(author, contents)
            print("\t\tRead %d texts for author." % len(tm.textsByAuthor(author)))

    if len(args.chunk) == 1:
        textFile, metaFile = tm.generateText(args.chunk[0], args.chunk[0])
    else:
        textFile, metaFile = tm.generateText(args.chunk[0], args.chunk[1])

    with open(args.outputtextfile, 'wb') as f:
        pickle.dump(textFile, f)
        print("Saved to pickle file", args.outputtextfile)

    with open(args.outputmetafile, 'wb') as f:
        pickle.dump(metaFile, f)
        print("Saved to pickle file", args.outputmetafile)

    with open(args.hrtxt, 'wt') as f:
        f.write(textFile)
    with open(args.hrmeta, 'wt') as f:
        f.write(metaFile)

main()
