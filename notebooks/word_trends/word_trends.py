# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: 'Python 3.8.5 64-bit (''text-analytics-symNAVlf-py3.8'': venv)'
#     metadata:
#       interpreter:
#         hash: f9f5370a66fe709225320b0a5e42eaf481fec3c92c4ac457a33063cd6d0e2297
#     name: 'Python 3.8.5 64-bit (''text-analytics-symNAVlf-py3.8'': venv)'
# ---


# %%

from dataclasses import dataclass

import penelope.notebook.dtm as vectorize_gui
import penelope.notebook.dtm.load_DTM_gui as load_DTM_gui
import penelope.notebook.word_trends as word_trends
from bokeh.plotting import output_notebook
from IPython.core.display import display
from penelope.corpus import VectorizedCorpus

import __paths__
from notebooks.common.spacy_pipelines import spaCy_DTM_pipeline
from notebooks.corpus_data_config import SSI, CorpusConfig

output_notebook()


@dataclass
class State:
    word_trend_data: word_trends.WordTrendData = None


ssi: CorpusConfig = SSI(corpus_folder=__paths__.data_folder)
state = State(word_trend_data=word_trends.WordTrendData())


def corpus_loaded_callback(
    corpus: VectorizedCorpus, corpus_tag: str, corpus_folder: str
):  # pylint: disable=unused-argument
    global state
    print("Corpus succesfully vectorized!")
    print("Generating trend data!")
    state.word_trend_data.update(
        corpus=corpus.group_by_year(),
        corpus_folder=corpus_folder,
        corpus_tag=corpus_tag,
        n_count=1000,
    )
    print("Data successfully created!")


# %%

gui_vectorize = vectorize_gui.display_gui(
    corpus_folder=__paths__.data_folder,
    corpus_config=ssi,
    pipeline_factory=spaCy_DTM_pipeline,
    done_callback=corpus_loaded_callback,
)

display(gui_vectorize.layout(hide_input=False, hide_output=False))

# %%

gui_load = load_DTM_gui.create_gui(
    corpus_folder=__paths__.data_folder,
    loaded_callback=corpus_loaded_callback,
)

display(gui_load.layout())

# %%

gui_trends = word_trends.create_gui(
    corpus=state.word_trend_data.corpus,
    corpus_folder=state.word_trend_data.corpus_folder,
    corpus_tag=state.word_trend_data.corpus_tag,
    word_trend_data=state.word_trend_data,
)
display(gui_trends.layout())

# %%
