from __future__ import division

class ClusterEvaluator:
    def __init__(self, verbose = False):
        self.Verbose = verbose
        return

    def evaluatePurity(self, clusters, text):
        #print(type(text))
        '''
        Calculates purity for each cluster
        :param: clusters -> return list from authorCluster
        :param: text: Text object containing sentence/author data
        :return: tuple (list of cluster majority authors, list of cluster purity values)
        '''

        # count author classes in cluster
        cluster_class_counts = {}
        for i, clus in enumerate(clusters):
            cluster_class_counts[i] = {}
            for sent in clus:
                #cur_class = sent.auth #TODO obtain author class from cur sentence
                author_index = text.getAuthorIndexForSentence(sent)
                if author_index not in cluster_class_counts[i]:
                    cluster_class_counts[i][author_index] = 0
                cluster_class_counts[i][author_index] += 1

        clusterMajorityAuthorIndices = []
        clusterPurities = []
        # assign majority class label to cluster
        for clusterIdx, class_counts in cluster_class_counts.items():
            total_count = sum(class_counts.values())
            majority_class = max(class_counts, key = lambda k: class_counts[k])
            majority_count = class_counts[majority_class]
            class_purity = majority_count/total_count
            clusterMajorityAuthorIndices.append(majority_class)
            clusterPurities.append(class_purity)

        return clusterMajorityAuthorIndices, clusterPurities
