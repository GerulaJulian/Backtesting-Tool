"""
router for /sites
"""

import streamlit as st

# Website layout
st.set_page_config(layout="wide")

home = st.Page("sites/home.py", title="Home")
single = st.Page("sites/single.py", title="Einzel Simulation")
compare = st.Page("sites/compare.py", title="Strategien Vergleichen")

sidebar = st.navigation([home, single, compare])
sidebar.run()