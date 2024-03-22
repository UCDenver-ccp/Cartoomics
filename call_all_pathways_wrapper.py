from inputs import *
import os
from wikipathways_converter import get_wikipathways_list
from graph_similarity_metrics import *

def main():

    kg_type,embedding_dimensions,weights,search_type, pdp_weight,input_type, cosine_similarity, pdp, guiding_term, input_substring,wikipathways,pfocr_urls,pfocr_urls_file,enable_skipping = generate_graphsim_arguments()

    wikipathways = get_wikipathways_list(wikipathways,pfocr_urls,pfocr_urls_file)

    for wikipathway in wikipathways:
        try:
            #Next generate subgraphs of wikipathways graphs
            command = 'python creating_subgraph_from_KG.py --input-dir ./wikipathways_graphs --output-dir ./wikipathways_graphs/' + wikipathway + '_output' + ' --knowledge-graph pkl --input-type annotated_diagram --input-substring ' + wikipathway + ' --enable-skipping True'

            os.system(command)
        except:
            pass


if __name__ == '__main__':
    main()