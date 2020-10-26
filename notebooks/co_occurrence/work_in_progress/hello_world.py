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
#     display_name: 'Python 3.8.5 64-bit (''text_analytics'': pipenv)'
#     language: python
#     name: python_defaultSpec_1600258470310
# ---

# %%
import os
import sys

# %% tags=[]
import pandas as pd
from westac.corpus import vectorized_corpus

root_folder = os.path.join(os.getcwd().split('text_analytics')[0], 'text_analytics')
sys.path = list(set(sys.path + [root_folder]))

assert sys.version_info > (3, 8, 5)


# %% tags=[]
corpus_tag = 'legal_instrument_corpus_L2_-N_+S'
corpus_folder = os.path.join(root_folder, 'data')

x_corpus = vectorized_corpus.VectorizedCorpus.load(corpus_tag, folder=corpus_folder)  # .stats()
# .slice_by_n_count(n_count)\
# .slice_by_n_top(n_top)
# .filter(year_filter)\


top = pd.DataFrame.from_dict(x_corpus.n_top_tokens(500), orient='index')
docs = x_corpus.documents.sort_values(by=['year'])
display(top, docs)
