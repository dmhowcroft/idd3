IDD3
====

This is my fork of [@andrecunha](https://github.com/andrecunha)'s IDD3 system.

IDD3 (*Propositional Idea Density from Dependency Trees*) is a Python library that can extract propositions from a sentence, given its dependency tree. Propositions are extracted according to Chand et al.'s rubric [1].

The original system and evaluation is described in a 4-page IEEE conference paper [2].

This is the code used in:

> Howcroft, David M., and Vera Demberg. 2017. "Psycholinguistic Models of Sentence Processing Improve Sentence Readability Ranking". EACL. [ACL Anthology Page](https://aclanthology.coli.uni-saarland.de/papers/E17-1090/e17-1090)

Installation
------------

To install my fork of IDD3 on your system, run can run:

```
$ git clone https://github.com/dmhowcroft/idd3.git
$ cd idd3
$ python setup.py install
```

You might want to install IDD3 inside a virtualenv.

How to run the example file
---------------------------

IDD3 ships with a `run.py` file, that illustrates how the library can be accessed. This file can be used to easily analyze sentences and see the system's output. You can use this file to analyze either a raw sentence, or its dependency tree, stored in a CoNLL-X file. In order to analyze raw sentences, follow these steps:

1. `run.py` uses the Stanford Parser to extract the dependency tree. Download the latest version of it at http://nlp.stanford.edu/software/lex-parser.shtml#Download, and extract it where you want.
2. Change the variable `stanford_path` in `run.py` to point to the path where you extracted the parser in the previous step (the default value is `~/Develop/stanford_tools/`).
3. Place the sentences you want to analyze in a file, let's say `input.txt`, one sentence per line.
4. Run IDD3 as `python run.py input.txt`

If you have a CoNLL-X file, say `input.conll`, that already has the dependency trees for the sentences you want IDD3 to analyze, you can just run `python run.py input.conll`, with no need to configure the Stanford Parser.

References
----------

[1]  V. Chand, K. Baynes, L. Bonnici, and S. T. Farias, *Analysis of Idea Density (AID): A Manual*, University of California at Davis, 2010. Available from (http://mindbrain.ucdavis.edu/labs/Baynes/AIDManual.ChandBaynesBonniciFarias.1.26.10.pdf)

[2] Cunha, A. L. V. Da, L. B. De Sousa, L. L. Mansur, & S. M. Aluísio. (2015). "Automatic Proposition Extraction from Dependency Trees: Helping Early Prediction of Alzheimer’s Disease from Narratives". *2015 IEEE 28th International Symposium on Computer-Based Medical Systems*, 127–130. doi:10.1109/CBMS.2015.19. Available (behind a paywall) from [IEEExplore](http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=7167471).
