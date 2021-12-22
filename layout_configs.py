"""
Layout Configs for setting up chart behavior
"""
import plotly.graph_objects as go

###########################################
# Utilitiy Layouts
###########################################
layout = go.Layout(
    template="plotly_dark",
    # plot_bgcolor="#FFFFFF",
    hovermode="x",
    hoverdistance=100,  # Distance to show hover label of data point
    spikedistance=1000,  # Distance to show spike
    xaxis=dict(
        title="time",
        linecolor="#BCCCDC",
        showspikes=True,
        spikesnap="cursor",
        spikethickness=1,
        spikedash="dot",
        spikecolor="#999999",
        spikemode="across",
    ),
    yaxis=dict(
        title="price",
        linecolor="#BCCCDC",
        tickformat=".2%",
        showspikes=True,
        spikesnap="cursor",
        spikethickness=1,
        spikedash="dot",
        spikecolor="#999999",
        spikemode="across",
    ),
)

layout_simple = go.Layout(
    template="plotly_dark",
    # plot_bgcolor="#FFFFFF",
    hovermode="x",
    hoverdistance=100,  # Distance to show hover label of data point
    spikedistance=1000,  # Distance to show spike
    xaxis=dict(
        showgrid=True,
        title="time",
        # linecolor="#000",
        linecolor="#BCCCDC",
        showspikes=True,
        spikesnap="cursor",
        spikethickness=1,
        spikedash="dot",
        spikecolor="#999999",
        spikemode="across",
    ),
    yaxis=dict(
        showgrid=True,
        title="price",
        # linecolor="#000",
        linecolor="#BCCCDC",
        showspikes=True,
        spikesnap="cursor",
        spikethickness=1,
        spikedash="dot",
        spikecolor="#999999",
        spikemode="across",
    ),
)

layout_bars = go.Layout(
    template="plotly_dark",
    # plot_bgcolor="#FFFFFF",
    xaxis=dict(title=""),
    yaxis=dict(
        title="",
    ),
)

layout_vertical = go.Layout(
    template="plotly_dark",
    # plot_bgcolor="#FFFFFF",
    hovermode="y",
    hoverdistance=100,  # Distance to show hover label of data point
    xaxis=dict(
        title="time",
        linecolor="#BCCCDC",
        showspikes=True,
        spikesnap="cursor",
        spikethickness=1,
        spikedash="dot",
        spikecolor="#999999",
        spikemode="across",
    ),
    yaxis=dict(
        title="price",
        linecolor="#BCCCDC",
        showspikes=True,
        spikesnap="cursor",
        spikethickness=1,
        spikedash="dot",
        spikecolor="#999999",
        spikemode="across",
    ),
)

#############################################################################
# Drawing tools and widget removal
#############################################################################
tool_config = {
    "modeBarButtonsToAdd": [
        "drawline",
        "drawopenpath",
        "drawclosedpath",
        "drawcircle",
        "drawrect",
        "eraseshape",
        "hoverclosest",
        "hovercompare",
    ],
    "modeBarButtonsToRemove": [
        "zoom2d",
        "pan2d",
        "select2d",
        "lasso2d",
        "zoomIn2d",
        "zoomOut2d",
        "autoScale2d",
    ],
    "showTips": False,
    "displaylogo": False,
}
