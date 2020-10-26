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
#     display_name: 'Python 3.8.2 64-bit (''text_analytics'': venv)'
#     metadata:
#       interpreter:
#         hash: feaa6644a67d98bc2c380c25a7ae5b1ab301b95bfc0add23663419f9cdbe38f8
#     name: 'Python 3.8.2 64-bit (''text_analytics'': venv)'
# ---

# %%

# %%
import os
import sys

import glove
from penelope.corpus.readers import TextTokenizer

root_folder = (lambda x: os.path.join(os.getcwd().split(x)[0], x))("text_analytics")
sys.path.insert(0, root_folder)


corpus_folder = os.path.join(root_folder, "data")
corpus_path = os.path.join(corpus_folder, "legal_instrument_corpus_preprocessed.zip")

tokenizer = TextTokenizer(
    source=corpus_path,
    filename_pattern="*.txt",
    fix_whitespaces=True,
    fix_hyphenation=True,
    filename_fields=None,
)

reader = (tokens for _, tokens in tokenizer)

corpus = glove.Corpus()

corpus.fit(reader, 5, False)
