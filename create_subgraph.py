# Given a starting graph of node pairs, find all paths between them to create a subgraph
from find_path import find_shortest_path,find_shortest_path_pattern
from find_path import prioritize_path_cs,prioritize_path_pdp
from find_path import calculate_paths_cosine_sim,generate_comparison_terms_dict
import pandas as pd
from tqdm import tqdm
from evaluation import output_path_lists
from evaluation import output_num_paths_pairs
from igraph import * 

def subgraph_shortest_path(input_nodes_df,graph,g_nodes,labels_all,triples_df,weights,search_type):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    for i in range(len(input_nodes_df)):
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        shortest_path_df = find_shortest_path(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type)
        all_paths.append(shortest_path_df)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S','P','O'])

    return df

def subgraph_shortest_path_pattern(input_nodes_df,graph,g_nodes,labels_all,triples_df,weights,search_type,kg_type,manually_chosen_uris):

    input_nodes_df.columns = input_nodes_df.columns.str.lower()

    all_paths = []

    for i in range(len(input_nodes_df)):
        start_node = input_nodes_df.iloc[i].loc['source']
        end_node = input_nodes_df.iloc[i].loc['target']
        shortest_path_df,manually_chosen_uris = find_shortest_path_pattern(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type,kg_type,input_nodes_df,manually_chosen_uris)
        if len(shortest_path_df) > 0:
            all_paths.append(shortest_path_df)

    if len(all_paths) > 0:
        df = pd.concat(all_paths)
        df.reset_index(drop=True, inplace=True)
        #Remove duplicate edges
        df = df.drop_duplicates(subset=['S','P','O'])

    else:
        df = pd.DataFrame()

    return df,manually_chosen_uris

# Have user define weights to upweight
def user_defined_edge_weights(graph, triples_df,kg_type ):
    if kg_type == 'pkl':
        edges = graph.labels_all[graph.labels_all['entity_type'] == 'RELATIONS'].label.tolist()
        print("### Unique Edges in Knowledge Graph ###")
        print('\n'.join(edges))
        still_adding = True
        to_weight= []
        print('\n')
        print('Input the edges to avoid in the path search (if possible). When finished input "Done."')
        while(still_adding):
            user_input = input('Edge or "Done": ')
            if user_input == 'Done':
                still_adding = False
            else:
                to_weight.append(user_input)
        to_weight = graph.labels_all[graph.labels_all['label'].isin(to_weight)]['entity_uri'].tolist()

    if kg_type == 'kg-covid19':
        edges = set(list(graph.igraph.es['predicate']))
        print("### Unique Edges in Knowledge Graph ###")
        print('\n'.join(edges))
        still_adding = True
        to_weight= []
        print('\n')
        print('Input the edges to avoid in the path search (if possible). When finished input "Done"')
        while(still_adding):
            user_input = input('Edge or "Done"')
            if user_input == 'Done':
                still_adding = False
            else:
                to_weight.append(user_input)

    edges= graph.igraph.es['predicate']
    graph.igraph.es['weight'] = [10 if x in to_weight else 1 for x in edges]
    return(graph)

# Have user define weights to upweight
def user_defined_edge_exclusion(graph,kg_type ):
    if kg_type == 'pkl':
        edges = graph.labels_all[graph.labels_all['entity_type'] == 'RELATIONS'].label.tolist()
        print("### Unique Edges in Knowledge Graph ###")
        print('\n'.join(edges))
        still_adding = True
        to_drop= []
        print('\n')
        print('Input the edges to avoid in the path search (if possible). When finished input "Done."')
        while(still_adding):
            user_input = input('Edge or "Done": ')
            if user_input == 'Done':
                still_adding = False
            else:
                to_drop.append(user_input)
        to_drop = graph.labels_all[graph.labels_all['label'].isin(to_drop)]['entity_uri'].tolist()
        
    if kg_type == 'kg-covid19':
        edges = set(list(graph.igraph.es['predicate']))
        print("### Unique Edges in Knowledge Graph ###")
        print('\n'.join(edges))
        still_adding = True
        to_drop= []
        print('\n')
        print('Input the edges to avoid in the path search (if possible). When finished input "Done"')
        while(still_adding):
            user_input = input('Edge or "Done"')
            if user_input == 'Done':
                still_adding = False
            else:
                to_drop.append(user_input)
    for edge in to_drop:
        graph.igraph.delete_edges(graph.igraph.es.select(predicate = edge))
    return(graph)


# Edges to remove
def automatic_defined_edge_exclusion(graph,kg_type):
    if kg_type == 'pkl':
        to_drop = ['http://purl.obolibrary.org/obo/RO_0002160','http://purl.obolibrary.org/obo/BFO_0000050','http://www.w3.org/1999/02/22-rdf-syntax-ns#type','http://purl.obolibrary.org/obo/RO_0001025','http://purl.obolibrary.org/obo/RO_0000087']
    if kg_type != 'pkl':
        to_drop = ['biolink:category','biolink:in_taxon']
    for edge in to_drop:
        graph.igraph.delete_edges(graph.igraph.es.select(predicate = edge))
    return(graph)

    
def subgraph_prioritized_path_cs(input_nodes_df,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,output_dir,input_dir,embedding_dimensions,kg_type,find_graph_similarity = False):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    num_paths_df = pd.DataFrame(columns = ['source_node','target_node','num_paths'])

    #List of all chosen paths for subgraph
    all_chosen_path_nodes = []

    for i in tqdm(range(len(input_nodes_df))):
        df_paths = pd.DataFrame()
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        node_pair = input_nodes_df.iloc[i]
        path_nodes,cs_shortest_path_df,all_paths_cs_values,chosen_path_nodes_cs = prioritize_path_cs(input_nodes_df,node_pair,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,input_dir,embedding_dimensions,kg_type)
        all_paths.append(cs_shortest_path_df)
        df_paths['source_node'] = [start_node]
        df_paths['target_node'] = [end_node]
        df_paths['num_paths'] = [len(path_nodes)]
        num_paths_df = pd.concat([num_paths_df,df_paths],axis=0)
        #Output path list to file where index will match the pair# in the _Input_Nodes_.csv
        #Get sum of all cosine values in value_list
        path_list = list(map(sum, all_paths_cs_values))
        output_path_lists(output_dir,path_list,'CosineSimilarity',i)
        all_chosen_path_nodes.append(chosen_path_nodes_cs)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S','P','O'])

    output_num_paths_pairs(output_dir,num_paths_df,'CosineSimilarity')

    return df,all_paths_cs_values,all_chosen_path_nodes

def subgraph_prioritized_path_pdp(input_nodes_df,graph,g_nodes,labels_all,triples_df,weights,search_type,pdp_weight,output_dir, kg_type):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    num_paths_df = pd.DataFrame(columns = ['source_node','target_node','num_paths'])

    #List of all chosen paths for subgraph
    all_chosen_path_nodes = []

    for i in tqdm(range(len(input_nodes_df))):
        df_paths = pd.DataFrame()
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        node_pair = input_nodes_df.iloc[i]
        path_nodes,pdp_shortest_path_df,paths_pdp,chosen_path_nodes_pdp = prioritize_path_pdp(input_nodes_df,node_pair,graph,g_nodes,labels_all,triples_df,weights,search_type,pdp_weight,kg_type)
        all_paths.append(pdp_shortest_path_df)
        df_paths['source_node'] = [start_node]
        df_paths['target_node'] = [end_node]
        df_paths['num_paths'] = [len(path_nodes)]
        num_paths_df = pd.concat([num_paths_df,df_paths],axis=0)
        #Output path list to file where index will match the pair# in the _Input_Nodes_.csv
        output_path_lists(output_dir,paths_pdp,'PDP',i)
        all_chosen_path_nodes.append(chosen_path_nodes_pdp)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S','P','O'])

    output_num_paths_pairs(output_dir,num_paths_df,'PDP')

    return df,paths_pdp,all_chosen_path_nodes

def subgraph_prioritized_path_guiding_term(input_nodes_df,term_row,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,output_dir,input_dir,embedding_dimensions,kg_type):

    input_nodes_df.columns= input_nodes_df.columns.str.lower()

    all_paths = []

    num_paths_df = pd.DataFrame(columns = ['source_node','target_node','num_paths'])

    term_foldername = 'Guiding_Term_'+term_row['term_label'].replace(" ","_").replace(".","_").replace(":","_").replace("'",'')
    for i in tqdm(range(len(input_nodes_df))):
        df_paths = pd.DataFrame()
        start_node = input_nodes_df.iloc[i].loc['source_label']
        end_node = input_nodes_df.iloc[i].loc['target_label']
        node_pair = input_nodes_df.iloc[i]
        path_nodes,cs_shortest_path_df,all_paths_cs_values,chosen_path_nodes_cs = prioritize_path_cs(input_nodes_df,node_pair,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,input_dir,embedding_dimensions,kg_type,term_row)
        all_paths.append(cs_shortest_path_df)
        df_paths['source_node'] = [start_node]
        df_paths['target_node'] = [end_node]
        df_paths['num_paths'] = [len(path_nodes)]
        num_paths_df = pd.concat([num_paths_df,df_paths],axis=0)
        #Output path list to file where index will match the pair# in the _Input_Nodes_.csv
        #Get sum of all cosine values in value_list
        path_list = list(map(sum, all_paths_cs_values))
        output_path_lists(output_dir,path_list,term_foldername,i)

    df = pd.concat(all_paths)
    df.reset_index(drop=True, inplace=True)
    #Remove duplicate edges
    df = df.drop_duplicates(subset=['S','P','O'])

    output_num_paths_pairs(output_dir,num_paths_df,term_foldername)

    return df,all_paths_cs_values,term_foldername

def compare_paths_guiding_terms(s,all_chosen_path_nodes,g, output_dir, comparison_terms_df,weights,search_type,triples_list_file,input_dir,embedding_dimensions,kg_type):

    #List of all average cosine similarity values for each path in subgraph to the given term
    all_avg_paths_cosine_sim = []

    #Get chosen path to calculate cosine values
    for t in tqdm(range(len(comparison_terms_df))):
        term_row = comparison_terms_df.iloc[t]
        avg_paths_cosine_sim = calculate_paths_cosine_sim(s,all_chosen_path_nodes,term_row,g.igraph,g.igraph_nodes,g.labels_all,g.edgelist,weights,search_type,triples_list_file,output_dir,input_dir,embedding_dimensions,kg_type)

        #Organize all path cosine similarity values into dictionary per term
        all_avg_paths_cosine_sim = generate_comparison_terms_dict(all_avg_paths_cosine_sim,term_row,avg_paths_cosine_sim)

    return all_avg_paths_cosine_sim


