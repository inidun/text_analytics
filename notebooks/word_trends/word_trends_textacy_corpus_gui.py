import glob
import os
import types

import ipywidgets as widgets
from IPython.display import display
from sklearn.feature_extraction.text import CountVectorizer

import notebooks.word_trends.corpus_tools as corpus_tools
import text_analytic_tools.corpus.vectorized_corpus as vectorized_corpus

# add corpus, document_index, n_count, n_top, normalize_axis=None, year_range=(1920, 2020)
def vectorize_textacy_corpus(corpus, document_index, n_count, n_top, normalize_axis=None, year_range=(1920, 2020), extract_args=None, vecargs=None):

    document_stream = ( ' '.join([ w for w in doc]) for doc in corpus_tools.extract_corpus_terms(corpus, extract_args=(extract_args or {})) )

    tokenizer = lambda x: x.split()

    vectorizer = CountVectorizer(tokenizer=tokenizer, **(vecargs or {}))

    bag_term_matrix = vectorizer.fit_transform(document_stream)
    token2id = vectorizer.vocabulary_

    x_corpus = vectorized_corpus.VectorizedCorpus(
        bag_term_matrix, token2id, document_index
    )

    year_range = (
            x_corpus.document_index.year.min(),
            x_corpus.document_index.year.max(),
        )
    year_filter = lambda x: year_range[0] <= x["year"] <= year_range[1]

    x_corpus = (
            x_corpus.filter(year_filter)
            .group_by_year()
            .slice_by_n_count(n_count)
            .slice_by_n_top(n_top)
    )

    for axis in normalize_axis or []:
        x_corpus = x_corpus.normalize(axis=axis, keep_magnitude=False)
    return x_corpus

# FIXME: !!!! Use this callback
def load_vectorized_corpus(
    corpus, document_index, n_count, n_top, normalize_axis=None, year_range=(1920, 2020)
):

    try:
        # FIXME: 
        x_corpus = vectorize_textacy_corpus(corpus, extract_args=None)

        year_range = (
            x_corpus.document_index.year.min(),
            x_corpus.document_index.year.max(),
        )
        year_filter = lambda x: year_range[0] <= x["year"] <= year_range[1]

        x_corpus = (
            x_corpus.filter(year_filter)
            .group_by_year()
            .slice_by_n_count(n_count)
            .slice_by_n_top(n_top)
        )

        for axis in normalize_axis or []:
            x_corpus = x_corpus.normalize(axis=axis, keep_magnitude=False)

        return x_corpus

    except Exception as ex:
        print(ex)
        raise
        # return None


def display_gui(corpus_folder, container=None):

    # corpus_tools.get_textacy_corpus(corpus_folder, corpus_folder)
    # vectorize

    candidate_corpus_filenames = [ os.path.basename(x) for x in glob.glob(os.path.join(corpus_folder, '*.zip')) ]
    year_range = [1920, 2020]

    normalize_options = {
        "None": [],
        "Over year": [0],
        "Over word": [1],
        "Over year and word": [0, 1],
    }
    gui = types.SimpleNamespace(

        # FIXME: ändra så att man kan välja en korpus zipfil - corpus_filename
        # ~ glob.glob.datafolder.zip

        corpus_filename=widgets.Dropdown(
            description="Corpus",
            options=candidate_corpus_filenames,
            value=None,
            layout=widgets.Layout(width="420px", color="green"),
        ),
        n_min_count=widgets.IntSlider(
            description="Min count",
            min=1,
            max=10000,
            value=1,
            layout=widgets.Layout(width="400px", color="green"),
        ),
        n_top_count=widgets.IntSlider(
            description="Top count",
            min=10,
            max=1000000,
            value=5000,
            layout=widgets.Layout(width="400px", color="green"),
        ),
        normalize=widgets.Dropdown(
            description="Normalize",
            options=normalize_options,
            value=[0],
            disabled=False,
            layout=widgets.Layout(width="420px", color="green"),
        ),
        load=widgets.Button(
            description="Load",
            disabled=False,
            layout=widgets.Layout(width="80px", color="green"),
        ),
        year_range=widgets.IntRangeSlider(
            value=year_range,
            min=year_range[0],
            max=year_range[1],
            step=1,
            description="Period:",
        ),

        # FIXME: lägg in dropdown för postaggar, multiselect (lista på all postaggar, default alla)
        # FIXME: lägg in dropdown för val av nomralisering av orden - lemma, lowercase etc

        # FIXME: add dropdown for kwargs in corpus_extract.extract_corpus_terms()
        # see: textacy.Doc.to_terms_list


        output=widgets.Output(layout=widgets.Layout(width="500px")),
    )

    def load(*args):  # pylint: disable=unused-argument

        gui.output.clear_output()

        with gui.output:

            gui.load.disabled = True
            gui.load.description = "Wait..."
            gui.corpus_filename.disabled = True

            # FIXME: load selected zipped text corpus as a spacy
            # Convert spacy corpus to vectorized corpus
            corpus_filename = os.path.join(corpus_folder, gui.corpus_filename.value)
            index_filename = os.path.join(corpus_folder, 'legal_instrument_index.csv')
            
            extract_args = {
                'normalize': 'lemma',
                'min_length':  1,        # FIXME gui
                'as_strings':  True,
                'filter_stops': True,   # FIXME gui
                'filter_punct': True,   # FIXME gui
                'filter_nums':  True,    # FIXME gui
                'include_pos':  ['NN'],
                'exclude_pos':  [],
                'min_freq': 1,
                #'include_types': (str or Set[str]),
                #'exclude_types': (str or Set[str],
                #'drop_determiners': False
            }

            container.t_corpus, container.index = corpus_tools.get_textacy_corpus(corpus_filename, index_filename)
            container.corpus = vectorize_textacy_corpus(container.t_corpus, container.index, n_count=gui.n_min_count.value, n_top=gui.n_top_count.value, normalize_axis=gui.normalize.value, year_range=gui.year_range.value, extract_args=extract_args) # FIXME: add args

            gui.load.disabled = False
            gui.corpus_filename.disabled = False
            gui.load.description = "Load"

        # gui.output.clear_output()
        # with gui.output:
        #    print("Corpus loaded.")

    gui.load.on_click(load)

    display(
        widgets.HBox(
            [
                widgets.VBox(
                    [
                        gui.corpus_filename,
                        gui.normalize,
                        gui.n_min_count,
                        gui.n_top_count,
                        gui.year_range,
                    ]
                ),
                widgets.VBox([gui.load]),
                gui.output,
            ]
        )
    )

    return gui
