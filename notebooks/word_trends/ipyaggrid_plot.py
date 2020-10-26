import pandas as pd
from ipyaggrid import Grid


def default_column_defs(df):
    column_defs = [
        {
            'headerName': column.title(),
            'field': column,
            # 'rowGroup':False,
            # 'hide':False,
            'cellRenderer': "function(params) { return params.value.toFixed(6); }" if column != 'year' else None,
            # 'type': 'numericColumn'
        }
        for column in df.columns
    ]
    return column_defs


def display(data, **_):

    if isinstance(data, dict):
        df = pd.DataFrame(data=data)  # .set_index('year')
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        raise ValueError('Illegal data type')

    column_defs = default_column_defs(df)
    grid_options = {
        'columnDefs': column_defs,
        'enableSorting': True,
        'enableFilter': True,
        'enableColResize': True,
        'enableRangeSelection': False,
    }

    g = Grid(
        grid_data=df,
        grid_options=grid_options,
        quick_filter=False,
        show_toggle_edit=False,
        export_mode="buttons",
        export_csv=True,
        export_excel=False,
        theme='ag-theme-balham',
        show_toggle_delete=False,
        columns_fit='auto',
        index=True,
        keep_multiindex=False,
        menu={'buttons': [{'name': 'Export Grid', 'hide': True}]},
    )

    return g


def simple_plot(df):

    grid_options = {
        # 'columnDefs' : column_defs,
        'enableSorting': True,
        'enableFilter': True,
        'enableColResize': True,
        'enableRangeSelection': False,
    }

    g = Grid(
        grid_data=df,
        grid_options=grid_options,
        quick_filter=False,
        show_toggle_edit=False,
        export_mode="buttons",
        export_csv=True,
        export_excel=False,
        theme='ag-theme-balham',
        show_toggle_delete=False,
        columns_fit='auto',
        index=True,
        keep_multiindex=False,
        menu={'buttons': [{'name': 'Export Grid', 'hide': True}]},
    )

    return g
