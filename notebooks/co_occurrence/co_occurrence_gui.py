from typing import Any, Mapping

import ipywidgets as widgets
import pandas as pd
import penelope.notebook.co_occurrence.explore_co_occurrence_gui as explore_gui
import penelope.notebook.co_occurrence.load_co_occurrences_gui as load_gui
import penelope.notebook.co_occurrence.to_co_occurrence_gui as compute_gui
from IPython.core.display import display
from penelope.corpus import VectorizedCorpus
from penelope.notebook.co_occurrence.compute_callback_pipeline import compute_co_occurrence
from penelope.notebook.word_trends.trends_data import TrendsData
from penelope.pipeline import CorpusConfig

import __paths__

CORPUS_FOLDER = __paths__.data_folder

view = widgets.Output(layout={'border': '2px solid green'})


@view.capture(clear_output=True)
def create_co_occurrence_explorer_gui(
    corpus: VectorizedCorpus,
    corpus_tag: str,
    corpus_folder: str,
    co_occurrences: pd.DataFrame,
    compute_options: Mapping[str, Any],
    **_,
) -> explore_gui.ExploreCoOccurrencesGUI:

    trends_data = (
        TrendsData(
            compute_options=compute_options,
            corpus=corpus,
            corpus_folder=corpus_folder,
            corpus_tag=corpus_tag,
            n_count=25000,
        )
        .update()
        .remember(co_occurrences=co_occurrences)
    )

    gui_explore: explore_gui.ExploreCoOccurrencesGUI = explore_gui.ExploreCoOccurrencesGUI(
        trends_data=trends_data,
    )

    return gui_explore


@view.capture(clear_output=True)
def dispatch_co_occurrence_explorer(*args, **kwargs):
    gui = create_co_occurrence_explorer_gui(*args, **kwargs)
    display(gui.layout())


def create_gui(corpus_config_name: str, corpus_folder: str = __paths__.data_folder) -> widgets.VBox:
    config = CorpusConfig.find(corpus_config_name, __paths__.resources_folder).folder(corpus_folder)
    gui_compute = compute_gui.create_gui(
        corpus_folder=corpus_folder,
        corpus_config=config,
        compute_callback=compute_co_occurrence,
        done_callback=dispatch_co_occurrence_explorer,
    )

    gui_load = load_gui.create_gui(
        data_folder=corpus_folder,
        filename_pattern="*co_occurrence.csv.zip",
        loaded_callback=dispatch_co_occurrence_explorer,
    )

    accordion = widgets.Accordion(
        children=[
            widgets.VBox(
                [
                    gui_load.layout(),
                ],
                layout={'border': '1px solid black', 'padding': '16px', 'margin': '4px'},
            ),
            widgets.VBox(
                [
                    gui_compute.layout(),
                ],
                layout={'border': '1px solid black', 'padding': '16px', 'margin': '4px'},
            ),
        ]
    )

    accordion.set_title(0, "LOAD AN EXISTING CO-OCCURRENCE COMPUTATION")
    accordion.set_title(1, '...OR COMPUTE A NEW CO-OCCURRENCE')
    accordion.set_title(2, '...OR LOAD AND EXPLORE A CO-OCCURRENCE DTM')
    accordion.set_title(3, '...OR COMPUTE OR DOWNLOAD CO-OCCURRENCES AS EXCEL')

    return widgets.VBox([accordion, view])
