from typing import Mapping

import bokeh
import ipywidgets as widgets
import pandas as pd
from IPython.display import display
from penelope.plot.word_trend_plot import (
    empty_multiline_datasource,
    yearly_token_distributions_bar_plot,
    yearly_token_distributions_datasource,
    yearly_token_distributions_multiline_datasource,
    yearly_token_distributions_multiline_plot,
)


def display_as_table(data, **_):
    df = pd.DataFrame(data=data)
    df = df[["year"] + [x for x in df.columns if x != "year"]].set_index("year")
    display(df)


def plot_multiline(data, **kwargs):
    kwargs.get("data_source").data.update(data)
    bokeh.io.push_notebook(handle=kwargs.get('handle'))


def plot_bar(data, **kwargs):
    p = yearly_token_distributions_bar_plot(data, **kwargs)
    bokeh.io.show(p)


def display_gui(state: Mapping):

    output_widget = widgets.Output(layout=widgets.Layout(width="600px", height="200px"))
    words_widget = widgets.Textarea(
        description="",
        rows=4,
        value="cultural diversity property heritage",
        layout=widgets.Layout(width="600px", height="200px"),
    )
    tab_widget = widgets.Tab()
    tab_widget.children = [widgets.Output(), widgets.Output(), widgets.Output()]

    tab_plot_types = ["Table", "Line", "Bar"]
    data_compilers = [
        yearly_token_distributions_datasource,
        yearly_token_distributions_multiline_datasource,
        yearly_token_distributions_datasource,
    ]
    data_displayers = [display_as_table, plot_multiline, plot_bar]
    clear_output = [True, False, True]
    _ = [tab_widget.set_title(i, x) for i, x in enumerate(tab_plot_types)]

    # smooth = False
    # smoothers = (
    #     []
    #     if not smooth
    #     else [
    #         # cf.rolling_average_smoother('nearest', 3),
    #         cf.pchip_spline
    #     ]
    # )

    z_corpus = None
    x_corpus = None

    def update_plot(*_):

        nonlocal z_corpus, x_corpus

        if state.get("corpus", None) is None:

            with output_widget:
                print("Please load a corpus!")

            return

        if z_corpus is None or z_corpus is not state.get("corpus"):

            with output_widget:
                print("Corpus changed...")

            z_corpus = state.get("corpus")
            x_corpus = z_corpus.todense()

            tab_widget.children[1].clear_output()

            with tab_widget.children[1]:

                data_source = empty_multiline_datasource()

                p = yearly_token_distributions_multiline_plot(
                    data_source,
                    x_ticks=[x for x in x_corpus.xs_years()],  # pylint: disable=unnecessary-comprehension
                    plot_width=1000,
                    plot_height=500,
                )  # pylint: disable=unnecessary-comprehension

                state['handle'] = bokeh.plotting.show(p, notebook_handle=True)
                state['data_source'] = data_source

        tokens = "\n".join(words_widget.value.split()).split()
        index = tab_widget.selected_index
        indices = [x_corpus.token2id[token] for token in tokens if token in x_corpus.token2id]

        with output_widget:

            if len(indices) == 0:
                print("Nothing to show!")
                return

            missing_tokens = [token for token in tokens if token not in x_corpus.token2id]
            if len(missing_tokens) > 0:
                print("Not in corpus subset: {}".format(" ".join(missing_tokens)))

        if clear_output[index]:
            tab_widget.children[index].clear_output()

        with tab_widget.children[index]:

            data = data_compilers[index](x_corpus, indices)
            data_displayers[index](data, **state)

    words_widget.observe(update_plot, names="value")
    tab_widget.observe(update_plot, "selected_index")

    g = widgets.VBox([widgets.HBox([words_widget, output_widget]), tab_widget])

    # update_plot()
    return g
