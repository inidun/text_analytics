# -*- coding: utf-8 -*-
import collections
import functools
import itertools
import logging
import os
import re
import sys

import ftfy
import pandas as pd
import spacy
import textacy
import textacy.preprocessing
from sklearn.feature_extraction.text import CountVectorizer
from spacy import attrs
from spacy.language import Language
from spacy.tokens.doc import Doc as SpacyDoc

import text_analytic_tools.common.text_corpus as text_corpus
import text_analytic_tools.common.textacy_utility as textacy_utility
import text_analytic_tools.corpus.vectorized_corpus as vectorized_corpus
import text_analytic_tools.utility.utils as utility


def get_document_stream(prepped_source_path, document_index):

    reader = text_corpus.CompressedFileReader(prepped_source_path)
    document_index = document_index.set_index('filename')

    for document_name, text in reader:

        metadata = document_index.loc[document_name].to_dict()
        document_id = metadata['unesco_id']

        yield document_name, document_id, text, metadata


def get_textacy_corpus(corpus_path, index_path):

    document_index = pd.read_csv(index_path, sep=';', header=0)
    stream = get_document_stream(corpus_path, document_index)
    nlp = textacy_utility.setup_nlp_language_model('en', disable=('ner', ))
    corpus = textacy_utility.create_textacy_corpus(stream, nlp)

    return corpus, document_index



def infrequent_words(corpus, normalize="lemma", weighting="count", threshold=0, as_strings=False):
    """Returns set of infrequent words i.e. words having total count less than given threshold"""

    if weighting == "count" and threshold <= 1:
        return set([])

    word_counts = corpus.word_counts(
        normalize=normalize, weighting=weighting, as_strings=as_strings
    )
    words = set([w for w in word_counts if word_counts[w] < threshold])

    return words


def frequent_document_words(corpus, normalize="lemma", weighting="freq", dfs_threshold=80, as_strings=True):
    """Returns set of words that occurrs freuently in many documents, candidate stopwords"""
    document_freqs = corpus.word_doc_counts(
        normalize=normalize, weighting=weighting, smooth_idf=True, as_strings=True
    )
    frequent_document_words = set(
        [
            w
            for w, f in document_freqs.items()
            if int(round(f, 2) * 100) >= dfs_threshold
        ]
    )
    return frequent_document_words


def extract_document_terms(doc, extract_args):
    """Extracts documents and terms from a corpus

    Parameters
    ----------
    corpus : textacy Corpus
        Corpus in textacy format.

    extract_args : dict
        Dict that contains args that specifies the filter and transforms
        extract_args['args'] positional arguments for textacy.Doc.to_terms_list
        extract_args['kwargs'] Keyword arguments for textacy.Doc.to_terms_list
        extract_args['substitutions'] Dict (map) with term substitution
        extract_args['extra_stop_words'] List of additional stopwords to use

    Returns
    -------
    iterable of documents (which is iterable of terms)
        Documents where terms have ben filtered and transformed according to args.

    """
    kwargs = extract_args.get("kwargs", {})
    args = extract_args.get("args", {})

    extra_stop_words = set(extract_args.get("extra_stop_words", None) or [])
    substitutions = extract_args.get("substitutions", None)
    min_length = extract_args.get("min_length", 2)

    ngrams = args.get("ngrams", 1)
    named_entities = args.get("named_entities", None)
    normalize = args.get("normalize", "lemma")
    as_strings = args.get("as_strings", True)

    def tranform_token(w, substitutions=None):
        if "\n" in w:
            w = w.replace("\n", "_")
        if substitutions is not None and w in substitutions:
            w = substitutions[w]
        return w

    terms = (
        z
        for z in (
            tranform_token(w, substitutions)  # only w instead
            for w in doc._.to_terms_list(
                ngrams=ngrams,
                entities=named_entities,
                normalize=normalize,
                as_strings=as_strings,
                **kwargs
            )
            if len(w) >= min_length  # and w not in extra_stop_words
            # FIXME: if necessary - Maybe filter pos
            # and w.pos_ in POS_LIST (see culture of international relations)
        )
        if z not in extra_stop_words
    )

    return terms


def extract_corpus_terms(corpus, extract_args):
    """Extracts documents and terms from a corpus

    Parameters
    ----------
    corpus : textacy Corpus
        Corpus in textacy format.

    extract_args : dict
        Dict that contains args that specifies the filter and transforms
        extract_args['args'] positional arguments for textacy.Doc.to_terms_list
        extract_args['kwargs'] Keyword arguments for textacy.Doc.to_terms_list
        extract_args['extra_stop_words'] List of additional stopwords to use
        extract_args['substitutions'] Dict (map) with term substitution
        DEPRECATED extract_args['mask_gpe'] Boolean flag indicating if GPE should be substituted
        extract_args['min_freq'] Integer value specifying min global word count.
        extract_args['max_doc_freq'] Float value between 0 and 1 indicating threshold
          for documentword frequency, Words that occur in more than `max_doc_freq`
          documents will be filtered out.

    None
    ----
        extract_args.min_freq and extract_args.min_freq is the same value but used differently
        kwargs.min_freq is passed directly as args to `textacy_doc.to_terms_list`
        tokens below extract_args.min_freq threshold are added to the `extra_stop_words` list
    Returns
    -------
    iterable of documents (which is iterable of terms)
        Documents where terms have ben filtered and transformed according to args.

    """

    kwargs = dict(extract_args.get("kwargs", {}))
    args = dict(extract_args.get("args", {}))
    normalize = args.get("normalize", "lemma")
    substitutions = extract_args.get("substitutions", {})
    extra_stop_words = set(extract_args.get("extra_stop_words", None) or [])
    chunk_size = extract_args.get("chunk_size", None)
    min_length = extract_args.get("min_length", 2)

    # mask_gpe = extract_args.get('mask_gpe', False)
    # if mask_gpe is True:
    #    gpe_names = { x: '_gpe_' for x in get_gpe_names(corpus) }
    #    substitutions = utility.extend(substitutions, gpe_names)

    min_freq = extract_args.get("min_freq", 1)

    if min_freq > 1:
        words = infrequent_words(
            corpus,
            normalize=normalize,
            weighting="count",
            threshold=min_freq,
            as_strings=True,
        )
        extra_stop_words = extra_stop_words.union(words)
        # logger.info('Ignoring {} low-frequent words!'.format(len(words)))

    max_doc_freq = extract_args.get("max_doc_freq", 100)

    if max_doc_freq < 100:
        words = frequent_document_words(
            corpus,
            normalize=normalize,
            weighting="freq",
            dfs_threshold=max_doc_freq,
            as_strings=True,
        )
        extra_stop_words = extra_stop_words.union(words)
        # logger.info('Ignoring {} high-frequent words!'.format(len(words)))

    extract_args = {
        "args": args,
        "kwargs": kwargs,
        "substitutions": substitutions,
        "extra_stop_words": extra_stop_words,
        "chunk_size": None,
    }

    terms = (extract_document_terms(doc, extract_args) for doc in corpus)

    return terms
