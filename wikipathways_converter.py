from wikinetworks_mod import *
import networkx as nx
import argparse
import os
import requests
from bs4 import BeautifulSoup
import ast

from inputs import *
from create_graph import create_graph
from assign_nodes import interactive_search_wrapper
from create_subgraph import subgraph_prioritized_path_cs
from create_subgraph import subgraph_prioritized_path_pdp
from create_subgraph import  subgraph_prioritized_path_guiding_term
from create_subgraph import user_defined_edge_exclusion

from graph_similarity_metrics import *
from constants import (
    WIKIPATHWAYS_SUBFOLDER
)

def get_wikipathway_from_pfocr_url(pfocr_url):
    response = requests.get(pfocr_url)
    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the image tag
    image_tag = soup.find('img', alt='WikiPathways')
    # Extract the message attribute
    if image_tag:
        message_attr = image_tag.get('src')
        # Extracting the part after 'message='
        wikipathway = message_attr.split('message=')[1].split('&')[0]
        print("Wikipathway:", wikipathway)
        return(wikipathway)
    else:
        print("Wikipathway not found.")
    

def download_wikipathways_edgelist(w_dir,wikipathway):

    if not os.path.exists(w_dir+"/"+wikipathway):
        os.makedirs(w_dir+"/"+wikipathway)

    os.chdir(w_dir+"/"+wikipathway)

    __all__ = ["WikiPathways"]
    s = WikiPathways()

    graph = runParsePathway(s, wikipathway)

    print(graph)
    

def convert_wikipathways_input(all_wikipathways_dir,wikipathway):


    wikipathways_edgelist = pd.read_csv(all_wikipathways_dir + '/' + wikipathway + '/' + wikipathway + '_edgeList.csv')

    edgelist_df = wikipathways_edgelist[['Source', 'Target']]
    edgelist_df = edgelist_df.rename(columns={'Source' : 'source', 'Target': 'target'})

    if not os.path.exists(all_wikipathways_dir+ '/annotated_diagram'):
        os.makedirs(all_wikipathways_dir+ '/annotated_diagram')

    examples_file = all_wikipathways_dir + '/annotated_diagram/' + wikipathway + '_example_input.csv'
    edgelist_df.to_csv(examples_file,sep='|',index=False)
    logging.info('Output example file for %s: %r',wikipathway,examples_file)

    return examples_file

#Converts PFOCRs as a file or list into Wikipathway IDs, if provided
def get_wikipathways_list(wikipathways,pfocr_urls,pfocr_urls_file):

    #Convert string input to list
    if wikipathways:
        wikipathways = ast.literal_eval(wikipathways)
    elif pfocr_urls:
        pfocr_urls = ast.literal_eval(pfocr_urls)
        wikipathways = []
        for p in pfocr_urls:
            #Gets wikpathway from pfocr_url
            wikipathways.append[get_wikipathway_from_pfocr_url(p)]
    elif pfocr_urls_file:
        fname = os.getcwd() + "/wikipathways_graphs/" + 'PFOCR_url_list.txt'
        f = open(fname, "r")
        data = f.read()
        pfocr_urls = data.split("\n")
        wikipathways = []
        for p in pfocr_urls:
            #Gets wikpathway from pfocr_url
            wikipathways.append(get_wikipathway_from_pfocr_url(p))
        if not os.path.isfile(fname):
            raise Exception('Missing file in wikipathways_graphs directory: ' + fname)
            logging.error('Missing file in wikipathways_graphs directory: ' + fname)

    return wikipathways


def main():

    kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping = generate_graphsim_arguments()

    input_dir = os.getcwd() + '/' + WIKIPATHWAYS_SUBFOLDER

    triples_list_file,labels_file = get_wikipathways_graph_files(input_dir,kg_type,input_type,guiding_term,input_substring)

    print("Creating knowledge graph object from inputs.....")

    g = create_graph(triples_list_file,labels_file, kg_type)

    wikipathways = get_wikipathways_list(wikipathways,pfocr_urls,pfocr_urls_file)

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    for wikipathway in wikipathways:

        output_dir = all_wikipathways_dir + '/' + wikipathway + '_output'
        
        #Check for existence of output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        #Downloads wikipathway diagrams as edgelists
        download_wikipathways_edgelist(all_wikipathways_dir,wikipathway)

        #Converts wikipathway diagram edgelists to format necessary for subgraph generation
        examples_file = convert_wikipathways_input(all_wikipathways_dir,wikipathway)

        #Index wikipathway diagram
        print("Mapping between user inputs and KG nodes for " + wikipathway + ".......")
    
        s = interactive_search_wrapper(g, [examples_file], output_dir, input_type,kg_type, enable_skipping)

        if guiding_term:

            guiding_term_df = interactive_search_wrapper(g, examples_file, output_dir, 'guiding_term', kg_type,input_dir)

        print("Mapping complete")


if __name__ == '__main__':
    main()


