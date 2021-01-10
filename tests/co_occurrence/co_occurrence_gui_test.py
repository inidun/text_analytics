import ipywidgets as widgets
import penelope.co_occurrence as co_occurrence
import penelope.notebook.co_occurrence as explore_gui

view = widgets.Output(layout={'border': '2px solid green'})


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
