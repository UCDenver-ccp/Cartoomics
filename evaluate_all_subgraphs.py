from inputs import *
from create_graph import create_graph
from assign_nodes import *
from evaluation import *

from wikipathways_converter import get_wikipathways_list
from graph_similarity_metrics import *
from constants import (
    WIKIPATHWAYS_SUBFOLDER
)

def main():

    #python wikipathways_converter.py --knowledge-graph pkl --input-type annotated_diagram --pfocr-urls-file True --enable-skipping True

    kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping = generate_graphsim_arguments()

    input_dir = os.getcwd() + '/' + WIKIPATHWAYS_SUBFOLDER

    triples_list_file,labels_file = get_wikipathways_graph_files(input_dir,kg_type,input_type,guiding_term,input_substring)

    print("Creating knowledge graph object from inputs.....")

    g = create_graph(triples_list_file,labels_file, kg_type)

    wikipathways = get_wikipathways_list(wikipathways,pfocr_urls,pfocr_urls_file)

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    for wikipathway in wikipathways:

        output_dir = all_wikipathways_dir + '/' + wikipathway + '_output'

        print("Outputting Evaluation......")

        input_nodes,subgraph_cs,cs_noa_df,path_total_cs = get_subgraph_dfs(output_dir,'annotated_diagram','CosineSimilarity')
        input_nodes,subgraph_pdp,pdp_noa_df,path_pdp = get_subgraph_dfs(output_dir,'annotated_diagram','PDP')

        '''ranked_prioritization_df = ranked_comparison(output_dir=output_dir,cs=path_total_cs,pdp=path_pdp)

        path_length_df = path_length_comparison(output_dir,input_nodes,g.labels_all,search_type,cs=subgraph_cs,pdp=subgraph_pdp)

        num_nodes_df = num_nodes_comparison(output_dir=output_dir,cs=subgraph_cs,pdp=subgraph_pdp)'''

        edge_types_df = edge_type_comparison(output_dir=output_dir,cs=subgraph_cs,pdp=subgraph_pdp)

        intermediate_nodes_df = intermediate_nodes_comparison(output_dir,g.labels_all,kg_type,cs=cs_noa_df,pdp=pdp_noa_df)

if __name__ == '__main__':
    main()
