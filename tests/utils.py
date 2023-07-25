import os
from typing import Callable, List, Sequence, Union

import numpy as np
import pandas as pd
from penelope.corpus import TextReaderOpts, VectorizedCorpus, ZipCorpusReader

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
) -> ZipCorpusReader:
    reader = ZipCorpusReader(
        filename,
        reader_opts=TextReaderOpts(
            filename_pattern=filename_pattern,
            filename_filter=filename_filter,
            as_binary=False,
        ),
    )
    return reader


def create_abc_corpus(dtm: List[List[int]], document_years: List[int] = None) -> VectorizedCorpus:
    bag_term_matrix = np.array(dtm)
    token2id = {chr(ord('a') + i): i for i in range(0, bag_term_matrix.shape[1])}

    years: List[int] = (
        document_years if document_years is not None else [2000 + i for i in range(0, bag_term_matrix.shape[0])]
    )

    document_index = pd.DataFrame(
        {
            'year': years,
            'filename': [f'{2000+i}_{i}.txt' for i in years],
            'document_id': [i for i in range(0, bag_term_matrix.shape[0])],
        }
    )
    corpus: VectorizedCorpus = VectorizedCorpus(bag_term_matrix, token2id=token2id, document_index=document_index)
    return corpus


def create_vectorized_corpus() -> VectorizedCorpus:
    bag_term_matrix = np.array(
        [
            [2, 1, 4, 1],
            [2, 2, 3, 0],
            [2, 3, 2, 0],
            [2, 4, 1, 1],
            [2, 0, 1, 1],
        ]
    )
    token2id = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
    document_index = pd.DataFrame({'year': [2013, 2013, 2014, 2014, 2014]})
    v_corpus: VectorizedCorpus = VectorizedCorpus(bag_term_matrix, token2id=token2id, document_index=document_index)
    return v_corpus
