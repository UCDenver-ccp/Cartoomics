
from find_path import get_uri
import pandas as pd
from igraph import * 
import numpy as np
import os
import glob
import logging.config
from pythonjsonlogger import jsonlogger
from scipy.stats import zscore
import csv


# logging
log_dir, log, log_config = 'builds/logs', 'cartoomics_log.log', glob.glob('**/logging.ini', recursive=True)
try:
    if not os.path.exists(log_dir): os.mkdir(log_dir)
except FileNotFoundError:
    log_dir, log_config = '../builds/logs', glob.glob('../builds/logging.ini', recursive=True)
    if not os.path.exists(log_dir): os.mkdir(log_dir)
logger = logging.getLogger(__name__)
logging.config.fileConfig(log_config[0], disable_existing_loggers=False, defaults={'log_file': log_dir + '/' + log})


def ranked_comparison(output_dir,**value_dfs):

    df = pd.DataFrame()

    for i in value_dfs.items():
        paths_list = list(i[1]['Value'])
        r = [sorted(paths_list,reverse=True).index(x) for x in paths_list]
        df[i[0]] = r

    output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    df.to_csv(output_folder+'/ranked_comparison.csv',sep=',',index=False)
    logging.info('Create ranked comparison file: %s',output_folder+'/ranked_comparison.csv')
    return df

def path_length_comparison(output_dir,input_nodes_df,labels_all,search_type,**subgraph_dfs):

    df = pd.DataFrame()
    
    for sg in subgraph_dfs.items():
        sg_df = sg[1]
        #Change order of columns for igraph object
        sg_df = sg_df[['S', 'O', 'P']]
        path_lengths = []
        g = Graph.DataFrame(sg_df,directed=True,use_vids=False)
        for i in range(len(input_nodes_df)):
            #node1 = get_uri(labels_all,input_nodes_df.iloc[i].loc['source'])
            node1 = input_nodes_df.iloc[i].loc['source_label']
            node2 = input_nodes_df.iloc[i].loc['target_label']
            p = g.get_all_shortest_paths(v=node1, to=node2, weights=None, mode=search_type)
            path_lengths.append(len(p[0]))
        df[sg[0]] = path_lengths
        
    output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    df.to_csv(output_folder+'/path_length_comparison.csv',sep=',',index=False)
    logging.info('Create path length comparison file: %s',output_folder+'/path_length_comparison.csv')
    return df

def num_nodes_comparison(output_dir,**subgraph_dfs):

    df = pd.DataFrame()

    for sg in subgraph_dfs.items():
        sg_df = sg[1]

        n = pd.unique(sg_df[['S', 'O']].values.ravel())
        df[sg[0]] = [len(n)]

    output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    df.to_csv(output_folder+'/num_nodes_comparison.csv',sep=',',index=False)
    logging.info('Create number of nodes comparison file: %s',output_folder+'/num_nodes_comparison.csv')
    return df

def get_ontology_labels(noa_df,labels_all,kg_type,subgraph_df):

    ont_types = ['/CHEBI_','/PR_','/PW_','/gene','/MONDO_','/HP_','/VO_','/EFO_','NCBITaxon_','/GO_','/DOID_','/reactome','/SO_',
    'ENSEMBL:','UniProt','GO:','NCBIGene','CHEMBL.','ensembl','/CL_','/CLO']

    ont_labels = []

    num_intermediate_nodes = 0

    #Get all intermediate nodes from subgraph
    for i in range(len(noa_df)):
        ont_found = 'false'
        if noa_df.iloc[i].loc['Attribute'] == 'Extra':
            #For when we were not outputting node ID
            #uri = get_uri(labels_all,noa_df.iloc[i].loc['Node'],kg_type)
            #Use subgraph to get uri
            try:
                uri = subgraph_df.loc[subgraph_df['S'] == noa_df.iloc[i].loc['Node'],'S_ID'].values[0]
            except IndexError:
                uri = subgraph_df.loc[subgraph_df['O'] == noa_df.iloc[i].loc['Node'],'O_ID'].values[0]
            num_intermediate_nodes += 1
            for j in ont_types:
                if j in uri:
                    ont_labels.append(j)
                    ont_found = 'true'
            if ont_found == 'false':
                print('Ontology not accounted for in list: ',uri)
                raise Exception('Ontology type not accounted for in list: ',uri,', add this ontology type to get_ontology_labels function (evaluation.py).')
                logging.error('Ontology type not accounted for in list: %s, add this ontology type to get_ontology_labels function (evaluation.py).',uri)   
    
    ont_labels, counts = np.unique(ont_labels,return_counts=True)
    ont_labels = ont_labels.tolist()
    counts = counts.tolist()

    return ont_labels, counts, num_intermediate_nodes


def intermediate_nodes_comparison(intermediate_nodes_df,labels_all,kg_type,wikipathway,subgraph_df,**noa_dfs):

    all_ont_labels = []

    df = pd.DataFrame()

    #Get all possible ontology types from all subgraphs given
    onts_used = []
    for nd in noa_dfs.items():
        n_df = nd[1]
        #Get unique ontology types from this subgraph, add to running list for each subgraph, counts not used here
        ont_labels, counts, num_intermediate_nodes = get_ontology_labels(n_df,labels_all,kg_type,subgraph_df)
        all_ont_labels.extend(ont_labels)
        
    #List of all unique ontology types from all subgraphs
    all_ont_labels = np.unique(all_ont_labels)

    #Add all unique ont labels to df
    df['Ontology_Type'] = all_ont_labels
    df.sort_values(by=['Ontology_Type'], ascending=(True),inplace=True)
        
    #Get counts of each ontology type
    for nd in noa_dfs.items():
        values = []
        algorithm = []
        pathway = []
        n_df = nd[1]
        ont_labels, counts, num_intermediate_nodes = get_ontology_labels(n_df,labels_all,kg_type,subgraph_df)
        #Add any ontology types not already in subgraph
        for i in all_ont_labels:
            if i not in ont_labels:
                ont_labels.append(i)
                counts.append(0)

        #Normalize counts
        counts_norm = [i/num_intermediate_nodes for i in counts]
        onts_dict = {ont_labels[i]: counts_norm[i] for i in range(len(ont_labels))}
        #Sort dict the same way as df is sorted
        for key in sorted(onts_dict.keys()):
            values.append(onts_dict[key])
            algorithm.append(nd[0])
            pathway.append(wikipathway)
        #df[nd[0]] = values
        df['Algorithm'] = algorithm
        df['Percent_Nodes'] = values
        df['Pathway_ID'] = pathway

    intermediate_nodes_df = pd.concat([intermediate_nodes_df,df], axis=0)

    return intermediate_nodes_df
    
    '''output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    df.to_csv(output_folder+'/intermediate_nodes_comparison.csv',sep=',',index=False)
    logging.info('Create intermediate nodes comparison file: %s',output_folder+'/intermediate_nodes_comparison.csv')
    return df'''

def output_node_edge_type_file(output_dir,df,filename):

    output_folder = output_dir+'/node_edge_evaluation'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    df.to_csv(output_folder+'/' + filename + '.csv',sep=',',index=False)
    logging.info('Creating ' + filename + ' file: %s',output_folder+'/' + filename + '.csv')
    return df

def edge_type_comparison(edge_type_df,wikipathway,**subgraph_dfs):

    all_edge_labels = []

    df = pd.DataFrame()

    #Get all possible edge types from all subgraphs given
    for sg in subgraph_dfs.items():
        sg_df = sg[1]
        #Get unique edge types from this subgraph, add to running list for each subgraph, counts not used here
        edge_labels, counts = np.unique(sg_df['P'], return_counts=True)
        all_edge_labels.extend(edge_labels)
        
    #List of all unique ontology types from all subgraphs
    all_edge_labels = np.unique(all_edge_labels)

    #Add all unique edge labels to df
    df['Edge_Type'] = all_edge_labels
    df.sort_values(by=['Edge_Type'], ascending=(True),inplace=True)

    for sg in subgraph_dfs.items():
        values = []
        algorithm = []
        pathway = []
        sg_df = sg[1]

        #Need to account for the fact that ont types will be different for each sg_df (i.e. values)
        edge_labels, counts = np.unique(sg_df['P'], return_counts=True)
        edge_labels = list(edge_labels)
        counts = list(counts)
        #Add any edge types not already in subgraph
        for i in all_edge_labels:
            if i not in edge_labels:
                edge_labels.append(i)
                counts.append(0)
        #Normalize counts
        counts_norm = [i/len(sg_df['P']) for i in counts]
        edge_dict = {edge_labels[i]: counts_norm[i] for i in range(len(edge_labels))}
        #Sort dict the same way as df is sorted
        for key in sorted(edge_dict.keys()):
            values.append(edge_dict[key])
            algorithm.append(sg[0])
            pathway.append(wikipathway)
        #df[sg[0]] = values
        df['Algorithm'] = algorithm
        df['Percent_Edges'] = values
        df['Pathway_ID'] = pathway

    edge_type_df = pd.concat([edge_type_df,df], axis=0)

    return edge_type_df

    '''output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    df.to_csv(output_folder+'/edge_type_comparison.csv',sep=',',index=False)
    logging.info('Create edge type comparison file: %s',output_folder+'/edge_type_comparison.csv')
    return df'''


#Gets subgraph df for specific algorithm, supporting types are CosineSimilarity and PDP
def get_subgraph_dfs(output_dir,input_type,subgraph_algorithm):

    input_nodes_file = output_dir+"/_" + input_type + "_Input_Nodes_.csv"
    #input_nodes_file = output_dir+'/_Input_Nodes_.csv'
    input_nodes = pd.read_csv(input_nodes_file, sep = "|")

    subgraph_file = output_dir+'/'+subgraph_algorithm+'/Subgraph.csv'
    subgraph_df = pd.read_csv(subgraph_file, sep = "|")

    noa_file = output_dir+'/'+subgraph_algorithm+'/Subgraph_attributes.noa'
    noa_df = pd.read_csv(noa_file, sep = "|")

    #path_list_file = output_dir+'/Evaluation_Files/paths_list_'+subgraph_algorithm+'.csv'
    #path_list = pd.read_csv(path_list_file, sep=",")
    path_list = []

    return input_nodes,subgraph_df,noa_df,path_list


def output_path_lists(output_dir,path_list,subgraph_algorithm,idx):

    df = pd.DataFrame()

    df['Value'] = path_list

    output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    df.to_csv(output_folder+'/paths_list_'+subgraph_algorithm+'_'+str(idx)+'.csv',sep=',',index=False)
    logging.info('Create path list file: %s',output_folder+'/paths_list_'+subgraph_algorithm+'_'+str(idx)+'.csv')

def output_num_paths_pairs(output_dir,num_paths_df,subgraph_algorithm):

    output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    num_paths_df.to_csv(output_folder+'/num_paths_'+subgraph_algorithm+'.csv',sep=',',index=False)
    logging.info('Create number of paths file: %s',output_folder+'/num_paths_'+subgraph_algorithm+'.csv')

def output_literature_comparison_df(output_dir,all_subgraphs_cosine_sim,search_type):

    output_folder = output_dir+'/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    all_subgraphs_cosine_sim_df = pd.DataFrame.from_dict(all_subgraphs_cosine_sim, orient='columns')

    all_subgraphs_cosine_sim_df.to_csv(output_folder+'/literature_comparison_evaluation_' + search_type + '.csv',sep=',',index=False)
    logging.info('Create literature comparison evaluation file: %s',output_folder+'/literature_comparison_evaluation_' + search_type + '.csv')

    return all_subgraphs_cosine_sim_df

def compare_literature_terms_across_pathways(all_subgraphs_cosine_sim_df):

    z = all_subgraphs_cosine_sim_df.groupby(['Pathway_ID','Algorithm']).Average_Cosine_Similarity.transform(zscore, ddof=1)

    all_subgraphs_cosine_sim_df['zscore'] = z

    avg_z_by_compare_pathways = all_subgraphs_cosine_sim_df.groupby(['Compared_Pathway','Algorithm']).zscore.transform(mean)

    all_subgraphs_cosine_sim_df['avg_zscore_per_pathway'] = avg_z_by_compare_pathways

    all_subgraphs_zscore_df = all_subgraphs_cosine_sim_df[['Algorithm','Pathway_ID','Compared_Pathway','avg_zscore_per_pathway']]

    all_subgraphs_zscore_df = all_subgraphs_zscore_df.drop_duplicates()

    all_subgraphs_zscore_df.loc[all_subgraphs_zscore_df.Compared_Pathway != all_subgraphs_zscore_df.Pathway_ID, 'Compared_Pathway'] = 'Other_Pathway'
    all_subgraphs_zscore_df.loc[all_subgraphs_zscore_df.Compared_Pathway == all_subgraphs_zscore_df.Pathway_ID, 'Compared_Pathway'] = 'Same_Pathway'

    return all_subgraphs_zscore_df

'''def output_idf_evaluation_df(output_dir,idf_evaluation_df):

    output_folder = output_dir+'/literature_comparison/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    idf_evaluation_df.to_csv(output_folder+'/subgraph_idf_evaluation.csv',sep=',',index=False)
    logging.info('Create subgraph idf evaluation file: %s',output_folder+'/subgraph_idf_evaluation.csv')'''

def output_nodes_not_in_KG(all_wikipathways_dir,nodes_not_in_KG):

    results_fields = ['Curie','Uri']

    output_folder = all_wikipathways_dir+'/literature_comparison/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    results_file = output_folder + '/idf_nodes_not_in_KG.csv'

    with open(results_file, 'w') as f:
        write = csv.writer(f)
        write.writerow(results_fields)
        write.writerows(nodes_not_in_KG)

def output_idf_metrics(all_wikipathways_dir,idf_metrics):

    results_fields = ['Pathway_ID','Algorithm','Node','Node_ID','IDF']

    output_folder = all_wikipathways_dir+'/literature_comparison/Evaluation_Files'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    results_file = output_folder + '/subgraph_idf_evaluation.csv'

    with open(results_file, 'w') as f:
        write = csv.writer(f)
        write.writerow(results_fields)
        write.writerows(idf_metrics)

    return results_file
