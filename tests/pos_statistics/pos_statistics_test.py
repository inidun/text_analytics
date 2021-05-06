from typing import List
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import penelope.pipeline as pipeline
import pytest
from penelope.notebook.token_counts import tokens_count_gui


def monkey_patch(*_, **__):
    ...


def load_corpus_config(_: str) -> pd.DataFrame:
    corpus_config: pipeline.CorpusConfig = pipeline.CorpusConfig.load('./tests/test_data/SSI.yml')
    return corpus_config


def load_document_index_patch(*_, **__):
    return MagicMock(pd.DataFrame)


def create_document_index():
    return pd.DataFrame(
        data={
            'year': [2020, 2020, 2021],
            'Noun': [10, 30, 25],
            'n_raw_tokens': [50, 60, 70],
        }
    )


def patch_pipeline(*_, **__):
    attrs = {'payload.document_index': create_document_index()}
    mock = Mock(spec=pipeline.CorpusPipeline, **attrs)
    mock.exhaust = lambda: mock
    return mock


@patch('penelope.notebook.ipyaggrid_utility.display_grid', monkey_patch)
@patch('penelope.notebook.token_counts.plot.plot_by_bokeh', monkey_patch)
def test_create_token_count_gui():

    gui = tokens_count_gui.TokenCountsGUI(
        compute_callback=monkey_patch,
        load_document_index_callback=load_document_index_patch,
        load_corpus_config_callback=load_corpus_config,
    )

    gui = gui.setup(['tests/test_data/SSI.yml'])

    assert not gui.smooth
    assert not gui.normalize
    assert gui.grouping == tokens_count_gui.TOKEN_COUNT_GROUPINGS[-1]

    layout = gui.layout()

    assert layout is not None

    gui.alert("test")
    gui.warn("test")

    gui.display()

    gui._smooth.value = True  # pylint: disable=protected-access

    gui.display()


@patch('penelope.notebook.ipyaggrid_utility.display_grid', monkey_patch)
@patch('penelope.notebook.token_counts.plot.plot_by_bokeh', monkey_patch)
def test_create_gui():
    gui = tokens_count_gui.create_token_count_gui('./tests/test_data/', './tests/test_data/')
    assert gui is not None


@pytest.mark.parametrize(
    'normalize,smooth,expected',
    [
        (False, False, [40.0, 25.0]),
        (True, False, [1.0, 1.0]),
        (True, True, [1.0, 1.0]),
    ],
)
def test_compute_token_count_data(normalize: bool, smooth: bool, expected: List[float]):
    attrs = {'categories': [], 'grouping': 'year', 'normalize': normalize, 'smooth': smooth}
    args = Mock(spec=tokens_count_gui.TokenCountsGUI, **attrs)
    document_index = pd.DataFrame(
        data={
            'year': [2020, 2020, 2021],
            'Noun': [10, 30, 25],
            '#Tokens': [10, 30, 25],
        }
    )
    data = tokens_count_gui.compute_token_count_data(args, document_index)
    assert len(data) == 2
    assert np.allclose(data.Noun.tolist(), expected)


@patch('penelope.pipeline.spacy.pipelines.to_tagged_frame_pipeline', patch_pipeline)
def test_load_document_index():
    corpus_config: pipeline.CorpusConfig = pipeline.CorpusConfig.load('./tests/test_data/SSI.yml')
    document_index = tokens_count_gui.load_document_index(corpus_config)

    assert document_index is not None
    assert len(document_index) == 3
    assert 'decade' in document_index.columns
    assert 'lustrum' in document_index.columns
    assert '#Tokens' in document_index.columns
