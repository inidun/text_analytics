import os
from typing import Callable, Sequence, Union

from penelope.corpus.readers import TextReaderOpts, ZipTextIterator

TEST_CORPUS_FILENAME = './tests/test_data/test_corpus.zip'
TEST_OUTPUT_FOLDER = './tests/output'

if __file__ in globals():
    this_file = os.path.dirname(__file__)
    this_path = os.path.abspath(this_file)
    TEST_CORPUS_FILENAME = os.path.join(this_path, TEST_CORPUS_FILENAME)


def create_text_files_reader(
    filename: str = TEST_CORPUS_FILENAME,
    filename_pattern: str = "*.txt",
    filename_filter: Union[Callable, Sequence[str]] = None,
) -> ZipTextIterator:

    reader = ZipTextIterator(
        filename,
        reader_opts=TextReaderOpts(
            filename_pattern=filename_pattern,
            filename_filter=filename_filter,
            as_binary=False,
        ),
    )
    return reader
