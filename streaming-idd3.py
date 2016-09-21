#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Using IDD3 with spaCy
# Copyright (C) 2015  David M. Howcroft
#
# This program is an extension of IDD3, which requires the GPL.
# It also uses spaCy, which is available under the MIT license.
# If you are able to arrange an alternative license for IDD3,
# I am happy to consider an alternative license for this script as well.
#
# IDD3 is free software: you can redistribute it and/or modify it
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
from collections import defaultdict

import logging
logging.basicConfig(level=logging.INFO)

import os
# columns is the width of the terminal the user is viewing
# This is used for output pretty printing
# _, columns = os.popen('stty size', 'r').read().split()
columns = 50

try:
    from termcolor import colored
    raise ImportError
except ImportError:
    def colored(string, color, attrs):
        return string


def get_sentence(graph):
    """Turns a graph into a list of words.
    """
    return ' '.join([graph.nodes[node]['word'] for node in graph.nodes if graph.nodes[node]['word']])


def process_graphs(graphs, verbose=False):
    engine = Engine(rules.all_rulesets, transform.all_transformations)
    stats = defaultdict(int)

    for index in range(len(graphs) - 1):
        if verbose:
            print('-' * int(columns))
        relations = []
        for node in graphs[index].nodes:
            relation = graphs[index].nodes[node]
            if relation['rel'] == 'ROOT':
                relation['rel'] = 'root'
            relations.append(Relation(**relation))

        if verbose:
            print(colored('Sentence %d:' % (index + 1), 'white', attrs=['bold']))
            print('\t' + get_sentence(graphs[index]))

            print(colored('Propositions:', 'white', attrs=['bold']))
        try:
            engine.analyze(relations)
            for i, prop in enumerate(engine.props):
                if verbose:
                    print(str(i + 1) + ' ' + str(prop))
                stats[prop.kind] += 1
        except Exception:
            pass

    if verbose:
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


def print_usage():
    print('Usage: python', argv[0], '<input file>')


def main():
    if len(argv) < 2:
        print_usage()
        exit()

    in_filename = argv[1]

    if in_filename.endswith('.conll'):
        graphs = nltk.parse.dependencygraph.DependencyGraph.load(in_filename)
    else:
        print("Importing English model for spaCy parsing...")
        from spacy.en import English
        spacy_en = English()
        print("Done loading models.")

        in_file = open(in_filename, 'r')

        graphs = []
        for line in in_file:
            sent = spacy_en(line.strip('\n.?!'))

            dg = nltk.parse.dependencygraph.DependencyGraph()
            for token in sent:
                address = token.i+1
                word = token.text
                tag = spacy_en.vocab.strings[token.tag]
                head = token.head.i+1
                rel = spacy_en.vocab.strings[token.dep]
                if rel == "ROOT":
                    head = 0
                dg.nodes[address].update(
                {
                    'address': address,
                    'word': word,
                    'lemma': word,
                    'ctag': tag,
                    'tag': tag,
                    'feats': '',
                    'head': head,
                    'rel': rel,
                }
                )
                dg.nodes[head]['deps'][rel].append(address)

            if dg.nodes[0]['deps']['ROOT']:
                root_address = dg.nodes[0]['deps']['ROOT'][0]
                dg.root = dg.nodes[root_address]
            else:
                warnings.warn(
                    "The graph doesn't contain a node "
                    "that depends on the root element."
                )
            graphs.append(dg)
            print(dg)

    print_sentfeats(process_graphs(graphs))


if __name__ == '__main__':
    main()
