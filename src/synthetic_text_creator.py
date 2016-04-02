import os

class TextMerger(object):
    def __init__(self, debug = False):
        self.debug = debug
        self.texts = []

    def addText(self, textPath):
        with open(textPath, 'rt') as f:
            self.texts.append(f.readall())

    def generateText(self, lower, upper):
        return None, None #TODO

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--texts', help='paths to texts', required=True, nargs = '*')
    parser.add_argument('-c', '--chunk', help='chunk size, as -c <size> or -c <lower> <upper> for random values between a range', required=True, nargs = '*')
    parser.add_argument('-ot', '--outputtextfile', help='output text file', required=True)
    parser.add_argument('-om', '--outputmetafile', help='output metadata file', required=True)
    args = parser.parse_args()

    tm = TextMerger()
    for t in args.texts:
        tm.addText(t)
    if len(args.chunk) == 1:
        textFile, metaFile = tm.generateText(args.chunk[0], args.chunk[0])
    else:
        textFile, metaFile = tm.generateText(args.chunk[0], args.chunk[1])

    with open(args.outputtextfile, 'w') as f: # TODO
        f.write('\n')

main()
