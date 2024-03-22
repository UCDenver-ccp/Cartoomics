from inputs import *
from create_graph import create_graph
from assign_nodes import *
from evaluation import *
from create_subgraph import compare_subgraph_guiding_terms
from graph_embeddings import Embeddings
from evaluation_plots_all import visualize_graph_similarity_metrics,visualize_graph_node_percentage_metrics,edge_type_comparison_visualization,intermediate_nodes_comparison_visualization

from wikipathways_converter import get_wikipathways_list
from graph_similarity_metrics import *
from constants import (
    WIKIPATHWAYS_SUBFOLDER
)

def main():

    #python wikipathways_graph_evaluations.py --knowledge-graph pkl --input-type annotated_diagram --wikipathways "['WP4565']" --enable-skipping True

    kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping = generate_graphsim_arguments()

    #ablation = 'true'
    ablation = 'false'

    input_dir = os.getcwd() + '/' + WIKIPATHWAYS_SUBFOLDER

    triples_list_file,labels_file = get_wikipathways_graph_files(input_dir,kg_type,input_type,guiding_term,input_substring)

    print("Creating knowledge graph object from inputs.....")

    g = create_graph(triples_list_file,labels_file, kg_type)

    wikipathways = get_wikipathways_list(wikipathways,pfocr_urls,pfocr_urls_file)

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    if ablation == 'true':

        all_wikipathways_dir = all_wikipathways_dir + '_ablations'

    #List for all graph similarity metrics
    graph_similarity_metrics = []
    #List for all graph node percentage metrics
    graph_node_percentage_metrics = []
    
    edge_types_df = pd.DataFrame()
    intermediate_nodes_df = pd.DataFrame()

    for wikipathway in wikipathways:

        if ablation == 'true':

            wikipathway = wikipathway + '_ablation_0'
       
        output_dir = all_wikipathways_dir + '/' + wikipathway + '_output'


        if cosine_similarity == 'true':

            #Get graph similarity metrics
            graph_similarity_metrics = generate_graph_similarity_metrics(graph_similarity_metrics,wikipathway,'CosineSimilarity',all_wikipathways_dir)

            #Get node and edge type metrics
            input_nodes,subgraph_cs,cs_noa_df,path_total_cs = get_subgraph_dfs(output_dir,'annotated_diagram','CosineSimilarity')
            edge_types_df = edge_type_comparison(edge_types_df,wikipathway,CosineSimilarity=subgraph_cs)
            intermediate_nodes_df = intermediate_nodes_comparison(intermediate_nodes_df,g.labels_all,kg_type,wikipathway,subgraph_cs,CosineSimilarity=cs_noa_df)

            #Get node percentage metrics
            graph_node_percentage_metrics = generate_graph_mapping_statistics(graph_node_percentage_metrics,wikipathway,'CosineSimilarity',all_wikipathways_dir)

        if pdp == 'true':

            #Get graph similarity metrics
            graph_similarity_metrics = generate_graph_similarity_metrics(graph_similarity_metrics,wikipathway,'PDP',all_wikipathways_dir)

            #Get node and edge type metrics
            input_nodes,subgraph_pdp,pdp_noa_df,path_pdp = get_subgraph_dfs(output_dir,'annotated_diagram','PDP')
            edge_types_df = edge_type_comparison(edge_types_df,wikipathway,PDP=subgraph_pdp)
            intermediate_nodes_df = intermediate_nodes_comparison(intermediate_nodes_df,g.labels_all,kg_type,wikipathway,subgraph_pdp,PDP=pdp_noa_df)

            #Get node percentage metrics
            graph_node_percentage_metrics = generate_graph_mapping_statistics(graph_node_percentage_metrics,wikipathway,'PDP',all_wikipathways_dir)


    #Output files and visualization for graph similarity metrics
    graph_similarity_results_file = output_graph_similarity_metrics(all_wikipathways_dir,graph_similarity_metrics)
    visualize_graph_similarity_metrics(graph_similarity_results_file,all_wikipathways_dir)

    #Output files and visualization for graph node percentage metrics
    graph_node_percentage_results_file = output_graph_node_percentage_metrics(all_wikipathways_dir,graph_node_percentage_metrics)
    visualize_graph_node_percentage_metrics(graph_node_percentage_results_file,all_wikipathways_dir)

    ##FOr testing
    ##all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER
    ##edge_types_df = pd.read_csv('/Users/brooksantangelo/Documents/HunterLab/Cartoomics/git/Cartoomics/wikipathways_graphs/node_edge_evaluation/edge_type_comparison.csv',sep=',')
    ##intermediate_nodes_df = pd.read_csv('/Users/brooksantangelo/Documents/HunterLab/Cartoomics/git/Cartoomics/wikipathways_graphs/node_edge_evaluation/intermediate_nodes_comparison.csv',sep=',')

    #Output files and visualization for edge and node type evaluations
    output_node_edge_type_file(all_wikipathways_dir,edge_types_df,'edge_type_comparison')
    output_node_edge_type_file(all_wikipathways_dir,intermediate_nodes_df,'intermediate_nodes_comparison')
    edge_type_comparison_visualization(all_wikipathways_dir,edge_types_df)
    intermediate_nodes_comparison_visualization(all_wikipathways_dir,intermediate_nodes_df)

if __name__ == '__main__':
    main()



