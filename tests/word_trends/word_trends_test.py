from unittest.mock import patch

import numpy as np
import pandas as pd
import penelope.corpus.dtm as dtm
import penelope.pipeline as pipeline

import notebooks.word_trends.word_trends_gui as word_trends_gui

from ..utils import SSI_config


def create_vectorized_corpus() -> dtm.VectorizedCorpus:
    bag_term_matrix = np.array(
        [
            [2, 1, 4, 1],
            [2, 2, 3, 0],
            [2, 3, 2, 0],
            [2, 4, 1, 1],
            [2, 0, 1, 1],
        ]
    )
    token2id = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
    document_index = pd.DataFrame({'year': [2013, 2013, 2014, 2014, 2014]})
    v_corpus: dtm.VectorizedCorpus = dtm.VectorizedCorpus(bag_term_matrix, token2id, document_index)
    return v_corpus


def monkey_patch(*_, **__):
    ...


def find_corpus_config(*_, **__) -> pd.DataFrame:
    corpus_config: pipeline.CorpusConfig = pipeline.CorpusConfig.loads(SSI_config)
    return corpus_config


def test_corpus_loaded_callback():
    corpus_tag = "dummy"
    corpus_folder = "dummy"
    corpus = create_vectorized_corpus()
    word_trends_gui.corpus_loaded_callback(corpus, corpus_tag, corpus_folder)


@patch('penelope.notebook.dtm.compute_DTM_pipeline.compute_document_term_matrix', monkey_patch)
def test_corpus_compute_callback():
    word_trends_gui.corpus_compute_callback()


@patch('penelope.pipeline.CorpusConfig.find', find_corpus_config)
def test_create_gui():

    config_name = "SSI"
    corpus_folder = "dummy"
    gui = word_trends_gui.create_gui(corpus_folder, corpus_config_name=config_name)
    assert gui is not None
