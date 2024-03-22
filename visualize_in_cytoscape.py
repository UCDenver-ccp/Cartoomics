from inputs import *
import os
from wikipathways_converter import get_wikipathways_list
from visualize_subgraph import create_cytoscape_png
from tqdm import tqdm
from graph_similarity_metrics import generate_graphsim_arguments

from constants import (
    ALL_WIKIPATHWAYS,
    WIKIPATHWAYS_SUBFOLDER
)


#Have Cytoscape running, will only output png of subgraph(s) when subgraph.csv and subgraph_attributions.noa exist
def main():

    kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping = generate_graphsim_arguments()

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    wikipathways = get_wikipathways_list(wikipathways,pfocr_urls,pfocr_urls_file)

    for wikipathway in tqdm(wikipathways):

        output_dir = all_wikipathways_dir + '/' + wikipathway + '_output'

        s = pd.read_csv(output_dir + '/_annotated_diagram_Input_Nodes_.csv',sep='|')

        if cosine_similarity == 'true':

            subgraph_df = pd.read_csv(output_dir + '/CosineSimilarity/Subgraph.csv',sep='|')

            subgraph_attributes_df = pd.read_csv(output_dir + '/CosineSimilarity/Subgraph_attributes.noa',sep='|')

            create_cytoscape_png(subgraph_df,subgraph_attributes_df,output_dir+'/CosineSimilarity')

        if pdp == 'true':

            subgraph_df = pd.read_csv(output_dir + '/PDP/Subgraph.csv',sep='|')

            subgraph_attributes_df = pd.read_csv(output_dir + '/PDP/Subgraph_attributes.noa',sep='|')

            create_cytoscape_png(subgraph_df,subgraph_attributes_df,output_dir+'/PDP')


if __name__ == '__main__':
    main()