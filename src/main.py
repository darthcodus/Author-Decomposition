from authorclustering.multi_author_text import Text
from authorclustering.authorcluster import AuthorCluster
from authorclustering.clusterEvaluator import ClusterEvaluator


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-pt','--pickledtext', help='path to a pickled text object', required=True)
    parser.add_argument('-nc', '--numclusters', help='number of author clusters', required=True)
    parser.add_argument('-chunk', '--chunksize', help='number of sentences per chunk', required=False, default = 20)
    parser.add_argument('-op', '--outputfile', help='number of sentences per chunk', required=False, default = 'cluster_evaluation_output.txt')
    args = parser.parse_args()
    text = Text.loadFromFile(args.pickledtext)
    nc = args.numclusters

    ac = AuthorCluster()
    ce = ClusterEvaluator()
    clusters = ac.cluster(text, int(args.chunksize), int(nc))

    clusterMajorityAuthorIndices, clusterPurities = ce.evaluatePurity(clusters, text)
    assert len(clusterMajorityAuthorIndices) == len(clusterPurities)
    with open(args.outputfile, "w") as fout:
        for clusterIdx in range(0, len(clusterMajorityAuthorIndices)):
            majority_class = clusterMajorityAuthorIndices[clusterIdx]
            class_purity = clusterPurities[clusterIdx]
            fout.write("Cluster {0}: authorIdx = {1}, purity = {2}\n".format(str(clusterIdx), str(majority_class), str(class_purity)))
            print("Cluster {0}: authorIdx = {1}, purity = {2}\n".format(str(clusterIdx), str(majority_class), str(class_purity)))

main()
