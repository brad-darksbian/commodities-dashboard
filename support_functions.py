"""
    This files contains all the major functions

    We have functions for getting the reports and processing as well as
    generating the actual charts.

    This file is called by both the main app as well as the business logic

"""
import zipfile
import urllib.request
import shutil
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import layout_configs as lc
import plotly.graph_objects as go

#############################################################################
# Configuration - Change these to suit
#############################################################################
# Path location
base_path = "/tmp/"

# Set a list of years to retrieve for analysis
# Data is available from 2006 until current
# *Note* Adding more years will considerably slow down the dashboard
analysis_years = [
    "2022",
    "2021",
    "2020",
]

# Set the base URL for the CFTC repository - should not need to be changed
base_url = "https://www.cftc.gov/files/dea/history/"


#############################################################################
# Data Retreival and Handling
#############################################################################
# Function to retrieve reports
def get_COT(url, file_name):

    with urllib.request.urlopen(url) as response, open(file_name, "wb") as out_file:
        shutil.copyfileobj(response, out_file)

    with zipfile.ZipFile(file_name) as zf:
        zf.extractall()


# Function to make sure things are fresh for data
def process_reports(report, current_date, file_path, file_name, url_path):
    if report == "Deacot":
        src_file = "annual.txt"
    else:
        src_file = "f_year.txt"

    if os.path.exists(file_path):
        filetime = datetime.fromtimestamp(os.path.getctime(file_path))
        if (filetime - timedelta(days=7)) <= current_date:
            print(report + " file exists and is current - using cached data")
        else:
            get_COT(
                url_path,
                file_name,
            )
            os.rename(src_file, file_path)
            print(report + " file is stale - getting fresh copy")
    else:
        print(report + " file does not exist - getting fresh copy")
        get_COT(
            url_path,
            file_name,
        )
        os.rename(src_file, file_path)


def get_reports():
    freshness_date = datetime.now() - timedelta(days=7)

    # Loop through the years list for the deacot report
    for i in analysis_years:
        # Set up basic path constructs
        url_path = base_url + "deacot" + i + ".zip"
        file_name = "deacot" + i + ".zip"
        file_path = base_path + "deacot" + i + ".txt"

        process_reports("Deacot", freshness_date, file_path, file_name, url_path)

    # Loop again for the DA report
    for i in analysis_years:
        url_path = base_url + "fut_disagg_txt_" + i + ".zip"
        file_name = "fut_disagg_txt_" + i + ".zip"
        file_path = base_path + "deacot_DA_" + i + ".txt"

        process_reports("DA", freshness_date, file_path, file_name, url_path)


# function to aggregate all the reports into one dataframe for each report type
def aggregate_reports(report_name):
    if report_name == "deacot":
        file_prefix = "deacot"
    else:
        file_prefix = "deacot_DA_"
    df = pd.DataFrame()
    for i in analysis_years:
        file_path = base_path + file_prefix + i + ".txt"
        df1 = pd.read_csv(file_path, na_values="x", low_memory=False)
        df = df.append(
            df1,
            ignore_index=True,
        )
    return df


# Process raw reports (DEACOT)
def deacot_process(df):
    df.rename(
        {
            "Market and Exchange Names": "Exchange",
            "As of Date in Form YYYY-MM-DD": "Date",
            "Open Interest (All)": "Open_Interest",
            "Noncommercial Positions-Short (All)": "Funds_Short_Positions",
            "Noncommercial Positions-Long (All)": "Funds_Long_Positions",
            "Commercial Positions-Long (All)": "Speculators_Long_Positions",
            "Commercial Positions-Short (All)": "Speculators_Short_Positions",
            "Nonreportable Positions-Long (All)": "NonReporting_Long_Positions",
            "Nonreportable Positions-Short (All)": "NonReporting_Short_Positions",
            "% of OI-Noncommercial-Long (All)": "funds_long_pct",
            "% of OI-Noncommercial-Short (All)": "funds_short_pct",
            "% of OI-Commercial-Long (All)": "dealers_long_pct",
            "% of OI-Commercial-Short (All)": "dealers_short_pct",
            "% of OI-Nonreportable-Long (All)": "nonreporting_long_pct",
            "% of OI-Nonreportable-Short (All)": "nonreporting_short_pct",
        },
        axis=1,
        inplace=True,
    )
    df = df.sort_values("Date")
    # Add a few fields for later use:
    # Set it equal to contracts and then switch it up later if needed
    df["oi_ounces"] = df.Open_Interest * 1
    df["fsp_ounces"] = df.Funds_Short_Positions * 1
    df["flp_ounces"] = df.Funds_Long_Positions * 1
    df["ssp_ounces"] = df.Speculators_Short_Positions * 1
    df["slp_ounces"] = df.Speculators_Long_Positions * 1
    df["nrsp_ounces"] = df.NonReporting_Short_Positions * 1
    df["nrlp_ounces"] = df.NonReporting_Long_Positions * 1
    df["total_long"] = df.flp_ounces + df.slp_ounces + df.nrlp_ounces
    df["total_short"] = df.fsp_ounces + df.ssp_ounces + df.nrsp_ounces
    df["oi_balance"] = df.oi_ounces - df.total_long

    # Add a couple calculations we need
    df["dealers_balance"] = 1 - (df["dealers_long_pct"] + df["dealers_short_pct"])
    df["funds_balance"] = 1 - (df["funds_long_pct"] + df["funds_short_pct"])
    # break out the exchange and commodity into new columns
    df["commodity"] = df["Exchange"].str.split(" - ", expand=True)[0]
    df["market"] = df["Exchange"].str.split(" - ", expand=True)[1]
    return df


# Process raw reports (DEACOT)
def DA_process(df):
    df.rename(
        {
            "Market_and_Exchange_Names": "Exchange",
            "Report_Date_as_YYYY-MM-DD": "Date",
            "Open_Interest_All": "Open_Interest",
            "Prod_Merc_Positions_Long_All": "prod_long_all",
            "Prod_Merc_Positions_Short_All": "prod_short_all",
            "Swap_Positions_Long_All": "swap_long_all",
            "Swap__Positions_Short_All": "swap_short_all",
            "Swap__Positions_Spread_All": "swap_spread_all",
            "M_Money_Positions_Long_All": "money_long_all",
            "M_Money_Positions_Short_All": "money_short_all",
            "M_Money_Positions_Spread_All": "money_spread_all",
            "Other_Rept_Positions_Long_All": "other_long_all",
            "Other_Rept_Positions_Short_All": "other_short_all",
            "Other_Rept_Positions_Spread_All": "other_spread_all",
            "Tot_Rept_Positions_Long_All": "total_report_long_all",
            "Tot_Rept_Positions_Short_All": "total_report_short_all",
            "NonRept_Positions_Long_All": "nonreport_long_all",
            "NonRept_Positions_Short_All": "nonreport_short_all",
            "Pct_of_Open_Interest_All": "open_interest_pct",
            "Pct_of_OI_Prod_Merc_Long_All": "prod_long_pct",
            "Pct_of_OI_Prod_Merc_Short_All": "prod_short_pct",
            "Pct_of_OI_Swap_Long_All": "swap_long_pct",
            "Pct_of_OI_Swap_Short_All": "swap_short_pct",
            "Pct_of_OI_Swap_Spread_All": "swap_spread_pct",
            "Pct_of_OI_M_Money_Long_All": "money_long_pct",
            "Pct_of_OI_M_Money_Short_All": "money_short_pct",
            "Pct_of_OI_M_Money_Spread_All": "money_spread_pct",
            "Pct_of_OI_Other_Rept_Long_All": "other_long_pct",
            "Pct_of_OI_Other_Rept_Short_All": "other_short_pct",
            "Pct_of_OI_Other_Rept_Spread_All": "other_spread_pct",
            "Pct_of_OI_Tot_Rept_Long_All": "total_report_long_pct",
            "Pct_of_OI_Tot_Rept_Short_All": "total_report_short_pct",
            "Pct_of_OI_NonRept_Long_All": "nonreport_long_pct",
            "Pct_of_OI_NonRept_Short_All": "nonreport_short_pct",
        },
        axis=1,
        inplace=True,
    )
    df = df.sort_values("Date")
    # break out the exchange and commodity into new columns
    df["commodity"] = df["Exchange"].str.split(" - ", expand=True)[0]
    df["market"] = df["Exchange"].str.split(" - ", expand=True)[1]
    # add columns to deal with date format for rangeslider
    df["date_begin"] = df["Date"].min()
    df["date_end"] = df["Date"].values.astype("datetime64[D]")
    # Use numpy function to set the week number based on Tuesday when reports
    # are released by the CFTC
    df["week_number"] = np.busday_count(
        df["date_begin"].values.astype("M8[D]"),
        df["date_end"].values.astype("M8[D]"),
        weekmask="Tue",
    )

    return df


#############################################################################
# Charts
#############################################################################
# Create DEACOT position chart - not currently used
def make_chart(df, commodity, units):
    fig = go.Figure(layout=lc.layout)

    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.oi_ounces,
            name="Open Interest",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.flp_ounces,
            name="Funds Long",
            line_width=1,
            visible="legendonly",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.fsp_ounces,
            name="Funds Short",
            line_width=1,
            visible="legendonly",
        )
    )

    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.slp_ounces,
            name="Speculators Long",
            visible="legendonly",
            line_width=1,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.ssp_ounces,
            name="Speculators Short",
            visible="legendonly",
            line_width=1,
        )
    )

    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.nrlp_ounces,
            name="Non-Reporting Long",
            visible="legendonly",
            line_width=1,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.nrsp_ounces,
            name="Non-Reporting Short",
            visible="legendonly",
            line_width=1,
        )
    )

    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.total_long,
            name="Total Long",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.total_short,
            name="Total Short",
            line_width=2,
        )
    )

    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.oi_balance,
            name="Open Interest Remain",
            line_width=2,
            fill="tozeroy",
        )
    )

    fig.update_layout(
        newshape=dict(line_color="yellow"),
        title=commodity + " Positions of Funds, Speculators, and Others (DEACOT)",
        xaxis_title="",
        yaxis_title=units,
    )
    # fig.show(config=lc.tool_config)
    return fig


# Create DEACOT sentiment chart
def make_sentiment_chart(df, commodity):
    fig = go.Figure(layout=lc.layout_simple)
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.funds_long_pct,
            name="Funds Long",
            showlegend=False,
            mode="lines",
            line_width=1,
            line_color="fuchsia",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.funds_short_pct,
            name="Funds Short",
            showlegend=False,
            mode="lines",
            line_width=2,
            line_dash="dash",
            line_color="fuchsia",
            fill="tonexty",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.dealers_long_pct,
            name="Spec. Long",
            showlegend=False,
            mode="lines",
            line_width=1,
            line_color="silver",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.dealers_short_pct,
            name="Spec. Short",
            showlegend=False,
            mode="lines",
            line_width=2,
            line_dash="dash",
            line_color="silver",
            fill="tonexty",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.nonreporting_long_pct,
            name="NonRep Long",
            showlegend=False,
            mode="lines",
            line_width=1,
            line_color="aqua",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.nonreporting_short_pct,
            name="NonRep Short",
            showlegend=False,
            mode="lines",
            line_width=2,
            line_dash="dash",
            line_color="aqua",
            fill="tonexty",
        )
    )

    fig.update_layout(
        newshape=dict(line_color="yellow"),
        title=commodity + " Market Sentiment - Speculators, Funds, Others (DEACOT)",
        xaxis_title="",
        yaxis_title="Percent",
    )
    # fig.show(config=lc.tool_config)
    return fig


# Create DA position chart
def make_chart_DA(df, commodity, units):
    fig = go.Figure(layout=lc.layout_simple)

    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.Open_Interest,
            name="Open Interest",
            line_width=2,
            # fill="tonexty",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.total_report_long_all + df.nonreport_long_all,
            name="Total Long",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.total_report_short_all + df.nonreport_short_all,
            name="Total Short",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.total_report_long_all,
            name="Total Reporting Long",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.total_report_short_all,
            name="Total Reporting Short",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.prod_long_all,
            name="Producer Long",
            visible="legendonly",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.prod_short_all,
            name="Producer Short",
            visible="legendonly",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.swap_long_all,
            name="Swap Long",
            visible="legendonly",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.swap_short_all,
            name="Swap Short",
            visible="legendonly",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.swap_spread_all,
            name="Swap Spread",
            visible="legendonly",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.money_long_all,
            name="Money Manager Long",
            visible="legendonly",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.money_short_all,
            name="Money Manager Short",
            visible="legendonly",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.money_spread_all,
            name="Money Manager Spread",
            visible="legendonly",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.other_long_all,
            name="Other Long",
            visible="legendonly",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.other_short_all,
            name="Other Short",
            visible="legendonly",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.other_spread_all,
            name="Other Spread",
            visible="legendonly",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.nonreport_long_all,
            name="Non-Reporting Long",
            line_width=2,
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df.nonreport_short_all,
            name="Non-Reporting Short",
            line_width=2,
        )
    )

    fig.update_layout(
        newshape=dict(line_color="yellow"),
        title=commodity + " Disaggregated Report of all positions (DA)",
        xaxis_title="",
        yaxis_title=units,
    )
    # fig.show(config=lc.tool_config)
    return fig


# Create DA barchart for current week positions
def make_barchart_DA(df, commodity, spare):
    class_long = [
        "producer",
        "swap",
        "money manager",
        "other",
        "total reporting",
        "total non-reporting",
        "open interest",
    ]
    class_short = [
        "producer",
        "swap",
        "money manager",
        "other",
        "total reporting",
        "total non-reporting",
        "open interest",
    ]
    class_spread = [
        "swap",
        "money manager",
        "other",
        "total reporting",
    ]

    longs = [
        df.iloc[0]["prod_long_pct"],
        df.iloc[0]["swap_long_pct"],
        df.iloc[0]["money_long_pct"],
        df.iloc[0]["other_long_pct"],
        df.iloc[0]["total_report_long_pct"],
        df.iloc[0]["nonreport_long_pct"],
        df.iloc[0]["total_report_long_pct"] + df.iloc[0]["nonreport_long_pct"],
    ]
    shorts = [
        df.iloc[0]["prod_short_pct"],
        df.iloc[0]["swap_short_pct"],
        df.iloc[0]["money_short_pct"],
        df.iloc[0]["other_short_pct"],
        df.iloc[0]["total_report_short_pct"],
        df.iloc[0]["nonreport_short_pct"],
        df.iloc[0]["total_report_short_pct"] + df.iloc[0]["nonreport_short_pct"],
    ]
    spreads = [
        df.iloc[0]["swap_spread_pct"],
        df.iloc[0]["money_spread_pct"],
        df.iloc[0]["other_spread_pct"],
        df.iloc[0]["swap_spread_pct"]
        + df.iloc[0]["money_spread_pct"]
        + df.iloc[0]["other_spread_pct"],
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                name="Long",
                x=class_long,
                y=longs,
                text=longs,
                textposition="auto",
            ),
            go.Bar(
                name="Short",
                x=class_short,
                y=shorts,
                text=shorts,
                textposition="auto",
            ),
            go.Bar(
                name="Spread",
                x=class_spread,
                y=spreads,
                text=spreads,
                textposition="auto",
            ),
        ]
    )

    fig.update_traces(
        marker_line_width=1, marker_line_color="rgb(192, 192, 192)", opacity=1
    )

    fig.update_layout(
        barmode="group",
        newshape=dict(line_color="yellow"),
        title=commodity + " Disaggregated Report Positions (DA): " + df.index[0],
        xaxis_title="",
        yaxis_title="percent",
    )
    # fig.show(config=lc.tool_config)
    return fig


# Create DA diff barchart for last two weeks (pct)
def make_diff_barchart_DA(df, commodity, spare):
    class_long = [
        "producer",
        "swap",
        "money manager",
        "other",
        "total reporting",
        "total non-reporting",
    ]
    class_short = [
        "producer",
        "swap",
        "money manager",
        "other",
        "total reporting",
        "total non-reporting",
    ]
    class_spread = [
        "swap",
        "money manager",
        "other",
        "total reporting",
    ]

    longs = [
        df.iloc[1]["prod_long_pct"] - df.iloc[0]["prod_long_pct"],
        df.iloc[1]["swap_long_pct"] - df.iloc[0]["swap_long_pct"],
        df.iloc[1]["money_long_pct"] - df.iloc[0]["money_long_pct"],
        df.iloc[1]["other_long_pct"] - df.iloc[0]["other_long_pct"],
        df.iloc[1]["total_report_long_pct"] - df.iloc[0]["total_report_long_pct"],
        df.iloc[1]["nonreport_long_pct"] - df.iloc[0]["nonreport_long_pct"],
    ]
    shorts = [
        df.iloc[1]["prod_short_pct"] - df.iloc[0]["prod_short_pct"],
        df.iloc[1]["swap_short_pct"] - df.iloc[0]["swap_short_pct"],
        df.iloc[1]["money_short_pct"] - df.iloc[0]["money_short_pct"],
        df.iloc[1]["other_short_pct"] - df.iloc[0]["other_short_pct"],
        df.iloc[1]["total_report_short_pct"] - df.iloc[0]["total_report_short_pct"],
        df.iloc[1]["nonreport_short_pct"] - df.iloc[0]["nonreport_short_pct"],
    ]
    spreads = [
        df.iloc[1]["swap_spread_pct"] - df.iloc[0]["swap_spread_pct"],
        df.iloc[1]["money_spread_pct"] - df.iloc[0]["money_spread_pct"],
        df.iloc[1]["other_spread_pct"] - df.iloc[0]["other_spread_pct"],
        (
            df.iloc[1]["swap_spread_pct"]
            + df.iloc[1]["money_spread_pct"]
            + df.iloc[1]["other_spread_pct"]
            - (
                df.iloc[0]["swap_spread_pct"]
                + df.iloc[0]["money_spread_pct"]
                + df.iloc[0]["other_spread_pct"]
            )
        ),
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                name="Long",
                x=class_long,
                y=longs,
                text=longs,
                textposition="auto",
            ),
            go.Bar(
                name="Short",
                x=class_short,
                y=shorts,
                text=shorts,
                textposition="auto",
            ),
            go.Bar(
                name="Spread",
                x=class_spread,
                y=spreads,
                text=spreads,
                textposition="auto",
            ),
        ]
    )

    fig.update_traces(
        marker_line_width=1,
        marker_line_color="rgb(192, 192, 192)",
        opacity=1,
        texttemplate="%{text:.2f}",
    )

    fig.update_layout(
        barmode="group",
        newshape=dict(line_color="yellow"),
        title=commodity
        + " Disaggregated Report Positions Percentage<br>(week-over-week change) (DA): "
        + df.index[1]
        + " - "
        + df.index[0],
        xaxis_title="",
        yaxis_title="percent",
    )
    # fig.show(config=lc.tool_config)
    return fig


# Create DA net position chart (pct)
def make_net_DA(df, commodity, units):
    fig = go.Figure(layout=lc.layout_simple)

    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df["prod_long_pct"] - df["prod_short_pct"],
            name="Producer Net",
            # visible="legendonly",
            line_width=2,
            fill="tozeroy",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df["swap_long_pct"] - df["swap_short_pct"],
            name="Swap Net",
            # visible="legendonly",
            line_width=2,
            fill="tozeroy",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df["money_long_pct"] - df["money_short_pct"],
            name="Money Manager Net",
            # visible="legendonly",
            line_width=2,
            fill="tozeroy",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df["other_long_pct"] - df["other_short_pct"],
            name="Other Net",
            # visible="legendonly",
            line_width=2,
            fill="tozeroy",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df["nonreport_long_pct"] - df["nonreport_short_pct"],
            name="Non-Reporting Net",
            line_width=2,
            fill="tozeroy",
        )
    )
    fig.add_hline(y=0, line_width=1, line_color="white")

    fig.update_layout(
        newshape=dict(line_color="yellow"),
        title=commodity + " Disaggregated Report Net Percent Positions (DA)",
        xaxis_title="",
        yaxis_title="Net Percent Participation",
    )
    # fig.show(config=lc.tool_config)
    return fig


# Create DA net position chart (contracts)
def make_net_DA_pos(df, commodity, units):
    fig = go.Figure(layout=lc.layout_simple)

    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df["prod_long_all"] - df["prod_short_all"],
            name="Producer Net",
            # visible="legendonly",
            line_width=2,
            fill="tozeroy",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df["swap_long_all"] - df["swap_short_all"],
            name="Swap Net",
            # visible="legendonly",
            line_width=2,
            fill="tozeroy",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df["money_long_all"] - df["money_short_all"],
            name="Money Manager Net",
            # visible="legendonly",
            line_width=2,
            fill="tozeroy",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df["other_long_all"] - df["other_short_all"],
            name="Other Net",
            # visible="legendonly",
            line_width=2,
            fill="tozeroy",
        )
    )
    fig.add_traces(
        go.Scatter(
            x=df.index,
            y=df["nonreport_long_all"] - df["nonreport_short_all"],
            name="Non-Reporting Net",
            line_width=2,
            fill="tozeroy",
        )
    )
    fig.add_hline(y=0, line_width=1, line_color="white")

    fig.update_layout(
        newshape=dict(line_color="yellow"),
        title=commodity + " Disaggregated Report Net Positions (DA)",
        xaxis_title="",
        yaxis_title="Net Orders",
    )
    # fig.show(config=lc.tool_config)
    return fig


# Create DA diff barchart for last two weeks (contracts)
def make_diff_barchart_DA_actual(df, commodity, spare):
    class_long = [
        "producer",
        "swap",
        "money manager",
        "other",
        "total reporting",
        "total non-reporting",
        "open interest",
    ]
    class_short = [
        "producer",
        "swap",
        "money manager",
        "other",
        "total reporting",
        "total non-reporting",
        "open interest",
    ]
    class_spread = [
        "swap",
        "money manager",
        "other",
        "total reporting",
    ]

    longs = [
        df.iloc[1]["prod_long_all"] - df.iloc[0]["prod_long_all"],
        df.iloc[1]["swap_long_all"] - df.iloc[0]["swap_long_all"],
        df.iloc[1]["money_long_all"] - df.iloc[0]["money_long_all"],
        df.iloc[1]["other_long_all"] - df.iloc[0]["other_long_all"],
        df.iloc[1]["total_report_long_all"] - df.iloc[0]["total_report_long_all"],
        df.iloc[1]["nonreport_long_all"] - df.iloc[0]["nonreport_long_all"],
        (df.iloc[1]["total_report_long_all"] + df.iloc[1]["nonreport_long_all"])
        - (df.iloc[0]["total_report_long_all"] + df.iloc[0]["nonreport_long_all"]),
    ]
    shorts = [
        df.iloc[1]["prod_short_all"] - df.iloc[0]["prod_short_all"],
        df.iloc[1]["swap_short_all"] - df.iloc[0]["swap_short_all"],
        df.iloc[1]["money_short_all"] - df.iloc[0]["money_short_all"],
        df.iloc[1]["other_short_all"] - df.iloc[0]["other_short_all"],
        df.iloc[1]["total_report_short_all"] - df.iloc[0]["total_report_short_all"],
        df.iloc[1]["nonreport_short_all"] - df.iloc[0]["nonreport_short_all"],
        (df.iloc[1]["total_report_short_all"] + df.iloc[1]["nonreport_short_all"])
        - (df.iloc[0]["total_report_short_all"] + df.iloc[0]["nonreport_short_all"]),
    ]
    spreads = [
        df.iloc[1]["swap_spread_all"] - df.iloc[0]["swap_spread_all"],
        df.iloc[1]["money_spread_all"] - df.iloc[0]["money_spread_all"],
        df.iloc[1]["other_spread_all"] - df.iloc[0]["other_spread_all"],
        (
            df.iloc[1]["swap_spread_all"]
            + df.iloc[1]["money_spread_all"]
            + df.iloc[1]["other_spread_all"]
            - (
                df.iloc[0]["swap_spread_all"]
                + df.iloc[0]["money_spread_all"]
                + df.iloc[0]["other_spread_all"]
            )
        ),
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                name="Long",
                x=class_long,
                y=longs,
                text=longs,
                textposition="auto",
            ),
            go.Bar(
                name="Short",
                x=class_short,
                y=shorts,
                text=shorts,
                textposition="auto",
            ),
            go.Bar(
                name="Spread",
                x=class_spread,
                y=spreads,
                text=spreads,
                textposition="auto",
            ),
        ]
    )

    fig.update_traces(
        marker_line_width=1,
        marker_line_color="rgb(192, 192, 192)",
        opacity=1,
    )

    fig.update_layout(
        barmode="group",
        newshape=dict(line_color="yellow"),
        title=commodity
        + " Disaggregated Report Contract Positions<br>(week-over-week change) (DA): "
        + df.index[1]
        + " - "
        + df.index[0],
        xaxis_title="",
        yaxis_title="Contracts",
    )
    # fig.show(config=lc.tool_config)
    return fig


def da_3d_surface(df, commodity):
    # This is an experiment in charting the DA for a commodity in 3d
    # We'll use the net values to give a postive-negative view
    y_data = [
        "Pr - Net",
        "NR - Net",
        "SD - Net",
        "MM - Net",
        "Ot - Net",
    ]

    z_data = [
        df["prod_long_all"] - df["prod_short_all"],
        df["nonreport_long_all"] - df["nonreport_short_all"],
        df["swap_long_all"] - df["swap_short_all"],
        df["money_long_all"] - df["money_short_all"],
        df["other_long_all"] - df["other_short_all"],
    ]

    fig = go.Figure(
        go.Surface(
            contours={
                "z": {
                    "show": True,
                    "start": 0.5,
                    "end": 0.8,
                    "size": 0.05,
                    "width": 2,
                    "color": "black",
                },
            },
            x=df.index,
            y=y_data,
            z=z_data,
        )
    )
    fig.update_layout(
        title=commodity
        + " Disaggregated Report Net Positions<br>(DA): "
        + df.index.values[0]
        + " - "
        + df.index.values[-1],
        scene={
            "xaxis_title": "",
            "yaxis_title": "",
            "zaxis_title": "",
            "camera_eye": {"x": 1, "y": -1, "z": 0.75},
            "aspectratio": {"x": 0.75, "y": 0.75, "z": 0.5},
        },
        margin=dict(
            b=10,
            l=10,
            r=10,
        ),
    )
    # fig.show()
    return fig


def da_3d_surface_all(df, commodity):
    # This is a chart for all positions
    # Comparatively, it gives a better sense of movement
    # Downside is the Y axis arrangement

    # Used abbreviations for display consistency
    y_data = [
        "Pr - S",
        "SD - S",
        "MM - S",
        "NR - S",
        "Ot - S",
        "Pr - L",
        "Ot - L",
        "NR - L",
        "SD - L",
        "MM - L",
    ]

    # changed the sign on short positions to create a better logical flow
    z_data = [
        df["prod_short_all"] * -1,
        df["swap_short_all"] * -1,
        df["money_short_all"] * -1,
        df["nonreport_short_all"] * -1,
        df["other_short_all"] * -1,
        df["prod_long_all"],
        df["other_long_all"],
        df["nonreport_long_all"],
        df["swap_long_all"],
        df["money_long_all"],
    ]

    fig = go.Figure(
        go.Surface(
            contours={
                "z": {
                    "show": True,
                    "start": 0.5,
                    "end": 0.8,
                    "size": 0.05,
                    "width": 2,
                    "color": "black",
                },
            },
            x=df.index,
            y=y_data,
            z=z_data,
        )
    )

    # Explicitly defined paramters to allow all y-axis labels to display
    fig.update_layout(
        title=commodity
        + " Disaggregated Report Actual Positions<br>(DA): "
        + df.index.values[0]
        + " - "
        + df.index.values[-1],
        scene=dict(
            xaxis_title="",
            yaxis=dict(
                title="",
                nticks=10,
                ticktext=y_data,
            ),
            zaxis_title="",
            camera_eye_x=1,
            camera_eye_y=-1,
            camera_eye_z=0.75,
            aspectratio_x=0.75,
            aspectratio_y=0.75,
            aspectratio_z=0.5,
        ),
        margin=dict(
            b=10,
            l=10,
            r=10,
        ),
    )
    # fig.show()
    return fig


#############################################################################
# Backstop
#############################################################################
if __name__ == "__main__":
    print("Support Functions has nothing to run directly")
