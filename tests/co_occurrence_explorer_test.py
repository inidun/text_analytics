import unittest.mock as mock
from os.path import join as jj

import ipywidgets as widgets
import penelope.notebook.word_trends.trends_gui as trends_gui
import pytest
from penelope.co_occurrence.convert import load_co_occurrences
from penelope.corpus import VectorizedCorpus
from penelope.notebook.word_trends import ITrendDisplayer, TrendsData
from penelope.notebook.word_trends.displayers._displayer import YearTokenDataMixin
from penelope.utility.file_utility import read_json

import notebooks.co_occurrence.co_occurrence_gui as co_occurrence_gui

view = widgets.Output(layout={'border': '2px solid green'})


def test_dispatch_co_occurrence_explorer():

    corpus_folder = './tests/test_data/co_occurrence_bundle/'
    corpus_tag = 'VENUS'
    co_occurrences_filename = jj(corpus_folder, f"{corpus_tag}_co-occurrence.csv.zip")
    options_filename = jj(corpus_folder, f"{corpus_tag}_co-occurrence.csv.json")
    corpus = VectorizedCorpus.load(folder=corpus_folder, tag=corpus_tag)
    co_occurrences = load_co_occurrences(co_occurrences_filename)
    compute_options = read_json(options_filename)

    gui = co_occurrence_gui.create_co_occurrence_explorer_gui(
        corpus=corpus,
        corpus_tag=corpus_tag,
        corpus_folder=corpus_folder,
        co_occurrences=co_occurrences,
        compute_options=compute_options,
    )

    assert gui is not None
    assert gui.data is not None
    assert gui.layout() is not None


def generic_patch(return_value):
    def _generic_patch(*x, **y):  # pylint: disable=unused-argument
        return return_value

    return _generic_patch


@mock.patch('penelope.notebook.word_trends.utils.find_candidate_words', generic_patch(['article/shall']))
@mock.patch('penelope.notebook.word_trends.utils.find_n_top_words', generic_patch(['article/shall']))
def test_word_trends_tabs_gui_update_plot():

    corpus_folder = './data/CERES/'
    corpus_tag = 'CERES'
    corpus = VectorizedCorpus.load(folder=corpus_folder, tag=corpus_tag)

    trends_data = TrendsData(
        corpus=corpus,
        corpus_folder=corpus_folder,
        corpus_tag=corpus_tag,
        n_count=10000,
    ).update()

    def get_mock_context():
        mock_context = mock.MagicMock()
        mock_context.__enter__.return_value = 0
        mock_context.__exit__.return_value = False
        return mock_context

    fake_gui = mock.Mock(
        spec=trends_gui.TrendsGUI,
        **{
            'normalize': False,
            'words': ['article/shall'],
            'word_count': 1000,
            'current_output': get_mock_context(),
            'current_displayer': mock.Mock(spec=ITrendDisplayer, **{}),
        },
    )

    trends_gui.update_plot(fake_gui, trends_data)

    fake_gui.current_displayer.compile.assert_called()
    fake_gui.current_displayer.plot.assert_called()
    with pytest.raises(AssertionError):
        fake_gui.layout.assert_called()


def test_word_trends_year_token_data_mixin_compile():

    corpus_folder = './data/CERES/'
    corpus_tag = 'CERES'
    corpus = VectorizedCorpus.load(folder=corpus_folder, tag=corpus_tag).group_by_year()

    indices = [0, 1, 2, 3]
    data = YearTokenDataMixin().compile(corpus, indices)

    assert data is not None

    assert len(corpus.xs_years()) == corpus.data.shape[0]