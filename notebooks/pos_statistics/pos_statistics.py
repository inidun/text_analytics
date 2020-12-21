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

# %% tags=[]
# %load_ext autoreload
# %autoreload 2

from IPython.core.display import display
import __paths__
import notebooks.pos_statistics.tokens_count_gui as tokens_count_gui

gui = tokens_count_gui.create_token_count_gui("SSI")
display(gui.layout())
# %%
