import ipywidgets as widgets
import penelope.co_occurrence as co_occurrence
import penelope.notebook.co_occurrence as explore_gui

view = widgets.Output(layout={'border': '2px solid green'})


def test_create_co_occurrence_explorer_gui():

    corpus_filename: str = './tests/test_data/VENUS/VENUS_co-occurrence.csv.zip'
    bundle = co_occurrence.load_bundle(corpus_filename, compute_corpus=False)

    trends_data = co_occurrence.to_trends_data(bundle).update()
    gui_explore: explore_gui.ExploreGUI = explore_gui.ExploreGUI().setup().display(trends_data=trends_data)

    assert gui_explore is not None


def generic_patch(return_value):
    def _generic_patch(*x, **y):  # pylint: disable=unused-argument
        return return_value

    return _generic_patch
