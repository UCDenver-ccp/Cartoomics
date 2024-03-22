



from igraph import *
import pandas as pd
import networkx as nx
import os
import matplotlib.pyplot as plt
from graph_similarity_metrics import *
import argparse
import ast
import csv

from wikipathways_converter import get_wikipathways_list
from graph_similarity_metrics import *
from constants import (
    WIKIPATHWAYS_SUBFOLDER
)

#python compare_subgraphs.py --knowledge-graph pkl --input-type annotated_diagram --wikipathways "['WP4829','WP5372','WP5283']" --enable-skipping True

def main():

    kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping = generate_graphsim_arguments()

    wikipathways = get_wikipathways_list(wikipathways,pfocr_urls,pfocr_urls_file)

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    subgraph_types = []
    results_fields = ['SubgraphType','Pathway','Metric','Score']
    results_file = all_wikipathways_dir + '/Graph_Similarity_Metrics.csv'
    with open(results_file, 'w') as f:
        write = csv.writer(f)
        write.writerow(results_fields)

    for wikipathway in wikipathways:

        #Generates subgraphs of wikipathways graphs once edgelists are already downloaded into corresponding folder wikipathways_graphs/<p>
        if cosine_similarity == 'true': 
            subgraph_types.append('CosineSimilarity')
        if pdp == 'true':
            subgraph_types.append('PDP')
        if guiding_term:
            subgraph_types.append('GuidingTerm_'+guiding_term)

        for algorithm in subgraph_types:
            wikipathways_graph,cartoomics_graph = prepare_subgraphs(wikipathway,algorithm,all_wikipathways_dir)
            all_metrics = []
            all_metrics.append([algorithm,wikipathway,'Jaccard',jaccard_similarity(wikipathways_graph,cartoomics_graph)])
            all_metrics.append([algorithm,wikipathway,'Overlap',overlap_metric(wikipathways_graph,cartoomics_graph)])
            #Graph edit distance not supported yet
            #all_metrics.append([algorithm,wikipathway,'EditDistance',edit_distance_metric(wikipathways_graph,cartoomics_graph)])

            with open(results_file, 'a') as f:
                write = csv.writer(f)
                write.writerows(all_metrics) 

            visualize_graph_metrics(results_file,all_wikipathways_dir,algorithm)

if __name__ == '__main__':
    main()