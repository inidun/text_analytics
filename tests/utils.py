import os

from penelope.corpus.readers import streamify_text_source

TEST_CORPUS_FILENAME = './tests/test_data/test_corpus.zip'
TEST_OUTPUT_FOLDER = './tests/output'

if __file__ in globals():
    this_file = os.path.dirname(__file__)
    this_path = os.path.abspath(this_file)
    TEST_CORPUS_FILENAME = os.path.join(this_path, TEST_CORPUS_FILENAME)


def create_text_files_reader(filename=TEST_CORPUS_FILENAME, filename_pattern="*.txt", filename_filter=None):
    kwargs = dict(filename_pattern=filename_pattern, filename_filter=filename_filter)
    reader = streamify_text_source(filename, **kwargs)
    return reader


SSI_config = """
corpus_name: ssi_unesco
corpus_pattern: '*.zip'
corpus_type: 1
language: english
pipeline_payload:
  document_index_sep: ;
  document_index_source: legal_instrument_index.csv
  filenames: null
  memory_store:
    lang: en
    lemma_column: lemma_
    pos_column: pos_
    spacy_model: en_core_web_sm
    tagger: spaCy
    text_column: text
  pos_schema_name: Universal
  source: legal_instrument_corpus.zip
tagged_tokens_filter_opts:
  data:
    is_alpha: null
    is_digit: null
    is_punct: false
    is_stop: null
text_reader_opts:
  as_binary: false
  filename_fields:
  - unesco_id:_:2
  - year:_:3
  - city:\\w+\\_\\d+\\_\\d+\\_\\d+\\_(.*)\\.txt
  filename_filter: null
  filename_pattern: '*.txt'
  index_field: null
"""
