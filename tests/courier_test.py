import pandas as pd
from penelope import pipeline as pp
from penelope.notebook import topic_modelling as ntm
from penelope.notebook.token_counts import pipeline_gui as tc_gui
from penelope.utility.pivot_keys import PivotKeys

from notebooks.source.courier import load_document_index, overload_state_on_loaded_handler

# pylint: disable=protected-access


def test_load_document_index():
    filename: str = "/data/inidun/courier/corpus/v0.2.0/document_index.csv"
    sep: str = "\t"
    di: pd.DataFrame = load_document_index(filename, sep=sep)

    assert 'author_category_id' in di.columns


PIVOT_KEYS_SPECIFICATION: dict = {
    'author_category': {
        'text_name': 'author_category',
        'id_name': 'author_category_id',
        'values': {
            'Unknown': 0,
            'Poet': 1,
            'Lyricist': 2,
            'Other': 3,
        },
    }
}


def test_pivot_keys():
    pivot_keys = PivotKeys()

    pivot_keys.pivot_keys = PIVOT_KEYS_SPECIFICATION

    assert pivot_keys is not None

    assert pivot_keys.is_satisfied()
    assert pivot_keys.has_pivot_keys
    assert pivot_keys.get(text_name='author_category') == PIVOT_KEYS_SPECIFICATION['author_category']
    assert pivot_keys.text_names == ['author_category']
    assert pivot_keys.id_names == ['author_category_id']

    assert pivot_keys.key_name2key_id == {'author_category': 'author_category_id'}
    assert pivot_keys.key_id2key_name == {'author_category_id': 'author_category'}

    assert pivot_keys.key_value_id2name(text_name='author_category') == {
        0: 'Unknown',
        1: 'Poet',
        2: 'Lyricist',
        3: 'Other',
    }
    assert pivot_keys.key_value_name2id(text_name='author_category') == {
        'Unknown': 0,
        'Poet': 1,
        'Lyricist': 2,
        'Other': 3,
    }


def test_courier_tm_find_documents():
    folder: str = '/data/inidun/courier/tm/v0.2.0/tm_courier_v0.2.0_50-TF5-MP0.02-500000-lc.gensim_mallet-lda'

    state: ntm.TopicModelContainer = ntm.TopicModelContainer()

    state.register(object(), callback=overload_state_on_loaded_handler)
    state.load(folder=folder)

    assert 'author_category_id' in state.inferred_topics.document_index.columns

    gui: ntm.WithPivotKeysText.FindTopicDocumentsGUI = ntm.WithPivotKeysText.FindTopicDocumentsGUI(state=state)

    assert gui is not None

    gui.setup()
    _ = gui.layout()

    gui._find_text.value = 'film'
    gui._filter_keys_picker.value = ['author_category']
    gui._filter_values_picker.value = ['author_category: UN']

    gui.update()


def test_token_counts_gui():
    resources_folder = "/data/inidun/resources"

    gui = tc_gui.TokenCountsGUI()

    gui.setup(pp.CorpusConfig.list_all(resources_folder, recursive=True))

    layout = gui.layout()

    gui._corpus_configs.value = gui._corpus_configs.options['curated_courier']

    gui.display()

    assert layout is not None
