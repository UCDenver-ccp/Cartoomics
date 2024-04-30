import os
import csv
import pandas as pd
import argparse
from assign_nodes import convert_to_uri,normalize_node_api,create_skipped_node_file,map_input_to_nodes,manage_user_input
from graph_similarity_metrics import get_wikipathways_graph_files
from create_graph import create_graph

from constants import (
    ALL_WIKIPATHWAYS,
    LITERATURE_SEARCH_TYPES,
    PKL_SUBSTRINGS,
    PKL_OBO_URI,
    WIKIPATHWAYS_SUBFOLDER
)

#Generates unannotated file of terms from manually curated keywords
def generate_keywords_file(output_path,metadata_df,wikipathway):

    terms = metadata_df.loc[metadata_df['Pathway_ID'] == wikipathway,'Keywords'].values[0].split(';')

    df = pd.DataFrame(terms,columns=['term'])

    df.to_csv(output_path,index=False)

#Generates annotated file using concept annotations
def generate_abstract_file_concept_annotations(file,labels,enable_skipping):

    df = pd.DataFrame(columns = ['term','term_label','term_id','NER_Method'])
    

    id_df = pd.read_csv(file,header=None,sep='\t')
    id_df.columns = [['TermID','Term_Info','Label']]

    guiding_term_skipped_nodes = []

    for i in range(len(id_df)):
        annotated_terms = {}
        use_node = True
        
        curie = id_df.iloc[i].loc['Term_Info'].iloc[0].split(' ')[0]
        #Remove _CC, _BP from GO terms
        if "GO_" in curie:
            id = curie.split(":")[1]
            curie = "GO_" + id
        curie = curie.replace('_',":")
        ##Transform to known ontologies
        if "DRUGBANK" in curie:
            curie = normalize_node_api(curie)
        uri = convert_to_uri(curie)

        if enable_skipping:
            #Ensure that uri is in PheKnowLator
            try:
                label = labels.loc[labels['entity_uri'] == uri,'label'].values[0]
            except IndexError:
                guiding_term_skipped_nodes.append(id_df.iloc[i].loc['Label'].values[0])
                use_node = False

        if use_node:
            #Add term
            annotated_terms['term'] = id_df.iloc[i].loc['Label'].iloc[0]
            #Add term_label
            annotated_terms['term_label'] = id_df.iloc[i].loc['Label'].iloc[0]
            #Add term_id
            annotated_terms['term_id'] = uri
            #Add method
            annotated_terms['NER_Method'] = 'lab'
            d = pd.DataFrame([annotated_terms])
            df = pd.concat([d,df])

    return df,guiding_term_skipped_nodes

#assumes skipping is enabled
def generate_abstract_file_models(file,wikipathway,g,literature_annotations_df,guiding_term_skipped_nodes,method):

    df = pd.read_csv(file,sep=',')
    df = df.loc[df['PubMed_id'] == wikipathway]

    new_node_rows = []

    for i in range(len(df)):
        node_label = df.iloc[i].loc['entity'].lower()

        found_nodes,nrow,exact_match = map_input_to_nodes(node_label,g,'true')
        
        if exact_match: 
            node_label,bad_input,id_given = manage_user_input(found_nodes,found_nodes,g,exact_match)
            node_uri = id_given
        else:
            if len(found_nodes) < 4:
                for i in range(len(found_nodes)):
                    if "MONDO" in found_nodes.iloc[i].loc['entity_uri']:
                        node_uri = found_nodes.iloc[i].loc['entity_uri']
                else:
                    node_uri = 'none'
            else:
                node_uri = 'none'
                guiding_term_skipped_nodes.append(node_label)

        new_node_rows.append([node_label,node_label,node_uri,method])

    annotations_df = pd.DataFrame(new_node_rows, columns = literature_annotations_df.columns) 

    literature_annotations_df = pd.concat([literature_annotations_df,annotations_df])

    return literature_annotations_df,guiding_term_skipped_nodes

def main():

    #Hardcoded for now to skip terms that are annotated but not in PheKnowLator
    enable_skipping = True

    metadata_file = os.getcwd() + "/Wikipathways_Text_Annotation/Wikipathways_MetaData.csv"

    all_wikipathways_dir = os.getcwd() + "/" + WIKIPATHWAYS_SUBFOLDER

    triples_list_file,labels_file = get_wikipathways_graph_files(all_wikipathways_dir,'pkl','annotated_terms')

    g = create_graph(triples_list_file,labels_file, 'pkl')

    metadata_df = pd.read_csv(metadata_file,sep=',')
    # Using external list of wikipathways instead
    # wikipathways = metadata_df.Pathway_ID.unique()

    #Files to read
    gpt4_file = os.getcwd() + "/Wikipathways_Text_Annotation/pfocr_abstracts_GPT4.csv"
    ner_file = os.getcwd() + "/Wikipathways_Text_Annotation/pfocr_abstracts_NER_processed.csv"

    for wikipathway in ALL_WIKIPATHWAYS:

        for search_type in LITERATURE_SEARCH_TYPES:

            # Search by ID, PMID for abstracts, PMC for full text
            if search_type == "abstract":
                search_id = "PMID"
            elif search_type == "full_text":
                # PMC3514635 missing
                search_id = "PMC"
            
            id = str(metadata_df.loc[metadata_df['Pathway_ID'] == wikipathway,search_id].values[0])
            if id == "nan": continue
            #File to read
            id_file = os.getcwd() + "/Wikipathways_Text_Annotation/Concept_Annotations_" + search_type + "/" + id + ".bionlp"

            base_dir = all_wikipathways_dir + '/literature_comparison/' + search_type
            wikipathway_output_dir = all_wikipathways_dir + "/" + wikipathway + "_output/"
            wikipathway_specific_dir = wikipathway_output_dir + search_type

            # Create directories
            os.makedirs(base_dir, exist_ok=True)
            os.makedirs(wikipathway_specific_dir, exist_ok=True)


            #output_path = base_dir + '/' + wikipathway + '_Literature_Comparison_Terms.csv'

            #generate_keywords_file(output_path,metadata_df,wikipathway)

            #For Hunter Lab concept annotations
            literature_annotations_df,guiding_term_skipped_nodes = generate_abstract_file_concept_annotations(id_file,g.labels_all,enable_skipping)

            if search_type == "abstract":
                #For NER concept annotation
                literature_annotations_df,guiding_term_skipped_nodes = generate_abstract_file_models(ner_file,wikipathway,g,literature_annotations_df,guiding_term_skipped_nodes,'ner')

                #For GPT concept annotation
                literature_annotations_df,guiding_term_skipped_nodes = generate_abstract_file_models(gpt4_file,wikipathway,g,literature_annotations_df,guiding_term_skipped_nodes,'gpt')

            df_file = wikipathway_specific_dir + "/_literature_comparison_Input_Nodes_.csv"

            #For comparing cosine similarity across all abstracts - used by wikipathways_literature_comparison_evaluations.py
            df_specific_file = base_dir + "/" + wikipathway + "_literature_comparison_Input_Nodes_.csv"

            literature_annotations_df = literature_annotations_df.drop_duplicates()
            literature_annotations_df.to_csv(df_file,sep='|',index=False)
            #Write the same file to a general folder for comparing cosine similarity across all abstracts
            literature_annotations_df.to_csv(df_specific_file,sep='|',index=False)

            #Creates a skipped_node file per input diagram
            if enable_skipping:
                create_skipped_node_file(guiding_term_skipped_nodes,wikipathway_output_dir,'guidingTerms')

if __name__ == '__main__':
    main()



