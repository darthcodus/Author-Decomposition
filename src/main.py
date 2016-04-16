from multi_author_text import Text

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-pt','--pickledtext', help='path to a pickled text object', required=True)
    parser.add_argument('-nc', '--numclusters', help='number of author clusters', required=True)
    args = parser.parse_args()
    text = Text.loadFromFile(args.pickledtext)

main()
