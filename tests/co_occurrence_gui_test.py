import ipywidgets as widgets
import penelope.co_occurrence as co_occurrence
import penelope.notebook.co_occurrence as explore_gui

import __paths__

view = widgets.Output(layout={'border': '2px solid green'})


@view.capture(clear_output=True)
def test_create_co_occurrence_explorer_gui():

    corpus_filename: str = './tests/test_data/VENUS/VENUS_co-occurrence.csv.zip'
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


# def create_gui_test():
#     corpus_config_name: str = "SSI"
#     corpus_folder: str = './data'
#     config = CorpusConfig.find(corpus_config_name, __paths__.resources_folder).folder(corpus_folder)

#     gui = co_occurrence_gui.create_gui(corpus_config_name=corpus_config_name, corpus_folder=corpus_folder)

#     gui_compute = compute_gui.create_gui(
#         corpus_folder=corpus_folder,
#         corpus_config=config,
#         compute_callback=compute_co_occurrence,
#         done_callback=co_occurrence_gui._dispatch_co_occurrence_explorer,  # pylint: disable=protected-access
#     )

#     gui_load = load_gui.create_gui(
#         data_folder=corpus_folder,
#         filename_pattern=co_occurrence.CO_OCCURRENCE_FILENAME_PATTERN,
#         loaded_callback=co_occurrence_gui._dispatch_co_occurrence_explorer,  # pylint: disable=protected-access
#     )

#     accordion = widgets.Accordion(
#         children=[
#             widgets.VBox(
#                 [
#                     gui_load.layout(),
#                 ],
#                 layout={'border': '1px solid black', 'padding': '16px', 'margin': '4px'},
#             ),
#             widgets.VBox(
#                 [
#                     gui_compute.layout(),
#                 ],
#                 layout={'border': '1px solid black', 'padding': '16px', 'margin': '4px'},
#             ),
#         ]
#     )

#     accordion.set_title(0, "LOAD AN EXISTING CO-OCCURRENCE COMPUTATION")
#     accordion.set_title(1, '...OR COMPUTE A NEW CO-OCCURRENCE')
#     accordion.set_title(2, '...OR LOAD AND EXPLORE A CO-OCCURRENCE DTM')
#     accordion.set_title(3, '...OR COMPUTE OR DOWNLOAD CO-OCCURRENCES AS EXCEL')

#     return widgets.VBox([accordion, view])
