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

import os
from typing import Iterable, List

import numpy as np
import pandas as pd
from IPython.display import display
from penelope.corpus.readers import TextReaderOpts, TextTransformOpts
from penelope.pipeline import PipelinePayload, SpacyPipeline

import __paths__

CORPUS_FOLDER = os.path.join(__paths__.ROOT_FOLDER, "data")


# # %% [markdown]
# # ## Prepare and load SSI Legal Intruments corpus

# %% tags=[]

POS_TO_COUNT = {
    'SYM': 0,
    'PART': 0,
    'ADV': 0,
    'NOUN': 0,
    'CCONJ': 0,
    'ADJ': 0,
    'DET': 0,
    'ADP': 0,
    'INTJ': 0,
    'VERB': 0,
    'NUM': 0,
    'PRON': 0,
    'PROPN': 0,
}

POS_NAMES = list(sorted(POS_TO_COUNT.keys()))


def compute_corpus_statistics(
    document_index: pd.DataFrame,
    df_docs: Iterable[pd.DataFrame],
    group_by_column: str = "year",
    include_pos: List[str] = None,
):

    doc_year = document_index.year.to_dict()

    datuma = (
        pd.concat((df.assign(year=doc_year[i]) for i, df in enumerate(df_docs)))
        .groupby(['year', 'pos_'])
        .size()
        .reset_index()
        .rename({0: 'count'}, axis=1)
        .assign(count=lambda x: x['count'])
        .pivot(index='year', columns="pos_", values='count')
        .fillna(0)
        .astype(np.int64)
        .reset_index()
    )

    value_columns = list(POS_NAMES) if (len(include_pos or [])) == 0 else list(include_pos)

    datuma["lustrum"] = (datuma.year - datuma.year.mod(5)).astype(int)
    datuma["decade"] = (datuma.year - datuma.year.mod(10)).astype(int)
    datuma["total"] = datuma[value_columns].apply(sum, axis=1)

    aggregates = {x: ["sum"] for x in value_columns}
    aggregates["total"] = ["sum", "mean", "min", "max", "size"]

    datuma = datuma.groupby(group_by_column).agg(aggregates)
    datuma.columns = [("Total, " + x[1].lower()) if x[0] == "total" else x[0] for x in datuma.columns]
    columns = sorted(value_columns) + sorted([x for x in datuma.columns if x.startswith("Total")])

    return datuma[columns]


def display_corpus_statistics(
    corpus_folder: str,
    lang: str,  # pylint: disable=unused-argument
):

    source_path = os.path.join(corpus_folder, "legal_instrument_corpus.zip")
    document_index = pd.read_csv(os.path.join(corpus_folder, "legal_instrument_index.csv"), sep=";", header=0)

    if 'document_id' not in document_index:
        document_index['document_id'] = document_index.index

    filename_fields = ["unesco_id:_:2", "year:_:3", r'city:\w+\_\d+\_\d+\_\d+\_(.*)\.txt']

    reader_opts = TextReaderOpts(filename_pattern="*.txt", filename_fields=filename_fields)
    transform_opts = TextTransformOpts()
    payload = PipelinePayload(source=source_path, document_index=document_index)

    df_docs = (
        SpacyPipeline(payload=payload)
        .load_text(reader_opts=reader_opts, transform_opts=transform_opts)
        .set_spacy_model("en_core_web_sm")
        .text_to_spacy()
        .passthrough()
        .spacy_to_pos_tagged_frame()
        .checkpoint(os.path.join(CORPUS_FOLDER, "ssi_pos_csv.zip"))
        .to_content()
    ).resolve()

    datuma: pd.DataFrame = compute_corpus_statistics(
        document_index, df_docs=df_docs, group_by_column="lustrum", include_pos=None
    )

    display(datuma)


display_corpus_statistics(CORPUS_FOLDER, lang="en")

# %%
