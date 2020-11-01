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

# pylint: disable=wrong-import-order, no-member
import os
import types

import bokeh.plotting
import notebooks.word_trends.word_trends_compute_gui as word_trends_gui

root_folder = __paths__.ROOT_FOLDER
corpus_folder = os.path.join(root_folder, 'data')
bokeh.plotting.output_notebook(hide_banner=True)

container = types.SimpleNamespace(
    corpus=None, t_corpus=None, index=None, handle=None, data_source=None, data=None, figure=None
)


# %% [markdown]
# ### Load and display corpus
#
#
# The corpus was created with the following settings:
#  - Tokens were converted to lower case.
#  - Only tokens that contains at least one alphanumeric character (isalnum).
#  - Accents are ot removed (deacc)
#  - Min token length 2 (min_len)
#  - Max length not set (max_len)
#  - Numerals are removed (numerals, -N)
#  - Symbols are removed (symbols, -S)
#
# Use the `vectorize_corpus` script to create a new corpus with different settings.
#
# The corpus is processed in the following ways when loaded:
#
#  - Exclude tokens having a total word count less than `Min count`
#  - Include at most `Top count` most frequent words.
#  - Group and sum up documents by year.
#  - Normalize token distribution over years to 1.0
#

# %% tags=[]

_ = word_trends_gui.display_gui(corpus_folder, container=container)

# %%
