from dataclasses import dataclass
from typing import Callable, List

import ipywidgets as widgets
import pandas as pd
import penelope.pipeline.spacy.pipelines as pipelines
from bokeh.io import output_notebook
from penelope.notebook.ipyaggrid_utility import display_grid
from penelope.notebook.utility import OutputsTabExt
from penelope.pipeline import CorpusConfig
from penelope.pipeline.interfaces import PipelineError
from penelope.utility import PoS_Tag_Scheme, getLogger, path_add_suffix

import __paths__

from .plot import plot_by_bokeh as plot_dataframe

logger = getLogger("penelope")

TOKEN_COUNT_GROUPINGS = ['decade', 'lustrum', 'year']

debug_view = widgets.Output()
# pylint: disable=too-many-instance-attributes


@dataclass
class TokenCountsGUI:
    """GUI component that displays word trends"""

    compute_callback: Callable

    load_document_index_callback: Callable
    load_corpus_config_callback: Callable

    document_index: pd.DataFrame = None

    _corpus_configs: widgets.Dropdown = widgets.Dropdown(
        description='', options=['SSI'], value='SSI', layout={'width': '200px'}
    )
    _normalize: widgets.ToggleButton = widgets.ToggleButton(
        description="Normalize", icon='check', value=False, layout=widgets.Layout(width='140px')
    )
    _smooth: widgets.ToggleButton = widgets.ToggleButton(
        description="Smooth", icon='check', value=False, layout=widgets.Layout(width='140px')
    )
    _grouping: widgets.Dropdown = widgets.Dropdown(
        options=TOKEN_COUNT_GROUPINGS,
        value='year',
        description='',
        disabled=False,
        layout=widgets.Layout(width='90px'),
    )
    _status: widgets.Label = widgets.Label(layout=widgets.Layout(width='50%', border="0px transparent white"))
    _categories: widgets.SelectMultiple = widgets.SelectMultiple(
        options=[],
        value=[],
        rows=12,
        layout=widgets.Layout(width='120px'),
    )

    _output = widgets.Output()

    _tab: OutputsTabExt = OutputsTabExt(["Table", "Plot"], layout={'width': '98%'})

    def layout(self) -> widgets.HBox:
        return widgets.HBox(
            [
                widgets.VBox(
                    [
                        widgets.HTML("<b>PoS groups</b>"),
                        self._categories,
                    ],
                    layout={'width': '140px'},
                ),
                widgets.VBox(
                    [
                        widgets.HBox(
                            [
                                self._normalize,
                                self._smooth,
                                self._grouping,
                                self._corpus_configs,
                                self._status,
                            ]
                        ),
                        widgets.HBox(
                            [
                                self._tab,
                            ],
                            layout={'width': '98%'},
                        ),
                    ],
                    layout={'width': '98%'},
                ),
            ],
            layout={'width': '98%'},
        )

    def _plot_counts(self, *_):

        try:
            if self.document_index is None:  # pragma: no cover
                self.alert("Please load a corpus!")
                return

            data = self.compute_callback(self, self.document_index)

            self._tab.display_content(
                0,
                what=display_grid(data),
                clear=True,
            )

            self._tab.display_content(
                1,
                what=lambda: plot_dataframe(data_source=data.set_index(self.grouping), smooth=self.smooth),
                # what=lambda: data.set_index(self.grouping).plot_bokeh(
                #     kind="line",
                #     figsize=(1100, 600),
                # ),
                clear=True,
            )

            self.alert("✔")

        except ValueError as ex:  # pragma: no cover
            self.alert(str(ex))
        except Exception as ex:  # pragma: no cover
            logger.exception(ex)
            self.warn(str(ex))

    def setup(self) -> "TokenCountsGUI":

        self._categories.observe(self._plot_counts, names='value')
        self._normalize.observe(self._plot_counts, names='value')
        self._smooth.observe(self._plot_counts, names='value')
        self._grouping.observe(self._plot_counts, names='value')
        self._corpus_configs.observe(self.display, names='value')

        return self

    def _display(self, _):
        self.display(corpus_config_name=self._corpus_configs.value)

    def display(self, *, corpus_config_name: str) -> "TokenCountsGUI":
        global debug_view
        corpus_config: CorpusConfig = self.load_corpus_config_callback(corpus_config_name)
        pos_schema = corpus_config.pos_schema
        self._categories.values = []
        self._categories.options = ['#Tokens'] + pos_schema.PD_PoS_groups.index.tolist()
        self._categories.values = ['#Tokens']

        self.document_index = self.load_document_index_callback(corpus_config)

        debug_view.clear_output()
        self._output.clear_output()

        with self._output:
            self._plot_counts()

        return self

    def alert(self, msg: str):
        self._status.value = msg

    def warn(self, msg: str):
        self.alert(f"<span style='color=red'>{msg}</span>")

    @property
    def smooth(self) -> bool:
        return self._smooth.value

    @property
    def normalize(self) -> bool:
        return self._normalize.value

    @property
    def grouping(self) -> str:
        return self._grouping.value

    @property
    def categories(self) -> List[str]:
        return list(self._categories.value)


DATA = None


@debug_view.capture()
def compute_token_count_data(args: TokenCountsGUI, document_index: pd.DataFrame) -> pd.DataFrame:
    global DATA
    if len(args.categories or []) > 0:
        count_columns = list(args.categories)
    else:
        count_columns = [x for x in document_index.columns if x not in TOKEN_COUNT_GROUPINGS]

    data = document_index.groupby(args.grouping).sum()[count_columns]
    DATA = data
    if args.normalize:
        data = data / data.sum(axis=0)
    # args.smooth

    if args.smooth:
        data = data.interpolate(method='index')

    return data.reset_index()


@debug_view.capture()
def load_corpus_config(corpus_config_name: str) -> pd.DataFrame:
    corpus_config: CorpusConfig = CorpusConfig.find(corpus_config_name, __paths__.resources_folder).folder(
        __paths__.data_folder
    )
    return corpus_config


@debug_view.capture()
def load_document_index(corpus_config: CorpusConfig) -> pd.DataFrame:

    checkpoint_filename: str = path_add_suffix(corpus_config.pipeline_payload.source, '_pos_csv')

    pipeline = pipelines.to_tagged_frame_pipeline(corpus_config, checkpoint_filename).exhaust()

    document_index = pipeline.payload.document_index

    if 'n_raw_tokens' not in document_index.columns:
        raise PipelineError("expected required column `n_raw_tokens` not found")

    document_index['lustrum'] = document_index.year - document_index.year % 5
    document_index['decade'] = document_index.year - document_index.year % 10

    document_index = document_index.rename(columns={"n_raw_tokens": "#Tokens"}).fillna(0)

    # strip away irrelevant columns

    pos_schema: PoS_Tag_Scheme = corpus_config.pos_schema

    groups = TOKEN_COUNT_GROUPINGS + ['#Tokens'] + pos_schema.PD_PoS_groups.keys().tolist()

    columns = [x for x in groups if x in document_index.columns]

    document_index = document_index[columns]

    return document_index


def create_token_count_gui(
    corpus_config_name: str,
):

    # pd.set_option('plotting.backend', 'pandas_bokeh')
    # pd.plotting.output_notebook()
    # pandas_bokeh.output_notebook()
    output_notebook()

    gui = (
        TokenCountsGUI(
            compute_callback=compute_token_count_data,
            load_document_index_callback=load_document_index,
            load_corpus_config_callback=load_corpus_config,
        )
        .setup()
        .display(corpus_config_name=corpus_config_name)
    )

    return gui
