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
# # Setup notebook

# %% tags=[]
# %load_ext autoreload
# %autoreload 2

# %%
import collections
import os
from typing import List

# pylint: disable=wrong-import-order
import __paths__

# import notebooks.common.ipyaggrid_plot as ipyaggrid_plot
import pandas as pd
import penelope.utility.utils as utility
import penelope.vendor.textacy as textacy_utility
import textacy
from IPython.display import display
from penelope.vendor.textacy.pipeline import CreateTask, LoadTask, PreprocessTask, SaveTask, TextacyCorpusPipeline
import notebooks.common.ipyaggrid_plot as ipyaggrid_plot

ROOT_FOLDER = __paths__.ROOT_FOLDER
CORPUS_FOLDER = os.path.join(ROOT_FOLDER, "data")


# %% [markdown]
# ## Prepare and load `SSI Legal Intruments` corpus


def get_pos_statistics(doc):

    pos_iter = (x.pos_ for x in doc if x.pos_ not in ["NUM", "PUNCT", "SPACE"])
    pos_counts = dict(collections.Counter(pos_iter))
    stats = utility.extend(
        dict(document_id=doc.user_data["textacy"]["meta"]["document_id"]),
        dict(textacy_utility.POS_TO_COUNT),
        pos_counts,
    )
    return stats


def add_corpus_metadata(corpus: textacy.Corpus, documents: pd.DataFrame) -> pd.DataFrame:

    metadata = [get_pos_statistics(doc) for doc in corpus]
    df = pd.DataFrame(metadata).set_index("document_id")
    df = df.merge(documents, how="inner", left_index=True, right_on="unesco_id")
    df["words"] = df[textacy_utility.POS_NAMES].apply(sum, axis=1)

    return df


def compute_corpus_statistics(
    documents: pd.DataFrame,
    textacy_corpus: textacy.Corpus,
    group_by_column: str = "year",
    include_pos: List[str] = None,
):

    documents = add_corpus_metadata(textacy_corpus, documents)
    value_columns = list(textacy_utility.POS_NAMES) if (len(include_pos or [])) == 0 else list(include_pos)

    documents["signed_lustrum"] = (documents.year - documents.year.mod(5)).astype(int)
    documents["signed_decade"] = (documents.year - documents.year.mod(10)).astype(int)
    documents["total"] = documents[value_columns].apply(sum, axis=1)

    aggregates = {x: ["sum"] for x in value_columns}
    aggregates["total"] = ["sum", "mean", "min", "max", "size"]

    documents = documents.groupby(group_by_column).agg(aggregates)
    documents.columns = [("Total, " + x[1].lower()) if x[0] == "total" else x[0] for x in documents.columns]
    columns = sorted(value_columns) + sorted([x for x in documents.columns if x.startswith("Total")])
    return documents[columns]


def display_corpus_statistics(
    corpus_folder: str,
    lang: str,
):

    source_path = os.path.join(corpus_folder, "legal_instrument_corpus.zip")
    documents = pd.read_csv(os.path.join(corpus_folder, "legal_instrument_index.csv"), sep=";", header=0)
    filename_fields = ["unesco_id:_:2", "year:_:3", r'city:\w+\_\d+\_\d+\_\d+\_(.*)\.txt']

    options = dict(filename=source_path, lang=lang, documents=documents, filename_fields=filename_fields)
    tasks = [
        PreprocessTask,
        CreateTask,
        SaveTask,
        LoadTask,
    ]
    pipeline = TextacyCorpusPipeline(**options, tasks=tasks)
    corpus = pipeline.process().corpus

    corpus_stats: pd.DataFrame = compute_corpus_statistics(documents, corpus)

    display(ipyaggrid_plot.simple_plot(corpus_stats))


display_corpus_statistics(corpus_folder=CORPUS_FOLDER, lang="en")
