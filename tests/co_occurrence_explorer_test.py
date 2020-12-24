import ipywidgets as widgets
import penelope.co_occurrence as co_occurrence
from penelope.corpus import VectorizedCorpus
from penelope.notebook.word_trends.displayers._compile_mixins import CategoryDataMixin
from penelope.utility import read_json, replace_extension

import notebooks.co_occurrence.co_occurrence_gui as co_occurrence_gui

view = widgets.Output(layout={'border': '2px solid green'})


def test_dispatch_co_occurrence_explorer():

    corpus_folder, corpus_tag = './tests/test_data/VENUS/', 'VENUS'
    co_occurrences_filename = co_occurrence.folder_and_tag_to_filename(folder=corpus_folder, tag=corpus_tag)
    options_filename = replace_extension(co_occurrences_filename, '.json')
    bundle = co_occurrence.Bundle(
        corpus_folder=corpus_folder,
        co_occurrences_filename=co_occurrences_filename,
        corpus_tag=corpus_tag,
        co_occurrences=co_occurrence.load_co_occurrences(co_occurrences_filename),
        corpus=VectorizedCorpus.load(folder=corpus_folder, tag=corpus_tag),
        compute_options=read_json(options_filename),
    )
    gui = co_occurrence_gui._create_co_occurrence_explorer_gui(bundle=bundle)  # pylint: disable=protected-access

    assert gui is not None
    assert gui.trends_data is not None
    assert gui.layout() is not None


def generic_patch(return_value):
    def _generic_patch(*x, **y):  # pylint: disable=unused-argument
        return return_value

    return _generic_patch


# @mock.patch('penelope.notebook.word_trends.utils.find_candidate_words', generic_patch(['article/shall']))
# @mock.patch('penelope.notebook.word_trends.utils.find_n_top_words', generic_patch(['article/shall']))
# def test_word_trends_tabs_gui_update_plot():

#     corpus_folder = './data/CERES/'
#     corpus_tag = 'CERES'
#     corpus = VectorizedCorpus.load(folder=corpus_folder, tag=corpus_tag)

#     trends_data = TrendsData(
#         corpus=corpus,
#         corpus_folder=corpus_folder,
#         corpus_tag=corpus_tag,
#         n_count=10000,
#     ).update()

#     def get_mock_context():
#         mock_context = mock.MagicMock()
#         mock_context.__enter__.return_value = 0
#         mock_context.__exit__.return_value = False
#         return mock_context

#     fake_gui = mock.Mock(
#         spec=trends_gui.TrendsGUI,
#         **{
#             'normalize': False,
#             'words': ['article/shall'],
#             'word_count': 1000,
#             'current_output': get_mock_context(),
#             'current_displayer': mock.Mock(spec=ITrendDisplayer, **{}),
#         },
#     )

#     trends_gui.update_plot(fake_gui, trends_data)

#     fake_gui.current_displayer.compile.assert_called()
#     fake_gui.current_displayer.plot.assert_called()
#     with pytest.raises(AssertionError):
#         fake_gui.layout.assert_called()


def test_word_trends_year_token_data_mixin_compile():

    corpus_folder = './data/CERES/'
    corpus_tag = 'CERES'
    corpus = VectorizedCorpus.load(folder=corpus_folder, tag=corpus_tag).group_by_year()

    indices = [0, 1, 2, 3]
    data = CategoryDataMixin().compile(corpus, indices)

    assert data is not None

    assert len(corpus.xs_years()) == corpus.data.shape[0]
