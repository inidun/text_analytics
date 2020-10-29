
# %%
import os
from typing import Any, Dict, Tuple
import pandas as pd
from penelope.vendor.textacy import TextacyCorpusPipeline, ITask
from penelope.vendor.textacy.pipeline import CreateTask, LoadTask, PreprocessTask, SaveTask
import textacy

# class VectorizeTask(ITask):

#     def __init(self, lemma='lemma', includes=''):
#python -m spacy download en_core_web_sm

corpus_folder = '/home/roger/source/inidun/text_analytics/data'
source_path = os.path.join(corpus_folder, "legal_instrument_corpus.zip")
documents = pd.read_csv(os.path.join(corpus_folder, "legal_instrument_index.csv"), sep=";", header=0)
filename_fields = ["unesco_id:_:2", "year:_:3", r'city:\w+\_\d+\_\d+\_\d+\_(.*)\.txt']
lang = 'en'
options = dict(filename=source_path, lang=lang, documents=documents, filename_fields=filename_fields)
tasks = [
    PreprocessTask,
    CreateTask,
    SaveTask,
    LoadTask,
]
pipeline = TextacyCorpusPipeline(**options, tasks=tasks)
corpus = pipeline.process().corpus
extract_args = {
    # extract_args['args'] positional arguments for textacy.Doc.to_terms_list
    # extract_args['kwargs'] Keyword arguments for textacy.Doc.to_terms_list
    # extract_args['extra_stop_words'] List of additional stopwords to use
    # extract_args['substitutions'] Dict (map) with term substitution
    # DEPRECATED extract_args['mask_gpe'] Boolean flag indicating if GPE should be substituted
    # extract_args['min_freq'] Integer value specifying min global word count.
    # extract_args['max_doc_freq'] Float value between 0 and 1 indicating threshold
    #   for documentword frequency, Words that occur in more than `max_doc_freq`
    #   documents will be filtered out.
}

from penelope.vendor.textacy import extract_corpus_terms
extract_corpus_terms(corpus=corpus, extract_args=extract_args)

# %%
tuple('ner,'.split(','))
# %%
import penelope.vendor.textacy as textacy_utility
from penelope.corpus import VectorizedCorpus
from sklearn.feature_extraction.text import CountVectorizer

# class TextacyCorpusVectorizer:
#     def __init__(self):
#         self.vectorizer = None
#         self.vectorizer_opts = {}

#     def fit_transform(
#         self,
#         corpus: textacy.Corpus,
#         *,
#         lowercase: bool = False,
#         stop_words: str = None,
#         max_df: float = 1.0,
#         min_df: int = 1,
#     ) -> VectorizedCorpus:
#         """Returns a vectorized corpus from of `corpus`

#         Note:
#           -  Input texts are already tokenized, so tokenizer is an identity function

#         Parameters
#         ----------
#         corpus : tokenized_corpus.TokenizedCorpus
#             [description]

#         Returns
#         -------
#         vectorized_corpus.VectorizedCorpus
#             [description]
#         """

#         #https://github.com/chartbeat-labs/textacy/blob/master/src/textacy/vsm/matrix_utils.py

#         vocabulary = corpus.spacy_lang.vocab.strings        # i.e. token2id, StringStore

#         tokenized_docs = (
#             doc._.to_terms_list(ngrams=1, entities=False, as_strings=True)
#             for doc in corpus)

#         vectorizer = textacy.vsm.Vectorizer(apply_idf=True, norm="l2", min_df=3, max_df=0.95)

#         doc_term_matrix = vectorizer.fit_transform(tokenized_docs)

#         if tokenizer is None:  # Iterator[Tuple[str,Iterator[str]]]
#             tokenizer = _no_tokenize
#             if lowercase:
#                 tokenizer = lambda tokens: [t.lower() for t in tokens]
#             lowercase = False

#         vectorizer_opts = dict(
#             tokenizer=tokenizer,
#             lowercase=lowercase,
#             stop_words=stop_words,
#             max_df=max_df,
#             min_df=min_df,
#             vocabulary=vocabulary,
#         )

#         if hasattr(corpus, 'terms'):
#             terms = corpus.terms
#         else:
#             terms = (x[1] for x in corpus)

#         self.vectorizer = CountVectorizer(**vectorizer_opts)
#         self.vectorizer_opts = vectorizer_opts

#         bag_term_matrix = self.vectorizer.fit_transform(terms)
#         token2id = self.vectorizer.vocabulary_

#         if hasattr(corpus, 'documents'):
#             documents = corpus.documents
#         else:
#             logger.warning("corpus has no `documents` property (generating a dummy index")
#             documents = pd.DataFrame(
#                 data=[{'index': i, 'filename': f'file_{i}.txt'} for i in range(0, bag_term_matrix.shape[0])]
#             ).set_index('index')
#             documents['document_id'] = documents.index
#         # ignored_words = self.vectorizer.stop_words_

#         v_corpus = VectorizedCorpus(bag_term_matrix, token2id, documents)

#         return v_corpus

# def vectorize_textacy_corpus(
#     corpus,
#     documents: pd.DataFrame,
#     n_count: int,
#     n_top: int,
#     normalize_axis=None,
#     year_range: Tuple[int, int] = (1920, 2020),
#     extract_args: Dict[str, Any] = None,
#     vectorizer_opts=None,
#     ):

#     # FIXME: index column unesco_id
#     document_stream = (
#         " ".join(doc) for doc in textacy_utility.extract_corpus_terms(corpus, extract_args=(extract_args or {}))
#     )

#     vectorizer_opts = dict(
#         tokenizer=lambda x: x.split(),
#         lowercase=lowercase,
#         stop_words=stop_words,
#         max_df=max_df,
#         min_df=min_df,
#         vocabulary=vocabulary,
#     )

#     vectorizer = CountVectorizer(tokenizer=lambda x: x.split(), **(vecargs or {}))

#     bag_term_matrix = vectorizer.fit_transform(document_stream)

#     x_corpus = VectorizedCorpus(bag_term_matrix, vectorizer.vocabulary_, documents)

#     year_range = (
#         x_corpus.documents.year.min(),
#         x_corpus.documents.year.max(),
#     )
#     year_filter = lambda x: year_range[0] <= x["year"] <= year_range[1]

#     x_corpus = x_corpus.filter(year_filter).group_by_year().slice_by_n_count(n_count).slice_by_n_top(n_top)

#     for axis in normalize_axis or []:
#         x_corpus = x_corpus.normalize(axis=axis, keep_magnitude=False)

#     return x_corpus

