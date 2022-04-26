from typing import List
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest
from penelope import pipeline
from penelope.notebook.token_counts import pipeline_gui


def monkey_patch(*_, **__):
    ...


def load_corpus_config(_: str) -> pipeline.CorpusConfig:
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
@patch('penelope.notebook.token_counts.plot.plot_multiline', monkey_patch)
@patch('penelope.notebook.token_counts.plot.plot_stacked_bar', lambda *_, **__: None)
def test_create_token_count_gui():
    def compute_callback(_: pipeline_gui.TokenCountsGUI, __: pd.DataFrame) -> pd.DataFrame:
        ...

    gui = pipeline_gui.TokenCountsGUI(
        compute_callback=compute_callback,
        load_document_index_callback=load_document_index_patch,
        load_corpus_config_callback=load_corpus_config,
    )

    gui = gui.setup(['tests/test_data/SSI.yml'])

    assert not gui.smooth
    assert not gui.normalize
    assert gui.grouping == pipeline_gui.TOKEN_COUNT_GROUPINGS[-1]

    layout = gui.layout()

    assert layout is not None

    gui.alert("test")
    gui.warn("test")

    gui.display()

    gui._smooth.value = True  # pylint: disable=protected-access

    gui.display()


@patch('penelope.notebook.ipyaggrid_utility.display_grid', monkey_patch)
@patch('penelope.notebook.token_counts.plot.plot_multiline', monkey_patch)
@patch('penelope.notebook.token_counts.plot.plot_stacked_bar', lambda *_, **__: None)
def test_create_gui():
    gui = pipeline_gui.create_token_count_gui('./tests/test_data/', './tests/test_data/')
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
    args = Mock(spec=pipeline_gui.TokenCountsGUI, **attrs)
    document_index = pd.DataFrame(
        data={
            'year': [2020, 2020, 2021],
            'Noun': [10, 30, 25],
            '#Tokens': [10, 30, 25],
        }
    )
    data = pipeline_gui.compute_token_count_data(args, document_index)
    assert len(data) == 2
    assert np.allclose(data.Noun.tolist(), expected)


def test_load_document_index():
    corpus_config: pipeline.CorpusConfig = pipeline.CorpusConfig.load('./tests/test_data/SSI.yml')
    corpus_config.pipeline_payload.folders('./tests/test_data')
    document_index = pipeline_gui.load_document_index(corpus_config)

    assert document_index is not None
    assert len(document_index) == 5
    assert 'decade' in document_index.columns
    assert 'lustrum' in document_index.columns
    assert '#Tokens' in document_index.columns
