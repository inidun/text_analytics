# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py,md
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
# %load_ext autoreload
# %autoreload 2

import unittest

import pandas as pd
import scipy
from scipy.cluster.hierarchy import (  # pylint: disable=unused-import
    linkage)

import westac.corpus.tokenized_corpus as corpora
from westac.corpus import corpus_vectorizer
from westac.tests.utils import create_text_tokenizer

unittest.main(argv=['first-arg-is-ignored'], exit=False)


class Test_ChiSquare(unittest.TestCase):

    def setUp(self):
        pass

    def create_reader(self):
        filename_fields = dict(year=r".{5}(\d{4})_.*", serial_no=r".{9}_(\d+).*")
        reader = create_text_tokenizer(filename_fields=filename_fields, fix_whitespaces=True, fix_hyphenation=True)
        return reader

    def create_corpus(self):
        reader = self.create_reader()
        kwargs = dict(only_any_alphanumeric=True, to_lower=True, remove_accents=False, min_len=2, max_len=None, keep_numerals=False)
        corpus = corpora.TokenizedCorpus(reader, **kwargs)
        return corpus

    def skip_test_chisquare(self):
        corpus = self.create_corpus()
        vectorizer = corpus_vectorizer.CorpusVectorizer()
        v_corpus = vectorizer\
            .fit_transform(corpus)\
            .group_by_year()\
            .slice_by_n_count(0)
        X2 = scipy.stats.chisquare(v_corpus.term_bag_matrix.todense(), f_exp=None, ddof=0, axis=0) # pylint: disable=unused-variable
        _ = linkage(v_corpus.term_bag_matrix, 'ward') # pylint: disable=unused-variable
        results = None
        expected = None
        self.assertEqual(expected, results)

def plot_dists(v_corpus):
    df = pd.DataFrame(v_corpus.bag_term_matrix.toarray(), columns=list(v_corpus.get_feature_names()))
    df['year'] = df.index + 45
    df = df.set_index('year')
    df['year'] =  pd.Series(df.index).apply(lambda x: v_corpus.document_index[x][0])
    df[['krig']].plot() #.loc[df["000"]==49]


# unittest.main(argv=['first-arg-is-ignored'], exit=False)
