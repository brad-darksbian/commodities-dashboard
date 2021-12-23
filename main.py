import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import business_logic as bl
import layout_configs as lc
import support_functions as sf

#############################################################################
# Style modifications
#############################################################################
CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
}

TEXT_STYLE = {"textAlign": "center"}

DROPDOWN_STYLE = {"textAlign": "left"}

#############################################################################
# Content
#############################################################################
# Create drop-down selector
future_select = dbc.Row(
    [
        dbc.Col(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id="future",
                            options=[{"label": i, "value": i} for i in bl.da_list],
                            value="SILVER - COMMODITY EXCHANGE INC.",
                        ),
                    ],
                    className="dash-bootstrap",
                ),
            ],
            md=6,
        )
    ]
)

# Info Bar
info_bar = html.Div(
    id="summary",
)

# Container for sentiment charts
sentiment_direction = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(
                id="deacot_sent",
                style={"height": "70vh"},
                config=lc.tool_config,
            ),
            md=6,
        ),
        dbc.Col(
            dcc.Graph(
                id="da_sent",
                style={"height": "70vh"},
                config=lc.tool_config,
            ),
            md=6,
        ),
    ]
)

# Container for postion charts
da_postiions = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(
                id="da_pos_all",
                style={"height": "70vh"},
                config=lc.tool_config,
            ),
            md=6,
        ),
        dbc.Col(
            dcc.Graph(
                id="da_pos_pct",
                style={"height": "70vh"},
                config=lc.tool_config,
            ),
            md=6,
        ),
    ]
)

# Reference cards for bottom disclosures
# References relating to DEACOT report
deacot_reference_card = (
    dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5("DEACOT Report References", className="card-title"),
                    html.P(
                        "Speculators are traders with a commercial interest in the underlying commodity"
                    ),
                    html.P(
                        "Funds are traders with no commercial interest in the underlying commodity"
                    ),
                    html.P(
                        "Others / Non-Reporting are aggregated traders not required to individually register positions"
                    ),
                    html.P("Dashed lines signify short position levels."),
                    html.P("Data retrieved from CFTC.gov:"),
                    dbc.CardLink(
                        "DEACOT Report",
                        href="https://www.cftc.gov/files/dea/history/deacot2021.zip",
                    ),
                ]
            )
        ]
    ),
)
# References relating to Disaggregation report
da_reference_card = (
    dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5("Disaggregation Report References", className="card-title"),
                    html.P(
                        "A “producer/merchant/processor/user” is an entity that predominantly engages in the production, processing, packing or handling of a physical commodity."
                    ),
                    html.P(
                        "A “swap dealer” is an entity that deals primarily in swaps for a commodity. The swap dealer counterparties may be speculative traders, like hedge funds, or traditional commercial clients."
                    ),
                    html.P(
                        "A “money manager” is a registered commodity trading advisor (CTA); a registered commodity pool operator (CPO); or an unregistered fund identified by CFTC."
                    ),
                    html.P(
                        "Every other reportable trader that is not placed into one of the other three categories is placed into the “other reportables” category."
                    ),
                    html.P("Data retrieved from CFTC.gov:"),
                    dbc.CardLink(
                        "Disaggregation Report",
                        href="https://www.cftc.gov/files/dea/history/fut_disagg_txt_2021.zip",
                    ),
                ]
            )
        ]
    ),
)


# Container for 3d Net Postion Chart
da_3d_positions = dbc.Row(
    [
        dbc.Col(
            html.Div(deacot_reference_card),
            md=3,
        ),
        dbc.Col(
            dcc.Graph(
                id="da_3d_net",
                style={"height": "70vh"},
                config=lc.tool_config,
            ),
            md=6,
        ),
        dbc.Col(
            html.Div(da_reference_card),
            md=3,
        ),
    ]
)

# Container for relative change bar charts
da_diffs = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(
                id="da_diff_all",
                style={"height": "75vh"},
                config=lc.tool_config,
            ),
            md=6,
        ),
        dbc.Col(
            dcc.Graph(
                id="da_diff_pct",
                style={"height": "75vh"},
                config=lc.tool_config,
            ),
            md=6,
        ),
    ]
)

# Container for the latest week position bar chart
da_pos_snap = dbc.Row(
    [
        dbc.Col(
            dcc.Graph(
                id="da_bar",
                style={"height": "75vh"},
                config=lc.tool_config,
            ),
            md=12,
        ),
    ]
)


# Container to put the reference row together
references = dbc.Row(
    [
        dbc.Col(
            html.Div(deacot_reference_card),
            md=6,
        ),
        dbc.Col(
            html.Div(da_reference_card),
            md=6,
        ),
    ]
)


####################################################
# Layout Creation Section
####################################################
main_page = html.Div(
    [
        html.Hr(),
        html.H5("Futures Market Comparison and Analysis", style=TEXT_STYLE),
        html.Hr(),
        future_select,
        html.Hr(),
        info_bar,
        html.Hr(),
        sentiment_direction,
        html.Hr(),
        da_postiions,
        html.Hr(),
        da_3d_positions,
        html.Hr(),
        da_pos_snap,
        html.Hr(),
        da_diffs,
        html.Hr(),
    ],
    style=CONTENT_STYLE,
)

#############################################################################
# Application parameters
#############################################################################
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.CYBORG],
)
app.config.suppress_callback_exceptions = True
app.title = "CFTC Data Analysis"
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)

# Multi-page selector callback - not really used, but left in for future use
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    # Left in because I'm not sure if this will be a muli-page app at some point

    # if pathname == "/market-sentiment":
    #     return volumes
    # else:
    return main_page


####################################################
#  Callbacks - charts
####################################################

# Sentiment charts
@app.callback(
    dash.dependencies.Output("deacot_sent", "figure"),
    [dash.dependencies.Input("future", "value")],
)
def deacot_sentiment(future1):
    df1 = bl.df_deacot[bl.df_deacot["Exchange"] == future1]
    df1.set_index("Date", inplace=True)

    arr = df1["commodity"].unique()
    asset = arr[0]

    fig = sf.make_sentiment_chart(df1, asset)
    return fig


@app.callback(
    dash.dependencies.Output("da_sent", "figure"),
    [dash.dependencies.Input("future", "value")],
)
def deacot_sentiment(future1):
    df1 = bl.df_da[bl.df_da["Exchange"] == future1]
    df1.set_index("Date", inplace=True)

    arr = df1["commodity"].unique()
    asset = arr[0]

    fig = sf.make_chart_DA(df1, asset, "Contracts")
    return fig


# Positions Charts
@app.callback(
    dash.dependencies.Output("da_pos_all", "figure"),
    [dash.dependencies.Input("future", "value")],
)
def deacot_sentiment(future1):
    df1 = bl.df_da[bl.df_da["Exchange"] == future1]
    df1.set_index("Date", inplace=True)

    arr = df1["commodity"].unique()
    asset = arr[0]

    fig = sf.make_net_DA_pos(df1, asset, "Contracts")
    return fig


@app.callback(
    dash.dependencies.Output("da_pos_pct", "figure"),
    [dash.dependencies.Input("future", "value")],
)
def deacot_sentiment(future1):
    df1 = bl.df_da[bl.df_da["Exchange"] == future1]
    df1.set_index("Date", inplace=True)

    arr = df1["commodity"].unique()
    asset = arr[0]

    fig = sf.make_net_DA(df1, asset, "Contracts")
    return fig


# 3d postiion chart
@app.callback(
    dash.dependencies.Output("da_3d_net", "figure"),
    [dash.dependencies.Input("future", "value")],
)
def deacot_sentiment(future1):
    df1 = bl.df_da[bl.df_da["Exchange"] == future1]
    df1.set_index("Date", inplace=True)

    arr = df1["commodity"].unique()
    asset = arr[0]

    fig = sf.da_3d_surface(df1, asset)
    return fig


# Week-over-week diffs in positions charts
@app.callback(
    dash.dependencies.Output("da_diff_all", "figure"),
    [dash.dependencies.Input("future", "value")],
)
def deacot_sentiment(future1):
    df1 = bl.df_da[bl.df_da["Exchange"] == future1]
    df1.set_index("Date", inplace=True)

    arr = df1["commodity"].unique()
    asset = arr[0]
    df = df1.iloc[-2:]

    fig = sf.make_diff_barchart_DA_actual(df, asset, "Contracts")
    return fig


@app.callback(
    dash.dependencies.Output("da_diff_pct", "figure"),
    [dash.dependencies.Input("future", "value")],
)
def deacot_sentiment(future1):
    df1 = bl.df_da[bl.df_da["Exchange"] == future1]
    df1.set_index("Date", inplace=True)

    arr = df1["commodity"].unique()
    asset = arr[0]
    df = df1.iloc[-2:]
    fig = sf.make_diff_barchart_DA(df, asset, "Contracts")
    return fig


# Total position breakdown chart
@app.callback(
    dash.dependencies.Output("da_bar", "figure"),
    [dash.dependencies.Input("future", "value")],
)
def deacot_sentiment(future1):
    df1 = bl.df_da[bl.df_da["Exchange"] == future1]
    df1.set_index("Date", inplace=True)

    arr = df1["commodity"].unique()
    asset = arr[0]
    df = df1.iloc[-1:]

    fig = sf.make_barchart_DA(df, asset, "Contracts")
    return fig


###################################################
# Summary Block
###################################################
@app.callback(
    dash.dependencies.Output("summary", "children"),
    [dash.dependencies.Input("future", "value")],
)
def dashboard_summary_numbers(future1):
    # Grab some values from the most recent DA datafame
    df1 = bl.df_da[bl.df_da["Exchange"] == future1]
    df1.set_index("Date", inplace=True)

    # I only care about the most recent row so pull it
    #  It makes reference easier further down.
    df = df1.iloc[-1:]

    # Return the entire structured block
    return html.Div(
        dbc.Row(
            [
                dbc.Col(
                    dbc.Alert(
                        [
                            html.H6("Latest Date: "),
                            html.H6(df.index),
                        ],
                        color="light",
                    ),
                    md=2,
                ),
                dbc.Col(
                    dbc.Alert(
                        [
                            html.H6("Open Interest: "),
                            html.H6(df.Open_Interest),
                        ],
                        color="success",
                    ),
                    md=2,
                ),
                dbc.Col(
                    dbc.Alert(
                        [
                            html.H6("Total Reporting Long: "),
                            html.H6(df.total_report_long_all),
                        ],
                        color="primary",
                    ),
                    md=2,
                ),
                dbc.Col(
                    dbc.Alert(
                        [
                            html.H6("Total Reporting Short: "),
                            html.H6(df.total_report_short_all),
                        ],
                        color="warning",
                    ),
                    md=2,
                ),
                dbc.Col(
                    dbc.Alert(
                        [
                            html.H6("Total Non-Reporting Long: "),
                            html.H6(df.nonreport_long_all),
                        ],
                        color="primary",
                    ),
                    md=2,
                ),
                dbc.Col(
                    dbc.Alert(
                        [
                            html.H6("Total Non-Reporting Short: "),
                            html.H6(df.nonreport_short_all),
                        ],
                        color="warning",
                    ),
                    md=2,
                ),
            ]
        )
    )


###################################################
# Server Run
###################################################
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050, dev_tools_hot_reload=True)
