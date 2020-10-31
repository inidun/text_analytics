# %%
import os

import pandas as pd
from penelope.corpus import CorpusVectorizer, VectorizedCorpus
from penelope.vendor.textacy import TextacyCorpusPipeline
from penelope.vendor.textacy.pipeline import CreateTask, LoadTask, PreprocessTask, SaveTask

# python -m spacy download en_core_web_sm

corpus_folder = '/home/roger/source/inidun/text_analytics/data'
source_path = os.path.join(corpus_folder, "legal_instrument_corpus.zip")
documents = pd.read_csv(os.path.join(corpus_folder, "legal_instrument_index.csv"), sep=";", header=0)
filename_fields = ["unesco_id:_:2", "year:_:3", r'city:\w+\_\d+\_\d+\_\d+\_(.*)\.txt']
lang = 'en'

corpus = (
    TextacyCorpusPipeline(
        **dict(filename=source_path, lang=lang, documents=documents, filename_fields=filename_fields),
        tasks=[
            PreprocessTask,
            CreateTask,
            SaveTask,
            LoadTask,
        ],
    )
    .process()
    .corpus
)

# %%
vectorizer = CorpusVectorizer()
v_corpus: VectorizedCorpus = vectorizer.fit_transform(corpus, tokenizer=None)
vocabulary = list(v_corpus.token2id.keys())
word_endings = {'ment', 'tion'}
candidates = {x for x in vocabulary if any((x.endswith(w) for w in word_endings))}
w_corpus = v_corpus.slice_by(lambda w: w in candidates)

# TODO: Display `w_corpus` using word_trends clustering NB
# TODO: GUI where user can specify endings ans stopwords
