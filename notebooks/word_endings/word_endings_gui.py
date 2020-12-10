from dataclasses import dataclass
from typing import Callable

from ipyfilechooser import FileChooser
from IPython.display import display
from ipywidgets import HTML, Button, HBox, Output, Text, VBox
from penelope.corpus.readers import ExtractTaggedTokensOpts, TextTransformOpts
from penelope.pipeline import CorpusConfig, SpacyPipeline


@dataclass
class GUI:

    folder: FileChooser = FileChooser()
    output: Output = Output()
    execute: Button = Button(description="Execute")
    callback: Callable = None
    checkpoint: Text = Text(disabled=True)
    word_endings: Text = Text(disabled=False)

    def _callback(self, *_):

        if self.callback is not None:
            with self.output:
                self.callback(self)

    def layout(self):
        return VBox(
            VBox(
                self.folder,
                HBox(
                    VBox(
                        HTML("<b>Checkpoint filename</b>"),
                        self.checkpoint,
                        HTML("<b>Word endings</b>"),
                        self.word_endings,
                    ),
                    self.execute,
                ),
            ),
            self.output,
        )

    def setup(self, *, checkpoint: str, callback):
        self.callback = callback
        self.checkpoint.value = checkpoint
        self.execute.on_click(self._callback)
        return self

    def get_extract_opts(self) -> ExtractTaggedTokensOpts:
        pass


def execute_callback(config: CorpusConfig, gui: GUI):

    checkpoint_filename = gui.checkpoint_filename
    extract_tokens_opts: ExtractTaggedTokensOpts = ExtractTaggedTokensOpts(lemmatize=False)

    # pipeline = create_pos_checkpoint_pipeline(config=config, checkpoint_filename=checkpoint_filename)

    pipeline = (
        SpacyPipeline(payload=config.pipeline_payload)
        .set_spacy_model(config.pipeline_payload.memory_store['spacy_model'])
        .load_text(reader_opts=config.text_reader_opts, transform_opts=TextTransformOpts())
        .text_to_spacy()
        .tqdm()
        .passthrough()
        .spacy_to_pos_tagged_frame()
        .checkpoint(checkpoint_filename)
        .tagged_frame_to_tokens(extract_tokens_opts)
        .tokens_to_text()
    )
    # pipeline.exhaust()

    v_corpus = pipeline.to_dtm()

    assert v_corpus is not None

    # corpus = TokenizedCorpus(i)
    # vectorizer: CorpusVectorizer = CorpusVectorizer()
    # v_corpus: VectorizedCorpus = vectorizer.fit_transform(corpus, already_tokenized=True)
    # vocabulary = list(v_corpus.token2id.keys())
    # word_endings = {'ment', 'tion'}
    # candidates = {x for x in vocabulary if any((x.endswith(w) for w in word_endings))}
    # w_corpus = v_corpus.slice_by(lambda w: w in candidates)


def display_gui(config: CorpusConfig, data_folder: str, checkpoint_filename: str):  # pylint: disable=unused-argument
    def callback(gui: GUI):
        execute_callback(config=config, gui=gui)

    checkpoint_filename = f"{config.corpus_name}_pos_csv.zip"

    gui: GUI = GUI().setup(checkpoint=checkpoint_filename, callback=callback)

    display(gui.layout())


# def slice_by_word_ending(
#     v_corpus: VectorizedCorpus, word_endings: Sequence[str], documents: pd.DataFrame = None
# ):  # pylint: disable=unused-argument
#     """
#     Add an ability to enter a number of specific word endings such as -ment, -tion and -sion.
#     The system should finds all words having the specified endings, and displays the (optionally normalized)
#     frequency list as a table, or bar chart. It should also be possible to export the list, and to a apply a
#     filter that excludes any number of words (in a text box).

#     It should be possible to display the data grouped by document, year or user defined periods.

#     See Moretti, Pestre Bank Speek, page 89
#     """

#     vocabulary = list(v_corpus.token2id.keys())

#     candidates = {x for x in vocabulary if any(x.endswith(word_ending) for word_ending in word_endings)}

#     w_corpus = v_corpus.slice_by(lambda w: w in candidates)

#     return w_corpus

# vectorized_ssi_corpus = None

# def loaded_callback(output: Any, corpus: VectorizedCorpus, **_):
#     global vectorized_ssi_corpus
#     vectorized_ssi_corpus = corpus
#     with output:
#         print("Corpus loaded!")

# load_vectorized_corpus_gui.display_gui(loaded_callback=loaded_callback)

# we_corpus = slice_by_word_ending(vectorized_ssi_corpus, documents=ssi_documents, word_endings={"ment", "tion", "sion"})
# statement = we_corpus.data[:, we_corpus.token2id['statement']].todense().A1
# pd.DataFrame(data={'statement': statement}).plot()
# print(we_corpus.data.sum(axis=0).toarray())
# pd.DataFrame(we_corpus.data.sum(axis=0).A1).plot()
# print(we_corpus.group_by_year())
