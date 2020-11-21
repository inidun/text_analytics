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
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Setup Notebook

# %% tags=[] vscode={}
# %load_ext autoreload
# %autoreload 2

import __paths__  # isort:skip

# %% [markdown]
# ### Load and display corpus
import importlib

# pylint: disable=wrong-import-order, no-member
import os

import notebooks.word_trends.word_trends_compute_gui as vectorize_corpus_gui
import penelope.notebook.vectorized_corpus_load_gui as load_corpus_gui
from bokeh.plotting import output_notebook
from penelope.notebook.word_trends import display_word_trends

root_folder = __paths__.ROOT_FOLDER
corpus_folder = os.path.join(root_folder, 'data')
output_notebook(hide_banner=True)


importlib.reload(vectorize_corpus_gui)

filename_fields = ["unesco_id:_:2", "year:_:3", r'city:\w+\_\d+\_\d+\_\d+\_(.*)\.txt']
year_range = [1945, 2020]

vectorize_corpus_gui.display_gui(
    filename_fields=filename_fields,
    corpus_folder=corpus_folder,
    year_range=year_range,
    display_callback=display_word_trends,
)

# %%
load_corpus_gui.display_gui(loaded_callback=display_word_trends)
