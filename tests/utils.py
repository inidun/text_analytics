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
