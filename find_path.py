from graph_embeddings import Embeddings
import numpy as np
import pandas as pd
from scipy import spatial
from scipy.spatial import distance
from collections import defaultdict
from assign_nodes import unique_nodes
import networkx
from functools import reduce
from operator import itemgetter


#Go from label to entity_uri (for PKL original labels file) or Label to Idenifier (for microbiome PKL)
# kg_type adds functionality for kg-covid19
def get_uri(labels,value, kg_type):

    if kg_type == 'pkl':
        uri = labels.loc[labels['label'] == value,'entity_uri'].values[0]
    if kg_type == 'kg-covid19':
        uri = labels.loc[labels['label'] == value,'id'].values[0]
    
        
    return uri

def get_label(labels,value,kg_type):
    if kg_type == 'pkl':
        label = labels.loc[labels['entity_uri'] == value,'label'].values[0]
    if kg_type == 'kg-covid19':
        label = labels.loc[labels['id'] == value,'label'].values[0]        
    return label



def get_key(dictionary,value):

    for key, val in dictionary.items():
        if val == value:
            return key

def define_path_triples(g_nodes,triples_df,path_nodes,search_type):

    #Dict to store all dataframes of shortest mechanisms for this node pair
    mechanism_dfs = {}

    #Keep track of # of mechanisms generated for this node pair in file name for all shortest paths
    count = 1 

    #When there is no connection in graph, path_nodes will equal 1 ([[]]) or when there's a self loop
    if len(path_nodes[0]) != 0:
        for p in range(len(path_nodes)):
            #Dataframe to append each triple to
            full_df = pd.DataFrame()
            n1 = g_nodes[path_nodes[p][0]]
            for i in range(1,len(path_nodes[p])):
                n2 = g_nodes[path_nodes[p][i]]
                if search_type.lower() == 'all':
                    #Try first direction which is n1 --> n2
                    df = triples_df.loc[(triples_df['subject'] == n1) & (triples_df['object'] == n2)]
                    full_df = pd.concat([full_df,df])
                    if len(df) == 0:
                        #If no results, try second direction which is n2 --> n1
                        df = triples_df.loc[(triples_df['object'] == n1) & (triples_df['subject'] == n2)]
                        full_df = pd.concat([full_df,df])
                elif search_type.lower() == 'out':
                    #Only try direction n1 --> n2
                    df = triples_df.loc[(triples_df['subject'] == n1) & (triples_df['object'] == n2)]
                    full_df = pd.concat([full_df,df])
                full_df = full_df.reset_index(drop=True)
                n1 = n2
                                        
            #For all shortest path search
            if len(path_nodes) > 1:
                #Generate df
                full_df.columns = ['S_ID','P_ID','O_ID']
                mechanism_dfs['mech#_'+str(count)] = full_df
                count += 1
                
            #For shortest path search
        if len(path_nodes) == 1:
            #Generate df
            full_df.columns = ['S_ID','P_ID','O_ID']
            return full_df

    #Return dictionary if all shortest paths search
    if len(path_nodes) > 1:
        return mechanism_dfs

def find_all_shortest_paths(node_pair,graph,g_nodes,labels_all,triples_df,weights,search_type, kg_type):

    try:
        if node_pair['source_id'] != 'not_needed':
            node1 = node_pair['source_id']
        else:
            node1 = get_uri(labels_all,node_pair['source_label'], kg_type)
    #Handle case where no ID was input for any nodes or only 1 node
    except KeyError: 
        node1 = get_uri(labels_all,node_pair['source_label'], kg_type)
   
    try:
        if node_pair['target_id'] != 'not_needed':
            node2 = node_pair['target_id']
        else:
            node2 = get_uri(labels_all,node_pair['target_label'], kg_type)
    #Handle case where no ID was input for any nodes or only 1 node
    except KeyError:
        node2 = get_uri(labels_all,node_pair['target_label'], kg_type)
    
    #Add weights if specified
    if weights:
        w = graph.es["weight"]
    else:
        w = None

    #Dict to store all dataframes of shortest mechanisms for this node pair
    mechanism_dfs = {}

    #list of nodes
    path_nodes = graph.get_all_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)
    
    #Remove duplicates for bidirectional nodes, only matters when search type=all for mode
    path_nodes = list(set(tuple(x) for x in path_nodes))
    path_nodes = [list(tup) for tup in path_nodes]
    path_nodes = sorted(path_nodes,key = itemgetter(1))

    #Dictionary of all triples that are shortest paths, not currently used
    #mechanism_dfs = define_path_triples(g_nodes,triples_df,path_nodes,search_type)
    
    return path_nodes


### networkx implementation of find all shortest paths. Still uses both graphs (3/21/24)(LG)

def find_all_shortest_paths_networkx(node_pair,graph,g_nodes,labels_all,triples_df,weights,search_type, kg_type, networkx_graph):

    try:
        if node_pair['source_id'] != 'not_needed':
            node1 = node_pair['source_id']
        else:
            node1 = get_uri(labels_all,node_pair['source_label'], kg_type)
    #Handle case where no ID was input for any nodes or only 1 node
    except KeyError: 
        node1 = get_uri(labels_all,node_pair['source_label'], kg_type)
   
    try:
        if node_pair['target_id'] != 'not_needed':
            node2 = node_pair['target_id']
        else:
            node2 = get_uri(labels_all,node_pair['target_label'], kg_type)
    #Handle case where no ID was input for any nodes or only 1 node
    except KeyError:
        node2 = get_uri(labels_all,node_pair['target_label'], kg_type)
    
    #Add weights if specified
    # if weights:
    #     w = graph.es["weight"]
    # else:
    #     w = None

    #Dict to store all dataframes of shortest mechanisms for this node pair
    mechanism_dfs = {}

    #list of nodes
    
    node1_nx = graph.vs.find(name = node1).index
    node2_nx = graph.vs.find(name = node2).index

    path_nodes = networkx.all_shortest_paths(networkx_graph,node1_nx,node2_nx)

    #Remove duplicates for bidirectional nodes, only matters when search type=all for mode
    path_nodes = list(set(tuple(x) for x in path_nodes))
    path_nodes = [list(tup) for tup in path_nodes]

    #Dictionary of all triples that are shortest paths, not currently used
    #mechanism_dfs = define_path_triples(g_nodes,triples_df,path_nodes,search_type)
    
    return path_nodes


def convert_path_nodes(path_node,entity_map):

    n = entity_map[path_node]

    return n

def get_embedding(emb,node):

    embedding_array = emb[str(node)]
    embedding_array = np.array(embedding_array)

    return embedding_array

def calc_cosine_sim(emb,entity_map,path_nodes,g_nodes,triples_df,search_type,labels_all,kg_type,guiding_term,input_nodes_df):

    #Set target embedding value to target node if no guiding term is provided
    if guiding_term.empty:
        n1 = g_nodes[path_nodes[0][len(path_nodes[0])-1]]  

    #Set target embedding value to guiding term if it exists
    else:
        try:
            n1 = guiding_term['term_id']
        except KeyError:
            n1 = get_uri(labels_all,guiding_term['term_label'], kg_type)

    n1_int = convert_path_nodes(n1,entity_map)
    target_emb = get_embedding(emb,n1_int)

    #Dict of all embeddings to reuse if they exist
    embeddings = defaultdict(list)

    #List of lists of cosine similarity for each node in paths of path_nodes, should be same length as path_nodes
    all_paths_cs_values = []

    for l in path_nodes:
        cs = []
        for i in range(0,len(l)-1):
            n1 = g_nodes[l[i]]
            n1_int = convert_path_nodes(n1,entity_map)
            if n1_int not in list(embeddings.keys()):
                e = get_embedding(emb,n1_int)
                embeddings[n1_int] = e
            else:
                embeddings[n1_int] = e
            cs.append(1 - spatial.distance.cosine(e,target_emb))
        all_paths_cs_values.append(cs)

    #Get sum of all cosine values in value_list
    value_list = list(map(sum, all_paths_cs_values))
    chosen_path_nodes_cs = select_max_path(value_list,path_nodes)

    #Will only return 1 dataframe
    df = define_path_triples(g_nodes,triples_df,chosen_path_nodes_cs,search_type)

    df = convert_to_labels(df,labels_all,kg_type,input_nodes_df)

    return df,all_paths_cs_values,chosen_path_nodes_cs[0]

def calc_cosine_sim_from_label_list(emb,entity_map,node_labels,annotated_nodes,labels_all,kg_type,embeddings,guiding_term):

    annotated_node_labels = unique_nodes(annotated_nodes[['source','target']])

    #Set target embedding value to guiding term if it exists
    try:
        n1 = guiding_term['term_id']
    except KeyError:
        n1 = get_uri(labels_all,guiding_term['term_label'], kg_type)

    #Dict of all embeddings to reuse if they exist
    #embeddings = defaultdict(list)

    n1_int = convert_path_nodes(n1,entity_map)
    if n1_int not in list(embeddings.keys()):
        target_emb= get_embedding(emb,n1_int)
        embeddings[n1_int] = target_emb
    else:
        target_emb = embeddings[n1_int]
    
    #List of lists of cosine similarity for each node in paths of path_nodes, should be same length as path_nodes
    all_paths_cs_values = []

    #Searches for cosine similarity between each node and the guiding term
    for node in node_labels:
        if node in annotated_node_labels:
            try:
                n1 = annotated_nodes.loc[annotated_nodes['source'] == node,'source_id'].values[0]
            except IndexError:
                n1 = annotated_nodes.loc[annotated_nodes['target'] == node,'target_id'].values[0]
        else:
            n1 = get_uri(labels_all,node, kg_type)
        n1_int = convert_path_nodes(n1,entity_map)
        if n1_int not in list(embeddings.keys()):
            e = get_embedding(emb,n1_int)
            embeddings[n1_int] = e
        else:
            e = embeddings[n1_int]
        cs = 1 - spatial.distance.cosine(e,target_emb)
        all_paths_cs_values.append(cs)

    #Calculate average cosine similarity to this guiding term for entire subgraph
    avg_cosine_sim = sum(all_paths_cs_values) / len(all_paths_cs_values)

    return avg_cosine_sim,embeddings

def calc_cosine_sim_from_uri_list(emb,entity_map,node_uris,labels_all,kg_type,embeddings,guiding_term):

    #Set target embedding value to guiding term if it exists
    try:
        n1 = guiding_term['term_id']
    except KeyError:
        n1 = get_uri(labels_all,guiding_term['term_label'], kg_type)
    
    #Dict of all embeddings to reuse if they exist
    #embeddings = defaultdict(list)

    n1_int = convert_path_nodes(n1,entity_map)
    if n1_int not in list(embeddings.keys()):
        target_emb= get_embedding(emb,n1_int)
        embeddings[n1_int] = target_emb
    else:
        target_emb = embeddings[n1_int]
    
    #List of lists of cosine similarity for each node in paths of path_nodes, should be same length as path_nodes
    all_paths_cs_values = []

    #Searches for cosine similarity between each node and the guiding term
    for n1 in node_uris:
        n1_int = convert_path_nodes(n1,entity_map)
        if n1_int not in list(embeddings.keys()):
            e = get_embedding(emb,n1_int)
            embeddings[n1_int] = e
        else:
            e = embeddings[n1_int]
        cs = 1 - spatial.distance.cosine(e,target_emb)
        all_paths_cs_values.append(cs)

    #Calculate average cosine similarity to this guiding term for entire subgraph
    avg_cosine_sim = sum(all_paths_cs_values) / len(all_paths_cs_values)

    return avg_cosine_sim,embeddings

def calc_pdp(path_nodes,graph,w,g_nodes,triples_df,search_type,labels_all,kg_type,input_nodes_df):

    #List of pdp for each path in path_nodes, should be same length as path_nodes
    #paths_pdp = []

    #List of lists of pdp for each node in paths of path_nodes, should be same length as path_nodes
    all_paths_pdp_values = []

    for l in path_nodes:
        pdp = 1
        for i in range(0,len(l)-1):
            dp = graph.degree(l[i],mode='all',loops=True)
            dp_damped = pow(dp,-w)
            pdp = pdp*dp_damped

        #paths_pdp.append(pdp)
        all_paths_pdp_values.append(pdp)

    chosen_path_nodes_pdp = select_max_path(all_paths_pdp_values,path_nodes)

    #Will only return 1 dataframe
    df = define_path_triples(g_nodes,triples_df,chosen_path_nodes_pdp,search_type)

    df = convert_to_labels(df,labels_all,kg_type,input_nodes_df)

    return df,all_paths_pdp_values,chosen_path_nodes_pdp

def select_max_path(value_list,path_nodes):

    #Get max value from value_list, use that idx of path_nodes then create mechanism
    max_index = value_list.index(max(value_list))
    #Must be list of lists for define_path_triples function
    chosen_path_nodes = [path_nodes[max_index]]

    return chosen_path_nodes

def convert_to_labels(df,labels_all,kg_type,input_nodes_df):

    all_s = []
    all_p = []
    all_o = []

    if kg_type == 'pkl':
        for i in range(len(df)):
            try:
                S = input_nodes_df.loc[input_nodes_df['source_id'] == df.iloc[i].loc['S_ID'],'source_label'].values[0]
            except IndexError:
                S = labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['S_ID'],'label'].values[0]
            P = labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['P_ID'],'label'].values[0]
            try:
                O = input_nodes_df.loc[input_nodes_df['target_id'] == df.iloc[i].loc['O_ID'],'target_label'].values[0]
            except IndexError:
                O = labels_all.loc[labels_all['entity_uri'] == df.iloc[i].loc['O_ID'],'label'].values[0]
            all_s.append(S)
            all_p.append(P)
            all_o.append(O)
    #Need to test for kg-covid19 that S_ID/P_ID/O_ID addition to df works 
    if kg_type == 'kg-covid19':
        for i in range(len(df)):
            try:
                S = input_nodes_df.loc[input_nodes_df['source_id'] == df.iloc[i].loc['S_ID'],'source_label'].values[0]
            except IndexError:
                s_label =  labels_all.loc[labels_all['id'] == df.iloc[i].loc['S_ID'],'label'].values[0]
                if s_label != "":
                    S = s_label
            P = df.iloc[i].loc['P_ID'].split(':')[-1]
            try:
                O = input_nodes_df.loc[input_nodes_df['target_id'] == df.iloc[i].loc['O_ID'],'target_label'].values[0]
            except IndexError:
                o_label =  labels_all.loc[labels_all['id'] == df.iloc[i].loc['O_ID'],'label'].values[0]
                if o_label != "":
                    O = o_label 

    df['S'] = all_s
    df['P'] = all_p
    df['O'] = all_o
    #Reorder columns
    df = df[['S','P','O','S_ID','P_ID','O_ID']]
    df = df.reset_index(drop=True)
    return df

# Wrapper functions
#Returns the path as a dataframe of S/P/O of all triples' labels within the path
def find_shortest_path(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type, kg_type):

    node1 = get_uri(labels_all,start_node,kg_type)
    node2 = get_uri(labels_all,end_node,kg_type)

    #Add weights if specified
    if weights:
        w = graph.es["weight"]
    else:
        w = None

    #list of nodes
    path_nodes = graph.get_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)

    df = define_path_triples(g_nodes,triples_df,path_nodes,search_type)

    df = convert_to_labels(df,labels_all,kg_type,input_nodes_df)

    return df

#Returns the path as a dataframe of S/P/O of all triples' labels within the path
def find_shortest_path_pattern(start_node,end_node,graph,g_nodes,labels_all,triples_df,weights,search_type, kg_type,s,manually_chosen_uris):

    node1 = start_node
    node2 = end_node

    #Add weights if specified
    if weights:
        w = graph.es["weight"]
    else:
        w = None

    #list of nodes
    path_nodes = graph.get_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)

    if len(path_nodes[0]) > 0:

        df = define_path_triples(g_nodes,triples_df,path_nodes,search_type)

    else:
        df = pd.DataFrame()

    return df,manually_chosen_uris

def prioritize_path_cs(input_nodes_df,node_pair,graph,g_nodes,labels_all,triples_df,weights,search_type,triples_file,input_dir,embedding_dimensions, kg_type, networkx_graph, path_nodes = 'none', guiding_term=pd.Series()):
  
    # igraph implementation
    # path_nodes = find_all_shortest_paths(node_pair,graph,g_nodes,labels_all,triples_df,False,search_type, kg_type)
  
    if path_nodes == 'none':
        path_nodes = find_all_shortest_paths(node_pair,graph,g_nodes,labels_all,triples_df,False,search_type, kg_type)

    path_nodes = find_all_shortest_paths_networkx(node_pair,graph,g_nodes,labels_all,triples_df,False,'all', kg_type, networkx_graph)
    e = Embeddings(triples_file,input_dir,embedding_dimensions, kg_type)
    emb,entity_map = e.generate_graph_embeddings(kg_type)
    df,all_paths_cs_values,chosen_path_nodes_cs = calc_cosine_sim(emb,entity_map,path_nodes,g_nodes,triples_df,search_type,labels_all, kg_type, guiding_term,input_nodes_df)

    return path_nodes,df,all_paths_cs_values,chosen_path_nodes_cs

def generate_comparison_terms_dict(subgraph_cosine_sim,term_row,avg_cosine_sim,algorithm,wikipathway,compared_pathway):

    #Add average cosine similarity of subgraph for this term to dictionary
    l = {}
    l['Term'] = term_row['term_label']
    l['Term_ID']= term_row['term_id']
    l['Average_Cosine_Similarity'] = avg_cosine_sim
    l['Algorithm'] = algorithm
    l['Pathway_ID'] = wikipathway
    l['Compared_Pathway'] = compared_pathway

    subgraph_cosine_sim.append(l)
    
    return subgraph_cosine_sim


def prioritize_path_pdp(input_nodes_df,node_pair,graph,g_nodes,labels_all,triples_df,weights,search_type,pdp_weight, kg_type, networkx_graph, path_nodes = 'none'):

    if path_nodes == 'none':
        path_nodes = find_all_shortest_paths_networkx(node_pair,graph,g_nodes,labels_all,triples_df,False,search_type, kg_type,networkx_graph)
    

    df,all_paths_pdp_values,chosen_path_nodes_pdp = calc_pdp(path_nodes,graph,pdp_weight,g_nodes,triples_df,search_type,labels_all, kg_type,input_nodes_df)

    return path_nodes,df,all_paths_pdp_values,chosen_path_nodes_pdp[0]

# expand nodes by drugs 1 hop away
def drugNeighbors(graph,nodes, kg_type,input_nodes_df):
    neighbors = []
    if kg_type == 'kg-covid19':
        nodes = list(graph.labels_all[graph.labels_all['label'].isin(nodes)]['id'])
    for node in nodes:
        tmp_nodes = graph.igraph.neighbors(node,mode = "in")
        tmp = graph.igraph.vs(tmp_nodes)['name']
        drug_neighbors = [i for i in tmp if re.search(r'Drug|Pharm',i)]
        if len(drug_neighbors) != 0:
            for source in drug_neighbors:
                path = graph.igraph.get_shortest_paths(v = source, to = node)
                path_triples = define_path_triples(graph.igraph_nodes,graph.edgelist,path, 'all')
                path_labels = convert_to_labels(path_triples,graph.labels_all,kg_type,input_nodes_df)
                neighbors.append(path_labels)
    all_neighbors = pd.concat(neighbors)
    return all_neighbors
    


def drug_neighbors_wrapper(input_nodes_df, subgraph_df,graph,kg_type):
    subgraph_nodes = unique_nodes(subgraph_df[['S','O']])
    all_neighbors = drugNeighbors(graph,subgraph_nodes,kg_type,input_nodes_df)
    updated_subgraph = pd.concat([subgraph_df,all_neighbors])
    for_input = pd.concat([all_neighbors[['S','O']],all_neighbors[['S','O']]],axis = 1)
    for_input.columns = ['source', 'target', 'source_label', 'target_label']
    updated_input_nodes_df = pd.concat([input_nodes_df, for_input])
    return updated_input_nodes_df, updated_subgraph
