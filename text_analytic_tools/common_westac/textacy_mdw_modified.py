# This file is a modified version of textacy vsm.most_discriminating_terms
# Oríginal source: https://github.com/chartbeat-labs/textacy/blob/master/textacy/ke/utils.py
# License: MIT https://github.com/chartbeat-labs/textacy/blob/master/LICENSE.txt
#
# Copyright 2016 Chartbeat, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import operator
import pandas as pd
import logging
import numpy as np

from textacy import vsm

from memoization import cached

logger = logging.getLogger("humlab_text_analytic_tools")
logger.setLevel(logging.INFO)

def compute_most_discriminating_terms(x_corpus, top_n_terms=25, max_n_terms=1000, group1_indices=None, group2_indices=None):

    if len(group1_indices) == 0 or len(group2_indices) == 0:
        return None

    if len(set(group1_indices.values).intersection(set(group2_indices.values))) > 0:
        logger.error("The two groups are overlapping. That is NOT okey!")
        return None

    indices = group1_indices.append(group2_indices)

    in_group1 = [True] * group1_indices.size + [False] * group2_indices.size

    dtm = x_corpus.data[indices, :]

    logger.info("Corpus size after GROUP filter %s x %s.", *dtm.shape)

    logger.info("Computing MDW (this might take some time)...")

    terms = most_discriminating_terms(dtm, x_corpus.id2token, in_group1, top_n_terms=top_n_terms, max_n_terms=max_n_terms)
    min_terms = min(len(terms[0]), len(terms[1]))
    df = pd.DataFrame({'Group 1': terms[0][:min_terms], 'Group 2': terms[1][:min_terms] })

    return df

# This modified version takes a document-term-matrix and a vocubulary as arguments instead of a terms list
def most_discriminating_terms(
    dtm,
    id2term,
    bool_array_grp1, *, max_n_terms=1000, top_n_terms=25
):
    """
    Given a collection of documents assigned to 1 of 2 exclusive groups, get the
    ``top_n_terms`` most discriminating terms for group1-and-not-group2 and
    group2-and-not-group1.

    Args:
        terms_lists (Iterable[Iterable[str]]): Sequence of documents, each as a
            sequence of (str) terms; used as input to :func:`doc_term_matrix()`
        bool_array_grp1 (Iterable[bool]): Ordered sequence of True/False values,
            where True corresponds to documents falling into "group 1" and False
            corresponds to those in "group 2".
        max_n_terms (int): Only consider terms whose document frequency is within
            the top ``max_n_terms`` out of all distinct terms; must be > 0.
        top_n_terms (int or float): If int (must be > 0), the total number of most
            discriminating terms to return for each group; if float (must be in
            the interval (0, 1)), the fraction of ``max_n_terms`` to return for each group.

    Returns:
        List[str]: Top ``top_n_terms`` most discriminating terms for grp1-not-grp2
        List[str]: Top ``top_n_terms`` most discriminating terms for grp2-not-grp1

    References:
        King, Gary, Patrick Lam, and Margaret Roberts. "Computer-Assisted Keyword
        and Document Set Discovery from Unstructured Text." (2014).
        http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.458.1445&rep=rep1&type=pdf
    """
    alpha_grp1 = 1 # alfa group R
    alpha_grp2 = 1 # alfa group S
    if isinstance(top_n_terms, float):
        top_n_terms = top_n_terms * max_n_terms
    bool_array_grp1 = np.array(bool_array_grp1)
    bool_array_grp2 = np.invert(bool_array_grp1)

    # vectorizer = vsm.Vectorizer(
    #     tf_type="linear",
    #     norm=None,
    #     idf_type="smooth",
    #     min_df=3,
    #     max_df=0.95,
    #     max_n_terms=max_n_terms,
    # )
    # dtm = vectorizer.fit_transform(terms_lists)
    # id2term = vectorizer.id_to_term

    # get doc freqs for all terms in grp1 documents
    dtm_grp1 = dtm[bool_array_grp1, :]
    n_docs_grp1 = dtm_grp1.shape[0]                          # Number of docs in R
    doc_freqs_grp1 = vsm.get_doc_freqs(dtm_grp1)

    # get doc freqs for all terms in grp2 documents
    dtm_grp2 = dtm[bool_array_grp2, :]
    n_docs_grp2 = dtm_grp2.shape[0]                          # Number of docs in S
    doc_freqs_grp2 = vsm.get_doc_freqs(dtm_grp2)

    # get terms that occur in a larger fraction of grp1 docs than grp2 docs
    term_ids_grp1 = np.where(doc_freqs_grp1 / n_docs_grp1 > doc_freqs_grp2 / n_docs_grp2)[0]

    # get terms that occur in a larger fraction of grp2 docs than grp1 docs
    term_ids_grp2 = np.where(doc_freqs_grp1 / n_docs_grp1 < doc_freqs_grp2 / n_docs_grp2)[0]

    # get grp1 terms doc freqs in and not-in grp1 and grp2 docs, plus marginal totals
    grp1_terms_grp1_df = doc_freqs_grp1[term_ids_grp1] # Doc freqs in corpus R of terms in corpus R
    grp1_terms_grp2_df = doc_freqs_grp2[term_ids_grp1] # Doc freqs in corpus S of terms in corpus R
    # get grp2 terms doc freqs in and not-in grp2 and grp1 docs, plus marginal totals
    grp2_terms_grp2_df = doc_freqs_grp2[term_ids_grp2]
    grp2_terms_grp1_df = doc_freqs_grp1[term_ids_grp2]

    # get grp1 terms likelihoods, then sort for most discriminating grp1-not-grp2 terms
    grp1_terms_likelihoods = compute_likelihoods(term_ids_grp1, grp1_terms_grp1_df, alpha_grp1, grp1_terms_grp2_df, alpha_grp2, n_docs_grp1, n_docs_grp2, id2term)

    # get grp2 terms likelihoods, then sort for most discriminating grp2-not-grp1 terms
    grp2_terms_likelihoods = compute_likelihoods(term_ids_grp2, grp2_terms_grp2_df, alpha_grp2, grp2_terms_grp1_df, alpha_grp1, n_docs_grp2, n_docs_grp1, id2term)

    top_grp1_terms = get_top_likelihoods(grp1_terms_likelihoods, top_n_terms)
    top_grp2_terms = get_top_likelihoods(grp2_terms_likelihoods, top_n_terms)

    return (top_grp1_terms, top_grp2_terms)

def get_top_likelihoods(terms_likelihoods, top_n_terms):
    top_terms = [
        term for term, likelihood in sorted(terms_likelihoods.items(), key=operator.itemgetter(1), reverse=True)[:top_n_terms]
    ]
    return top_terms

# https://stackoverflow.com/questions/16325988/factorial-of-a-large-number-in-python
@cached
def range_prod(lo,hi):
    if lo+1 < hi:
        mid = (hi+lo)//2
        return range_prod(lo,mid) * range_prod(mid+1,hi)
    if lo == hi:
        return lo
    return lo*hi

def F(n):
    if n < 2:
        return 1
    return range_prod(1,n)

def compute_likelihoods(term_ids, nr_RS, aRS, nr_SS, aSS, NRS, NSS, id2term):
    """

                                   Γ(nr_RS + αRS) × Γ(nr_SS + αSS)       Γ(NRS − nr_RS + αRS) × Γ(NSS − nr_SS + αSS)
     p(y1, ...yn|αRS, αSS, r)  ∝          -----------------          ×               -----------------
                                    Γ(nr_RS + nr_SS + αRS + αSS)          Γ(NRS − nr_RS + NSS − nr_SS + αRS + αSS)


    """

    terms_likelihoods = {}

    for idx, term_id in enumerate(term_ids):
        likelihood = (
            F(nr_RS[idx] + aRS - 1) * F(nr_SS[idx] + aSS - 1) / \
                F(nr_RS[idx] + nr_SS[idx] + aRS + aSS - 1)
        ) * \
        (
            F(NRS - nr_RS[idx] + aRS - 1) * F(NSS - nr_SS[idx] + aSS - 1) / \
                F(NRS + NSS - nr_RS[idx] - nr_SS[idx] + aRS + aSS - 1)
        )
        terms_likelihoods[id2term[term_id]] = likelihood
    return terms_likelihoods
