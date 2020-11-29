from penelope.corpus.readers import TextReaderOpts
from penelope.pipeline import CorpusConfig, CorpusType, PipelinePayload

SSI = CorpusConfig(
    corpus_name='legal_instrument_unesco',
    corpus_type=CorpusType.Text,
    text_reader_opts=TextReaderOpts(
        filename_fields=["unesco_id:_:2", "year:_:3", r'city:\w+\_\d+\_\d+\_\d+\_(.*)\.txt'],
        filename_fields_key="unesco_id",
        filename_filter=None,
        filename_pattern="*.txt",
        as_binary=False,
    ),
    pipeline_payload=PipelinePayload(
        source="legal_instrument_corpus.zip",
        document_index_source="legal_instrument_index.csv",
        pos_schema_name="Universal",
        memory_store={'tagger': 'spaCy', 'spacy_model': "en_core_web_sm", 'nlp': None, 'lang': 'en,'},
    ),
)
