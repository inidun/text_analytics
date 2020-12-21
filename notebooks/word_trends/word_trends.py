# -*- coding: utf-8 -*-
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
# ## Word, or part-of-word, trend analysis
#
# ### Text Processing Pipeline
#
# | | Building block | Arguments | Description |
# | -- | :------------- | :------------- | :------------- |
# | ⚙ | <b>SetTagger</b>SpacyModel | 'en' | spaCy as PoS tagger
# | 📜| <b>LoadText</b> | reader_opts, transform_opts | Text stream provider
# | 🔎 | <b>Tqdm</b> | ⚪ | Progress indicator
# | ⌛ | <b>Passthrough</b> | ⚪ | Passthrough
# | 🔨 | Spacy<b>ToTagged</b>Frame | ⚪ | PoS tagging
# | 💾 | <b>Checkpoint</b> | checkpoint_filename | Checkpoint (tagged frames) to file
# | 🔨 | TaggedFrame<b>ToTokens</b> | extract_tagged_tokens_opts, filter_opts | Tokens extractor
# | 🔨 | <b>TokensTransform</b> | tokens_transform_opts | Tokens transformer
# | 🔨 | <b>ToDocumentContentTuple</b> | ⚪ | Protocol/API adapter
# | 🔎 | <b>Tqdm</b> | ⚪ | Progress indicator
# | 🔨 | <b>ToDTM</b> | vectorize_opts| DTM vectorizer
# | 💾 | <b>Checkpoint</b> | checkpoint_filename| Checkpoint (DTM) to file
#
# ### User instructions
#
# #### Compute DTM
#
# This notebook implements the entire processing pipeline from plain text to computed (and stored)
# document-term matrix that are the basis for the word trend exploration.
#
# For large corpora the DTM processing time can be considerable and in such a case you
# should consider using the CLI-version of the processing pipeline.
#
# Note that the computed DTM is saved on disk in the specified folder. You must enter a
# tag that will be used when namin the (principel) result data file. This file will be named
# tag + `_vectorized_data.pickle` and uniquely identifies the bundle of files that makes
# up the result. Note that if the `tag` already exists in specified folder then it will will
# be overwritten. The tag can be used to describe the main compute arguments. If the
# The result files will be stored in a subfolder named with the tag if the `Create folder` option is checked.
#
# | | Config element |  Description |
# | -- | :------------- | :------------- |
# | | Corpus type | Type of corpus, disabled since only text corpora are allowed in this notebook.
# | | Source corpus file | Select file (ZIP) or folder that contains the text documents.
# | | Output tag | String that will be prefix to result files. Only valid filename chars allowed.
# | | Output folder | Target folder for result files.
# | | Part-of-speech groups | Groups of tags to include in DTM given corpus PoS-schema
# | | Remove stopwords | Remove common stopwords using NLTK language specific stopwords
# | | Extra stopwords | Additional stopwords
# | | Filename fields | Specifies attribute values to be extracted from filenames
#
# N.B. Note that PoS schema (e.g. SUC, Universal, ON5 Penn Treebank tag sets) and language must be set for each corpus.
#
# #### Load DTM
#
# <b>To select a corpus:</b> <b>1)</b> press <b>`Change`</b> to open the file browser, <b>2)</b> find and select the file you want to open and <b>3)</b> press <b>`Change`</b> again to confirm the file and close the prowser. Then you can load the corpus by pressing <b>`Load`</b>.
#
# #### Word trends
#
# Add words of interest and/or regular expressions in the text box. The system will automatically plot matching word - words not plotted does not exist in the (processed) corpus. The regular expressions must be surrounded by vertical bars `|`. To find words ending with `tion` you can enter `|.*tion$|` in the textbox. I might seem cryptical, but is a very powerful notation for searching words. The vertical bars is specified only so that the system can distinguish the regexp from "normal" words. The actual expression is `^.*tion$`. The dot and star`.*` matches any character (the dot) any number of times (the `*`). The dollar sign `$` indicates the word ending. So this expression matches all words that begins with any number of characters follwoed, by the character sequence `tion` at the end of the word. To match all words starting with `info`you can enter `|^info.*|` where `^` specifies the start of the word.
#


# %%
# %load_ext autoreload
# %autoreload 2
from bokeh.plotting import output_notebook
from IPython.core.display import display

import __paths__  # pylint: disable=unused-import
from notebooks.word_trends import word_trends_gui

output_notebook()
display(word_trends_gui.create_gui(corpus_folder=__paths__.data_folder, corpus_config_name="SSI"))

# %%
