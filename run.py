#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Modified IDD3/run.py for larger corpora.
# Copyright (C) 2015  David M. Howcroft
#
# IDD3 - Propositional Idea Density from Dependency Trees
# Copyright (C) 2014  Andre Luiz Verucci da Cunha
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, unicode_literals, division

from idd3 import Relation, Engine, rules, transform
import nltk
from sys import argv
from subprocess import call
from collections import defaultdict

import logging
logging.basicConfig(level=logging.INFO)

import os
_, columns = os.popen('stty size', 'r').read().split()

try:
    from termcolor import colored
    raise ImportError
except ImportError:
    def colored(string, color, attrs):
        return string

CONLL_FILENAME = 'output.conll'
# We write the Stanford parse to a file as an intermediate stage in our processing.
TEMPORARY_FILENAME = 'tmp.tree'

# Stanford parser
# Change this variable to the path on your system
stanford_path = os.path.expanduser('~') + "/apps/stanford-corenlp"
# Define the path to the directory containing the version of Java you want to use
java_dir = '/usr/lib/jvm/java-8-openjdk-amd64/jre/bin/'

stanford_run_cmd = java_dir + 'java -mx1024m -cp ' + stanford_path + \
    '/*: edu.stanford.nlp.parser.lexparser.LexicalizedParser ' + \
    '-outputFormat penn edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz'
stanford_convert_tree_cmd = java_dir + 'java -mx1024m -cp ' + stanford_path + \
    '/*: edu.stanford.nlp.trees.EnglishGrammaticalStructure ' + \
    '-basic -conllx -treeFile'


def get_sentence(graph):
    """Turns a graph into a list of words.
    """
    return ' '.join([graph.nodes[node]['word'] for node in graph.nodes if graph.nodes[node]['word']])


def process_graphs(graphs):
    engine = Engine(rules.all_rulesets, transform.all_transformations)
    stats = defaultdict(int)

    for index in range(len(graphs) - 1):
        print('-' * int(columns))
        relations = []
        for node in graphs[index].nodes:
            relation = graphs[index].nodes[node]
            if relation['rel'] == 'ROOT':
                relation['rel'] = 'root'
            relations.append(Relation(**relation))

        print(colored('Sentence %d:' % (index + 1), 'white', attrs=['bold']))
        print('\t' + get_sentence(graphs[index]))

        print(colored('Propositions:', 'white', attrs=['bold']))
        try:
            engine.analyze(relations)
            for i, prop in enumerate(engine.props):
                print(str(i + 1) + ' ' + str(prop))
                stats[prop.kind] += 1
        except Exception:
            pass

    print('-' * int(columns))
    return stats


def print_stats(stats):
    print('Stats:')
    print('Kind\t#\t')
    for kind, n in stats.items():
        print('{0}\t{1}'.format(kind, n))


def print_sentfeats(stats):
    total = 0
    vals = []
    for kind in ['P', 'M', 'C']:
        n = stats.get(kind, 0)
        total += n
        vals.append(str(n))
    print(" ".join(vals))


def main():
    if len(argv) < 2:
        print('Usage: python', argv[0], '<input file>')
        return

    if argv[1].endswith('.conll'):
        graphs = nltk.parse.dependencygraph.DependencyGraph.load(argv[1])
    else:
        # I assume this is used when you're running the MALT parser.
        # tagged_sents = [nltk.pos_tag(nltk.word_tokenize(sent))
        #                 for sent in sents]

        # graphs = parser.tagged_parse_sents(tagged_sents)

        with open(TEMPORARY_FILENAME, mode='w') as tmp_file, \
                open(CONLL_FILENAME, mode='w') as conll_file, \
                open('error', 'w') as err_tmp,\
                open('conll.err', 'w') as err_conll:
            call((stanford_run_cmd + ' ' + argv[1]).split(' '), stdout=tmp_file, stderr=err_tmp)
            call((stanford_convert_tree_cmd + ' tmp.tree').split(' '), stdout=conll_file, stderr=err_conll)

        # Rewrite the root node label to match NLTK's expectations
        f = open(CONLL_FILENAME, 'r')
        fdata = f.read()
        f.close()
        f = open(CONLL_FILENAME, 'w')
        fdata = fdata.replace("root", "ROOT")
        f.write(fdata)
        f.close()

        graphs = nltk.parse.dependencygraph.DependencyGraph.load(CONLL_FILENAME)

    stats = process_graphs(graphs)
    # print_stats(stats)
    print_sentfeats(stats)


if __name__ == '__main__':
    main()
