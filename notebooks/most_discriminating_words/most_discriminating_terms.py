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
# ## Most Discriminating Terms
# References:
#     King, Gary, Patrick Lam, and Margaret Roberts. "Computer-Assisted Keyword
#     and Document Set Discovery from Unstructured Text." (2014).
#     http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.458.1445&rep=rep1&type=pdf

# %%
# %load_ext autoreload
# %autoreload 2

import __paths__
from IPython.display import display
from penelope.notebook.mdw import create_main_gui

__paths__.data_folder = "/data/inidun"
__paths__.resources_folder = "/data/inidun/resources"

gui = create_main_gui(folder=__paths__.data_folder)

display(gui.layout())

# %%
