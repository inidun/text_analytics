from unittest.mock import Mock, patch

import ipywidgets as widgets
import penelope.co_occurrence as co_occurrence
import penelope.notebook.co_occurrence as explore_gui
import penelope.notebook.word_trends as word_trends_gui
import penelope.pipeline as pipeline

import notebooks.co_occurrence.co_occurrence_gui as co_occurrence_gui

from ..utils import SSI_config

view = widgets.Output(layout={'border': '2px solid green'})


def monkey_patch(*_, **__):
    ...


def test_co_occurrence_gui_create():
    gui = co_occurrence_gui.create(
        data_folder='./tests/test_data', filename_pattern='*.*', loaded_callback=monkey_patch
    )
    assert gui is not None


@patch('penelope.notebook.co_occurrence.pipeline_compute_co_occurrence', monkey_patch)
def test_compute_co_occurrence_callback():
    config: pipeline.CorpusConfig = pipeline.CorpusConfig.loads(SSI_config)
    partition_key: str = 'year'
    args: explore_gui.ComputeGUI = Mock(spec=explore_gui.ComputeGUI)
    done_callback = monkey_patch
    checkpoint_file = '/tests/output/'
    co_occurrence_gui.compute_co_occurrence_callback(
        corpus_config=config,
        args=args,
        partition_key=partition_key,
        done_callback=done_callback,
        checkpoint_file=checkpoint_file,
    )


@patch('penelope.co_occurrence.to_trends_data', lambda x: Mock(spec=word_trends_gui.TrendsData))
@patch('penelope.notebook.co_occurrence.ExploreGUI', lambda: Mock(spec=explore_gui.ExploreGUI, **{'setup': Mock}))
def test_create_MainGUI():
    corpus_folder: str = './tests/test_data'
    config: pipeline.CorpusConfig = pipeline.CorpusConfig.loads(SSI_config)
    gui = co_occurrence_gui.MainGUI(corpus_config=config, corpus_folder=corpus_folder)
    layout = gui.layout()
    assert layout is not None
    gui.display_explorer(bundle=Mock(spec=co_occurrence.Bundle))


@view.capture(clear_output=True)
def test_create_co_occurrence_explorer_gui():

    corpus_filename: str = co_occurrence.folder_and_tag_to_filename(folder='./tests/test_data/VENUS', tag='VENUS')
    bundle = co_occurrence.load_bundle(corpus_filename, compute_corpus=False)

    # create by function
    gui = explore_gui.ExploreGUI()
    assert gui is not None

    # create by class
    trends_data = co_occurrence.to_trends_data(bundle).update()
    gui_explore: explore_gui.ExploreGUI = explore_gui.ExploreGUI(
        trends_data=trends_data,
    )

    assert gui_explore is not None
