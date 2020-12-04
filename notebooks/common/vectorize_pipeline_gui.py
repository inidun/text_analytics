import os
import types
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict

import ipyfilechooser
import ipywidgets as widgets
from penelope.corpus import TokensTransformOpts, VectorizedCorpus, VectorizeOpts
from penelope.corpus.readers import ExtractTaggedTokensOpts, TaggedTokensFilterOpts, TextTransformOpts
from penelope.pipeline import CorpusConfig, CorpusType, PipelineError, SpacyPipeline
from penelope.utility import default_data_folder, flatten, get_logger, get_pos_schema, path_add_suffix

logger = get_logger()

# pylint: disable=attribute-defined-outside-init, too-many-instance-attributes
layout_default = widgets.Layout(width='200px')
layout_button = widgets.Layout(width='140px')


def shorten_path_with_ellipsis(path: str, max_length: int):
    if len(path) > max_length:
        path, filename = os.path.split(path)
        path = f"{path[:max(0, max_length-len(filename))]}.../{filename}"
    return path


def shorten_filechooser_label(fc: ipyfilechooser.FileChooser, max_length: int):
    try:
        template = getattr(fc, '_LBL_TEMPLATE')
        if not template or not hasattr(template, 'format'):
            return
        fake = types.SimpleNamespace(
            format=lambda p, c: template.format(
                shorten_path_with_ellipsis(p, max_length),
                'green' if os.path.exists(p) else 'black',
            )
        )
        setattr(fc, '_LBL_TEMPLATE', fake)
        if len(fc.selected) > max_length:
            getattr(fc, '_label').value = fake.format(None, fc.selected, 'green')
    except:  # pylint: disable=bare-except
        pass


@dataclass
class GUI:

    default_corpus_path: str = None
    default_corpus_filename: str = field(default='')
    default_target_folder: str = None

    _config: CorpusConfig = None

    _courpus_filename: ipyfilechooser.FileChooser = None
    _target_folder: ipyfilechooser.FileChooser = None

    _corpus_type = widgets.Dropdown(
        description='',
        options={
            'Text': CorpusType.Text,
            'Pipeline': CorpusType.Pipeline,
            'Sparv4-CSV': CorpusType.SparvCSV,
        },
        value=CorpusType.Pipeline,
        layout=layout_default,
    )
    _corpus_tags = widgets.Text(
        value='',
        placeholder='Tag to prepend filenames',
        description='',
        disabled=False,
        layout=layout_default,
    )
    _pos_includes = widgets.SelectMultiple(
        options=[],
        value=[],
        rows=8,
        description='',
        disabled=False,
        layout=layout_default,
    )
    _count_threshold = widgets.IntSlider(description='', min=1, max=1000, step=1, value=1, layout=layout_default)
    _filename_fields = widgets.Text(
        value=r"year:prot\_(\d{4}).*",
        placeholder='Fields to extract from filename (regex)',
        description='',
        disabled=False,
        layout=layout_default,
    )
    _create_subfolder = widgets.ToggleButton(
        value=True, description='Create folder', icon='check', layout=layout_button
    )
    _lemmatize = widgets.ToggleButton(value=True, description='Lemmatize', icon='check', layout=layout_button)
    _to_lowercase = widgets.ToggleButton(value=True, description='To Lower', icon='check', layout=layout_button)
    _remove_stopwords = widgets.ToggleButton(value=True, description='No Stopwords', icon='check', layout=layout_button)
    _only_alphabetic = widgets.ToggleButton(value=False, description='Only Alpha', icon='', layout=layout_button)
    _only_any_alphanumeric = widgets.ToggleButton(
        value=False, description='Only Alphanum', icon='', layout=layout_button
    )
    _extra_stopwords = widgets.Textarea(
        value='örn',
        placeholder='Enter extra stop words',
        description='',
        disabled=False,
        rows=8,
        layout=widgets.Layout(width='350px'),
    )
    _vectorize_button = widgets.Button(
        description='Vectorize!',
        button_style='Success',
        layout=layout_button,
    )
    output = widgets.Output()
    compute_callback: Callable = None

    def layout(self, hide_input=False, hide_output=False):

        return widgets.VBox(
            (
                []
                if hide_input
                else [
                    widgets.HBox(
                        [
                            widgets.VBox(
                                [
                                    widgets.HTML("<b>Corpus type</b>"),
                                    self._corpus_type,
                                ]
                            ),
                            self._courpus_filename,
                        ]
                    ),
                ]
            )
            + (
                []
                if hide_output
                else [
                    widgets.HBox(
                        [
                            widgets.VBox(
                                [
                                    widgets.HTML("<b>Output tag</b>"),
                                    self._corpus_tags,
                                ]
                            ),
                            self._target_folder,
                        ]
                    ),
                ]
            )
            + [
                widgets.HBox(
                    [
                        widgets.VBox(
                            [
                                widgets.HTML("<b>Part-Of-Speech tags</b>"),
                                self._pos_includes,
                            ]
                        ),
                        widgets.VBox(
                            [
                                widgets.HTML("<b>Extra stopwords</b>"),
                                self._extra_stopwords,
                            ]
                        ),
                    ]
                ),
                widgets.HBox(
                    [
                        widgets.VBox(
                            [
                                widgets.VBox(
                                    [
                                        widgets.HTML("<b>Filename fields</b>"),
                                        self._filename_fields,
                                    ]
                                ),
                                widgets.VBox(
                                    [
                                        widgets.HTML("<b>Frequency threshold</b>"),
                                        self._count_threshold,
                                    ]
                                ),
                            ]
                        ),
                        widgets.VBox(
                            [
                                widgets.HBox(
                                    [
                                        widgets.VBox(
                                            [
                                                self._lemmatize,
                                                self._to_lowercase,
                                                self._remove_stopwords,
                                            ]
                                        ),
                                        widgets.VBox(
                                            [
                                                self._only_alphabetic,
                                                self._only_any_alphanumeric,
                                                self._create_subfolder,
                                                self._vectorize_button,
                                            ]
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
                self.output,
            ]
        )

    def _compute_handler(self, *_):
        if self.compute_callback is not None:
            with self.output:
                self._vectorize_button.disabled = True
                try:

                    self.compute_callback(self)

                except (ValueError, FileNotFoundError) as ex:
                    print(ex)
                except PipelineError as ex:
                    logger.info(ex)
                    raise
                finally:
                    self._vectorize_button.disabled = False

    def _corpus_type_changed(self, *_):
        self._pos_includes.disabled = self._corpus_type.value == 'text'
        self._lemmatize.disabled = self._corpus_type.value == 'text'

    def _toggle_state_changed(self, event):
        with self.output:
            try:
                event['owner'].icon = 'check' if event['new'] else ''
            except Exception as ex:
                logger.exception(ex)

    def _remove_stopwords_state_changed(self, *_):
        self._extra_stopwords.disabled = not self._remove_stopwords.value

    def setup(self, *, config: CorpusConfig, compute_callback: Callable):

        self._config = config

        self._courpus_filename = ipyfilechooser.FileChooser(
            path=self.default_corpus_path or default_data_folder(),
            filename=self.default_corpus_filename,
            filter_pattern='*.*',
            title='<b>Source corpus file</b>',
            show_hidden=False,
            select_default=True,
            use_dir_icons=True,
            show_only_dirs=False,
        )

        shorten_filechooser_label(self._courpus_filename, 50)

        self._target_folder = ipyfilechooser.FileChooser(
            path=self.default_target_folder or default_data_folder(),
            title='<b>Output folder</b>',
            show_hidden=False,
            select_default=True,
            use_dir_icons=True,
            show_only_dirs=True,
        )

        pos_schema = get_pos_schema(self._config.pipeline_payload.pos_schema_name)

        self._pos_includes.value = []
        self._pos_includes.options = pos_schema.groups
        self._pos_includes.value = [pos_schema.groups['Noun'], pos_schema.groups['Verb']]

        self._corpus_type.value = config.corpus_type
        self._corpus_type.disabled = True
        self._courpus_filename.filter_pattern = config.corpus_pattern
        self._filename_fields.value = ';'.join(config.text_reader_opts.filename_fields)
        self._filename_fields.disabled = True

        self.compute_callback = compute_callback

        self._vectorize_button.on_click(self._compute_handler)
        self._corpus_type.observe(self._corpus_type_changed, 'value')
        self._lemmatize.observe(self._toggle_state_changed, 'value')
        self._to_lowercase.observe(self._toggle_state_changed, 'value')
        self._remove_stopwords.observe(self._toggle_state_changed, 'value')
        self._remove_stopwords.observe(self._remove_stopwords_state_changed, 'value')
        self._only_alphabetic.observe(self._toggle_state_changed, 'value')
        self._only_any_alphanumeric.observe(self._toggle_state_changed, 'value')

        return self

    @property
    def tokens_transform_opts(self) -> TokensTransformOpts:

        opts = TokensTransformOpts(
            keep_numerals=True,
            keep_symbols=True,
            language=self._config.language,
            max_len=None,
            min_len=1,
            only_alphabetic=self._only_alphabetic.value,
            only_any_alphanumeric=self._only_any_alphanumeric.value,
            remove_accents=False,
            remove_stopwords=self._remove_stopwords.value,
            stopwords=None,
            extra_stopwords=None,
            to_lower=self._to_lowercase.value,
            to_upper=False,
        )

        if self._extra_stopwords.value.strip() != '':
            _words = [x for x in map(str.strip, self._extra_stopwords.value.strip().split()) if x != '']
            if len(_words) > 0:
                opts.extra_stopwords = _words

        return opts

    @property
    def extract_tagged_tokens_opts(self) -> ExtractTaggedTokensOpts:
        pos_schema = get_pos_schema(self._config.pipeline_payload.pos_schema_name)
        return ExtractTaggedTokensOpts(
            pos_includes=f"|{'|'.join(flatten(self._pos_includes.value))}|",
            pos_excludes=f"|{'|'.join(flatten(pos_schema.groups.get('Delimiter', [])))}|",
            lemmatize=self._lemmatize.value,
            passthrough_tokens=list(),
        )

    @property
    def tagged_tokens_filter_opts(self) -> TaggedTokensFilterOpts:

        return TaggedTokensFilterOpts(
            is_alpha=self._only_alphabetic.value, is_space=False, is_punct=False, is_digit=None, is_stop=None
        )

    @property
    def vectorize_opts(self) -> VectorizeOpts:
        return VectorizeOpts(already_tokenized=True, lowercase=False, max_df=1.0, min_df=1, verbose=False)

    @property
    def corpus_tag(self):
        return self._corpus_tags.value.strip()

    @property
    def target_folder(self):
        if self._create_subfolder:
            return os.path.join(self._target_folder.selected_path, self.corpus_tag)
        return self._target_folder.selected_path

    @property
    def corpus_folder(self):
        return self._courpus_filename.selected_path

    @property
    def corpus_filename(self):
        return self._courpus_filename.selected


def default_done_callback(*_, **__):
    print("Vectorization done!")


def dummy_context():
    class DummyContext:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):  # pylint: disable=unused-argument
            pass

    return DummyContext()


# pylint: disable=too-many-locals
def compute_document_term_matrix(
    corpus_config: CorpusConfig,
    args: GUI,
    done_callback: Callable,
    persist: bool = False,
):
    try:

        if persist and not args.corpus_tag:
            raise ValueError("undefined corpus tag")

        if persist and not args.target_folder:
            raise ValueError("target folder undefined")

        if not args.corpus_filename:
            raise ValueError("corpus file is falsy")

        if not args.corpus_folder:
            raise ValueError("corpus folder is falsy")

        if not os.path.isfile(args.corpus_filename):
            raise FileNotFoundError(args.corpus_filename)

        checkpoint_filename: str = path_add_suffix(args.corpus_filename, '_pos_csv')

        pipeline: SpacyPipeline = (
            SpacyPipeline(payload=corpus_config.pipeline_payload)
            .set_spacy_model(corpus_config.pipeline_payload.memory_store['spacy_model'])
            .load_text(reader_opts=corpus_config.text_reader_opts, transform_opts=TextTransformOpts())
            .text_to_spacy()
            .tqdm()
            .passthrough()
            .spacy_to_pos_tagged_frame()
            .checkpoint(checkpoint_filename)
            .tagged_frame_to_tokens(
                extract_opts=args.extract_tagged_tokens_opts,
                filter_opts=args.tagged_tokens_filter_opts,
            )
            .tokens_transform(tokens_transform_opts=args.tokens_transform_opts)
            .tokens_to_text()
            .to_document_content_tuple()
            .tqdm()
            .to_dtm(vectorize_opts=args.vectorize_opts)
        )

        corpus: VectorizedCorpus = pipeline.value()

        if persist:
            os.makedirs(args.target_folder, exist_ok=True)
            corpus.dump(tag=args.corpus_tag, folder=args.target_folder)

        (done_callback or default_done_callback)(
            corpus=corpus,
            corpus_tag=args.corpus_tag,
            corpus_folder=args.target_folder if persist else None,
            options=dict(
                config=asdict(corpus_config),
                extract_opts=asdict(args.extract_tagged_tokens_opts),
                filter_opts=args.tagged_tokens_filter_opts.props,
                transform_opts=asdict(args.tokens_transform_opts),
                vectorize_opts=asdict(args.vectorize_opts),
                # pipeline=pipeline.payload.memory_store,
            ),
            output=args.output if hasattr(args, 'output') else dummy_context(),
        )

    except Exception as ex:
        raise ex


def display_gui(
    *,
    corpus_folder: str,
    corpus_config: CorpusConfig,
    persist: bool,
    done_callback: Callable[[VectorizedCorpus, str, str, Dict[str, Any], widgets.Output], None],
) -> GUI:
    """Returns a GUI for turning a corpus pipeline to a document-term-matrix (DTM)"""
    corpus_config.set_folder(corpus_folder)
    gui = GUI(
        default_corpus_path=corpus_folder,
        default_corpus_filename=corpus_config.pipeline_payload.source,
        default_target_folder=corpus_folder,
    ).setup(
        config=corpus_config,
        compute_callback=lambda g: compute_document_term_matrix(corpus_config, g, done_callback, persist=True),
    )

    return gui
