import glob
import os
import types

import ipywidgets as widgets
import notebooks.word_trends.word_trends_output_gui as result_gui
import pandas as pd
from IPython.display import display
from penelope.vendor.textacy import vectorize_textacy_corpus
from penelope.vendor.textacy.pipeline import CreateTask, LoadTask, PreprocessTask, SaveTask, TextacyCorpusPipeline


# vectorize_corpus \
#         --to-lower \
#         --no-remove-accents \
#         --min-length 2 \
#         --keep-numerals \
#         --no-keep-symbols \
#         --only-alphanumeric \
#         --file-pattern '*.txt' \
#         --meta-field "document_type:_:0" \
#         --meta-field "document_id:_:2" \
#         --meta-field "year:_:3" \
#         ./data/legal_instrument_corpus.txt.zip \
#         ./data \


def display_gui(corpus_folder, container=None, lang: str = 'en'):

    candidate_corpus_filenames = [os.path.basename(x) for x in glob.glob(os.path.join(corpus_folder, "*.zip"))]

    year_range = [1920, 2020]

    normalize_options = {
        "None": [],
        "Over year": [0],
        "Over word": [1],
        "Over year and word": [0, 1],
    }
    gui = types.SimpleNamespace(
        corpus_filename=widgets.Dropdown(
            description="Corpus",
            options=candidate_corpus_filenames,
            value=None if not candidate_corpus_filenames else candidate_corpus_filenames[-1],
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
        prepare=widgets.Button(
            description="Prepare",
            disabled=True,
            layout=widgets.Layout(width="80px", color="green"),
        ),
        year_range=widgets.IntRangeSlider(
            value=year_range,
            min=year_range[0],
            max=year_range[1],
            step=1,
            description="Period:",
        ),
        min_length=widgets.IntSlider(
            value=1,
            min=1,
            max=100,
            step=1,
            description="Min lenght:",
        ),
        filter_stops=widgets.Checkbox(value=True, description="Filter stops", disabled=False, indent=False),
        filter_punct=widgets.Checkbox(value=True, description="Filter puncts", disabled=False, indent=False),
        filter_nums=widgets.Checkbox(value=True, description="Filter nums", disabled=False, indent=False),
        include_pos=widgets.SelectMultiple(
            options=POS_LIST,
            value=["ADJ", "NOUN", "VERB"],
            # rows=10,
            description="Include POS:",
            disabled=False,
        ),
        exclude_pos=widgets.SelectMultiple(
            options=POS_LIST,
            value=[],
            # rows=10,
            description="Exclude POS:",
            disabled=False,
        ),
        # FIXME: lägg in dropdown för postaggar, multiselect (lista på all postaggar, default alla)
        # FIXME: lägg in dropdown för val av nomralisering av orden - lemma, lowercase etc
        # FIXME: add dropdown for kwargs in corpus_extract.extract_corpus_terms()
        # see: textacy.Doc.to_terms_list
        output=widgets.Output(layout=widgets.Layout(width="500px")),
    )

    def load(*_):

        gui.output.clear_output()

        with gui.output:

            gui.load.disabled = True
            gui.load.description = "Wait..."
            gui.corpus_filename.disabled = True

            corpus_filename = os.path.join(corpus_folder, gui.corpus_filename.value)
            index_filename = os.path.join(corpus_folder, "legal_instrument_index.csv")
            filename_fields = ["unesco_id:_:2", "year:_:3", r'city:\w+\_\d+\_\d+\_\d+\_(.*)\.txt']

            documents = pd.read_csv(index_filename, sep=";", header=0)

            options = dict(filename=corpus_filename, lang=lang, documents=documents, filename_fields=filename_fields)
            tasks = [
                PreprocessTask,
                CreateTask,
                SaveTask,
                LoadTask,
            ]

            pipeline = TextacyCorpusPipeline(**options, tasks=tasks)

            container.t_corpus = pipeline.process().corpus
            container.index = documents

            gui.load.disabled = False
            gui.prepare.disabled = False
            gui.corpus_filename.disabled = False
            gui.load.description = "Load"

            print("Corpus loaded.")

    def prepare(*_):

        gui.output.clear_output()

        with gui.output:

            gui.prepare.disabled = True
            gui.prepare.description = "Wait..."

            extract_args = {
                "normalize": "lemma",
                "min_length": gui.min_length.value,
                "as_strings": True,
                "filter_stops": gui.filter_stops.value,
                "filter_punct": gui.filter_punct.value,
                "filter_nums": gui.filter_nums.value,
                "include_pos": gui.include_pos.value,
                "exclude_pos": gui.exclude_pos.value,
                "min_freq": 1,
                # 'include_types': (str or Set[str]),
                # 'exclude_types': (str or Set[str],
                # 'drop_determiners': False
            }

            container.corpus = vectorize_textacy_corpus(
                container.t_corpus,
                container.index,
                n_count=gui.n_min_count.value,
                n_top=gui.n_top_count.value,
                normalize_axis=gui.normalize.value,
                year_range=gui.year_range.value,
                extract_args=extract_args,
            )

            gui.prepare.disabled = False
            gui.prepare.description = "Prepare"

            print("Corpus vectorized.")

    gui.load.on_click(load)
    gui.prepare.on_click(prepare)

    corpus_widget = widgets.VBox(
        [
            gui.corpus_filename,
            gui.filter_stops,
            gui.filter_punct,
            gui.filter_nums,
            gui.include_pos,
            gui.exclude_pos,
            gui.load,
        ]
    )

    extra_args_widget = widgets.VBox(
        [
            gui.normalize,
            gui.n_min_count,
            gui.n_top_count,
            gui.year_range,
            gui.min_length,
            gui.prepare,
        ]
    )

    tab_widget = widgets.Tab()
    tab_widget.children = [corpus_widget, extra_args_widget, result_gui.display_gui(container)]
    tab_titles = ["1. Annotate", "2. Prepare", "3. Display"]
    _ = [tab_widget.set_title(i, x) for i, x in enumerate(tab_titles)]

    display(widgets.HBox([tab_widget, gui.output]))

    return gui
