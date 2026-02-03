# ============================================
# COMPLETE PETROPHYSICAL ANALYSIS APPLICATION
# Streamlit + Python
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Petrophysical Analysis",
    layout="wide"
)

st.title("🛢️ Complete Petrophysical Analysis Application")

# ============================================
# SIDEBAR – WELL INFORMATION
# ============================================
st.sidebar.header("Well Information")

well_name = st.sidebar.text_input("Well Name", "Well-01")
field_name = st.sidebar.text_input("Field Name", "Field-X")
reservoir_name = st.sidebar.text_input("Reservoir Name", "Reservoir-A")

st.sidebar.divider()

# ============================================
# SIDEBAR – ZONE DEFINITION
# ============================================
st.sidebar.header("Zone Definition")

n_zones = st.sidebar.number_input(
    "Number of Zones",
    min_value=1,
    max_value=10,
    value=3
)

zones = []

for i in range(n_zones):
    st.sidebar.subheader(f"Zone {i+1}")
    zone_name = st.sidebar.text_input("Zone Name", f"Zone_{i+1}", key=f"name{i}")
    top = st.sidebar.number_input("Top Depth", value=1000.0 + i*50, key=f"top{i}")
    base = st.sidebar.number_input("Base Depth", value=1050.0 + i*50, key=f"base{i}")

    zones.append({
        "Zone": zone_name,
        "Top": top,
        "Base": base
    })

zones_df = pd.DataFrame(zones)

# ============================================
# SIDEBAR – PETROPHYSICAL PARAMETERS
# ============================================
st.sidebar.divider()
st.sidebar.header("Petrophysical Parameters")

gr_clean = st.sidebar.number_input("GR Clean", value=30.0)
gr_shale = st.sidebar.number_input("GR Shale", value=120.0)

rho_matrix = st.sidebar.number_input("Matrix Density", value=2.65)
rho_fluid = st.sidebar.number_input("Fluid Density", value=1.0)
rho_shale = st.sidebar.number_input("Shale Density", value=2.4)

a = st.sidebar.number_input("Archie a", value=1.0)
m = st.sidebar.number_input("Archie m", value=2.0)
n = st.sidebar.number_input("Archie n", value=2.0)
rw = st.sidebar.number_input("Rw", value=0.1)

sw_method = st.sidebar.selectbox(
    "Water Saturation Method",
    ["Archie", "Indonesian"]
)

# ============================================
# SIDEBAR – CUTOFFS
# ============================================
st.sidebar.divider()
st.sidebar.header("Net Pay Cutoffs")

vsh_cutoff = st.sidebar.slider("Vsh Cutoff", 0.0, 1.0, 0.4)
phi_cutoff = st.sidebar.slider("Porosity Cutoff", 0.0, 0.4, 0.1)
sw_cutoff = st.sidebar.slider("Sw Cutoff", 0.0, 1.0, 0.6)

# ============================================
# MOCK LOG DATA (Replace with real data later)
# ============================================
depth = np.linspace(950, 1300, 700)

logs = pd.DataFrame({
    "Depth": depth,
    "GR": np.random.uniform(20, 130, len(depth)),
    "RHOB": np.random.uniform(2.1, 2.7, len(depth)),
    "NPHI": np.random.uniform(0.05, 0.35, len(depth)),
    "RT": np.random.uniform(0.2, 200, len(depth))
})

# ============================================
# PETROPHYSICAL FUNCTIONS
# ============================================
def calculate_vsh(gr, gr_clean, gr_shale):
    vsh = (gr - gr_clean) / (gr_shale - gr_clean)
    return np.clip(vsh, 0, 1)

def density_porosity(rhob, rho_ma, rho_fl):
    return (rho_ma - rhob) / (rho_ma - rho_fl)

def total_porosity(phi_d, phi_n):
    return (phi_d + phi_n) / 2

def effective_porosity(phi_t, vsh):
    return phi_t * (1 - vsh)

def sw_archie(rt, phi, rw, a, m, n):
    return ((a * rw) / (rt * (phi ** m))) ** (1 / n)

# ============================================
# CALCULATIONS
# ============================================
logs["Vsh"] = calculate_vsh(logs["GR"], gr_clean, gr_shale)
logs["PHID"] = density_porosity(logs["RHOB"], rho_matrix, rho_fluid)
logs["PHIT"] = total_porosity(logs["PHID"], logs["NPHI"])
logs["PHIE"] = effective_porosity(logs["PHIT"], logs["Vsh"])

logs["Sw"] = sw_archie(
    logs["RT"],
    logs["PHIE"].replace(0, np.nan),
    rw, a, m, n
)

logs["Sw"] = logs["Sw"].clip(0, 1)

# ============================================
# NET PAY FLAG
# ============================================
logs["NetPay"] = (
    (logs["Vsh"] <= vsh_cutoff) &
    (logs["PHIE"] >= phi_cutoff) &
    (logs["Sw"] <= sw_cutoff)
)

# ============================================
# TABS
# ============================================
tab1, tab2, tab3, tab4 = st.tabs(
    ["Input Data", "Calculations", "Plots", "Results Summary"]
)

# ============================================
# TAB 1 – INPUT DATA
# ============================================
with tab1:
    st.subheader("Zone Definition")
    st.dataframe(zones_df, use_container_width=True)

    st.subheader("Raw Logs")
    st.dataframe(logs.head(), use_container_width=True)

# ============================================
# TAB 2 – CALCULATIONS
# ============================================
with tab2:
    st.subheader("Calculated Logs")
    st.dataframe(
        logs[["Depth", "Vsh", "PHIE", "Sw", "NetPay"]].head(),
        use_container_width=True
    )

# ============================================
# TAB 3 – PLOTS
# ============================================
with tab3:
    st.subheader("Log Plots")

    fig, ax = plt.subplots(1, 4, figsize=(18, 8), sharey=True)

    ax[0].plot(logs["GR"], logs["Depth"])
    ax[0].set_xlabel("GR")

    ax[1].plot(logs["PHIE"], logs["Depth"])
    ax[1].set_xlabel("PHIE")

    ax[2].plot(logs["Sw"], logs["Depth"])
    ax[2].set_xlabel("Sw")

    ax[3].plot(logs["RT"], logs["Depth"])
    ax[3].set_xlabel("RT")

    for a in ax:
        a.invert_yaxis()
        a.grid()

    st.pyplot(fig)

# ============================================
# TAB 4 – RESULTS SUMMARY
# ============================================
with tab4:
    st.subheader("Zone Summary")

    summaries = []

    for _, zone in zones_df.iterrows():
        zone_data = logs[
            (logs["Depth"] >= zone["Top"]) &
            (logs["Depth"] <= zone["Base"])
        ]

        net = zone_data[zone_data["NetPay"]]

        summaries.append({
            "Zone": zone["Zone"],
            "Gross Thickness": zone["Base"] - zone["Top"],
            "Net Thickness": len(net) * (depth[1] - depth[0]),
            "Avg PHIE": net["PHIE"].mean(),
            "Avg Sw": net["Sw"].mean(),
            "NTG": len(net) / len(zone_data) if len(zone_data) > 0 else 0
        })

    summary_df = pd.DataFrame(summaries)
    st.dataframe(summary_df, use_container_width=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    f"**Well:** {well_name} | **Field:** {field_name} | **Reservoir:** {reservoir_name}"
)
