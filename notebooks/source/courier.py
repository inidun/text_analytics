import io
from os.path import dirname, isdir, isfile, join
from typing import Callable

import pandas as pd
from __paths__ import resources_folder
from loguru import logger
from penelope import corpus as pc
from penelope import pipeline as pp
from penelope.notebook import topic_modelling as tm

FilenameFieldSpec = list[str] | dict[str, Callable, str]

AUTHOR_CATEGORY_ID_CODEC = {
    'Unknown': 0,
    'UNESCO': 1,
    'United Nations': 2,
    'Other author': 3,
}


def property_values_specs() -> list[dict]:
    return [
        {
            'text_name': 'author_category',
            'id_name': 'author_category_id',
            'values': {
                'Unknown': 0,
                'UNESCO': 1,
                'United Nations': 2,
                'Other author': 3,
            },
        },
    ]


def load_document_index(
    filename: str | io.StringIO | pd.DataFrame,
    *,
    sep: str,
    document_id_field: str = 'document_id',
    filename_fields: list[FilenameFieldSpec] | None = None,
    probe_extensions: str = 'csv,csv.gz,csv.zip,zip,gz,feather',
    **read_csv_kwargs,
):
    document_index: pd.DataFrame = pc.load_document_index(
        filename=filename,
        sep=sep,
        document_id_field=document_id_field,
        filename_fields=filename_fields,
        probe_extensions=probe_extensions,
        **read_csv_kwargs,
    )

    document_index = overload_with_author_category(document_index)
    document_index = overload_with_issue_filename(document_index, join(resources_folder, 'issue_filenames.csv'))

    return document_index


def probe_issue_index_filename(state: tm.TopicModelContainer) -> str:
    config: pp.CorpusConfig = state.inferred_topics.corpus_config
    for folder in [config.pipeline_payload.corpus_folder, state.folder, resources_folder]:
        if not folder or not isdir(folder):
            continue
        filename = join(folder, 'issue_filenames.csv')
        if isfile(filename):
            return filename
    return None


def overload_state_on_loaded_handler(state: tm.TopicModelContainer, *_, **__):
    corpus_folder: str = state.inferred_topics.corpus_config.pipeline_payload.corpus_folder
    if not corpus_folder or not isdir(corpus_folder):
        corpus_folder = resources_folder
    document_index: pd.DataFrame = state.inferred_topics.document_index
    document_index = overload_with_author_category(document_index)
    document_index = overload_with_issue_filename(document_index, probe_issue_index_filename(state))
    state.inferred_topics.document_index = document_index


def overload_with_author_category(document_index: pd.DataFrame) -> pd.DataFrame:
    if 'author_category_id' in document_index.columns:
        return document_index

    document_index['author_category_id'] = 3

    for code, key in [(1, 'unesco'), (2, 'united nations')]:
        document_index.loc[
            ~document_index.authors.isna() & document_index.authors.str.lower().str.contains(key),
            ['author_category_id'],
        ] = code
    document_index.loc[document_index.authors.isna(), ['author_category_id']] = 0
    document_index.authors.fillna('Unknown', inplace=True)

    return document_index


def overload_with_issue_filename(document_index: pd.DataFrame, issues_filename: str) -> pd.DataFrame:
    try:
        if isfile(join(dirname(issues_filename), 'issue_filenames.csv')):
            issue_index: pd.DataFrame = pd.read_csv(
                join(dirname(issues_filename), 'issue_filenames.csv'), sep=','
            ).set_index('courier_id')
            issue_index.columns = ['issue_filename']

            document_index = document_index.merge(issue_index, left_on='courier_id', right_index=True, how='left')
    except:  # pylint: disable=bare-except
        logger.warning("issue_filenames.csv not found.")
        document_index['issue_filename'] = document_index.courier_id.apply(lambda x: f'{x:06}engo.pdf')

    return document_index


def get_unesco_index():
    unesco_index = pd.read_csv(
        'https://raw.githubusercontent.com/inidun/unesco_data_collection/master/data/courier/metadata/UNESCO_Courier_metadata.csv',
        sep=';',
    )

    unesco_index = unesco_index[unesco_index['Document type'] == "periodical issue"]
    unesco_index.columns = [
        'record_number',
        'catalogue_title',
        'authors',
        'titles_in_other_languages',
        'languages',
        'series',
        'catalogue_subjects',
        'document_type',
        'host_item',
        'catalogue_publication_date',
        'notes',
    ]
    # unesco_index.drop(columns=['titles_in_other_languages', 'notes', 'languages', 'document_type'], inplace=True)
    return unesco_index
