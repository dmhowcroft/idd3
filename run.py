#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Extension to Andre Cunha's IDD3
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


# MaltParser

# parser = nltk.parse.MaltParser(
#     working_dir="/home/andre/Develop/malt/maltparser-1.8",
#     mco="engmalt.linear-1.7",
#     additional_java_args=['-Xmx512m'])

# Stanford parser

# Change this variable to the path on your system
stanford_path = os.path.expanduser('~') + "/apps/stanford-corenlp"
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


def main():
    if len(argv) < 2:
        print('Usage: python', argv[0], '<input file>')
        return

    if argv[1].endswith('.conll'):
        graphs = nltk.parse.dependencygraph.DependencyGraph.load(argv[1])
    else:
        # tagged_sents = [nltk.pos_tag(nltk.word_tokenize(sent))
        #                 for sent in sents]

        # graphs = parser.tagged_parse_sents(tagged_sents)

        with open('tmp.tree', mode='w') as tmp_file, open('output.conll', mode='w') as conll_file:
            call((stanford_run_cmd + ' ' + argv[1]).split(' '), stdout=tmp_file)
            call((stanford_convert_tree_cmd + ' tmp.tree').split(' '),
                 stdout=conll_file)

        # Rewrite the root node label to match NLTK's expectations
        f = open('output.conll','r')
        fdata = f.read()
        f.close()
        f = open('output.conll','w')
        fdata = fdata.replace("root", "ROOT")
        f.write(fdata)
        f.close()

        graphs = nltk.parse.dependencygraph.DependencyGraph.load('output.conll')

    stats = process_graphs(graphs)
    print_stats(stats)


if __name__ == '__main__':
    main()
