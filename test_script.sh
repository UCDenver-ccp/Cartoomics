#! /bin/bash

# python creating_subgraph_from_KG.py --input-dir ./IM_Inputs/IL-1RA-Glutamate --output-dir ./IM_Outputs/IL-1RA-Glutamate --knowledge-graph pkl --input-type annotated_diagram

#Command to run test dataset
#python creating_subgraph_from_KG.py --input-dir ./Test_Data/Inputs_TestGraph  --output-dir ./Outputs_TestGraph --knowledge-graph pkl --input-type annotated_diagram

#Command to test pfocr input
#python creating_subgraph_from_KG.py --input-dir ./pfocr_tests --output-dir ./pfocr_tests --knowledge-graph pkl --input-type pathway_ocr --pfocr_url https://pfocr.wikipathways.org/figures/PMC5095497__IMM-149-423-g007.html

#Command to run annotated diagram input
#python creating_subgraph_from_KG.py --input-dir ./Test_Data/Inputs_Neuroinflammation  --output-dir ./Test_Data/Outputs_Neuroinflammation --knowledge-graph pkl --input-type annotated_diagram

#Command to test metapaths generation
#python creating_metapaths_from_KG.py --input-dir ./metapath_tests --output-dir ./metapath_tests --knowledge-graphs "['pkl']" --num-iterations 1 --batch-size 1 --node-input1 gene --node-input2 mondo

#Command to plot metapaths generated above
#python Paths_Distribution_Plot.py --directory ./metapath_tests --min-counts 1 --node-input1 gene --node-input2 disease

#Command to test guiding term input
#python creating_subgraph_from_KG.py --input-dir ./Test_Data/Inputs_Neuroinflammation  --output-dir ./Test_Data/Outputs_Neuroinflammation --knowledge-graph pkl --input-type annotated_diagram --guiding-term True
#python creating_subgraph_from_KG.py --input-dir ./Test_Data/Inputs_Covid19  --output-dir ./Test_Data/Inputs_Covid19 --knowledge-graph kg-covid19 --input-type annotated_diagram --guiding-term True

#Command to test wikipathways_converter with pfocr urls file
#python wikipathways_converter.py --knowledge-graph pkl --input-type annotated_diagram --pfocr-urls-file True --enable-skipping True

#Command to test wikipathways pipeline by ID with smaller graph
#python call_all_pathways_wrapper.py --knowledge-graph pkl --input-type annotated_diagram --wikipathways "['WP4533']" --enable-skipping True

#Command to visualize wikipathways output
#python visualize_in_cytoscape.py --knowledge-graph pkl --input-type annotated_diagram --wikipathways "['WP4533']" --enable-skipping True

#Command to test the wikipathways converter step for the ablation study
#python wikipathways_converter_ablations.py --knowledge-graph pkl --input-type annotated_diagram --pfocr-urls-file True --enable-skipping True
#Update call_all_pathways_wrapper.py input and output directories to include _ablation
#Update wikipathways_graph_evaluations.py, wikipathways_literature_comparison_evaluations.py, with ablation=true
#Literature evaluation
#python wikipathways_literature_comparison_evaluations.py --knowledge-graph pkl --input-type annotated_diagram --wikipathways "['WP4533', 'WP4534', 'WP4537', 'WP4538', 'WP4539', 'WP4542', 'WP4553', 'WP4562', 'WP4564', 'WP4565', 'WP4760', 'WP4856', 'WP5358', 'WP5368', 'WP5372', 'WP5373', 'WP5382', 'WP5385']" --enable-skipping True #'WP4532',     'WP4535' 'WP4829', 'WP5283', 
python wikipathways_idf_evaluations.py --knowledge-graph pkl --input-type annotated_diagram --wikipathways "['WP4532', 'WP4533', 'WP4534', 'WP4537', 'WP4538', 'WP4539', 'WP4542', 'WP4553', 'WP4562', 'WP4564', 'WP4565', 'WP4760', 'WP4856', 'WP5358', 'WP5368', 'WP5372', 'WP5373', 'WP5382', 'WP5385']" --enable-skipping True
