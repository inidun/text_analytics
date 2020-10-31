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
#     display_name: 'Python 3.8.5 64-bit (''text-analytics-symNAVlf-py3.8'': venv)'
#     metadata:
#       interpreter:
#         hash: f9f5370a66fe709225320b0a5e42eaf481fec3c92c4ac457a33063cd6d0e2297
#     name: 'Python 3.8.5 64-bit (''text-analytics-symNAVlf-py3.8'': venv)'
# ---


# %%

import __paths__ # isort:skip

import itertools
import os
from typing import Sequence

import pandas as pd
import textacy
from penelope.corpus import CorpusVectorizer, VectorizedCorpus
from penelope.vendor.textacy.extract import ExtractPipeline
from penelope.vendor.textacy.pipeline import CreateTask, LoadTask, PreprocessTask, SaveTask, TextacyCorpusPipeline

CORPUS_FOLDER = os.path.join(__paths__.ROOT_FOLDER, "data")

# %%


def load_corpus(filename, documents, filename_fields, lang="en"):

    options = dict(filename=filename, lang=lang, documents=documents, filename_fields=filename_fields)
    tasks = [
        PreprocessTask,
        CreateTask,
        SaveTask,
        LoadTask,
    ]
    pipeline = TextacyCorpusPipeline(**options, tasks=tasks)
    corpus = pipeline.process().corpus
    return corpus


def slice_by_word_ending(corpus: textacy.Corpus, word_endings: Sequence[str], documents: pd.DataFrame=None):
    """
    Add an ability to enter a number of specific word endings such as -ment, -tion and -sion.
    The system should finds all words having the specified endings, and displays the (optionally normalized)
    frequency list as a table, or bar chart. It should also be possible to export the list, and to a apply a
    filter that excludes any number of words (in a text box).

    It should be possible to display the data grouped by document, year or user defined periods.

    See Moretti, Pestre Bank Speek, page 89
    """
    terms = ExtractPipeline(corpus, target=None)\
            .min_character_filter(2).process()

    document_terms = itertools.zip_longest(documents.filename, terms)

    vectorizer = CorpusVectorizer()
    v_corpus: VectorizedCorpus = vectorizer.fit_transform(document_terms, documents=documents, tokenizer=None)
    v_corpus = v_corpus.normalize(axis=1)

    vocabulary = list(v_corpus.token2id.keys())

    candidates = {x for x in vocabulary if any(x.endswith(word_ending) for word_ending in word_endings)}

    w_corpus = v_corpus.slice_by(lambda w: w in candidates)

    return w_corpus


# %%

documents = pd.read_csv(os.path.join(CORPUS_FOLDER, "legal_instrument_index.csv"), sep=";", header=0)

corpus = load_corpus(
    filename=os.path.join(CORPUS_FOLDER, "legal_instrument_corpus.zip"),
    documents=documents,
    filename_fields=["unesco_id:_:2", "year:_:3", r'city:\w+\_\d+\_\d+\_\d+\_(.*)\.txt'],
    lang="en",
)

# %%

we_corpus = slice_by_word_ending(corpus=corpus, documents=documents, word_endings={"ment", "tion", "sion"})

# %%
we_corpus.data.shape
# %%
statement = we_corpus.data[:,we_corpus.token2id['statement']].todense().A1
pd.DataFrame(data={'statement': statement}).plot()

# %%
we_corpus.data.sum(axis=0).toarray()
# %%
pd.DataFrame(we_corpus.data.sum(axis=0).A1).plot()

# %%
we_corpus.group_by_year()
# %%
