



from igraph import *
import pandas as pd
import networkx as nx
import os
import matplotlib.pyplot as plt
import argparse
import glob
import logging.config
from pythonjsonlogger import jsonlogger
from inputs import *
import seaborn as sns
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

def define_graphsim_arguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    ## Required inputs
    parser.add_argument("--knowledge-graph",dest="KG",required=True,help="Knowledge Graph: either 'pkl' for PheKnowLator or 'kg-covid19' for KG-Covid19")

    ## Optional inputs
    parser.add_argument("--embedding-dimensions",dest="EmbeddingDimensions",required=False,default=128,help="EmbeddingDimensions")

    parser.add_argument("--weights",dest="Weights",required=False,help="Weights", type = bool, default = False)

    parser.add_argument("--search-type",dest="SearchType",required=False,default='all',help="SearchType")

    parser.add_argument("--pdp-weight",dest="PdpWeight",required=False,default=0.4,help="PdpWeight")

    parser.add_argument("--input-type",dest="InputType",required=True,help="InputType: either 'annotated_diagram','pathway_ocr', or 'experimental_data'")

    parser.add_argument("--pfocr_url",dest="PfocrURL",required=False, help="The URL for the PFOCR annotated figure (example, 'https://pfocr.wikipathways.org/figures/PMC5095497__IMM-149-423-g007.html'")

    parser.add_argument("--cosine-similarity",dest="CosineSimilarity",required=False,default='true',help="Search for paths using Cosine Similarity.",type = str)

    parser.add_argument("--pdp",dest="PDP",required=False,default='true',help="Search for paths using PDP.",type = str)
    
    parser.add_argument("--guiding-term",dest="GuidingTerm",required=False,default=False,help="Search for paths using Guiding Term(s).",type = bool)

    parser.add_argument("--input-substring",dest="InputSubstring",required=False,default='none',help="Substring to use in example_input.")
    
    ###CHECK THIS ONE
    #parser.add_argument("--guiding-term",dest="GuidingTerm",required=False,help="Search for paths using Guiding Term specified.",type = str)

    ## Required inputs for wikipathways diagrams
    parser.add_argument("--wikipathways",dest="Wikipathways",required=False,help="List of Wikipathways IDs (example input: '['WP5372']'), there is no default")
    
    parser.add_argument("--pfocr_urls",dest="PfocrUrls",required=False,help="List of pfocr urls (e.g., '['https://pfocr.wikipathways.org/figures/PMC6943888__40035_2019_179_Fig1_HTML.html']'), there is no default")
    
    parser.add_argument("--pfocr-urls-file",dest="PfocrUrlsFile",required=False,default=False,help="Specifies existance of file with list of pfocr urls",type=bool)

    parser.add_argument("--enable-skipping",dest="EnableSkipping",required=False,default=False,help="Enables option to skip nodes when exact match or synonym is not found.",type=bool)

    return(parser)

# Wrapper function
def generate_graphsim_arguments():

    #Generate argument parser and define arguments
    parser = define_graphsim_arguments()
    args = parser.parse_args()
    kg_type = args.KG
    embedding_dimensions = args.EmbeddingDimensions
    weights = args.Weights
    search_type = args.SearchType
    pdp_weight = args.PdpWeight
    input_type = args.InputType
    cosine_similarity = args.CosineSimilarity
    pdp = args.PDP
    guiding_term = args.GuidingTerm
    input_substring = args.InputSubstring

    wikipathways = args.Wikipathways
    pfocr_urls = args.PfocrUrls
    pfocr_urls_file = args.PfocrUrlsFile
    enable_skipping = args.EnableSkipping

    for arg, value in sorted(vars(args).items()):
        logging.info("Argument %s: %r", arg, value)

    if cosine_similarity not in ['true', 'false']:
        parser.print_help()
        sys.exit(1)

    if pdp not in ['true', 'false']:
        parser.print_help()
        sys.exit(1)

    return kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping

#Same as get_graph_files except does not get input example file, done later, and no pfocr_url or experimental dataset is possible
def get_wikipathways_graph_files(input_dir,kg_type,input_type, guiding_term = False, input_substring = 'none'):

    #Search for annotated diagram input
    # if input_type == 'annotated_diagram':
    #     folder = input_dir+'/annotated_diagram'
    #     if not os.path.isdir(folder):
    #         raise Exception('Missing folder input directory: ' + folder)
    #         logging.error('Missing folder input directory: ' + folder)
        
    # #Check for existence of guiding_terms file only
    # if guiding_term:
    #     guiding_term_file = input_dir + '/Guiding_Terms.csv'
    #     if not os.path.isfile(guiding_term_file):
    #         raise Exception('Missing file in input directory: ' + guiding_term_file)
    #         logging.error('Missing file in input directory: ' + guiding_term_file)

    if kg_type == "pkl":
        kg_dir = input_dir + '/' + kg_type + '/'
        if not os.path.exists(kg_dir):
            os.mkdir(kg_dir)
        if len(os.listdir(kg_dir)) < 2:
            download_pkl(kg_dir)


        existence_dict = {
            'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers':'false',
            'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels':'false',
        }
        
        
        for k in list(existence_dict.keys()):
            for fname in os.listdir(kg_dir):
                if k in fname:
                    if k == 'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers':
                        triples_list_file = input_dir + '/' + kg_type + '/' + fname
                    if k == 'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels':
                        labels_file = input_dir + '/' + kg_type + '/' + fname
                    existence_dict[k] = 'true'
    
    if kg_type == "kg-covid19":
        kg_dir = input_dir + '/' + kg_type + '/'
        if not os.path.exists(kg_dir):
            os.mkdir(kg_dir)
        if len(os.listdir(kg_dir)) < 2:
            download_kg19(kg_dir)
        
        existence_dict = {
            'merged-kg_edges.':'false',
            'merged-kg_nodes.':'false'
        }


        for k in list(existence_dict.keys()):
            for fname in os.listdir(kg_dir):
                if k in fname:
                    if k == 'merged-kg_edges.':
                        triples_list_file = input_dir + '/' + kg_type + '/' + fname
                    if k == 'merged-kg_nodes.':
                        labels_file = input_dir + '/' + kg_type + '/' + fname 
                    existence_dict[k] = 'true'

    #Check for existence of all necessary files, error if not

    #### Add exception
    for k in existence_dict:
        if existence_dict[k] == 'false':
            raise Exception('Missing file in input directory: ' + k)
            logging.error('Missing file in input directory: %s',k)
            

    return triples_list_file,labels_file


#Creates igraph object and a list of nodes
def create_igraph_graph(edgelist_df):

    '''#Edgelist generation for subgraphs produced with cartoomics
    if edgelist_type == 'subgraph':
        edgelist_df = edgelist_df[['S','O','P']]
        #Remove gene descriptions in parentheses such as " (human)"
        edgelist_df['S'] = edgelist_df['S'].str.replace(r"\([^()]*\)", "", regex=True).str.strip()
        edgelist_df['O'] = edgelist_df['O'].str.replace(r"\([^()]*\)", "", regex=True).str.strip()

        edgelist_df = edgelist_df.rename(columns={'Source' : 'S', 'edgeID': 'P','Target': 'O'})

    #Edgelist generation for wikipathways diagrams
    if edgelist_type == 'wikipathways':
        edgelist_df = edgelist_df[['Source',  'Target', 'edgeID']]
        edgelist_df = edgelist_df.rename(columns={'Source' : 'S', 'edgeID': 'P','Target': 'O'})'''

    g = Graph.DataFrame(edgelist_df,directed=True,use_vids=False)

    #g_nodes = g.vs()['name']

    return g 

#Networkx graph format is necessary for graph edit distance calculation
def create_networkx_graph(edgelist_df,edgelist_type):

    if edgelist_type == 'subgraph':
        edgelist_df = edgelist_df[['S','O','P']]
        #Remove gene descriptions in parentheses such as (human)
        edgelist_df['S'] = edgelist_df['S'].str.replace(r"\([^()]*\)", "", regex=True).str.strip()
        edgelist_df['O'] = edgelist_df['O'].str.replace(r"\([^()]*\)", "", regex=True).str.strip()

        edgelist_df = edgelist_df.rename(columns={'Source' : 'S', 'edgeID': 'P','Target': 'O'})

    if edgelist_type == 'wikipathways':
        edgelist_df = edgelist_df[['Source',  'Target', 'edgeID']]
        edgelist_df = edgelist_df.rename(columns={'Source' : 'S', 'edgeID': 'P','Target': 'O'})

    g = nx.from_pandas_edgelist(edgelist_df, 'S', 'O')

    return g

def prepare_subgraphs(wikipathway,algorithm,all_wikipathways_dir):

    wikipathway_dir = all_wikipathways_dir + '/' + wikipathway

    wikipathways_subgraph_file = wikipathway_dir + '/' + wikipathway + '_edgeList.csv'
    #Subgraph type must be CosineSimilarity, PDP, or GuidingTerm_<specified_term> to match current output structure
    cartoomics_subgraph_file = wikipathway_dir + '_output/' + algorithm + '/Subgraph.csv'

    wikipathways_df = pd.read_csv(wikipathways_subgraph_file,sep=',')
    cartoomics_df = pd.read_csv(cartoomics_subgraph_file,sep='|')

    #Edgelist generation for subgraphs produced with cartoomics
    cartoomics_df = cartoomics_df[['S','O','P']]
    #Remove gene descriptions in parentheses such as " (human)"
    cartoomics_df['S'] = cartoomics_df['S'].str.replace(r"\(human\)", "", regex=True).str.strip()
    cartoomics_df['O'] = cartoomics_df['O'].str.replace(r"\(human\)", "", regex=True).str.strip()
    #cartoomics_df['S'] = cartoomics_df['S'].str.replace("(human)", "", regex=True).str.strip()
    #cartoomics_df['O'] = cartoomics_df['O'].str.replace("(human)", "", regex=True).str.strip()

    #Edgelist generation for wikipathways diagrams
    wikipathways_df = wikipathways_df[['Source',  'Target', 'edgeID']]
    wikipathways_df = wikipathways_df.rename(columns={'Source' : 'S', 'edgeID': 'P','Target': 'O'})

    return wikipathways_df,cartoomics_df

    wikipathways_graph = create_igraph_graph(wikipathways_df,'wikipathways')
    cartoomics_graph = create_igraph_graph(cartoomics_df,'subgraph')

    return wikipathways_graph,cartoomics_graph

def jaccard_similarity(wikipathways_graph,cartoomics_graph):

    g_intersection = intersection([wikipathways_graph,cartoomics_graph],keep_all_vertices=False)
    g_union = union([wikipathways_graph,cartoomics_graph])

    j = g_intersection.vcount() / g_union.vcount()

    return j

def overlap_metric(wikipathways_graph,cartoomics_graph):

    g_intersection = intersection([wikipathways_graph,cartoomics_graph], keep_all_vertices=False)
    g_min = min([wikipathways_graph.vcount(),cartoomics_graph.vcount()])

    o = g_intersection.vcount() / g_min

    return o

def edit_distance_metric(wikipathways_graph,cartoomics_graph):

    e = nx.graph_edit_distance(wikipathways_graph,cartoomics_graph)

    return e

def generate_graph_similarity_metrics(all_metrics,wikipathway,algorithm,all_wikipathways_dir):

    wikipathways_df,cartoomics_df = prepare_subgraphs(wikipathway,algorithm,all_wikipathways_dir)
    wikipathways_graph = create_igraph_graph(wikipathways_df)
    cartoomics_graph = create_igraph_graph(cartoomics_df)
    all_metrics.append([algorithm,wikipathway,'Jaccard',jaccard_similarity(wikipathways_graph,cartoomics_graph)])
    all_metrics.append([algorithm,wikipathway,'Overlap',overlap_metric(wikipathways_graph,cartoomics_graph)])
    #Graph edit distance not supported yet
    #all_metrics.append([algorithm,wikipathway,'EditDistance',edit_distance_metric(wikipathways_graph,cartoomics_graph)])

    return all_metrics

def output_graph_similarity_metrics(all_wikipathways_dir,all_metrics):

    results_fields = ['Algorithm','Pathway_ID','Metric','Score']

    output_folder = all_wikipathways_dir+'/graph_similarity'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    results_file = output_folder + '/Graph_Similarity_Metrics.csv'

    with open(results_file, 'w') as f:
        write = csv.writer(f)
        write.writerow(results_fields)
        write.writerows(all_metrics)

    return results_file

def get_percent_nodes_mapped(wikipathways_df,cartoomics_df):

    wikipathways_list = set(wikipathways_df.S.tolist() + wikipathways_df.O.tolist())
    cartoomics_list = set(cartoomics_df.S.tolist() + cartoomics_df.O.tolist())
    #Gets all nodes in wikipathways that are in cartoomics subgraph/all nodes in wikipathways
    percent_nodes_mapped = sum(node in cartoomics_list for node in wikipathways_list)/len(wikipathways_list)

    return percent_nodes_mapped

def get_percent_intermediate_nodes(wikipathways_df,cartoomics_df):

    wikipathways_list = set(wikipathways_df.S.tolist() + wikipathways_df.O.tolist())
    cartoomics_list = set(cartoomics_df.S.tolist() + cartoomics_df.O.tolist())
    #Gets all intermediate nodes not in wikipathways/all nodes in the final cartoomics subgraph
    percent_intermediate_nodes = len(cartoomics_list.difference(wikipathways_list))/len(cartoomics_list) #Change this to divide by length of cartoomics_list
    
    return percent_intermediate_nodes

def generate_graph_mapping_statistics(all_metrics,wikipathway,algorithm,all_wikipathways_dir):

    wikipathways_df,cartoomics_df = prepare_subgraphs(wikipathway,algorithm,all_wikipathways_dir)

    all_metrics.append([algorithm,wikipathway,'Percent_Nodes_Mapped',get_percent_nodes_mapped(wikipathways_df,cartoomics_df)])
    all_metrics.append([algorithm,wikipathway,'Percent_Intermediate_Nodes',get_percent_intermediate_nodes(wikipathways_df,cartoomics_df)])

    return all_metrics

def output_graph_node_percentage_metrics(all_wikipathways_dir,all_metrics):

    results_fields = ['Algorithm','Pathway_ID','Metric','Score']

    output_folder = all_wikipathways_dir+'/graph_similarity'
    #Check for existence of output directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    results_file = output_folder + '/Graph_Node_Percentage_Metrics.csv'

    with open(results_file, 'w') as f:
        write = csv.writer(f)
        write.writerow(results_fields)
        write.writerows(all_metrics)

    return results_file





