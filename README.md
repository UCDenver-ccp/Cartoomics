# Cartoomics Figure Generation 

This Cartoomics repository consists of a workflow written in python that can generate an interaction network using a given knowledge graph from a automated or user derived description of a cartoon image. The goal of this workflow is to generate complete and detailed pathway diagrams using the vast information contained within a knowledge graph.

## Getting Started

These instructions will provide the necessary environments, programs with installation instructions, and input files in order to run the creating_subgraph_from_KG.py script, which will run this workflow from end to end. 

The path search algorithms available are:

- Shortest Path Search: find the shortest path between each source and target node. A random path is chosen from paths of identical length, regardless if graph is weighted or unweighted. Thus, shortest path may not be identical each time. 
- Cosine similarity Prioritization: prioritize all shortest paths between each source and target node by maximizing total cosine similarity of the start and all intermediate nodes to the target node in each path
- Path Degree Product Prioritization: prioritize all shortest paths between each source and target node by maximizing path degree product of all nodes in each path
- Edge Exclusion: remove specific semantic edge types from the paths for prioritization

The program will output a subgraph generated using both the Cosine Similarity and Path-Degree Product algorithms.

### Dependencies
The following dependencies are listed in the environment.yml file, and installed in the installation step. This software has only been tested on Unix based OS systems, not Windows.
```
Python>=3.8.3
tqdm>=4.64.0
gensim>=4.2.0
numpy>=1.22.4
scipy>=1.8.1
py4cytoscape>=1.3.0
csrgraph>=0.1.28
nodevectors>=0.1.23
igraph>=0.9.10
bioservices>=1.11.2
fiona>=1.9.5
geopandas>=0.14.1
shapely>=2.0.2
```

## Installation

```
git clone https://github.com/bsantan/Cartoomics-Grant
```

First install mamba, which will be used to create the environment. To create an environment with all dependencies and activate the environment, run the following commands:

```
conda install mamba

mamba env create -f environment.yml
conda activate Cartoomics
```

Ensure that Cytoscape (any version later than 3.8.0) is up and running before continuing.

## Running the Script

### Input Directory

The following files must exist in the input directory, in a folder named as is specified for the --knowledge-graph option:

<img width="994" alt="Screen Shot 2022-08-25 at 9 37 40 AM" src="https://user-images.githubusercontent.com/70932395/186709025-6eb4495d-6c12-4353-a1af-5626d835e4ea.png">

To access the v3 PheKnowLator knowledge graph, visit the GCS bucket: https://console.cloud.google.com/storage/browser/pheknowlator/current_build/knowledge_graphs/instance_builds/relations_only/owlnets?pageState=(%22StorageObjectListTable%22:(%22f%22:%22%255B%255D%22))&project=pheknowlator&prefix=&forceOnObjectsSortingFiltering=false

To access the kg-covid19 knowledge graph, visit the kg-covid19 Knowledge Graph Hub for the current tar.gz file (kg-covid-19.tar.gz):
https://kg-hub.berkeleybop.io/kg-covid-19/current/index.html

Add the necessary files for the knowledge graph (Triples file and Labels file) to a directory that also contains all files in the Input_Files folder of this repository, and specify this as your input directory.

### Defaults
  
The following values will be used if not otherwise specified:
- embedding dimensions: embeddings of the knowledge graph will be generated using node2vec of dimension 128, unless otherwise specified
  --embedding-dimensions <int> (Default 128)
- weights: edges will not be weighted unless otherwise specified. When set to True, edges defined in an interactive search will be excluded from the path search. 
  --weights True (Default False)
- search type: the shortest path algorithm used (contained within the python-igraph package) will search for paths in all directions, unless otherwise specified
  --search-type one (Default "all")

Below is an example of running this with the PheKnowLator knowledge graph. To specify the kg-covid19 knowledge graph, update the following command:
   
```
--knowledge-graph kg-covid19
```

Two different input edgelist types are supported:
1. annotated_diagram: This is user derived, based on a cartoon image, or automatically generated from a Wikipathways diagram (described in more detail below)
2. pathway_ocr: This is a automatically derived list of entities from within a Wikipathways diagram based on the Pathway Diagram Optical Character Recognition method (cite). When specified, a PFOCR url must be input either at execution time or later, if forgotten. 

Below is an example of running with an annotated diagram. To specify the pathway_ocr input type, update the following command:

```
--input-type pathway_ocr --pfocr-url <url>
```

### Command Line Argument: subgraph generation 
  
To run the script, execute the following command once the input directory is prepared:
  
```
python creating_subgraph_from_KG.py --input-dir INPUTDIR --output-dir OUTPUTDIR --knowledge-graph pkl --input-type annotated_diagram
```

**Note that the output-dir should be in quotes**

  
### Command Line Argument: evaluation files
  
To run the evaluation script, execute the following command once the subgraph generation script is run:
  
```
python evaluate_all_subgraphs.py --input-dir INPUTDIR --output-dir OUTPUTDIR --knowledge-graph pkl
```

## Expected Outputs
  
### Subgraph Files
  
The creating_subgraph_from_KG.py script will always generate the following files:
  
### Subgraph
  
A .csv file which shows all source and target nodes found in the path search that include the original example cartoon (Input file above) and any intermediate nodes found in the path search.

```
S|P|O
insulin receptor (human)|subClassOf|insulin receptor
insulin receptor (human)|participates_in|Insulin receptor signalling cascade
```
  
### Subgraph Attributes

A .noa file which specifies which input nodes are from the original example cartoon (Input file above) and which were intermediate nodes found in the path search. 
  
```
Node|Attribute
insulin receptor (human)|Extra
insulin receptor|Mechanism
```

### Subgraph Visualization
  
A .png file generated in cytoscape with all nodes found in the path search, colored by original nodes and intermediate nodes.

The creating_subgraph_using_cosinesim.py script will also generate the following intermediate files:
  
### Files generated for embeddings:
 
- PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integer_Identifier_Map
- PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integers_node2vecInput
- PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_node2vecInput_cleaned
- PheKnowLator_v3_node2vec_Embeddings<DIM>.emb (where <DIM> is the # dimensions specified)
  
*Note if the above files already exist in the output directory when running the script, the embeddings will not be re-generated.*

### Evaluation Files 
  
The evaluate_all_subgraphs.py script will always generate the following files:

### Number of Nodes Comparison
  
A .csv file with the number of nodes in each subgraph generated by algorithm (cs: Cosine Similarity, pdp: Path-Degree Product, and/or either with Edge Exclusion- ee_cs or ee_pdp).
  
```
cs,pdp
17,18
```
  
### Path Length Comparison
  
A .csv file with the path length of each pair that exists in each subgraph generated by algorithm (cs: Cosine Similarity, pdp: Path-Degree Product, and/or either with Edge Exclusion- ee_cs or ee_pdp).
  
```
cs,pdp
3,3
3,3
```
  
### Intermediate Nodes Comparison
  
A .csv file with the number of intermediate nodes between each specified pair that belong to ontologies (normalized). Defined for each subgraph generated by algorithm (cs: Cosine Similarity, pdp: Path-Degree Product, and/or either with Edge Exclusion- ee_cs or ee_pdp).
  
```
Ontology_Type,cs,pdp
/reactome,0.25,0.333
/PR_,0.16,0.16
/CHEBI_,0.33,0.25
```
  
### Path List (separate file for each algorithm (cs: Cosine Similarity, pdp: Path-Degree Product, and/or either with Edge Exclusion- ee_cs or ee_pdp)
  
A .csv file with the resulting calculation from each algorithm for each path from all-shortest paths. This value is used to rank each path and prioritize in the ranked_comparison.csv.
  
```
Value
1.14
0.83
```
  
### Ranked Comparison 
  
A .csv file with the rank of all paths for each algorithm, calculated using the path lists (cs: Cosine Similarity, pdp: Path-Degree Product, and/or either with Edge Exclusion- ee_cs or ee_pdp).
  
```
cs,pdp
0,1
1,3
3,2
2,0
```
  
## Wikipathways Diagram Input

The following details how to run the Cartoomics algorithm over a set of Wikipathways Diagrams in an automated fashion. This set of command line arguments will enable one to compare the output of pathway diagrams from Wikipathways to those generated with the cartoomics algorithms described above. 

### Command Line Arguments: Wikipathways Diagram download

The wikipathway_converter script which will download a single or set of pathway diagram(s) specified in a text file or via the command line to an edgelist. Next, the entites represented will be automatically indexed to nodes in the given KG. Indexing will be done using the Wikipathways diagram node metadata file, exact match to a node label, exact match to a node synonym, or partial match to the node label or synonyms.


The user can provide the following input types to specify the Wikipathways Diagrams to download and convert:
1. Wikipathway ID(s): a list of one or more Wikipathways ids: e.g., '['WP5372']'
2. PFOCR url(s): a list of one or more PFOCR urls, e.g. '['https://pfocr.wikipathways.org/figures/PMC6943888__40035_2019_179_Fig1_HTML.html']'
3. PFOCR_urls_file: a txt file containing one or more PFOCR urls. The PFOCR_urls_list.txt file can be used for this.

Below is an example of running this with the PheKnowLator knowledge graph. The annotated_diagram input type should always be used for this workflow.

```
python wikipathways_converter.py --knowledge-graph pkl --input-type annotated_diagram --pfocr-urls-file True
```

By default, if no nodes are found with the Wikipathways diagram node metadata file, exact match to a node label, or exact match to a node synonym, a partial match to the node label or synonyms will be used to index. When skipping is enabled, the node will be skipped and no triples with that node will be included in the subgraph. To enable skipping, udpate the following parameter:

```
python wikipathways_converter.py --wikipathway WIKIPATHWAY --input-type annotated_diagram --enable-skipping True
```

### Expected Outputs
  
#### Subgraph Files
  
The wikipathways_converter.py script will always generate the following files:
  
#### Wikipathways downloaded files

The following files will exist per Wikipathay diagram in a subfolder named by the Wikipathways ID, e.g. /wikipathways_graphs/<WP_ID>

1. WP4532_datanodeDF.csv: metadata file used to index nodes based on database, databaseID column
2. WP4532_edgeList.csv: edgelist used for comparison to original Wikipathways diagram
3. WP4532_graph.graphml: graphml file
4. WP4532_interactDF.csv: image description
  
#### Wikipathways edgelist in Cartoomics format

The following file will exist per Wikipathway diagram named by the Wikipathways ID, e.g., /wikipathways_graphs/annotated_diagram/<WP_ID>_example_input.csv

```
source|target
TCTEX1D2|WDR35
TCTEX1D2|IFT122
```

#### Wikipathways annotated edgelist to KG nodes

The following file will exist per Wikipathway diagram in a subfolder named by the Wikipathways ID, e.g. /wikipathways_graphs/<WP_ID>_output/_annotated_diagram_Input_Nodes_.csv

```
source|target|source_label|target_label|source_id|target_id
TCTEX1D2|WDR35|TCTEX1D2|WDR35|http://www.ncbi.nlm.nih.gov/gene/255758|http://www.ncbi.nlm.nih.gov/gene/57539
TCTEX1D2|IFT122|TCTEX1D2|IFT122|http://www.ncbi.nlm.nih.gov/gene/255758|http://www.ncbi.nlm.nih.gov/gene/55764
```

### Command Line Arguments: Wikipathways subgraph generation

This script can be run per Wikipathways diagram. To run the script for a Wikipathways diagram, execute the following command once the input directory is prepared:
  
```
'python creating_subgraph_from_KG.py --input-dir ./wikipathways_graphs --output-dir ./wikipathways_graphs/<WP_ID>_output --knowledge-graph pkl --input-type annotated_diagram --input-substring <WP_ID>
```

**Note that the output-dir should be in quotes**

The outputs will be the same as stated above in subgraph generation, within the /<WP_ID>_output subfolder.

### Command Line Arguments: compare subgraphs


The wikipathways_graph_evaluations script will output graph similarity metrics and node/edge evaluation metrics. The script will calculate the following graph similarity metrics over the original edgelist and the subgraph created for all pathways specified:
- Jaccard Similarity
- Overlap Coefficient
- Graph Edit Distance 


Additionally, the script will output the following node and edge metrics for all pathways specified:
- % of nodes in each ontology
- % of edge types

To run the wikipathways_graph_evaluations script, specify the wikipathway diagrams as a list e.g., '['WP5372']':

```
python wikipathways_graph_evaluations.py --knowledge-graph pkl --input-type annotated_diagram --wikipathways WIKIPATHWAYS --enable-skipping True
```

**Note that all subgraph files (described above) must be generated**
 
### Expected Outputs


All of the graph similarity files will be output in a graph_similarity subfolder within the wikipathways_graphs subfolder './wikipathways_graphs/graph_similarity'.
  
#### Graph Similarity Metrics 
  
A .csv file with the Jaccard and Overlap metrics per Wikipathways diagram per algorithm.

```
Algorithm,Pathway_ID,Jaccard,Overlap
CosineSimilarity,WP554,0.33,0.66
CosineSimilarity,WP5373,0.25,0.66 
PDP,WP554,0.25,0.33
PDP,WP5373,0.33,0.33
```
  
### Jaccard and Overlap Histogram
  
A .png file of all Jaccard and Overlap scores per Wikipathways diagram per algorithm. 


### Command Line Arguments: Wikipathways Literature Comparison

The wikipathways_literature_comparison_evaluations script will compare each subgraph specified to a given set of one or more guiding terms extracted from literature using cosine similarity. The intermediate nodes in all subgraphs of the specified algorithms will be compared to each term specified after indexing. 

The following file must exist, where WP_ID corresponds to the wikipathway(s) specified:

```
~/wikipathways_graphs/<WP_ID>_Literature_Comparison_Terms.csv
```

To run the wikipathways_literature_comparison_evaluations script, specify the wikipathway diagrams as a list e.g., '['WP5372']':

```
python wikipathways_literature_comparison_evaluations.py --knowledge-graph pkl --input-type annotated_diagram --wikipathways WIKIPATHWAYS --enable-skipping True
```

### Expected Outputs

All of the literature comparison files will be output in a literature_comparison subfolder within the wikipathways_graphs subfolder './wikipathways_graphs/literature_comparison'.

**Note that all subgraph files (described above in Wikipathways subgraph generation) will be generated**
  
#### Literature Comparison Metrics

All of the literature comparison files will be output in a literature_comparison subfolder within the wikipathways_graphs subfolder './wikipathways_graphs/literature_comparison'.

A .csv file of the average Cosine Similarity scores per term, per subgraph, per algorithm specified will be output.

```
Term,Average_Cosine_Similarity,Algorithm,Pathway_ID
Alzheimer's disease,-0.05,CosineSimilarity,WP4565
Alzheimer's disease,-0.02,PDP,WP4565
```

## Output Structure
  
```
├── Inputs
│   ├── annotated_diagram
│   │   └── _example_input.csv
│   ├── GuidingTerm.csv
│   ├── experimental_data
│   ├── kg-covid19
│   │   ├── merged-kg_Triples_Integer_Identifier_Map.tsv
│   │   ├── merged-kg_Triples_Integers_node2vecInput.tsv
│   │   ├── merged-kg_Triples_node2vecInput_cleaned.tsv
│   │   └── merged-kg_edges_node2vec_Embeddings128.emb
│   ├── pathway_ocr_diagram
│   │   ├── chemicals.tsv
│   │   ├── diseases.tsv
│   │   └── genes.tsv
│   └── pkl
│       ├── PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_NodeLabels.txt
│       ├── PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Identifiers.txt
│       ├── PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integer_Identifier_Map.txt
│       ├── PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_Integers_node2vecInput.txt
│       ├── PheKnowLator_v3.0.2_full_instance_relationsOnly_OWLNETS_Triples_node2vecInput_cleaned.txt
│       └── PheKnowLator_v3_node2vec_Embeddings128.emb
└── Outputs
    ├── CosineSimilarity
    │   ├── Subgraph.csv
    │   ├── Subgraph_Visualization.png
    │   └── Subgraph_attributes.noa
    ├── Evaluation_Files
    │   ├── edge_type_comparison.csv
    │   ├── intermediate_nodes_comparison.csv
    │   ├── num_nodes_comparison.csv
    │   ├── num_paths_CosineSimilarity.csv
    │   ├── num_paths_PDP.csv
    │   ├── path_length_comparison.csv
    │   ├── paths_list_CosineSimilarity_0-9.csv
    │   ├── paths_list_PDP_0-9.csv
    │   └── ranked_comparison.csv
    ├── PDP
    │   ├── Subgraph.csv
    │   ├── Subgraph_Visualization.png
    │   └── Subgraph_attributes.noa
    ├── Guiding_Term_<specified_term>
    │   ├── Subgraph.csv
    │   ├── Subgraph_Visualization.png
    │   └── Subgraph_attributes.noa
    ├── _annotated_diagram_Input_Nodes_.csv
    ├── _guiding_term_Input_Nodes_.csv
    ├── experimental_data_Input_Nodes_.csv
    └── pathway_ocr_Input_Nodes_.csv
```
  

# Software Design
  
Below is a class diagram describing the architecture of this workflow.
  
<img width="1017" alt="Screen Shot 2022-08-25 at 9 24 11 AM" src="https://user-images.githubusercontent.com/70932395/186705860-6982c26c-2b62-4dbc-9508-7f5de828849e.png">
