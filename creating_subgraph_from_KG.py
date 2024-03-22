from inputs import *
from create_graph import create_graph
from create_graph import kg_to_undirected_networkx
from assign_nodes import interactive_search_wrapper, skip_self_loops
from create_subgraph import subgraph_prioritized_path_cs
from create_subgraph import subgraph_prioritized_path_pdp
from create_subgraph import  subgraph_prioritized_path_guiding_term
from create_subgraph import user_defined_edge_exclusion,automatic_defined_edge_exclusion
from visualize_subgraph import output_visualization
from evaluation import *
from tqdm import tqdm
from memory_management import *
import networkx

def main():

    #limit_memory(percentage = 0.5)
    
    input_dir,output_dir,kg_type,embedding_dimensions,weights,search_type,pdp_weight,input_type,pfocr_url,cosine_similarity,pdp,guiding_term,input_substring,enable_skipping = generate_arguments()

    triples_list_file,labels_file,input_file = get_graph_files(input_dir,output_dir, kg_type,input_type,pfocr_url,guiding_term,input_substring)

    print("Creating knowledge graph object from inputs.....")

    g = create_graph(triples_list_file,labels_file, kg_type)
    
    print("Mapping between user inputs and KG nodes.......")
    
    #Somehow not outputting original labels########
    s = interactive_search_wrapper(g, input_file, output_dir, input_type,kg_type,enable_skipping)

    print(s)

    #For skipping self loops
    s = skip_self_loops(s)


    if guiding_term:

        guiding_term_df = interactive_search_wrapper(g, input_file, output_dir, 'guiding_term', kg_type, enable_skipping, input_dir)

    print("Mapping complete")

    if weights == True:
        #g = user_defined_edge_exclusion(g,kg_type)
        g = automatic_defined_edge_exclusion(g,kg_type)

    networkx_g = kg_to_undirected_networkx(g)
    
    if cosine_similarity == 'true':
        print("Finding subgraph using user input and KG embeddings for Cosine Similarity......")

        #Returns list of all chosen paths for subgraph as all_chosen_path_nodes
        subgraph_cs,all_paths_cs_values,all_chosen_path_nodes = subgraph_prioritized_path_cs(s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,triples_list_file,output_dir,input_dir,embedding_dimensions,kg_type,networkx_g)


        print("Outputting CS visualization......")

        cs_noa_df = output_visualization(s,subgraph_cs,output_dir+'/CosineSimilarity')

    if pdp == 'true':

        print("Finding subgraph using user input for PDP......")

        #Don't need to find shortest paths again if already run for cosine similarity
        if cosine_similarity == 'true':

            print('pdp and cosine true')

            subgraph_pdp,path_pdp,all_chosen_path_nodes = subgraph_prioritized_path_pdp(s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,pdp_weight,output_dir,kg_type,networkx_g,all_chosen_path_nodes)
    
        else:

            subgraph_pdp,path_pdp,all_chosen_path_nodes = subgraph_prioritized_path_pdp(s,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,pdp_weight,output_dir,kg_type,networkx_g)

        print("Outputting PDP visualization......")

        pdp_noa_df = output_visualization(s,subgraph_pdp,output_dir+'/PDP')

    if guiding_term:
        print("Finding subgraph using user input for Guiding Term(s)......")

        for t in tqdm(range(len(guiding_term_df))):
            term_row = guiding_term_df.iloc[t]

            #Don't need to find shortest paths again if already run for cosine similarity
            if cosine_similarity == 'true' or pdp == 'true':

                subgraph_guiding_term,all_paths_cs_values,output_foldername = subgraph_prioritized_path_guiding_term(s,term_row,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,triples_list_file,output_dir,input_dir,embedding_dimensions,kg_type,networkx_g,all_chosen_path_nodes)

            else:

                subgraph_guiding_term,all_paths_cs_values,output_foldername = subgraph_prioritized_path_guiding_term(s,term_row,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,triples_list_file,output_dir,input_dir,embedding_dimensions,kg_type,networkx_g)


            print("Outputting Guiding Term(s) visualization......")

            pdp_noa_df = output_visualization(s,subgraph_guiding_term,output_dir+'/'+output_foldername)


if __name__ == '__main__':
    main()
