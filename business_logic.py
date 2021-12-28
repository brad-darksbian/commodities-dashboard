"""
    This files does a lot of the dataframe work and larger data functions
    Mostly this is data retrieval, organization, and making sure everything
    is ready to be called by the main app via call backs.

    This is called by main.py and in turn calls support functions when needed

"""
import pandas as pd
import numpy as np
import plotly.io as pio
import support_functions as sf

pd.options.plotting.backend = "plotly"
pio.templates.default = "plotly_dark"

# Make sure we have data
# This will check to see if a file exists and if not gets one
#  This also checks the data freshness
sf.get_reports()

# Get the data frames to work with
# DEACOT report
df_deacot = sf.aggregate_reports("deacot")
df_deacot = sf.deacot_process(df_deacot)

# Disambiguation report
df_da = sf.aggregate_reports("da")
df_da = sf.DA_process(df_da)

####################################################
# Generate the commodities list - use the DA listing
####################################################
da_list = df_da["Exchange"].unique()
da_list = np.sort(da_list)

#############################################################################
# Backstop
#############################################################################
if __name__ == "__main__":
    print("business logic should not be run like this")
