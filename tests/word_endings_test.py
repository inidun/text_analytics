import os
import pathlib
import re
from typing import Any, Dict, List

import ipyfilechooser
import pandas as pd
import pytest
from penelope.corpus import TokensTransformOpts, VectorizedCorpus, VectorizeOpts
from penelope.corpus.readers import ExtractTaggedTokensOpts, TaggedTokensFilterOpts, TextReaderOpts, TextTransformOpts
from penelope.notebook.dtm.compute_DTM_pipeline import compute_document_term_matrix
from penelope.notebook.utility import shorten_filechooser_label
from penelope.pipeline import CorpusConfig, CorpusType, DocumentPayload, PipelinePayload, SpacyPipeline
from sklearn.feature_extraction.text import CountVectorizer

from notebooks.common.spacy_pipelines import spaCy_DTM_pipeline

CORPUS_FOLDER = './tests/test_data'
OUTPUT_FOLDER = './tests/output'

# pylint: disable=redefined-outer-name


@pytest.fixture(scope='module')
def config():
    return CorpusConfig(
        corpus_name='legal_instrument_unesco',
        corpus_type=CorpusType.Text,
        text_reader_opts=TextReaderOpts(
            filename_fields=["unesco_id:_:2", "year:_:3", r'city:\w+\_\d+\_\d+\_\d+\_(.*)\.txt'],
            index_field=None,
            filename_filter=None,
            filename_pattern="*.txt",
            as_binary=False,
        ),
        pipeline_payload=PipelinePayload(
            source=os.path.join(CORPUS_FOLDER, "legal_instrument_five_docs_test.zip"),
            document_index_source=os.path.join(CORPUS_FOLDER, "legal_instrument_five_docs_test.csv"),
            document_index_key=None,
            document_index_sep=';',
            pos_schema_name="Universal",
            memory_store={'tagger': 'spaCy', 'spacy_model': "en_core_web_sm", 'nlp': None, 'lang': 'en,'},
        ),
    )


def test_corpus_config_set_folder(config: CorpusConfig):

    current_source = config.pipeline_payload.source
    config.set_folder(CORPUS_FOLDER)

    assert config.pipeline_payload.source == os.path.join(CORPUS_FOLDER, current_source)


def test_load_text_returns_payload_with_expected_document_index(config: CorpusConfig):

    transform_opts = TextTransformOpts()

    pipeline = SpacyPipeline(payload=config.pipeline_payload).load_text(
        reader_opts=config.text_reader_opts, transform_opts=transform_opts
    )
    assert pipeline is not None

    payloads: List[DocumentPayload] = [x for x in pipeline.resolve()]

    assert len(payloads) == 5
    assert len(pipeline.payload.document_index) == 5
    assert len(pipeline.payload.metadata) == 5
    assert pipeline.payload.pos_schema_name == "Universal"
    assert pipeline.payload.get('text_reader_opts') == config.text_reader_opts.props
    assert isinstance(pipeline.payload.document_index, pd.DataFrame)

    columns = pipeline.payload.document_index.columns.tolist()
    assert columns == [
        'section_id',
        'unesco_id',
        'filename',
        'type',
        'href',
        'year',
        'date',
        'city',
        'x.title',
        'document_id',
        'document_name',
    ]
    assert all([x.split(':')[0] in columns for x in config.text_reader_opts.filename_fields])
    # assert pipeline.payload.document_index.index.name == config.pipeline_payload.document_index_key
    assert pipeline.payload.document_lookup('RECOMMENDATION_0201_049455_2017.txt')['unesco_id'] == 49455


def test_pipeline_load_text_tag_checkpoint_stores_checkpoint(config: CorpusConfig):

    checkpoint_filename: str = os.path.join(OUTPUT_FOLDER, 'checkpoint_pos_tagged_test.zip')

    transform_opts = TextTransformOpts()

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    pathlib.Path(checkpoint_filename).unlink(missing_ok=True)

    _ = (
        SpacyPipeline(payload=config.pipeline_payload)
        .set_spacy_model(config.pipeline_payload.memory_store['spacy_model'])
        .load_text(reader_opts=config.text_reader_opts, transform_opts=transform_opts)
        .text_to_spacy()
        .tqdm()
        .spacy_to_pos_tagged_frame()
        .checkpoint(checkpoint_filename)
    ).exhaust()

    assert os.path.isfile(checkpoint_filename)


def test_pipeline_can_load_pos_tagged_checkpoint(config: CorpusConfig):

    checkpoint_filename: str = os.path.join(CORPUS_FOLDER, 'checkpoint_pos_tagged_test.zip')

    pipeline = SpacyPipeline(payload=config.pipeline_payload).checkpoint(checkpoint_filename)

    payloads: List[DocumentPayload] = pipeline.to_list()

    assert len(payloads) == 5
    assert len(pipeline.payload.document_index) == 5
    assert isinstance(pipeline.payload.document_index, pd.DataFrame)


def test_pipeline_tagged_frame_to_tokens_succeeds(config: CorpusConfig):

    checkpoint_filename: str = os.path.join(CORPUS_FOLDER, 'checkpoint_pos_tagged_test.zip')

    extract_opts: ExtractTaggedTokensOpts = ExtractTaggedTokensOpts(lemmatize=True, pos_includes='|NOUN|')
    filter_opts: TaggedTokensFilterOpts = TaggedTokensFilterOpts(is_space=False, is_punct=False)

    tagged_payload = next(SpacyPipeline(payload=config.pipeline_payload).checkpoint(checkpoint_filename).resolve())

    tokens_payload = next(
        SpacyPipeline(payload=config.pipeline_payload)
        .checkpoint(checkpoint_filename)
        .tagged_frame_to_tokens(extract_opts=extract_opts, filter_opts=filter_opts)
        .resolve()
    )

    assert tagged_payload.filename == tokens_payload.filename
    assert len(tagged_payload.content[tagged_payload.content.pos_ == 'NOUN']) == len(tokens_payload.content)


def test_pipeline_tagged_frame_to_text_succeeds(config: CorpusConfig):

    checkpoint_filename: str = os.path.join(CORPUS_FOLDER, 'checkpoint_pos_tagged_test.zip')

    extract_opts: ExtractTaggedTokensOpts = ExtractTaggedTokensOpts(lemmatize=True, pos_includes='|NOUN|')
    filter_opts: TaggedTokensFilterOpts = TaggedTokensFilterOpts(is_space=False, is_punct=False)

    tagged_payload = next(SpacyPipeline(payload=config.pipeline_payload).checkpoint(checkpoint_filename).resolve())

    text_payload = next(
        SpacyPipeline(payload=config.pipeline_payload)
        .checkpoint(checkpoint_filename)
        .tagged_frame_to_tokens(extract_opts=extract_opts, filter_opts=filter_opts)
        .tokens_to_text()
        .resolve()
    )

    assert tagged_payload.filename == text_payload.filename
    assert len(tagged_payload.content[tagged_payload.content.pos_ == 'NOUN']) == len(text_payload.content.split())


def test_pipeline_tagged_frame_to_tuple_succeeds(config: CorpusConfig):

    checkpoint_filename: str = os.path.join(CORPUS_FOLDER, 'checkpoint_pos_tagged_test.zip')

    extract_opts: ExtractTaggedTokensOpts = ExtractTaggedTokensOpts(lemmatize=True, pos_includes='|NOUN|')
    filter_opts: TaggedTokensFilterOpts = TaggedTokensFilterOpts(is_space=False, is_punct=False)

    payloads = (
        SpacyPipeline(payload=config.pipeline_payload)
        .checkpoint(checkpoint_filename)
        .tagged_frame_to_tokens(extract_opts=extract_opts, filter_opts=filter_opts)
        .tokens_to_text()
        .to_document_content_tuple()
        .to_list()
    )
    assert len(payloads) == 5

    assert all([isinstance(payload.content, tuple) for payload in payloads])
    assert all([isinstance(payload.content[0], str) for payload in payloads])
    assert all([isinstance(payload.content[1], str) for payload in payloads])


def test_pipeline_to_dtm_succeeds(config: CorpusConfig):

    checkpoint_filename: str = os.path.join(CORPUS_FOLDER, 'checkpoint_pos_tagged_test.zip')

    extract_opts: ExtractTaggedTokensOpts = ExtractTaggedTokensOpts(lemmatize=True, pos_includes='|NOUN|')
    filter_opts: TaggedTokensFilterOpts = TaggedTokensFilterOpts(is_space=False, is_punct=False)

    corpus: VectorizedCorpus = (
        (
            SpacyPipeline(payload=config.pipeline_payload)
            .checkpoint(checkpoint_filename)
            .tagged_frame_to_tokens(extract_opts=extract_opts, filter_opts=filter_opts)
            .tokens_transform(tokens_transform_opts=TokensTransformOpts())
            .tokens_to_text()
            .to_document_content_tuple()
            .tqdm()
            .to_dtm()
        )
        .single()
        .content
    )

    corpus.dump(tag="kallekulakurtkurt", folder=OUTPUT_FOLDER)
    assert isinstance(corpus, VectorizedCorpus)
    assert corpus.data.shape[0] == 5
    assert len(corpus.token2id) == corpus.data.shape[1]


@pytest.fixture
def fake_config() -> CorpusConfig:
    return CorpusConfig(
        corpus_name='legal_instrument_unesco',
        corpus_type=CorpusType.Text,
        corpus_pattern="*.zip",
        language='english',
        text_reader_opts=TextReaderOpts(
            filename_fields=["unesco_id:_:2", "year:_:3", r'city:\w+\_\d+\_\d+\_\d+\_(.*)\.txt'],
            index_field=None,  # Use filename as key
            filename_filter=None,
            filename_pattern="*.txt",
            as_binary=False,
        ),
        pipeline_payload=PipelinePayload(
            source="./tests/test_data/legal_instrument_five_docs_test.zip",
            document_index_source="./tests/test_data/legal_instrument_five_docs_test.csv",
            document_index_key=None,
            document_index_sep=';',
            pos_schema_name="Universal",
            memory_store={'tagger': 'spaCy', 'spacy_model': "en_core_web_sm", 'nlp': None, 'lang': 'en,'},
        ),
    )


class MockGUI:
    corpus_tag: str = "SSI-test"
    corpus_filename: str = "./tests/test_data/legal_instrument_five_docs_test.zip"
    corpus_folder: str = './tests/test_data'
    target_folder: str = './tests/output'
    extract_tagged_tokens_opts: ExtractTaggedTokensOpts = ExtractTaggedTokensOpts(
        lemmatize=True,
        pos_includes='|NOUN|',
    )
    tokens_transform_opts: TokensTransformOpts = TokensTransformOpts(
        only_alphabetic=False,
        only_any_alphanumeric=False,
        to_lower=True,
        to_upper=False,
        min_len=1,
        max_len=None,
        remove_accents=False,
        remove_stopwords=True,
        stopwords=None,
        extra_stopwords=None,
        language="english",
        keep_numerals=True,
        keep_symbols=True,
    )
    transform_opts: TextTransformOpts = TextTransformOpts()
    tagged_tokens_filter_opts: TaggedTokensFilterOpts = TaggedTokensFilterOpts(
        is_space=False,
        is_punct=False,
    )
    vectorize_opts: VectorizeOpts = VectorizeOpts()


# pylint: disable=too-many-locals
def test_compute_document_term_matrix_when_persist_is_false(fake_config: CorpusConfig):

    gui: MockGUI = MockGUI()

    done_callback_is_called = False
    done_corpus = None

    def done_callback(
        corpus: VectorizedCorpus,
        corpus_tag: str,
        corpus_folder: str,
        options: Dict,
        output: Any,  # pylint: disable=unused-argument
    ):
        nonlocal done_callback_is_called, done_corpus, fake_config

        assert corpus is not None
        assert corpus_tag == gui.corpus_tag
        assert corpus_folder is None
        assert options is not None

        done_callback_is_called = True
        done_corpus = corpus

        corpus.remove(tag=gui.corpus_tag, folder=gui.corpus_folder)
        corpus.dump(tag=gui.corpus_tag, folder=gui.corpus_folder)

    compute_document_term_matrix(
        corpus_config=fake_config,
        pipeline_factory=spaCy_DTM_pipeline,
        args=gui,
        persist=False,
        done_callback=done_callback,
    )

    assert done_callback_is_called

    assert VectorizedCorpus.dump_exists(tag=gui.corpus_tag, folder=gui.corpus_folder)

    corpus = VectorizedCorpus.load(tag=gui.corpus_tag, folder=gui.corpus_folder)

    assert corpus is not None

    assert corpus.data.shape == done_corpus.data.shape

    y_corpus = corpus.group_by_year()

    assert y_corpus is not None


def sample_corpus() -> VectorizedCorpus:
    corpus = [
        "the information we have is that the house had a tiny little mouse",
        "the sleeping cat saw the mouse",
        "the mouse ran away from the house",
        "the cat finally ate the mouse",
        "the end of the mouse story",
        "but a beginning of the cat story",
        "the fox saw the cat",
        "the fox ate the cat",
    ]

    document_index = pd.DataFrame(
        {
            'filename': [f'document_{i}.txt' for i in range(1, len(corpus) + 1)],
            'document_id': [i for i in range(0, len(corpus))],
            'document_name': [f'document_{i}' for i in range(1, len(corpus) + 1)],
        }
    )

    count_vectorizer = CountVectorizer()
    bag_term_matrix = count_vectorizer.fit_transform(corpus)

    corpus = VectorizedCorpus(
        bag_term_matrix,
        token2id=count_vectorizer.vocabulary_,
        document_index=document_index,
    )
    return corpus


def test_shorten_select_path():

    fc: ipyfilechooser.FileChooser = ipyfilechooser.FileChooser(
        path='/home/roger/source/inidun/text_analytics/data/',
        filename='legal_instrument_corpus.zip',
        filter_pattern='*.*',
        title='<b>Source corpus file</b>',
        show_hidden=False,
        select_default=True,
        use_dir_icons=True,
        show_only_dirs=False,
    )
    value = fc.selected
    shorten_filechooser_label(fc, 50)
    assert value == fc.selected


def test_slice_py_regular_expressions():

    pattern = re.compile("^.*tion$")

    corpus: VectorizedCorpus = sample_corpus()

    sliced_corpus = corpus.slice_by(px=pattern.match)

    assert sliced_corpus is not None
    assert sliced_corpus.data.shape == (8, 1)
    assert len(sliced_corpus.token2id) == 1
    assert 'information' in sliced_corpus.token2id
