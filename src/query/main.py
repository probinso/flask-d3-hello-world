#!/usr/bin/env python3

# Batteries
from functools import partial
import json
from operator import and_, itemgetter
import random
import re
import sys

# Local
from term_frequency import TFLookupTable, TFDocument, Counter

import nltk
from nltk.stem.snowball import SnowballStemmer

language  = 'english'
stopwords = set(nltk.corpus.stopwords.words(language))
stemmer   = SnowballStemmer(language)


class AugmentedTFLookupTable(TFLookupTable):
    """
    Extends TFLookuptable to load all corpus in memory as well
    """
    def __init__(self, *args, **kwargs):
        self.corpus = dict()
        super().__init__(*args, **kwargs)

    def _load_from(self, idx, struct_doc):
        doc_id, contents = self._extract(idx, struct_doc)

        self.corpus[idx] = {'title': doc_id, 'contents' : contents}

        tf = Counter(self._transform(contents))
        for term in tf:
            self[term].add(idx, tf[term])

    def _randdoc(self):
        return random.choice(list(self.corpus))

    def _distribution(self, idx):
        document = self.corpus[idx]

        contents = document['contents']
        tokens   = self._transform(contents)
        #print(tokens)

        dist = dict()
        for s in set(tokens):
            results = self.query(and_, s)
            dist[s] = results[idx]
        return dist


class JSONTFLookupTable(AugmentedTFLookupTable):
    def _extract(self, idx, struct_doc):
        doc = json.loads(struct_doc)
        doc_id   = doc['proj_title']
        contents = doc['abstract_text']
        return doc_id, contents

    def _transform(self, contents):
        tokens = (word
                  for sent in nltk.sent_tokenize(contents)
                  for word in nltk.word_tokenize(sent))

        isnotstop = lambda s: s not in stopwords
        isword    = partial(re.search, '^[A-Za-z]*$')

        stems = map(stemmer.stem, filter(isword, filter(isnotstop, tokens)))
        return [s for s in stems if s not in stopwords]


import numpy as np 

def interface(ifname):
    lookup = JSONTFLookupTable(TFDocument)

    lookup.populate(ifname)
    idx  = lookup._randdoc()
    dist = sorted(lookup._distribution(idx).items(), key=itemgetter(1), reverse=True)

    head, tail = 50, -1
    words, _ = zip(*dist[head:tail])
    scores   = _ / np.sum(_)

    count  = 2
    qterms = np.random.choice(words, count, p=scores)

    print(qterms)
    print(lookup.corpus[idx]['title'])

    results = lookup.query(and_, *qterms)
    print(len(results))
    print(idx in results)
    print()
    for res in results:
        print(lookup.corpus[res]['title'])
        pass


def cli_interface():
    """
    by convention it is helpful to have a wrapper_cli method that interfaces
    from commandline to function space.
    """
    try:
        inpath  = sys.argv[1]
    except:
        print("usage: {}  <inpath>".format(sys.argv[0]))
        sys.exit(1)
    interface(inpath)


if __name__ == '__main__':
    cli_interface()