#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# script created using: https://github.com/VHRanger/nodevectors

# import needed libraries
import argparse
import csrgraph as cg
import nodevectors
from nodevectors_node2vec import Node2Vec
import os
import glob
import logging.config
from pythonjsonlogger import jsonlogger

# logging
log_dir, log, log_config = 'builds/logs', 'cartoomics_log.log', glob.glob('**/logging.ini', recursive=True)
try:
    if not os.path.exists(log_dir): os.mkdir(log_dir)
except FileNotFoundError:
    log_dir, log_config = '../builds/logs', glob.glob('../builds/logging.ini', recursive=True)
    if not os.path.exists(log_dir): os.mkdir(log_dir)
logger = logging.getLogger(__name__)
logging.config.fileConfig(log_config[0], disable_existing_loggers=False, defaults={'log_file': log_dir + '/' + log})


def main():
    parser = argparse.ArgumentParser(description='A wrapper for running Node2Vec on Very Large Graphs')
    parser.add_argument('-e', '--edgelist', help='Name/path to text file containing graph edge list', required=True)
    parser.add_argument('-d', '--dim', help='Embedding dimensions', required=True)
    parser.add_argument('-l', '--walklen', help='Random walk length', required=True)
    parser.add_argument('-r', '--walknum', help='Number of walks', required=True)
    parser.add_argument('-t', '--threads', help='# threads to use', default=0)
    parser.add_argument('-p', '--return_weight', help='Return node probability', default=1.)
    parser.add_argument('-q', '--explore_weight', help='Node visit probability', default=1.)
    parser.add_argument('-k', '--window', help='Context window size', required=True)
    parser.add_argument('-w', '--keep_walks', help='Save the random walks', default=False)
    parser.add_argument('-m', '--save_model', help='Save Gensim node2vec model', default=False)
    parser.add_argument('-o', '--output', help='Embedding File Output Location', default=False)
    args = parser.parse_args()

    logging.info('Node2vec wrapper.')
    for arg, value in sorted(vars(args).items()):
        logging.info("Argument %s: %r", arg, value)

    # print user parameters to console
    print('\n#######################################################################\n')
    print('NODE2VEC Parameters:')
    print('Edge List: {input_file}'.format(input_file=args.edgelist.split('/')[-1]))
    print('Embedding Dimensions: {dim}'.format(dim=args.dim))
    print('Random walk Length: {walk_len}'.format(walk_len=args.walklen))
    print('Number of random walks: {walk_num}'.format(walk_num=args.walknum))
    print('Threads: {threads}'.format(threads=args.threads))
    print('Return Weight (p): {p}'.format(p=args.return_weight))
    print('Explore Weight (q): {q}'.format(q=args.explore_weight))
    print('Context Window Size: {window_size}'.format(window_size=args.window))
    print('Save Random Walks with Node2Vec Model: {keep_walks}'.format(keep_walks=args.keep_walks))
    print('Save Gensim Node2Vec Model: {save_model}'.format(save_model=args.save_model))
    print('Embedding output: {write_loc}'.format(write_loc=args.output))
    print('\n#######################################################################\n')

    print('\n#### STEP 1: Convert Edge List to CSR Graph ####')
    graph = cg.read_edgelist(args.edgelist, sep=' ', header=None)

    print('\n#### STEP 2: Fit Embedding Model to Graph ####')  
    g2v = Node2Vec(n_components=int(args.dim),
                               walklen=int(args.walklen),
                               epochs=int(args.walknum),
                               return_weight=float(args.return_weight),
                               neighbor_weight=float(args.explore_weight),
                               threads=int(args.threads),
                               keep_walks=args.keep_walks,
                               verbose=True,
                               w2vparams={'window': int(args.window), 'epochs': 10})
    g2v.fit(graph)

    print('\n#### STEP 3: Save Model Output and Embeddings ####')
    # save embeddings (gensim.KeyedVector format)
    embeddings_file = args.output
   # print(embeddings_file)
    g2v.save_vectors(embeddings_file)

    #if args.save_model:
        # save node2vec model -- uses a lot of memory and takes a very long time to run on large graphs
        #g2v.save(args.edgelist.split('.')[0] + '_node2vec_Model.pkl')


if __name__ == '__main__':
    main()
