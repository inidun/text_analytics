import types
from typing import Callable

import ipywidgets as widgets
import pandas as pd
import textacy
from notebooks.word_endings.word_endings import CORPUS_FOLDER
from penelope.utility import PoS_TAGS_SCHEMES, flatten
from penelope.vendor.textacy import vectorize_textacy_corpus

# from penelope.utility.utils import right_chop, getLogger

# logger = getLogger('corpus_text_analysis')

# pylint: disable=attribute-defined-outside-init, too-many-instance-attributes


def display_gui(corpus: textacy.Corpus, documents: pd.DataFrame, generated_callback: Callable):
    lw = lambda w: widgets.Layout(width=w)

    pos_schema = PoS_TAGS_SCHEMES.Universal

    gui = types.SimpleNamespace(
        corpus_tag=widgets.Text(
            value='',
            placeholder='Enter a filename without extension',
            description='Result',
            disabled=False,
            layout=lw('400px'),
        ),
        pos_includes=widgets.SelectMultiple(
            options=pos_schema.groups,
            value=[pos_schema.groups['Noun'], pos_schema.groups['Verb']],
            rows=8,
            description='PoS',
            disabled=False,
            layout=lw('400px'),
        ),
        count_threshold=widgets.IntSlider(
            description='Min Count', min=1, max=1000, step=1, value=1, layout=lw('400px')
        ),
        lemmatize=widgets.ToggleButton(value=True, description='Lemmatize', icon='check', layout=lw('140px')),
        to_lowercase=widgets.ToggleButton(value=True, description='To Lower', icon='check', layout=lw('140px')),
        remove_stopwords=widgets.ToggleButton(value=True, description='No Stopwords', icon='check', layout=lw('140px')),
        button=widgets.Button(
            description='Load',
            button_style='Success',
            layout=lw('140px'),
        ),
        output=widgets.Output(),
    )

    def on_button_clicked(_):

        if gui.input_filename.value is None:
            return

        if gui.output_filename.value.strip() == "":
            return

        with gui.output:

            # gui.output.clear_output()
            # FIXME: #4 Use new value objects instead of dicts
            gui.button.disabled = True
            include_pos = set(list(flatten(flatten(gui.pos_includes.value))))
            v_corpus = vectorize_textacy_corpus(
                corpus,
                documents,
                n_count=gui.count_threshold.value,
                n_top=None,
                normalize_axis=[0, 1],
                year_range=(1920, 2020),
                extract_args=dict(
                    normalize='lemma' if gui.lemmatize.value else None,
                    as_strings=True,
                    filter_stops=gui.remove_stopwords.value,  # (bool)
                    filter_punct=True,  # (bool)
                    filter_nums=True,  # (bool)
                    include_pos=include_pos,  # (str or Set[str])
                    # min_freq=1,  # (int)
                    drop_determiners=True,  # (bool)
                ),
                vecargs=None,
            )

            v_corpus.dump(CORPUS_FOLDER, gui.corpus_tag.value)

            if generated_callback is not None:
                generated_callback(
                    gui.output,
                    corpus=v_corpus,
                    corpus_folder=CORPUS_FOLDER,
                    corpus_tag=gui.corpus_tag.value,
                )

            gui.button.disabled = False

    gui.button.on_click(on_button_clicked)

    return widgets.VBox(
        [
            widgets.HBox(
                [
                    widgets.VBox(
                        [
                            gui.corpus_tag,
                            gui.pos_includes,
                            gui.count_threshold,
                        ]
                    ),
                    widgets.VBox([gui.lemmatize, gui.to_lowercase, gui.remove_stopwords, gui.button]),
                ]
            ),
            gui.output,
        ]
    )
