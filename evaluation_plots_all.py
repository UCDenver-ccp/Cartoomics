from inputs import *
from create_graph import create_graph
from assign_nodes import *
from evaluation import *
import textwrap

from wikipathways_converter import get_wikipathways_list
from graph_similarity_metrics import *
from constants import (
    WIKIPATHWAYS_SUBFOLDER
)


'''def read_edge_type_file(all_dfs,output_dir):

    edge_type_comparison_file = output_dir + '/Evaluation_Files/edge_type_comparison.csv'

    df = pd.read_csv(edge_type_comparison_file,sep=',')

    all_dfs = pd.concat([all_dfs,df], axis=0)

    return all_dfs'''

'''def read_ontology_type_file(all_dfs,output_dir):

    intermediate_nodes_comparison_file = output_dir + '/Evaluation_Files/intermediate_nodes_comparison.csv'

    df = pd.read_csv(intermediate_nodes_comparison_file,sep=',')

    all_dfs = pd.concat([all_dfs,df], axis=0)

    return all_dfs'''

#Generates histogram with N number of categories by pathway, where lists are the input
def edge_type_comparison_visualization(output_dir,df):

    output_folder = output_dir+'/node_edge_evaluation'

    plt_file = output_folder + '/edge_type_comparison.png'
    sns_plot = sns.barplot(df, x='Edge_Type', y = 'Percent_Edges',hue='Algorithm',errorbar=None)
    sns_plot.set_title("Edge Type Comparison for all Wikipathway Diagrams")
    wrap_labels(sns_plot, 20)
    sns_plot.tick_params(axis='x', labelrotation=45)
    plt.tick_params(axis='x', which='major', labelsize=7)
    plt.savefig(plt_file,bbox_inches="tight")
    plt.close()
    logging.info('Created png: %s',plt_file)

def wrap_labels(ax, width, break_long_words=False):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        labels.append(textwrap.fill(text, width=width,
                      break_long_words=break_long_words))
    ax.set_xticklabels(labels, rotation=0)

def intermediate_nodes_comparison_visualization(output_dir,df):

    output_folder = output_dir+'/node_edge_evaluation'

    plt_file = output_folder + '/intermediate_nodes_comparison.png'
    sns_plot = sns.barplot(df, x='Ontology_Type', y = 'Percent_Nodes',hue='Algorithm',errorbar=None)
    sns_plot.set_title("Ontology Type Comparison for all Wikipathway Diagrams")
    plt.savefig(plt_file,bbox_inches="tight")
    plt.close()
    logging.info('Created png: %s',plt_file)

#Generates histogram with N number of categories by pathway, where lists are the input
def visualize_graph_similarity_metrics(results_file,all_wikipathways_dir):
    
    results_df = pd.read_csv(results_file,sep=',')
    algorithms = results_df.Algorithm.unique()

    for algorithm in algorithms:

        df = results_df.loc[results_df['Algorithm'] == algorithm]

        plt_file = all_wikipathways_dir + '/graph_similarity/' + algorithm + '_Graph_Similarity_Metrics_Jaccard_Overlap.png'
        sns_plot = sns.barplot(df, x='Pathway_ID', y = 'Score',hue='Metric',errorbar=None)
        sns_plot.set_title("Graph Similarity Metrics for Wikipathways Diagrams and "+ algorithm)
        plt.xticks(rotation=45)
        plt.savefig(plt_file,bbox_inches="tight")
        plt.close()
        logging.info('Created png: %s',plt_file)

def visualize_graph_node_percentage_metrics(results_file,all_wikipathways_dir):
    
    results_df = pd.read_csv(results_file,sep=',')
    algorithms = results_df.Algorithm.unique()
    metrics = results_df.Metric.unique()

    for algorithm in algorithms:

        df = results_df.loc[results_df['Algorithm'] == algorithm]

        plt_file = all_wikipathways_dir + '/graph_similarity/' + algorithm + '_Graph_Node_Percentage_Metrics.png'
        sns_plot = sns.barplot(df, x='Pathway_ID', y = 'Score',hue='Metric',errorbar=None)
        sns_plot.set_title("Graph Node Percentage Metrics for Wikipathways Diagrams and "+ algorithm)
        plt.xticks(rotation=45)
        plt.savefig(plt_file,bbox_inches="tight")
        plt.close()
        logging.info('Created png: %s',plt_file)

#Generates boxplot of each 
def visualize_literature_comparison_boxplot(all_subgraphs_cosine_sim_df,all_wikipathways_dir):

    output_folder = all_wikipathways_dir+'/literature_comparison/Evaluation_Files'

    plt_file = output_folder + '/Literature_Comparison_all_terms_boxplot.png'
    sns.swarmplot(data=all_subgraphs_cosine_sim_df, x="Pathway_ID", y="Average_Cosine_Similarity",hue="Algorithm", dodge=True, legend=False)
    sns.boxplot(data=all_subgraphs_cosine_sim_df, x='Pathway_ID', y = 'Average_Cosine_Similarity',hue='Algorithm').set_title("Cosine Similarity of subgraph to All Associated Literature Terms")
    plt.xticks(rotation=45)
    plt.savefig(plt_file,bbox_inches="tight")
    plt.close()
    logging.info('Created png: %s',plt_file)

def visualize_literature_comparison_scatterplot(all_subgraphs_cosine_sim_df,all_wikipathways_dir):

    pathways = all_subgraphs_cosine_sim_df.Pathway_ID.unique()

    for pathway in pathways:

        df = all_subgraphs_cosine_sim_df.loc[all_subgraphs_cosine_sim_df['Pathway_ID'] == pathway]
        terms = df.Term.unique()

        plt_file = all_wikipathways_dir + '/' + pathway + '_output/Evaluation_Files/Literature_Comparison_all_terms_scatterplot.png'
        sns_plot = sns.swarmplot(data=df, x='Algorithm', y = 'Average_Cosine_Similarity',hue='Term')
        sns.lineplot(x="Algorithm", dashes=False, y="Average_Cosine_Similarity", hue="Term", style="Term", data=df,legend=False).set_title("Cosine Similarity of " + pathway + " Subgraph to All Associated Literature Terms")

        sns.move_legend(sns_plot,"upper left", bbox_to_anchor=(1, 1))

        plt.xticks(rotation=45)
        plt.savefig(plt_file,bbox_inches="tight")
        plt.close()
        logging.info('Created png: %s',plt_file)

def visualize_literature_comparison_heatmap(term_averages_cosine_sim_df,all_wikipathways_dir):

    output_folder = all_wikipathways_dir+'/literature_comparison/Evaluation_Files'

    plt_file = output_folder + '/Literature_Comparison_all_terms_heatmap.png'
    df_matrix = term_averages_cosine_sim_df.pivot_table(index='Pathway_ID',columns='Algorithm',values='Average_Cosine_Similarity')
    sns.heatmap(df_matrix, fmt="g", cmap='viridis').set_title("Average Cosine Similarity of Subgraphs to All Associated Literature Terms")
    plt.savefig(plt_file,bbox_inches="tight")
    plt.close()
    logging.info('Created png: %s',plt_file)



#Generates boxplot of each 
def visualize_literature_comparison_boxplot_all_pathways(all_subgraphs_zscore_df,all_wikipathways_dir,search_type):

    output_folder = all_wikipathways_dir+'/literature_comparison/Evaluation_Files'

    all_subgraphs_other_pathways = all_subgraphs_zscore_df.loc[all_subgraphs_zscore_df.Compared_Pathway != "Same_Pathway"]

    all_subgraphs_same_pathway = all_subgraphs_zscore_df.loc[all_subgraphs_zscore_df.Compared_Pathway == "Same_Pathway"]

    plt_file = output_folder + '/Literature_Comparison_all_pathways_boxplot_' + search_type + '.png'
    sns.swarmplot(data=all_subgraphs_same_pathway, x="Pathway_ID", y="avg_zscore_per_pathway",hue='Algorithm',palette="flare",dodge=True, legend=False, marker="x", linewidth=1,size=10)
    sns.swarmplot(data=all_subgraphs_other_pathways, x="Pathway_ID", y="avg_zscore_per_pathway",hue="Algorithm", dodge=True, legend=False)
    sns.boxplot(data=all_subgraphs_other_pathways, x='Pathway_ID', y = 'avg_zscore_per_pathway',hue='Algorithm').set_title("Z-Score of Cosine Similarity to All Pathway Abstracts")
    plt.xticks(rotation=45)
    plt.savefig(plt_file,bbox_inches="tight")
    plt.close()
    logging.info('Created png: %s',plt_file)

def visualize_literature_comparison_scatterplot_all_pathways(all_subgraphs_zscore_df,all_wikipathways_dir,search_type):

    pathways = all_subgraphs_zscore_df.Pathway_ID.unique()

    for pathway in pathways:

        df = all_subgraphs_zscore_df.loc[all_subgraphs_zscore_df['Pathway_ID'] == pathway]
        plt_file = all_wikipathways_dir + '/' + pathway + '_output/Evaluation_Files/Literature_Comparison_all_pathways_scatterplot_' + search_type + '.png'
        sns_plot = sns.swarmplot(data=df, x='Algorithm', y = 'avg_zscore_per_pathway',hue='Compared_Pathway')
        sns.lineplot(x="Algorithm", dashes=False, y="avg_zscore_per_pathway", hue="Compared_Pathway", style="Compared_Pathway", data=df,legend=False).set_title("Z-Score of Cosine Similarity to All Pathway Abstracts for" + pathway)
        sns.move_legend(sns_plot,"upper left", bbox_to_anchor=(1, 1))
        plt.xticks(rotation=45)
        plt.savefig(plt_file,bbox_inches="tight")
        plt.close()
        logging.info('Created png: %s',plt_file)

def visualize_literature_comparison_heatmap_all_pathways(all_subgraphs_zscore_df,all_wikipathways_dir,search_type):

    output_folder = all_wikipathways_dir+'/literature_comparison/Evaluation_Files'

    plt_file = output_folder + '/Literature_Comparison_all_pathways_heatmap_' + search_type + '.png'
    df_matrix = all_subgraphs_zscore_df.pivot_table(index='Pathway_ID',columns='Algorithm',values='avg_zscore_per_pathway')
    sns.heatmap(df_matrix, fmt="g", cmap='viridis').set_title("Z-Score of Subgraphs to All Other Pathways")
    plt.savefig(plt_file,bbox_inches="tight")
    plt.close()
    logging.info('Created png: %s',plt_file)