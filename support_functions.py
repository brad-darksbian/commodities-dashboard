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
import layout_configs as lc
import plotly.graph_objects as go


# Configure file paths for both reports
# DO NOT CHANGE THE FILE NAME ITSELF - ONLY THE PATH
deacot_file = "/tmp/deacot2021.txt"
da_file = "/tmp/deacot_DA_2021.txt"


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
def get_reports():
    freshness_date = datetime.now() - timedelta(days=7)
    if os.path.exists(deacot_file):
        filetime = datetime.fromtimestamp(os.path.getctime(deacot_file))
        if (filetime - timedelta(days=7)) <= freshness_date:
            print("Deacot file exists and is current - using cached data")
        else:
            get_COT(
                "https://www.cftc.gov/files/dea/history/deacot2021.zip",
                "deacot2021.zip",
            )
            os.rename(r"annual.txt", deacot_file)
            print("Deacot file is stale - getting fresh copy")
    else:
        print("Deacot file does not exist - getting fresh copy")
        get_COT(
            "https://www.cftc.gov/files/dea/history/deacot2021.zip", "deacot2021.zip"
        )
        os.rename(r"annual.txt", deacot_file)

    if os.path.exists(da_file):
        filetime = datetime.fromtimestamp(os.path.getctime(da_file))
        if (filetime - timedelta(days=7)) <= freshness_date:
            print(
                "Disaggregation report file exists and is current - using cached data"
            )
        else:
            get_COT(
                "https://www.cftc.gov/files/dea/history/fut_disagg_txt_2021.zip",
                "fut_disagg_txt_2021.zip",
            )
            os.rename(r"f_year.txt", da_file)
            print("Disaggregation report file is stale - getting fresh copy")
    else:
        print("Disaggregation report file does not exist - getting fresh copy")
        get_COT(
            "https://www.cftc.gov/files/dea/history/fut_disagg_txt_2021.zip",
            "fut_disagg_txt_2021.zip",
        )
        os.rename(r"f_year.txt", da_file)


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
        title=commodity
        + " Disaggregation of Producers, Swaps, Money Managers, Others,<br> and Non-Reporting Participants",
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
        title=commodity
        + " Positions of Producers, Swaps, Money Managers, Others,<br> and Non-Reporting Participants: "
        + df.index[0],
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
        + " Positions of Producers, Swaps, Money Managers, Others,<br> and Non-Reporting Participants (week-over-week change): "
        + df.index[1]
        + " through "
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
        title=commodity
        + " Net Percent Positions of Producers, Swaps, Money Managers, Others,<br> and Non-Reporting Participants (DA)",
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
        title=commodity
        + " Net Positions of Producers, Swaps, Money Managers, Others,<br> and Non-Reporting Participants",
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
        + " Contract Positions of Producers, Swaps, Money Managers, Others,<br> and Non-Reporting Participants (week-over-week change): "
        + df.index[1]
        + " through "
        + df.index[0],
        xaxis_title="",
        yaxis_title="Contracts",
    )
    # fig.show(config=lc.tool_config)
    return fig


#############################################################################
# Backstop
#############################################################################
if __name__ == "__main__":
    print("Support Functions has nothing to run directly")
