import os
from dataclasses import dataclass, field
from typing import Sequence, TypeVar

import ipyfilechooser
import ipywidgets as widgets
import pandas as pd
from IPython.display import display
from penelope.corpus.readers import AnnotationOpts
from penelope.corpus.tokens_transformer import TokensTransformOpts
from penelope.utility import PoS_Tag_Scheme, PoS_TAGS_SCHEMES, flatten
from penelope.vendor.textacy import vectorize_textacy_corpus
from penelope.vendor.textacy.pipeline import CreateTask, LoadTask, PreprocessTask, SaveTask, TextacyCorpusPipeline

G = 'GUI'  # TypeVar("G", "GUI")


@dataclass
class GUI:  # pylint: disable=too-many-instance-attributes

    normalize_options = {
        "None": [],
        "Over year": [0],
        "Over word": [1],
        "Over year and word": [0, 1],
    }

    language: str = field(default="english")

    button_layout = widgets.Layout(width='120px')

    corpus_filename: ipyfilechooser.FileChooser = ipyfilechooser.FileChooser(
        # path=os.getcwd(),
        filter_pattern='*.zip',
        title='<b>Corpus file</b>',
        show_hidden=False,
        select_default=False,
        use_dir_icons=True,
        show_only_dirs=False,
    )

    index_filename: ipyfilechooser.FileChooser = ipyfilechooser.FileChooser(
        # path=os.getcwd(),
        filter_pattern='*.csv',
        title='<b>Index file</b>',
        show_hidden=False,
        select_default=False,
        use_dir_icons=True,
        show_only_dirs=False,
    )

    n_min_count = widgets.IntSlider(
        description="Min count",
        min=1,
        max=10000,
        value=1,
        layout=widgets.Layout(width="400px", color="green"),
    )

    n_top_count = widgets.IntSlider(
        description="Top count",
        min=10,
        max=1000000,
        value=5000,
        layout=widgets.Layout(width="400px", color="green"),
    )

    normalize_axis = widgets.Dropdown(
        description="Normalize",
        options=normalize_options,
        value=[0],
        disabled=False,
        layout=widgets.Layout(width="420px", color="green"),
    )

    load = widgets.Button(
        description="Load",
        disabled=False,
        layout=widgets.Layout(width="80px", color="green"),
    )

    vectorize = widgets.Button(
        description="Vectorize",
        disabled=True,
        layout=widgets.Layout(width="80px", color="green"),
    )

    year_range: widgets.IntRangeSlider = widgets.IntRangeSlider(
        value=[1900, 2020],
        min=1900,
        max=2020,
        step=1,
        description="Period:",
    )

    min_length = widgets.IntSlider(
        value=1,
        min=1,
        max=100,
        step=1,
        description="",
    )

    keep_numerals = widgets.Checkbox(value=True, description="Keep nums", disabled=False, indent=False)
    lemmatize = widgets.ToggleButton(value=True, description='Lemmatize', icon='check', layout=button_layout)
    to_lowercase = widgets.ToggleButton(value=True, description='To Lower', icon='check', layout=button_layout)
    remove_stopwords = widgets.ToggleButton(value=True, description='No Stopwords', icon='check', layout=button_layout)

    pos_includes = widgets.SelectMultiple(
        options=[],
        value=[],
        description="",
        disabled=False,
    )

    pos_excludes = widgets.SelectMultiple(
        options=[],
        value=[],
        description="",
        disabled=False,
    )

    filename_fields = widgets.Text(description="Fields:", value="", disabled=True)
    output = widgets.Output(layout=widgets.Layout(width="500px"))

    def set_PoS_scheme(self, pos_scheme: PoS_Tag_Scheme) -> G:

        self.pos_includes.value = []
        self.pos_includes.options = pos_scheme.groups
        self.pos_includes.value = [pos_scheme.groups['Noun'], pos_scheme.groups['Verb']]

        self.pos_excludes.value = []
        self.pos_excludes.options = pos_scheme.groups

        return self

    def set_corpus_folder(self, folder: str) -> G:
        self.corpus_filename.path = folder
        return self

    def set_year_range(self, values: Sequence[int]) -> G:
        if values is None:
            return self
        self.year_range.value = values
        self.year_range.min = values[0]
        self.year_range.max = values[1]
        return self

    def set_language(self, language: str) -> G:
        self.language = language
        return self

    def set_filename_fields(self, filename_fields) -> G:
        self.filename_fields.value = ','.join(filename_fields)
        return self

    @property
    def annotation_opts(self) -> AnnotationOpts:

        return AnnotationOpts(
            pos_includes=f"|{'|'.join(flatten(self.pos_includes.value))}|",
            pos_excludes=f"|{'|'.join(flatten(self.pos_excludes.value))}|",
            lemmatize=self.lemmatize.value,
        )

    @property
    def tokens_transform_opts(self) -> TokensTransformOpts:
        return TokensTransformOpts(
            to_lower=self.to_lowercase.value,
            to_upper=False,
            remove_stopwords=self.remove_stopwords.value,
            extra_stopwords=None,
            language=self.language if self.remove_stopwords.value else None,
            keep_numerals=self.keep_numerals.val,
            keep_symbols=False,
            only_alphabetic=False,
            only_any_alphanumeric=True,
        )

    def layout(self):

        corpus_widget = widgets.VBox(
            [
                self.corpus_filename,
                self.index_filename,
                widgets.HBox([self.remove_stopwords, self.lemmatize]),
                widgets.HBox(
                    [
                        widgets.VBox([widgets.HTML("<b>Include PoS tags</b>"), self.pos_includes]),
                        widgets.VBox([widgets.HTML("<b>Exclude PoS tags</b>"), self.pos_excludes]),
                    ]
                ),
                widgets.VBox([widgets.HTML("<b>Min length</b>"), self.min_length]),
                self.vectorize,
            ]
        )

        extra_args_widget = widgets.VBox(
            [
                self.normalize_axis,
                self.n_min_count,
                self.n_top_count,
                self.year_range,
                self.vectorize,
            ]
        )

        tab_widget = widgets.Tab()
        tab_widget.children = [
            corpus_widget,
            extra_args_widget,
            widgets.Output(),
        ]  # result_gui.display_gui(self.container)]
        tab_titles = ["1. Annotate", "2. Prepare", "3. Display"]
        _ = [tab_widget.set_title(i, x) for i, x in enumerate(tab_titles)]

        _layout = widgets.HBox([tab_widget, self.output])

        return _layout


def display_gui(
    *,
    filename_fields: Sequence[str],
    corpus_folder: str,
    lang: str = 'en',
    year_range: Sequence[int] = None,
    display_callback=None,
):
    textacy_corpus = None
    documents = None

    gui: GUI = (
        GUI()
        .set_corpus_folder(corpus_folder)
        .set_PoS_scheme(PoS_TAGS_SCHEMES.Universal)
        .set_year_range(year_range)
        .set_language('english')
        .set_filename_fields(filename_fields)
    )

    def load(*_):

        nonlocal textacy_corpus, documents

        gui.output.clear_output()

        with gui.output:

            gui.load.disabled = True
            gui.load.description = "Wait..."
            gui.corpus_filename.disabled = True

            corpus_filename = os.path.join(corpus_folder, gui.corpus_filename.value)
            documents = pd.read_csv(gui.index_filename, sep=";", header=0)

            options = dict(
                filename=corpus_filename,
                lang=lang,
                documents=documents,
                filename_fields=filename_fields.split(','),
            )

            pipeline = TextacyCorpusPipeline(**options, tasks=[PreprocessTask, CreateTask, SaveTask, LoadTask])

            textacy_corpus = pipeline.process().corpus

            gui.load.disabled = False
            gui.vectorize.disabled = False
            gui.corpus_filename.disabled = False
            gui.load.description = "Load"

            print("Corpus loaded.")

    def vectorize(*_):

        nonlocal textacy_corpus, documents

        gui.output.clear_output()

        with gui.output:

            if textacy_corpus is None:
                print("Please load a corpus foirst!")

            gui.vectorize.disabled = True
            gui.vectorize.description = "Wait..."

            corpus = vectorize_textacy_corpus(
                textacy_corpus=textacy_corpus,
                documents=documents,
                annotation_opts=gui.annotation_opts,
                tokens_transform_opts=gui.tokens_transform_opts,
                extract_args=None,  # { "min_length": gui.min_length.value, "as_strings": True, "min_freq": 1, },
            )

            year_range = (
                corpus.documents.year.min(),
                corpus.documents.year.max(),
            )
            year_filter = lambda x: year_range[0] <= x["year"] <= year_range[1]

            corpus = (
                corpus.filter(year_filter)
                .group_by_year()
                .slice_by_n_count(gui.n_min_count.value)
                .slice_by_n_top(n_top=gui.n_top_count.value)
            )

            for axis in gui.normalize_axis.value or []:
                corpus = corpus.normalize(axis=axis, keep_magnitude=False)

            gui.vectorize.disabled = False
            gui.vectorize.description = "Prepare"

            if display_callback is not None:
                display_callback(corpus)

            print("Corpus vectorized.")

    gui.load.on_click(load)
    gui.vectorize.on_click(vectorize)

    layout = gui.layout()

    display(layout)

    return gui
