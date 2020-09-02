import os
import itertools
import text_analytic_tools.utility as utility
import re
import collections
import pandas as pd

from spacy import attrs

def generate_word_count_score(corpus, normalize, count):
    wc = corpus.word_counts(normalize=normalize, weighting='count', as_strings=True)
    d = { i: set([]) for i in range(1, count+1)}
    for k, v in wc.items():
        if v <= count:
            d[v].add(k)
    return d

def generate_word_document_count_score(corpus, normalize, threshold=75):
    wc = corpus.word_doc_counts(normalize=normalize, weighting='freq', smooth_idf=True, as_strings=True)
    d = { i: set([]) for i in range(threshold, 101)}
    for k, v in wc.items():
        slot = int(round(v,2)*100)
        if slot >= threshold:
            d[slot].add(k)
    return d

def count_documents_by_pivot(corpus, attribute):
    ''' Return a list of document counts per group defined by attribute
    Assumes documents are sorted by attribute!
    '''
    fx_key = lambda doc: doc._.meta[attribute]
    return [ len(list(g)) for _, g in itertools.groupby(corpus, fx_key) ]

def count_documents_in_index_by_pivot(documents, attribute):
    ''' Return a list of document counts per group defined by attribute
    Assumes documents are sorted by attribute!
    Same as count_documents_by_pivot but uses document index instead of (textacy) corpus
    '''
    assert documents[attribute].is_monotonic_increasing, 'Documents *MUST* be sorted by TIME-SLICE attribute!'
    # FIXME: Either sort documents (and corpus or term stream!) prior to this call - OR force sortorder by filename (i.e add year-prefix)
    return list(documents.groupby(attribute).size().values)

def get_document_by_id(corpus, document_id, field_name='document_id'):
    for doc in corpus.get(lambda x: x._.meta[field_name] == document_id, limit=1):
        return doc
    assert False, 'Document {} not found in corpus'.format(document_id)
    return None

def generate_corpus_filename(source_path, language, nlp_args=None, preprocess_args=None, compression='bz2', period_group='', extension='bin'):
    nlp_args = nlp_args or {}
    preprocess_args = preprocess_args or {}
    disabled_pipes = nlp_args.get('disable', ())
    suffix = '_{}_{}{}_{}'.format(
        language,
        '_'.join([ k for k in preprocess_args if preprocess_args[k] ]),
        '_disable({})'.format(','.join(disabled_pipes)) if len(disabled_pipes) > 0 else '',
        (period_group or '')
    )
    filename = utility.path_add_suffix(source_path, suffix, new_extension='.' + extension)
    if (compression or '') != '':
        filename += ('.' + compression)
    return filename

def get_disabled_pipes_from_filename(filename):
    re_pipes = r'^.*disable\((.*)\).*$'
    x = re.match(re_pipes, filename).groups(0)
    if len(x or []) > 0:
        return x[0].split(',')
    return None

def infrequent_words(corpus, normalize='lemma', weighting='count', threshold=0, as_strings=False):

    '''Returns set of infrequent words i.e. words having total count less than given threshold'''

    if weighting == 'count' and threshold <= 1:
        return set([])

    token_counter = corpus.word_counts(normalize=normalize, weighting=weighting, as_strings=as_strings)
    words = set([ w for w in token_counter if token_counter[w] < threshold ])

    return words

def frequent_document_words(corpus, normalize='lemma', weighting='freq', dfs_threshold=80, as_strings=True):
    '''Returns set of words that occurrs freuently in many documents, candidate stopwords'''
    document_freqs = corpus.word_doc_counts(normalize=normalize, weighting=weighting, smooth_idf=True, as_strings=True)
    result = set([ w for w, f in document_freqs.items() if int(round(f,2)*100) >= dfs_threshold ])
    return result

def get_most_frequent_words(corpus, n_top, normalize='lemma', include_pos=None, weighting='count'):
    include_pos = include_pos or [ 'VERB', 'NOUN', 'PROPN' ]
    include = lambda x: x.pos_ in include_pos
    token_counter = collections.Counter()
    for doc in corpus:
        bow = doc_to_bow(doc, target=normalize, weighting=weighting, as_strings=True, include=include)
        token_counter.update(bow)
        if normalize == 'lemma':
            lower_cased_word_counts = collections.Counter()
            for k, v in token_counter.items():
                lower_cased_word_counts.update({ k.lower(): v })
            token_counter = lower_cased_word_counts
    return token_counter.most_common(n_top)

def doc_to_bow(doc, target='lemma', weighting='count', as_strings=False, include=None, n_min_count=2):

    weighing_keys = { 'count', 'freq' }
    target_keys = { 'lemma': attrs.LEMMA, 'lower': attrs.LOWER, 'orth': attrs.ORTH }

    default_exclude = lambda x: x.is_stop or x.is_punct or x.is_space
    exclude = default_exclude if include is None else lambda x: x.is_stop or x.is_punct or x.is_space or not include(x)

    assert weighting in weighing_keys
    assert target in target_keys

    target_weights = doc.count_by(target_keys[target], exclude=exclude)
    n_tokens = doc._.n_tokens

    if weighting == 'freq':
        target_weights = { id_: weight / n_tokens for id_, weight in target_weights.items() }

    store = doc.vocab.strings
    if as_strings:
        bow = { store[word_id]: count for word_id, count in target_weights.items() if count >= n_min_count}
    else:
        bow = target_weights # { word_id: count for word_id, count in target_weights.items() }

    return bow

POS_TO_COUNT = {
    'SYM': 0, 'PART': 0, 'ADV': 0, 'NOUN': 0, 'CCONJ': 0, 'ADJ': 0, 'DET': 0, 'ADP': 0, 'INTJ': 0, 'VERB': 0, 'NUM': 0, 'PRON': 0, 'PROPN': 0
}

POS_NAMES = list(sorted(POS_TO_COUNT.keys()))

def get_pos_statistics(doc):
    pos_iter = ( x.pos_ for x in doc if x.pos_ not in ['NUM', 'PUNCT', 'SPACE'] )
    pos_counts = dict(collections.Counter(pos_iter))
    stats = utility.extend(dict(POS_TO_COUNT), pos_counts)
    return stats

def get_corpus_data(corpus, document_index, title, columns_of_interest=None):
    metadata = [
        utility.extend({},
                       dict(document_id=doc._.meta['document_id']),
                       get_pos_statistics(doc)
                      )
        for doc in corpus
    ]
    df = pd.DataFrame(metadata)[['document_id'] + POS_NAMES]
    if columns_of_interest is not None:
        document_index = document_index[columns_of_interest]
    df = pd.merge(df, document_index, left_on='document_id', right_index=True, how='inner')
    df['title'] = df[title]
    df['words'] = df[POS_NAMES].apply(sum, axis=1)
    return df

def load_term_substitutions(filepath, default_term='_gpe_', delim=';', vocab=None):
    substitutions = {}
    if not os.path.isfile(filepath):
        return {}

    with open(filepath) as f:
        substitutions = {
            x[0].strip(): x[1].strip() for x in (
                tuple(line.lower().split(delim)) + (default_term,) for line in f.readlines()
            ) if x[0].strip() != ''
        }

    if vocab is not None:

        extras = { x.norm_: substitutions[x.lower_] for x in vocab if x.lower_ in substitutions }
        substitutions.update(extras)

        extras = { x.lower_: substitutions[x.norm_] for x in vocab if x.norm_  in substitutions }
        substitutions.update(extras)

    substitutions = { k: v for k, v in substitutions.items() if k != v }

    return substitutions

def term_substitutions(data_folder, filename='term_substitutions.txt', vocab=None):
    path = os.path.join(data_folder, filename)
    logger.info('Loading term substitution mappings...')
    data = load_term_substitutions(path, default_term='_masked_', delim=';', vocab=vocab)
    return data
