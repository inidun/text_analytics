from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
from penelope.corpus import VectorizedCorpus
import penelope.notebook.interface as interface
import penelope.pipeline as pipeline
from penelope.notebook.word_trends import main_gui


def create_vectorized_corpus() -> VectorizedCorpus:
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
    v_corpus: VectorizedCorpus = VectorizedCorpus(bag_term_matrix, token2id, document_index)
    return v_corpus


def monkey_patch(*_, **__):
    ...


def find_corpus_config(*_, **__) -> pipeline.CorpusConfig:
    corpus_config: pipeline.CorpusConfig = pipeline.CorpusConfig.load('./tests/test_data/SSI.yml')
    return corpus_config


def test_corpus_loaded_callback():
    corpus = create_vectorized_corpus()
    corpus_folder = "dummy"
    corpus_tag = "dummy"
    main_gui.loaded_callback(corpus, corpus_folder, corpus_tag)


@patch('penelope.workflows.document_term_matrix.compute', monkey_patch)
def test_corpus_compute_callback():
    main_gui.compute_callback(args=Mock(spec=interface.ComputeOpts), corpus_config=Mock(spec=pipeline.CorpusConfig))


@patch('penelope.pipeline.CorpusConfig.find', find_corpus_config)
def test_create_gui():

    config_name = "SSI"
    corpus_folder = "dummy"
    data_folder = "dummy"
    gui = main_gui.create_to_dtm_gui(corpus_folder=corpus_folder, data_folder=data_folder, corpus_config=config_name)
    assert gui is not None
