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
# ### Overview

# This notebook implements a processing pipeline from computes word co-occurrences from plain text. The term-term co-occurrence matrix is transformed into a DTM corpus that has a vocabulary consisting of token-pairs. The co-occurring word trends can hence be xxplored using the ordinary word trends analysis tools.

# For large corpora the processing time can be considerable and in such a case you
# should consider using the CLI-version of the processing pipeline.

# ### Text Processing Pipeline

# | | Building block | Arguments | Description |
# | -- | :------------- | :------------- | :------------- |
# | ⚙ | <b>SetTagger</b>SpacyModel | 'en' | spaCy as PoS tagger
# | 📜| <b>LoadText</b> | reader_opts, transform_opts | Text stream provider
# | 🔎 | <b>Tqdm</b> | ⚪ | Progress indicator
# | ⌛ | <b>Passthrough</b> | ⚪ | Passthrough
# | 🔨 | Spacy<b>ToTaggedFrame</b> | spaCy tagger | PoS tagging
# | 💾 | <b>Checkpoint</b> | checkpoint_filename | Checkpoint (tagged frames) to file
# | 🔨 | TaggedFrame<b>ToTokens</b> | extract_tagged_tokens_opts, filter_opts | Tokens extractor
# | 🔨 | <b>TokensTransform</b> | tokens_transform_opts | Tokens transformer
# | 🔨 | <b>Vocabulary</b> | ⚪ | Generate a token to integer ID mappin
# | 🔨 | <b>ToDocumentContentTuple</b> | ⚪ | Protocol/API adapter
# | 🔨 | <i>Partition</i> | ⚪ | Partition corpus into subsets based on predicate (year)
# | 🔎 | <b>ToCoOccurrence</b> | ⚪ | Transform each partition to TTM matrices
# | 🔨 | <i>ToCooFrame</i> | ⚪| Transform TTM into data frame with normalized values
# | 💾 | <i>Checkpoint</i> | checkpoint_filename| Store co-occurrence data frame
# | 🔨 | <b>ToDTM</b> | vectorize_opts| Transform data frame into DTM
# | 💾 | <b>Checkpoint</b> | checkpoint_filename| Checkpoint (DTM) to file


# ### How the co-occurrence counts are computed

# The co-occurrences are computed using a sliding window of size (D + 1 + D) that word by word moves through each document in the corpus, and keeps count of how many windows each pair of words co-occur in. Note that all windows will (currenty) always have an odd number of words, and the reason for this is the conditioned co-occurrence described below.

# The computation is done by first creating a (streamed) windowed corpus, consisting of all windows. From this corpus a DTM (document-term-matrix) is created, giving counts for each word in each window. This DTM is then used to compute a TTM (term-term-matrix) simply by multiplying the DTM with a transposed version of itself.

# Please note that the process of generating windows (currently) ignores sentences, paragraphs etc.

# ### Concept co-occurence

# The algorithm also allows for computing a conditioned co-occurrence, where the set of windows are constrained so that the center-most word must one of a number of specified (concept) words. This results in a set of co-occurrences that occur in close proximity (i.e. the max distance of D) of the center-most word.

# %%

from bokeh.plotting import output_notebook
from IPython.core.display import display

import __paths__  # pylint: disable=unused-import
from notebooks.co_occurrence import co_occurrence_gui

output_notebook()
display(co_occurrence_gui.create_gui(corpus_config_name="SSI"))

# %%
