

#Input a table of source and target nodes with their correspoding labels in PKL and generate the full pathway of triples. The Input nodes file format is: Source (PKL Node Label), Target (PKL Node Label), "|" delimited. Output will be 1 csv file of triples, 1 noa file of node attributes (Mechanism, Extra), and a Results file including the Path Length and result (exists, nonexistant) for each source/target pair. Input weighted edges as a string in the for of a list of edges, i.e. '[relationship_1, relationship_2]'

#python Mechanism_Predictions_FullPathway.py --triples-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers_withGutMGene_withMicrobes.txt --triples-integers-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_node2vecInput_cleaned_withGutMGene_withMicrobes.txt --pkl-labels-file /Users/brooksantangelo/Documents/HunterLab/Exploration/PKL_v3/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels.txt --gutmgene-labels-file /Users/brooksantangelo/Documents/Rotation2/Rocky/PKL_Additions/GutMGene/LabelTypes_gutMGene_URI_LABEL_MAP_contextual_manualRelationLabels.csv --pkl-identifiers-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integer_Identifier_Map_withGutMGene_withMicrobes.json --input-nodes-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant/Kynurenine_Pathway_Input_Nodes.csv --output-dir /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant

#python Mechanism_Predictions_FullPathway.py --triples-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers_withGutMGene_withMicrobes.txt --triples-integers-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_node2vecInput_cleaned_withGutMGene_withMicrobes.txt --pkl-labels-file /Users/brooksantangelo/Documents/HunterLab/Exploration/PKL_v3/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels.txt --gutmgene-labels-file /Users/brooksantangelo/Documents/Rotation2/Rocky/PKL_Additions/GutMGene/LabelTypes_gutMGene_URI_LABEL_MAP_contextual_manualRelationLabels.csv --pkl-identifiers-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integer_Identifier_Map_withGutMGene_withMicrobes.json --input-nodes-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant/UpdatedPathway/Kynurenine_Pathway_Input_Nodes_Updated.csv --output-dir /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant/UpdatedPathway/KynurenineUnweightedResult --mechanism-name Kynurenine_Pathway --original-nodes-file /Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant/kynurenine_pathway_original_pklv3.csv

import pandas as pd
import csv
import copy
import json
from igraph import *
from tqdm import tqdm
import os

import argparse


#Define arguments for each required and optional input
def defineArguments():
    parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--triples-file",dest="TriplesFile",required=True,help="TriplesFile")
    #'/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers_withGutMGene_withMicrobes.txt'

    parser.add_argument("--triples-integers-file",dest="TriplesIntegersFile",required=True,help="TriplesIntegersFile")
    #'/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_node2vecInput_cleaned_withGutMGene_withMicrobes.txt'

    parser.add_argument("--pkl-microbiome-labels-file",dest="PklMicrobiomeLabelsFile",required=True,help="PklMicrobiomeLabelsFile")
    #"/Users/brooksantangelo/Documents/HunterLab/Exploration/PKL_v3/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels.txt"

    parser.add_argument("--pkl-identifiers-file",dest="PklIdentifiersFile",required=True,help="PklIdentifiersFile")
    #'/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/Output/PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integer_Identifier_Map_withGutMGene_withMicrobes.json'

    parser.add_argument("--input-nodes-file",dest="InputNodesFile",required=True,help="InputNodesFile")
    #/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant/Kynurenine_Pathway_Input_Nodes.csv

    parser.add_argument("--original-nodes-file",dest="OriginalNodesFile",required=False,help="OriginalNodesFile")
    #/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant/Kynurenine_Pathway_Input_Nodes.csv

    parser.add_argument("--weight-important-edges",dest="WeightImportantEdges",required=False,help="WeightImportantEdges")
    parser.add_argument("--output-dir",dest="OutputDir",required=True,help="OutputDir")
    #/Users/brooksantangelo/Documents/HunterLab/GutMGene_PKL/CartoomicsGrant
    parser.add_argument("--mechanism-name",dest="MechanismName",required=True,help="MechanismName")

    parser.add_argument("--search-type",dest="SearchType",required=False,default='OUT',help="SearchType")

    parser.add_argument("--network-type",dest="NetworkType",required=False,default='shortest path',help="NetworkType")

    return parser


###Read in all files
def process_files(triples_file,pkl_microbiome_labels_file,pkl_identifiers_file,triples_integers_file,input_nodes_file):

    #Read in triples file to list
    with open(triples_file, 'r') as f_in:
        #Length matches original file length
        triples = set(tuple(x.split('\t')) for x in f_in.read().splitlines())
        f_in.close()

    triples_list = list(triples)

    triples_list = [ x for x in triples_list if "subject" not in x ]
    triples_list = [ x for x in triples_list if "Subject" not in x ]

    labels_all = {}

    with open(pkl_microbiome_labels_file) as f_in:
        for line in f_in:
            vals = line.strip().split("\t")
            try:
                #key, value = vals[2:4]
                key, value = vals[0:2]
                labels_all[key] = value
            except: pass

    #Read in identifiers file to dictionary
    f = open(pkl_identifiers_file)
    identifiers = json.load(f)

    #Read in node2vec input triples integers file as df
    edgelist_int = pd.read_csv(triples_integers_file, sep=" ")

    #Read in input nodes file as df
    input_nodes = pd.read_csv(input_nodes_file, sep=',')  #'|')

    return triples_list,labels_all,identifiers,edgelist_int,input_nodes

def generate_graph(triples_integers_file):

    #Read in edge list to igraph
    g = Graph.Read_Ncol(triples_integers_file, directed=True)
    g_nodes = g.vs()['name']  

    return g,g_nodes 

def get_url(labels,value):

    for key, val in labels.items(): 
        if val == value:
            return key

def get_key(dictionary,value):
    for key, val in dictionary.items():
        if val == value:
            return key


def weight_edges(g,triples_list,labels,weight_important_edges):

    #important_edges = ['participates in','molecularly interacts with','has gene product','has function']

    g_weights_list = []

    for i in range(len(triples_list)):
        if labels[triples_list[i][1]] in weight_important_edges:
            g_weights_list.append(1)
        else:
            g_weights_list.append(99)

    g.es["weight"] = g_weights_list

    return g

def find_full_network(node,triples_list,labels_all,df):

    for i in range(len(triples_list)):
        d = {}
        if node == labels_all[triples_list[i][0]] or node == labels_all[triples_list[i][2]]:
            d['S'] = labels_all[triples_list[i][0]]
            d['P'] = labels_all[triples_list[i][1]]
            d['O'] = labels_all[triples_list[i][2]]
            df = df.append(d,ignore_index=True)

    return df

def find_shortest_path(start_node,end_node,graph,g_nodes,identifiers,labels_all,triples_list,df,weights,search_type):
    
    node1 = str(identifiers[get_url(labels_all,start_node)])
    node2 = str(identifiers[get_url(labels_all,end_node)])

    #Add weights if specified
    if weights:
        w = graph.es["weight"]
    else:
        w = None

    #list of nodes
    path_nodes = graph.get_shortest_paths(v=node1, to=node2, weights=w, mode=search_type)

    paths = []

    print(path_nodes)

    #When there is no connection in graph, path_nodes will equal 1 ([[]])
    if len(path_nodes[0]) != 0:
        n1 = labels_all[get_key(identifiers,int(g_nodes[path_nodes[0][0]]))]
        for i in range(1,len(path_nodes[0])):
            idx = path_nodes[0][i]
            n2 = labels_all[get_key(identifiers,int(g_nodes[idx]))]
            for i in range(len(triples_list)):
                l = []
                if search_type.lower() == 'all':
                    if n1 == labels_all[triples_list[i][0]] and n2 == labels_all[triples_list[i][2]]:
                        l.append(labels_all[triples_list[i][0]])
                        l.append(labels_all[triples_list[i][1]])
                        l.append(labels_all[triples_list[i][2]])
                        paths.append(l)
                        break
                    elif n1 == labels_all[triples_list[i][2]] and n2 == labels_all[triples_list[i][0]]:
                        l.append(labels_all[triples_list[i][0]])
                        l.append(labels_all[triples_list[i][1]])
                        l.append(labels_all[triples_list[i][2]])
                        paths.append(l)
                elif search_type.lower() == 'out':
                    if n1 == labels_all[triples_list[i][0]] and n2 == labels_all[triples_list[i][2]]:
                        l.append(labels_all[triples_list[i][0]])
                        l.append(labels_all[triples_list[i][1]])
                        l.append(labels_all[triples_list[i][2]])
                        paths.append(l)
            n1 = n2

        #Generate df
        df = pd.DataFrame(paths,columns = ['S','P','O'])
        return df,'exists'

    else: 

        return df,'nonexistant'

def create_node_attributes(list_of_pairs,full_mechanism_df,network_type):
    
    if network_type == 'shortest path':
        all_nodes = [j for i in list_of_pairs for j in i]
    
    else: 
        all_nodes = list_of_pairs

    full_mechanism_attribute_df = pd.DataFrame(columns = ['Node','Attribute'])
        
    for i in range(len(full_mechanism_df)):
        #Only add subject and object columns, not the predicate
        for col in [0,2]:
            d = {}
            d['Node'] = full_mechanism_df.iloc[i,col]
            if d['Node'] in all_nodes:
                d['Attribute'] = 'Mechanism'
            else:
                d['Attribute'] = 'Extra'
            full_mechanism_attribute_df = full_mechanism_attribute_df.append(d,ignore_index=True)

    full_mechanism_attribute_df = full_mechanism_attribute_df.drop_duplicates(subset=['Node'])
    full_mechanism_attribute_df = full_mechanism_attribute_df.reset_index(drop=True)
    
    return full_mechanism_attribute_df


def create_csv_file(df,output_dir,mechanism_name,delimiter_used):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df.to_csv(output_dir+"/"+mechanism_name+'.csv',sep=delimiter_used,index=False)

def create_noa_file(df,output_dir,mechanism_name):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    l = df.values.tolist()

    with open(output_dir+"/"+mechanism_name+'_attributes.noa', "w", newline="") as f:
        writer = csv.writer(f,delimiter='|')
        writer.writerow(["Node","Attribute"])
        writer.writerows(l)

def show_original_nodes(full_mechanism_attribute_df,orig_nodes):

    orig_nodes_list =  orig_nodes.values.tolist()

    full_mechanism_attribute_df_new = copy.deepcopy(full_mechanism_attribute_df)

    for i in range(len(full_mechanism_attribute_df_new)):
        if full_mechanism_attribute_df_new.iloc[i].loc['Node'] in orig_nodes_list:
            full_mechanism_attribute_df_new.iloc[i].loc['Attribute'] = 'Mechanism'
        else:
            full_mechanism_attribute_df_new.iloc[i].loc['Attribute'] = 'Extra'

    return full_mechanism_attribute_df_new

def main():

    #Generate argument parser and define arguments
    parser = defineArguments()
    args = parser.parse_args()
    

    triples_file = args.TriplesFile
    pkl_microbiome_labels_file = args.PklMicrobiomeLabelsFile
    #gutmgene_labels_file = args.GutMGeneLabelsFile
    pkl_identifiers_file = args.PklIdentifiersFile
    triples_integers_file = args.TriplesIntegersFile
    input_nodes_file = args.InputNodesFile
    original_nodes_file = args.OriginalNodesFile
    weight_important_edges = args.WeightImportantEdges
    mechanism_name = args.MechanismName
    output_dir = args.OutputDir
    search_type = args.SearchType
    network_type = args.NetworkType

    #Establish if edge weights are desired
    if weight_important_edges:
        weights = True
    else:
        weights = False

    triples_list, labels_all, identifiers, edgelist_int, input_nodes = process_files(triples_file,pkl_microbiome_labels_file,pkl_identifiers_file,triples_integers_file,input_nodes_file)

    g, g_nodes = generate_graph(triples_integers_file)

    #Full mechanism will be all sub networks between list of pairs
    full_mechanism_df = pd.DataFrame(columns = ['S','P','O'])

    if network_type == 'full':
        
        mechanism_name = mechanism_name + '_full_network'

        nodes = pd.unique(input_nodes[["Source", "Target"]].values.ravel())

        for i in nodes:
            full_mechanism_df = find_full_network(i,triples_list,labels_all,full_mechanism_df)

        list_of_pairs = nodes
        
    elif network_type == 'shortest path':

        if weights:
            g = weight_edges(g,triples_list,labels_all,weight_important_edges)

        list_of_pairs = input_nodes.values.tolist()

        #Log of what mechanisms were generated
        mechanisms_generated = pd.DataFrame(columns = ['Source','Target','Path_Length','Result'])
        results_list = []

        #Full mechanism will be all sub networks between list of pairs
        #full_mechanism_df = pd.DataFrame(columns = ['S','P','O'])

        path_length = 0

        #list_of_pairs is a list of lists
        for i in tqdm(list_of_pairs):
            print(i)

            path_length_start = len(full_mechanism_df)

            full_mechanism_df,result = find_shortest_path(i[0],i[1],g,g_nodes,identifiers,labels_all,triples_list,full_mechanism_df,weights,search_type)

            results_list.append(result)

            #Log results
            d = {}
            d['Source'] = i[0]
            d['Target'] = i[1]
            d['Path_Length'] = len(full_mechanism_df) - path_length_start
            d['Result'] = result
            mechanisms_generated = mechanisms_generated.append(d,ignore_index=True)


    full_mechanism_df = full_mechanism_df.drop_duplicates(subset=['S','P','O'])
    full_mechanism_df = full_mechanism_df.reset_index(drop=True)
    create_csv_file(full_mechanism_df,output_dir,mechanism_name,'|')

    #Create attribute file 
    full_mechanism_attribute_df = create_node_attributes(list_of_pairs,full_mechanism_df,network_type)

    if original_nodes_file:
        #Read in original nodes file as df
        orig_nodes = pd.read_csv(original_nodes_file, sep='|')
        full_mechanism_attribute_df_orig = show_original_nodes(full_mechanism_attribute_df,orig_nodes)
        create_noa_file(full_mechanism_attribute_df_orig,output_dir,mechanism_name+'_orig')
    else:
        create_noa_file(full_mechanism_attribute_df,output_dir,mechanism_name)

    if network_type == 'shortest path':
        create_csv_file(mechanisms_generated,output_dir,mechanism_name+'_Input_Nodes_Result',',')

if __name__ == '__main__':
    main()
