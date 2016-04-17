from __future__ import division
import os
import sys
import string
import math
import re
reload(sys)
sys.setdefaultencoding('UTF8')

class ClusterEvaluator:
    def __init__(self):


    def evaluatePurity(self, clusters, text):
        '''
        Calculates purity for each cluster
        param: clusters -> return list from authorCluster
        text: pickledText containing sentence/author data
        '''
        out_text = open('cluster_evaluation_output.txt', "w")
        #count author classes in cluster
        cluster_class_counts = {}
        for clus in clusters:
            for sent in clus:
                #cur_class = sent.auth #TODO obtain author class from cur sentence
                author_index = text.getAuthorIndexforSentence(sent)
                if clus not in cluster_class_counts:
                    cluster_class_counts[clus] = {}
                if author_index not in cluster_class_counts[clus]:
                    cluster_class_counts[clus][author_index] = 1
                cluster_class_counts[clus][author_index] = cluster_class_counts[clus][author_index] + 1

        cluster_labels = {}

        #assign majority class label to cluster
        for cluster, class_counts in cluster_class_counts.iteritems():
            total_count=0;
            majority_count = 0;
            majority_class = '';
            for cur_class, count in class_counts.iteritems():
                if majority_count < count:
                    majority_count = count;
                    majority_class = cur_class;

                total_count = total_count+count

            class_purity = majority_count/total_count

            out_text.write("Cluster {0}: authorIdx = {1}, purity = {2}\n".format(str(cluster), str(majority_class), str(purity)))


if __name__ == '__main__':
    main()
