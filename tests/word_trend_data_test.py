import unittest.mock as mock

import pandas as pd
from penelope.corpus import VectorizedCorpus
from penelope.notebook.word_trends import TrendsData

# attrs = {
#     'compute_goddness_of_fits_to_uniform.return_value': mock.Mock(spec=pd.DataFrame),
#     'compile_most_deviating_words.return_value':  mock.Mock(spec=pd.DataFrame),
#     'get_most_deviating_words.return_value':  mock.Mock(spec=pd.DataFrame),
# }


@mock.patch(
    'penelope.common.goodness_of_fit.compute_goddness_of_fits_to_uniform', lambda *_, **__: mock.Mock(spec=pd.DataFrame)
)
@mock.patch(
    'penelope.common.goodness_of_fit.compile_most_deviating_words', lambda *_, **__: mock.Mock(spec=pd.DataFrame)
)
@mock.patch('penelope.common.goodness_of_fit.get_most_deviating_words', lambda *_, **__: mock.Mock(spec=pd.DataFrame))
def test_group_by_year():
    corpus_folder = './tests/test_data/VENUS'
    corpus_tag = 'VENUS'

    corpus: VectorizedCorpus = mock.Mock(spec=VectorizedCorpus)
    corpus = corpus.group_by_year()

    trends_data: TrendsData = TrendsData(
        corpus=corpus,
        corpus_folder=corpus_folder,
        corpus_tag=corpus_tag,
        n_count=100,
    ).update()

    assert trends_data is not None
