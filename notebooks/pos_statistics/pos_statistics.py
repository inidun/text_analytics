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

import notebooks.common.ipyaggrid_plot as ipyaggrid_plot
import pandas as pd
import paths
import penelope.utility.utils as utility
import penelope.vendor.textacy as textacy_utility
import textacy
from IPython.display import display
from penelope.corpus import preprocess_text_corpus
from penelope.corpus.readers import ZipTextIterator

ROOT_FOLDER = paths.ROOT_FOLDER
CORPUS_FOLDER = os.path.join(ROOT_FOLDER, "data")


# %% [markdown]
# ## Prepare and load `SSI Legal Intruments` corpus


def get_document_stream(prepped_source_path: str, documents: pd.DataFrame):

    reader = ZipTextIterator(prepped_source_path)
    documents = documents.set_index("filename")

    for document_name, text in reader:

        metadata = documents.loc[document_name].to_dict()
        document_id = metadata["unesco_id"]

        yield document_name, document_id, text, metadata


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


def load_corpus(source_path: str, documents: pd.DataFrame, lang="en"):

    nlp = textacy_utility.create_nlp(lang, disable=("ner",))

    prepped_source_path = utility.path_add_suffix(source_path, "_preprocessed")
    textacy_corpus_path = textacy_utility.generate_corpus_filename(prepped_source_path, lang)

    if not os.path.isfile(prepped_source_path):
        preprocess_text_corpus(source_path, prepped_source_path)

    textacy_corpus: textacy.Corpus = None
    if not os.path.isfile(textacy_corpus_path):

        stream = get_document_stream(prepped_source_path, documents)
        textacy_corpus = textacy_utility.create_corpus(stream, nlp)
        textacy_corpus.save(textacy_corpus_path)

    else:
        textacy_corpus = textacy_utility.load_corpus(textacy_corpus_path, nlp)

    return textacy_corpus


def display_corpus_statistics(
    corpus_folder: str,
    lang: str,
):

    source_path = os.path.join(corpus_folder, "legal_instrument_corpus.zip")

    documents = pd.read_csv(os.path.join(corpus_folder, "legal_instrument_index.csv"), sep=";", header=0)

    textacy_corpus = load_corpus(source_path, documents, lang)

    corpus_stats: pd.DataFrame = compute_corpus_statistics(documents, textacy_corpus)

    display(ipyaggrid_plot.simple_plot(corpus_stats))


display_corpus_statistics(corpus_folder=CORPUS_FOLDER, lang="en")
