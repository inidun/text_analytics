# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Token Count Statistics
# ### Text Processing Pipeline
#
# | | Building block | Arguments | Description |
# | -- | :------------- | :------------- | :------------- |
# | 💾 | <b>Checkpoint</b> | checkpoint_filename | Checkpoint (tagged frames) to file
#
# The PoS tagging notebook uses the same processing pipeline as the Word trends notebook to produce VRT data frames. The processing reads
# a checkpoint file if it exists, otherwise it will resolve the full pipeline.
#
# The word count statistics are collected in the tagging task (part-of-speech and lemma annotation). The computed statistics, total word count and the word counts for each PoS-grouping, are added (or updated) to the _document index file_ as new columns. This file is stored in the tagged text archive as `document_index.csv`.
#
# Note: The dcument index file is either a pre-existing document index or, if no such index exists, automatically generated during the initial text loading pipeline task.
# If no pre-existing file exists, then the necessary attributes (e.g. document's year) are extracted from the filename of each  document.

# %%

import __paths__  # pylint: disable=unused-import
from bokeh.io import output_notebook
from IPython.display import display
from penelope import pipeline as pp
from penelope.notebook.token_counts import pipeline_gui as tc_gui

output_notebook()

resources_folder = "/data/inidun/resources"
config_filenames: str = pp.CorpusConfig.list_all(resources_folder, recursive=True, try_load=True)

gui = tc_gui.TokenCountsGUI().setup(config_filenames).display()

display(gui.layout())
