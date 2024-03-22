import numpy as np
from inputs import *
from create_graph import create_graph
from assign_nodes import interactive_search_wrapper
from create_subgraph import subgraph_prioritized_path_cs
from create_subgraph import subgraph_prioritized_path_pdp
from create_subgraph import  subgraph_prioritized_path_guiding_term
from create_subgraph import user_defined_edge_exclusion
from graph_similarity_metrics import *
from assign_nodes import normalize_node_api,convert_to_uri,get_label
from find_path import get_uri
from create_subgraph import get_wikipathways_subgraph
from evaluation import output_nodes_not_in_KG,output_idf_metrics
from tqdm import tqdm
from assign_nodes import map_input_to_nodes,manage_user_input



from wikipathways_converter import get_wikipathways_list
from constants import (
    WIKIPATHWAYS_SUBFOLDER
)

def process_idf_file(file,labels,kg_type,all_wikipathways_dir):

    exists = 'false'

    output_dir = all_wikipathways_dir+'/literature_comparison/Evaluation_Files'
    output_idf_filename = 'concept_idf_annotated.csv'
    for fname in os.listdir(output_dir):
        if fname == output_idf_filename:
            exists = 'true'
            df = pd.read_csv(output_dir + '/' + fname)

    if exists == 'false':
        cols = ['idf','curie']

        df = pd.read_csv(file,sep=',',header=None, names=cols)

        nodes_not_in_KG = []

        uris = []
        all_labels = []
        for i in tqdm(range(len(df))):
            curie = df.iloc[i].loc['curie']
            #Transform to known ontogies if needed
            try:
                uri = convert_to_uri(curie)
            except IndexError:
                uri = 'none'
                nodes_not_in_KG.append([curie,uri])
            uris.append(uri)
            try:
                l = get_label(labels,uri,kg_type)
            except IndexError:
                nodes_not_in_KG.append([curie,uri])
                l = 'none'
            all_labels.append(l)

        df['uri'] = uris
        df['label'] = all_labels
        output_nodes_not_in_KG(all_wikipathways_dir,nodes_not_in_KG)
        print('writing to: ',output_dir + '/' + output_idf_filename)
        df.to_csv(output_dir + '/' + output_idf_filename,sep=',',index=False)
    return df

def get_subgraph_idf(subgraphs_idf_metrics,labels,kg_type,subgraph_df,idf_df,wikipathway,algorithm,g):

    #Structure of subgraphs_idf_metrics: Pathway_ID,Algorithm,Node,IDF
    unique_nodes = list(subgraph_df.S_ID.unique()) + list(subgraph_df.O_ID.unique())

    for node_id in unique_nodes:
        try:
            node = subgraph_df.loc[subgraph_df['S_ID'] == node_id,'S'].values[0]
        except IndexError:
            node = subgraph_df.loc[subgraph_df['O_ID'] == node_id,'O'].values[0]
        idf = get_node_id_idf(node_id,g,idf_df)
        subgraphs_idf_metrics.append([wikipathway,algorithm,node,node_id,idf])

    return subgraphs_idf_metrics

def get_node_id_idf(node_id,g,idf_df):

    idf = idf_df.loc[idf_df['uri'] == node_id,'idf']

    return idf

def get_node_idf_from_label(node,g,idf_df):
    
    found_nodes,nrow,exact_match = map_input_to_nodes(node,g,'true')
    
    if exact_match: 
        node_label,bad_input,id_given = manage_user_input(found_nodes,found_nodes,g,exact_match)
        node_uri = id_given
    else:
        node_uri = 'none'
    try:
        idf = idf_df.loc[idf_df['uri'] == node_uri,'idf'].values[0]
    except IndexError:
        idf = np.nan

    return idf

def main():

    kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping = generate_graphsim_arguments()

    input_dir = os.getcwd() + '/' + WIKIPATHWAYS_SUBFOLDER

    triples_list_file,labels_file = get_wikipathways_graph_files(input_dir,kg_type,input_type,guiding_term,input_substring)

    print("Creating knowledge graph object from inputs.....")

    g = create_graph(triples_list_file,labels_file, kg_type)

    wikipathways = get_wikipathways_list(wikipathways,pfocr_urls,pfocr_urls_file)

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    idf_file = os.getcwd() + "/Wikipathways_Text_Annotation/concept_idf.sorted.csv"

    idf_df = process_idf_file(idf_file,g.labels_all,kg_type,all_wikipathways_dir)


    #####
    #For comparison to subgraphs
    #####

    #List for all idf metrics
    '''subgraphs_idf_metrics = []

    for wikipathway in wikipathways:

        output_dir = all_wikipathways_dir + '/' + wikipathway + '_output'
        
        if cosine_similarity == 'true':

            subgraph_df = pd.read_csv(output_dir + '/CosineSimilarity/Subgraph.csv',sep='|')

            subgraphs_idf_metrics = get_subgraph_idf(subgraphs_idf_metrics,g.labels_all,kg_type,subgraph_df,idf_df,wikipathway,'CosineSimilarity',g)

        if pdp == 'true':

            subgraph_df = pd.read_csv(output_dir + '/PDP/Subgraph.csv',sep='|')

            subgraphs_idf_metrics = get_subgraph_idf(subgraphs_idf_metrics,g.labels_all,kg_type,subgraph_df,idf_df,wikipathway,'PDP',g)

        w_annotated_edgelist = pd.read_csv(output_dir + '/_annotated_diagram_Input_Nodes_.csv',sep='|')

        #Get original wikipathways edgelist
        wikipathways_subgraph_df = get_wikipathways_subgraph(w_annotated_edgelist)

        subgraphs_idf_metrics = get_subgraph_idf(subgraphs_idf_metrics,g.labels_all,kg_type,wikipathways_subgraph_df,idf_df,wikipathway,'original',g)'''

        #Output files and visualization for edge and node type evaluations
        #idf_file = output_idf_metrics(all_wikipathways_dir,subgraphs_idf_metrics)

    #####
    #For comparison to subgraphs
    #####

    #####
    #For comparison to abstract terms
    #####

    literature_comparison_file = all_wikipathways_dir +'/literature_comparison/Evaluation_Files/literature_comparison_evaluation.csv'
    literature_comparison_df = pd.read_csv(literature_comparison_file)

    #For appending to df
    node_idfs_list = []

    for i in range(len(literature_comparison_df)):
        term_id = literature_comparison_df.iloc[i].loc['Term_ID']
        try:
            idf = idf_df.loc[idf_df['uri'] == term_id,'idf'].values[0]
        except IndexError:
            idf = np.nan
        node_idfs_list.append(idf)

    literature_comparison_df['IDF'] = node_idfs_list

    literature_comparison_df.to_csv(all_wikipathways_dir +'/literature_comparison/Evaluation_Files/literature_comparison_evaluation_with_IDF.csv',sep=',',index=False)

if __name__ == '__main__':
    main()