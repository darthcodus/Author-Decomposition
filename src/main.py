from authorclustering.multi_author_text import Text
from authorclustering.authorcluster import AuthorCluster
from authorclustering.clusterEvaluator import ClusterEvaluator


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-pt','--pickledtext', help='path to a pickled text object', required=True)
    parser.add_argument('-nc', '--numclusters', help='number of author clusters', required=True)
    args = parser.parse_args()
    text = Text.loadFromFile(args.pickledtext)
    nc = args.numclusters

    ac = AuthorCluster()
    ce = ClusterEvaluator()
    clusters = ac.cluster(20, int(nc), text)

    ce.evaluatePurity(clusters)


main()
