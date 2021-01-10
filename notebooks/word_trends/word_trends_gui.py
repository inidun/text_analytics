import ipywidgets as widgets
import penelope.notebook.dtm.compute_DTM_pipeline as compute_DTM_pipeline
import penelope.notebook.dtm.load_DTM_gui as load_DTM_gui
import penelope.notebook.dtm.to_DTM_gui as to_DTM_gui
import penelope.notebook.word_trends as word_trends
import penelope.pipeline as pipeline
from IPython.core.display import display
from penelope.corpus import VectorizedCorpus
from penelope.pipeline.spacy.pipelines import spaCy_DTM_pipeline

import __paths__

view = widgets.Output(layout={'border': '2px solid green'})


@view.capture(clear_output=True)
def corpus_loaded_callback(
    corpus: VectorizedCorpus,
    corpus_tag: str,
    corpus_folder: str,
    **_,
):
    trends_data: word_trends.TrendsData = word_trends.TrendsData(
        corpus=corpus,
        corpus_folder=corpus_folder,
        corpus_tag=corpus_tag,
        n_count=25000,
    ).update()

    gui = word_trends.GofTrendsGUI(
        gofs_gui=word_trends.GoFsGUI().setup(),
        trends_gui=word_trends.TrendsGUI().setup(),
    )

    display(gui.layout())
    gui.display(trends_data=trends_data)


@view.capture(clear_output=True)
def corpus_compute_callback(*args, **kwargs):
    compute_DTM_pipeline.compute_document_term_matrix(*args, **kwargs)


def create_gui(corpus_folder: str, corpus_config_name: str) -> widgets.CoreWidget:
    config: pipeline.CorpusConfig = pipeline.CorpusConfig.find(corpus_config_name, __paths__.resources_folder).folder(
        corpus_folder
    )
    gui_compute: to_DTM_gui.ComputeGUI = to_DTM_gui.create_gui(
        corpus_folder=corpus_folder,
        corpus_config=config,
        pipeline_factory=spaCy_DTM_pipeline,
        compute_document_term_matrix=corpus_compute_callback,
        done_callback=corpus_loaded_callback,
    )

    gui_load: load_DTM_gui.LoadGUI = load_DTM_gui.create_gui(
        corpus_folder=corpus_folder,
        loaded_callback=corpus_loaded_callback,
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

    accordion.set_title(0, "LOAD AN EXISTING DOCUMENT-TERM MATRIX")
    accordion.set_title(1, '...OR COMPUTE A NEW DOCUMENT-TERM MATRIX')

    return widgets.VBox([accordion, view])
