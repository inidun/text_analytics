import os
from typing import Callable, Sequence

from penelope.corpus.readers import TextTokenizer
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
    transforms=None,
    chunk_size: int = None,
    filename_pattern: str = "*.txt",
    filename_filter: str = None,
    fix_whitespaces=False,
    fix_hyphenation=True,
    as_binary: bool = False,
    tokenize: Callable = None,
    filename_fields: Sequence[IndexOfSplitOrCallableOrRegExp] = None,
):
    kwargs = dict(
        transforms=transforms,
        chunk_size=chunk_size,
        filename_pattern=filename_pattern,
        filename_filter=filename_filter,
        text_transform_opts=TextTransformOpts(fix_whitespaces=fix_whitespaces, fix_hyphenation=fix_hyphenation),
        as_binary=as_binary,
        tokenize=tokenize,
        filename_fields=filename_fields,
    )
    reader = TextTokenizer(source_path, **kwargs)
    return reader
