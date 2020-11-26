import os
from typing import Callable, List, Sequence

from penelope.corpus.readers import TextTokenizer
from penelope.corpus.readers.interfaces import TextReaderOpts
from penelope.corpus.readers.text_transformer import TextTransformOpts
from penelope.utility import IndexOfSplitOrCallableOrRegExp

TEST_CORPUS_FILENAME = './westac/tests/test_data/test_corpus.zip'

# pylint: disable=too-many-arguments

if __file__ in globals():
    this_file = os.path.dirname(__file__)
    this_path = os.path.abspath(this_file)
    TEST_CORPUS_FILENAME = os.path.join(this_path, TEST_CORPUS_FILENAME)


def create_text_tokenizer(
    source_path=TEST_CORPUS_FILENAME,
    # TextTransformOpts
    fix_whitespaces: bool=False,
    fix_hyphenation: bool=True,
    extra_transforms: List[Callable]=None,
    # TextReaderOpts
    as_binary: bool = False,
    filename_pattern: str = "*.txt",
    filename_filter: str = None,
    filename_fields: Sequence[IndexOfSplitOrCallableOrRegExp] = None,
    filename_fields_key: str=None,
    # TokenizeOpts:
    tokenize: Callable = None,
    chunk_size: int = None,
):
    text_transform_opts = TextTransformOpts(
        fix_whitespaces=fix_whitespaces, fix_hyphenation=fix_hyphenation, extra_transforms=extra_transforms
    )
    reader_opts = TextReaderOpts(
        filename_pattern=filename_pattern,
        filename_filter=filename_filter,
        filename_fields=filename_fields,
        filename_fields_key=filename_fields_key,
        as_binary=as_binary,
    )

    reader = TextTokenizer(
        source=source_path,
        text_transform_opts=text_transform_opts,
        reader_opts=reader_opts,
        chunk_size=chunk_size,
        tokenize=tokenize
    )
    return reader
