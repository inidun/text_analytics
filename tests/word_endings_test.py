import numpy as np
import pytest
import textacy

from penelope.vendor import textacy as textacy_utility
from penelope.corpus import CorpusVectorizer, VectorizedCorpus


@pytest.fixture(scope="module")
def mary_had_a_little_lamb_corpus() -> textacy.Corpus:
    """Source: https://github.com/chartbeat-labs/textacy/blob/master/tests/test_vsm.py """
    texts = [
        "Mary had a little lamb. Its fleece was white as snow.",
        "Everywhere that Mary went the lamb was sure to go.",
        "It followed her to school one day, which was against the rule.",
        "It made the children laugh and play to see a lamb at school.",
        "And so the teacher turned it out, but still it lingered near.",
        "It waited patiently about until Mary did appear.",
        "Why does the lamb love Mary so? The eager children cry.",
        "Mary loves the lamb, you know, the teacher did reply.",
    ]
    corpus = textacy.Corpus("en", data=texts)
    return corpus


def test_word_endings(mary_had_a_little_lamb_corpus):

    expected_matrix = np.matrix([[0, 0], [0, 0], [1, 0], [0, 1], [0, 0], [0, 0], [0, 0], [0, 0]])

    # Arrange
    terms = (
        textacy_utility.ExtractPipeline(mary_had_a_little_lamb_corpus, target=None).min_character_filter(2).process()
    )
    document_terms = ((f'document_{i}.txt', tokens) for i, tokens in enumerate(terms))
    vectorizer = CorpusVectorizer()
    v_corpus: VectorizedCorpus = vectorizer.fit_transform(document_terms, tokenizer=None)

    vocabulary = list(v_corpus.token2id.keys())

    word_ending = 'ay'

    candidates = {x for x in vocabulary if x.endswith(word_ending)}

    w_corpus = v_corpus.slice_by(lambda w: w in candidates)

    assert (expected_matrix == w_corpus).all()
    assert {0: 'day', 1: 'play'} == w_corpus.id2token


"""
Add an ability to enter a number of specific word endings such as -ment, -tion and -sion.
The system should finds all words having the specified endings, and displays the (optionally normalized)
frequency list as a table, or bar chart. It should also be possible to export the list, and to a apply a
filter that excludes any number of words (in a text box).

It should be possible to display the data grouped by document, year or user defined periods.

See Moretti, Pestre Bank Speek, page 89
"""