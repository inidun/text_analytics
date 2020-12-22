# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Token Count Statistics
# ### Text Processing Pipeline

# | | Building block | Arguments | Description |
# | -- | :------------- | :------------- | :------------- |
# | 💾 | <b>Checkpoint</b> | checkpoint_filename | Checkpoint (tagged frames) to file
# | 🔨 | TaggedFrame<b>ToTokens</b> | extract_tagged_tokens_opts, filter_opts | Tokens extractor

# The PoS tagging uses the same pipeline to produce a tagged data frame
# as for instance the word trends pipeline do. The processing will hence read
# checkpoint file if it exists, otherwise the full pipeline is executed.
# The word count statistics are collected as a side effect of the tagging (annotation) task.
# The total word count, and the word counts for each PoS-grouping, is added to each document in the
# index (ledger) file as new columns.
#
# Note: The dcument index file is either a pre-existing document index or,
# if no such index exists, automatically generated during the initial pipeline tasks.
# If no pre-existing file exists, then the necessary attributes (e.g. document's year)
# are extracted from each document's filename.

# %% tags=[]
# %load_ext autoreload
# %autoreload 2

from IPython.core.display import display

import __paths__  # pylint: disable=unused-import
import notebooks.pos_statistics.tokens_count_gui as tokens_count_gui

gui = tokens_count_gui.create_token_count_gui("SSI")
display(gui.layout())
# %%
