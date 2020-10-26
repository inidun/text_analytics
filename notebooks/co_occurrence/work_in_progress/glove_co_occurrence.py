# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import itertools

import glove
import numpy as np
import pandas as pd
from glove import Corpus
from nltk.tokenize import word_tokenize


# See http://www.foldl.me/2014/glove-python/
def compute_GloVe_df(sentences, window=2, dictionary=None):

    corpus = Corpus(dictionary=dictionary)
    corpus.fit(sentences, window=window)

    dm = corpus.matrix.todense()
    inverse_dictionary = {i: w for w, i in corpus.dictionary.items()}
    id2token = [inverse_dictionary[i] for i in range(0, max(inverse_dictionary.keys()) + 1)]

    df = pd.DataFrame(dm.T, columns=id2token).assign(word=id2token).set_index('word')
    return df


# Create sorted dictionary to make HAL comparision easier
def create_sorted_dictionary(sentences):
    tokens = set()
    for sentence in sentences:
        tokens = tokens | set(sentence)
    tokens = list(tokens)
    tokens.sort()
    dictionary = {w: i for i, w in enumerate(tokens)}
    return dictionary


sentences = ["The Horse Raced Past The Barn Fell".title().split()]

dictionary = create_sorted_dictionary(sentences)

df = compute_GloVe_df(sentences, window=5, dictionary=dictionary)
df


# %%
# Glove CO-OCCURRENCE (as implemented in python-glove):
#  The counts are ALWAYS FORWARD i.e the window is added tvalues are ABSOLUTE c
#  Added increment for each pair = 1 / distance-between-other-word
#  NO normalization


pd.options.display.precision = 2
window = 4
docs = [
    'one two two one two two one two two one two two',
    'one two two one two two one two two one two two',
    #'This is the first document.',
    #'This document is the second document.',
    #'And this is the third one.',
    #'Is this the first document?',
]

docs = [[w.lower() for w in word_tokenize(doc) if len(w) > 1] for doc in docs]

model = glove.Corpus()
model.fit(docs, window=window)

X = model.matrix + model.matrix.T
T = len(model.dictionary)
id2token = {i: w for w, i in model.dictionary.items()}

df = pd.DataFrame(data=X.todense(), index=np.array(range(1, T + 1)), columns=np.array(range(1, T + 1)))
df.columns = list(id2token.values())
df['word'] = list(id2token.values())
df = df.set_index('word')
df

# %%
