from unittest.mock import Mock, patch

import ipywidgets as widgets
import penelope.notebook.word_trends as word_trends_gui
from penelope import co_occurrence, pipeline
from penelope.notebook import interface
from penelope.notebook.co_occurrence import explore_co_occurrence_gui, main_gui

view = widgets.Output(layout={'border': '2px solid green'})


def monkey_patch(*_, **__):
    ...


def test_main_gui_create():
    gui = main_gui.create(data_folder='./tests/test_data', filename_pattern='*.*', loaded_callback=monkey_patch)
    assert gui is not None


@patch('penelope.workflows.co_occurrence.compute_partitioned_by_key', monkey_patch)
def test_compute_co_occurrence_callback():
    config: pipeline.CorpusConfig = pipeline.CorpusConfig.load("./tests/test_data/SSI.yml")
    args: interface.ComputeOpts = Mock(spec=interface.ComputeOpts)
    main_gui.compute_co_occurrence_callback(
        args=args,
        corpus_config=config,
    )


@patch('penelope.co_occurrence.to_trends_data', lambda _: Mock(spec=word_trends_gui.BundleTrendsData))
@patch(
    'penelope.notebook.co_occurrence.ExploreGUI',
    lambda: Mock(spec=explore_co_occurrence_gui.ExploreGUI, **{'setup': Mock}),
)
def test_create_MainGUI():
    corpus_folder: str = './tests/test_data'
    config: pipeline.CorpusConfig = pipeline.CorpusConfig.load('./tests/test_data/SSI.yml')
    gui = main_gui.MainGUI(
        corpus_config=config, data_folder=corpus_folder, corpus_folder=corpus_folder, resources_folder=corpus_folder
    )
    layout = gui.layout()
    assert layout is not None

    gui.display_explorer(bundle=Mock(spec=co_occurrence.Bundle))


@view.capture(clear_output=True)
def test_create_co_occurrence_explorer_gui():

    corpus_filename: str = co_occurrence.to_filename(folder='./tests/test_data/VENUS', tag='VENUS')
    bundle: co_occurrence.Bundle = co_occurrence.Bundle.load(corpus_filename, compute_frame=False)

    trends_data = main_gui.to_trends_data(bundle).update()
    gui_explore: explore_co_occurrence_gui.ExploreGUI = (
        explore_co_occurrence_gui.ExploreGUI(bundle).setup().display(trends_data=trends_data)
    )

    assert gui_explore is not None
