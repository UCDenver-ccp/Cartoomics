import argparse
import os
import glob
import logging.config
from pythonjsonlogger import jsonlogger
import pandas as pd
from urllib.request import urlretrieve
import sys

# logging
log_dir, log, log_config = 'builds/logs', 'cartoomics_log.log', glob.glob('**/logging.ini', recursive=True)
try:
    if not os.path.exists(log_dir): os.mkdir(log_dir)
except FileNotFoundError:
    log_dir, log_config = '../builds/logs', glob.glob('../builds/logging.ini', recursive=True)
    if not os.path.exists(log_dir): os.mkdir(log_dir)
logger = logging.getLogger(__name__)
logging.config.fileConfig(log_config[0], disable_existing_loggers=False, defaults={'log_file': log_dir + '/' + log})


#Define arguments for each required and optional input
def define_arguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    ## Required inputs
    parser.add_argument("--input-dir",dest="InputDir",required=True,help="InputDir")

    parser.add_argument("--output-dir",dest="OutputDir",required=True,help="OutputDir")

    parser.add_argument("--knowledge-graph",dest="KG",required=True,help="Knowledge Graph: either 'pkl' for PheKnowLator or 'kg-covid19' for KG-Covid19")

    ## Optional inputs
    parser.add_argument("--embedding-dimensions",dest="EmbeddingDimensions",required=False,default=128,help="EmbeddingDimensions")

    # Default true for now
    parser.add_argument("--weights",dest="Weights",required=False,help="Weights", type = bool, default = True)

    parser.add_argument("--search-type",dest="SearchType",required=False,default='all',help="SearchType")

    parser.add_argument("--pdp-weight",dest="PdpWeight",required=False,default=0.4,help="PdpWeight")

    parser.add_argument("--input-type",dest="InputType",required=True,help="InputType: either 'annotated_diagram','pathway_ocr', or 'experimental_data'")

    parser.add_argument("--pfocr_url",dest="PfocrURL",required=False, help="The URL for the PFOCR annotated figure (example, 'https://pfocr.wikipathways.org/figures/PMC5095497__IMM-149-423-g007.html'")

    parser.add_argument("--cosine-similarity",dest="CosineSimilarity",required=False,default='true',help="Search for paths using Cosine Similarity.",type = str)

    parser.add_argument("--pdp",dest="PDP",required=False,default='true',help="Search for paths using PDP.",type = str)
    
    parser.add_argument("--guiding-term",dest="GuidingTerm",required=False,default=False,help="Search for paths using Guiding Term(s).",type = bool)

    parser.add_argument("--input-substring",dest="InputSubstring",required=False,default='none',help="Substring to use in example_input.")

    parser.add_argument("--enable-skipping",dest="EnableSkipping",required=False,default=False,help="Enables option to skip nodes when exact match or synonym is not found.",type=bool)

    return parser

# Wrapper function
def generate_arguments():

    #Generate argument parser and define arguments
    parser = define_arguments()
    args = parser.parse_args()
    input_dir = args.InputDir
    output_dir = args.OutputDir
    kg_type = args.KG
    embedding_dimensions = args.EmbeddingDimensions
    weights = args.Weights
    search_type = args.SearchType
    pdp_weight = args.PdpWeight
    input_type = args.InputType
    pfocr_url = args.PfocrURL
    cosine_similarity = args.CosineSimilarity
    pdp = args.PDP
    guiding_term = args.GuidingTerm
    input_substring = args.InputSubstring
    enable_skipping = args.EnableSkipping

    for arg, value in sorted(vars(args).items()):
        logging.info("Argument %s: %r", arg, value)

    if cosine_similarity not in ['true', 'false']:
        parser.print_help()
        sys.exit(1)

    if pdp not in ['true', 'false']:
        parser.print_help()
        sys.exit(1)

    return input_dir,output_dir,kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, pfocr_url, cosine_similarity, pdp, guiding_term, input_substring, enable_skipping

#Define arguments for each required and optional input
def define_arguments_metapaths():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    ## Required inputs
    parser.add_argument("--input-dir",dest="InputDir",required=True,help="InputDir")

    parser.add_argument("--output-dir",dest="OutputDir",required=True,help="OutputDir")

    parser.add_argument("--knowledge-graphs",dest="KgTypes",required=True,help="Knowledge Graph Types: only pkl supported")

    parser.add_argument("--num-iterations",dest="NumIterations",required=True,help="Number of iterations")

    parser.add_argument("--batch-size",dest="BatchSize",required=True,help="Batch size per node type")

    parser.add_argument("--node-input1",dest="NodeInput1",required=True,help="NodeInput1")

    parser.add_argument("--node-input2",dest="NodeInput2",required=True,help="NodeInput2")

    
    ## Optional inputs
    parser.add_argument("--embedding-dimensions",dest="EmbeddingDimensions",required=False,default=128,help="EmbeddingDimensions")

    parser.add_argument("--weights",dest="Weights",required=False,help="Weights", type = bool, default = True)

    parser.add_argument("--search-type",dest="SearchType",required=False,default='all',help="SearchType")

    parser.add_argument("--pdp-weight",dest="PdpWeight",required=False,default=0.4,help="PdpWeight")


   
    return parser


# Wrapper function
def generate_arguments_metapaths():

    #Generate argument parser and define arguments
    parser = define_arguments_metapaths()
    args = parser.parse_args()
    input_dir = args.InputDir
    output_dir = args.OutputDir
    kg_types = args.KgTypes
    num_iterations = args.NumIterations
    batch_size = args.BatchSize
    node_input1 = args.NodeInput1
    node_input2 = args.NodeInput2
    embedding_dimensions = args.EmbeddingDimensions
    weights = args.Weights
    search_type = args.SearchType
    pdp_weight = args.PdpWeight

    for arg, value in sorted(vars(args).items()):
        logging.info("Argument %s: %r", arg, value)

    return input_dir,output_dir,kg_types,num_iterations,batch_size,node_input1,node_input2,embedding_dimensions,weights,search_type,pdp_weight


### Download knowledge graph files
def download_pkl(kg_dir):
    os.system('wget https://storage.googleapis.com/pheknowlator/current_build/knowledge_graphs/instance_builds/relations_only/owlnets/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels.txt -P ' + kg_dir)
    logging.info('Downloaded Node Labels File: https://storage.googleapis.com/pheknowlator/current_build/knowledge_graphs/instance_builds/relations_only/owlnets/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels.txt: %s',kg_dir)
    os.system('wget https://storage.googleapis.com/pheknowlator/current_build/knowledge_graphs/instance_builds/relations_only/owlnets/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers.txt -P ' +kg_dir)
    logging.info('Downloaded Triples File: https://storage.googleapis.com/pheknowlator/current_build/knowledge_graphs/instance_builds/relations_only/owlnets/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers.txt: %s',kg_dir)

## downloading the KG-COVID19
def download_kg19(kg_dir):
    os.system('wget https://kg-hub.berkeleybop.io/kg-covid-19/current/kg-covid-19.tar.gz -P ' + kg_dir)
    os.system('tar -xvzf ' + kg_dir + "kg-covid-19.tar.gz -C " + kg_dir)
    logging.info('Downloaded Node labels and Triples File: https://kg-hub.berkeleybop.io/kg-covid-19/current/kg-covid-19.tar.gz: %s',kg_dir)

def get_graph_files(input_dir,output_dir, kg_type,input_type, pfocr_url, guiding_term = False, input_substring = 'none'):

    #Search for annotated diagram input
    if input_type == 'annotated_diagram':
        folder = input_dir+'/annotated_diagram'
        if not os.path.isdir(folder):
            raise Exception('Missing folder input directory: ' + folder)
            logging.error('Missing folder input directory: ' + folder)
        fname  = [v for v in os.listdir(folder) if 'example_input' in v]
        if len(fname) == 1:
            input_file = [folder + '/' + fname[0]]
        else:
            print(input_substring)
            if input_substring == 'none':
                raise Exception('Missing or duplicate file in input directory: ' + '_example_input')
                logging.error('Missing or duplicate file in input directory: _example_input')
            else:
                for i in fname:
                    if input_substring in i: input_file = [folder + '/' + i]

    
    #Search for Pathway OCR diagram input
    if input_type == 'pathway_ocr':
        if pfocr_url is None:
            user_input = input("Input the PFOCR URL for the figure: ")
        else:
            user_input = pfocr_url

        input_file = []
        pfocr_id = user_input.split("/")[-1].split(".")[0]
### Could add the Figure ID here. LG
        folder = input_dir+'/pathway_ocr_diagram/'
        if not os.path.isdir(folder):
            # raise Exception('Missing folder input directory: ' + folder)
            # logging.error('Missing folder input directory: ' + folder)
            os.makedirs(folder)

        mentions = ["genes", "chemicals", "diseases"]
        for mention in mentions:
            url = "https://raw.githubusercontent.com/wikipathways/pfocr-database/main/_data/" + pfocr_id+ "-"+mention+".tsv"
            filename = folder + mention+".tsv"
            try:
                urlretrieve(url, filename)
                print("downloaded " + mention)
            except:
                print("no content for " + mention)
        fnames  = [v for v in os.listdir(folder) if v != '.DS_Store']
        if len(fnames) == len(set(fnames)):
            for i in fnames:
                input_file.append(folder  + i)
        else:
            raise Exception('Duplicate file in input directory: genes.tsv OR chemicals.tsv OR disease.tsv')
            logging.error('Duplicate file in input directory: genes.tsv OR chemicals.tsv OR disease.tsv')

    #Search for Exerpimental data input
    if input_type == 'experimental_data':
        folder = input_dir+'/experimental_data'
        if not os.path.isdir(folder):
            raise Exception('Missing folder input directory: ' + folder)
            logging.error('Missing folder input directory: ' + folder)

    #Check for existence of guiding_terms file only
    if guiding_term:
        guiding_term_file = input_dir + '/Guiding_Terms.csv'
        if not os.path.isfile(guiding_term_file):
            raise Exception('Missing file in input directory: ' + guiding_term_file)
            logging.error('Missing file in input directory: ' + guiding_term_file)

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
            

    #Check for existence of output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return triples_list_file,labels_file,input_file

def get_graph_files_metapaths(input_dir,output_dir, kg_type):

    if kg_type == "pkl":
        kg_dir = input_dir + '/' + kg_type + '/'
        if not os.path.isdir(kg_dir):
            os.makedirs(kg_dir)
        if len(os.listdir(kg_dir)) < 2:
            download_pkl(kg_dir)

        existence_dict = {
            'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers':'false',
            'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels':'false'
        }

        for k in list(existence_dict.keys()):
            for fname in os.listdir(input_dir + '/' + kg_type):
                if k in fname:
                    if k == 'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers':
                        triples_list_file = input_dir + '/' + kg_type + '/' + fname
                    if k == 'PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels':
                        labels_file = input_dir + '/' + kg_type + '/' + fname
                    existence_dict[k] = 'true'
    
    #Check for existence of all necessary files, error if not

    #### Add exception
    for k in existence_dict:
        if existence_dict[k] == 'false':
            raise Exception('Missing file in input directory: ' + k)

    #Check for existence of output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return triples_list_file,labels_file

    
