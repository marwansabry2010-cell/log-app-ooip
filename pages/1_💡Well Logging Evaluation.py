# ============================================================
# PETROPHYSICAL ANALYSIS STREAMLIT APPLICATION
# Senior Petrophysicist & Python Software Engineer
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator , AutoMinorLocator


# ============================================================
# STREAMLIT CONFIGURATION
# ============================================================
if not st.session_state.get("authenticated"):
    st.warning("Please login first")
    st.switch_page("Welcome.py")

if st.session_state.get("authenticated"):
    st.set_page_config(page_title="Petrophysical Analysis", layout="wide")
    st.title("🛢️ Integrated Petrophysical Evaluation")

    # ============================================================
    # SIDEBAR – WELL INFORMATION
    # ============================================================
    st.sidebar.header("🧾 Well Information")
    well_name = st.sidebar.text_input("Well Name", "Well-01")
    field_name = st.sidebar.text_input("Field Name", "Field-A")

    st.sidebar.markdown("---")
    # n_zones = st.sidebar.number_input("Number of Zones", 1, 10, 3)

    # ============================================================
    # TABS
    # ============================================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "1️⃣ Input Data",
        "2️⃣ Petrophysical Calculations",
        "3️⃣ Log Plots",
        "4️⃣ Results & Summary"
    ])

    # ============================================================
    # TAB 1 – INPUT DATA & ZONE PARAMETERS
    # ============================================================
    with tab1:
        st.header("📥 Import Well Logs (CSV)")
        st.write("____________________________")  
        st.write("**Required Columns to start well analysis** : ")
        st.write(':blue[**Depth, GR, RHOB, NPHI, RT, PE**]')
        st.write("____________________________")  
        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            n_rows = st.slider('**Choose the number of rows to display** : ', min_value=5 , max_value=len(df),step=1)
            Columns_to_show=st.multiselect("**Select coloumns to show** : ", df.columns.to_list() , default=df.columns.to_list())
            numerical_columns = df.select_dtypes(include=np.number).columns.to_list()
            st.write(df[:n_rows][Columns_to_show])
            required_cols = ["Depth", "GR", "RHOB", "NPHI", "RT", "PE"]

            if not all(col in df.columns for col in required_cols):
                st.error("❌ CSV must contain all required curves")
            else:
                df = df.dropna().sort_values("Depth").reset_index(drop=True)
                st.success("✅ Well logs loaded successfully")
                st.dataframe(df.head())

        st.markdown("---")
        st.header("📊 Zone-Based Petrophysical Parameters")
        n_zones = st.number_input("**Insert Number of Zones below** :- ", 1, 200, 3)
        st.write("____________________________") 

        zone_input = {
            "Zone Name": [f"Zone_{i+1}" for i in range(n_zones)],
            "Top Depth": [0.0] * n_zones,
            "Base Depth": [0.0] * n_zones,
            "GR_clean": [20.0] * n_zones,
            "GR_shale": [120.0] * n_zones,
            "Matrix Density": [2.65] * n_zones,
            "Shale Density": [2.40] * n_zones,
            "Fluid Density": [1.00] * n_zones,
            "a": [1.0] * n_zones,
            "m": [2.0] * n_zones,
            "n": [2.0] * n_zones,
            "Rw": [0.03] * n_zones
        }

        zone_df = st.data_editor(pd.DataFrame(zone_input), num_rows="dynamic")

    # ============================================================
    # PETROPHYSICAL FUNCTIONS
    # ============================================================
    def vsh_linear(gr, gr_clean, gr_shale):
        vsh = (gr - gr_clean) / (gr_shale - gr_clean)
        return np.clip(vsh, 0, 1)

    def vsh_larionov(gr, gr_clean, gr_shale):
        igr = (gr - gr_clean) / (gr_shale - gr_clean)
        vsh = 0.083 * (2 ** (3.7 * igr) - 1)
        return np.clip(vsh, 0, 1)

    def density_porosity(rhob, rho_matrix, rho_fluid):
        return (rho_matrix - rhob) / (rho_matrix - rho_fluid)

    def neutron_density_porosity(nphi, phi_d):
        return (nphi + phi_d) / 2

    def sw_archie(rt, rw, phi, a, m, n):
        return ((a * rw) / (rt * (phi ** m))) ** (1 / n)

    def sw_simandoux(rt, rw, phi, vsh):
        return np.sqrt((rw / rt) / (phi ** 2 + vsh))

    def sw_indonesian(rt, rw, phi, vsh, m, n):
        return ((rw / rt) ** (1 / n)) / (phi ** m + vsh ** 2)

    # ============================================================
    # TAB 2 – PETROPHYSICAL CALCULATIONS
    # ============================================================
    with tab2:
        st.header("🧮 Petrophysical Calculations")

        if uploaded_file:

            # ---- METHODS ----
            vsh_method = st.selectbox("Shale Volume Method", ["Linear", "Larionov"])
            porosity_method = st.selectbox("Porosity Method", ["Density", "Neutron-Density"])
            sw_method = st.selectbox("Water Saturation Method", ["Archie", "Simandoux", "Indonesian"])

            st.subheader("Net Pay Cutoffs")
            vsh_cutoff = st.number_input("Vsh Cutoff", value=0.4)
            phi_cutoff = st.number_input("Porosity Cutoff", value=0.10)
            sw_cutoff = st.number_input("Water Saturation Cutoff", value=0.6)

            results = []

            for _, zone in zone_df.iterrows():
                mask = (df["Depth"] >= zone["Top Depth"]) & (df["Depth"] <= zone["Base Depth"])
                z = df[mask].copy()

                # ---- VSH ----
                if vsh_method == "Linear":
                    z["Vsh"] = vsh_linear(z["GR"], zone["GR_clean"], zone["GR_shale"])
                else:
                    z["Vsh"] = vsh_larionov(z["GR"], zone["GR_clean"], zone["GR_shale"])

                # ---- POROSITY ----
                phi_d = density_porosity(z["RHOB"], zone["Matrix Density"], zone["Fluid Density"])
                if porosity_method == "Neutron-Density":
                    z["PHIT"] = neutron_density_porosity(z["NPHI"], phi_d)
                else:
                    z["PHIT"] = phi_d

                z["PHIE"] = z["PHIT"] * (1 - z["Vsh"])

                # ---- WATER SATURATION ----
                if sw_method == "Archie":
                    z["Sw"] = sw_archie(z["RT"], zone["Rw"], z["PHIE"], zone["a"], zone["m"], zone["n"])
                elif sw_method == "Simandoux":
                    z["Sw"] = sw_simandoux(z["RT"], zone["Rw"], z["PHIE"], z["Vsh"])
                else:
                    z["Sw"] = sw_indonesian(z["RT"], zone["Rw"], z["PHIE"], z["Vsh"], zone["m"], zone["n"])

                z["Sw"] = np.clip(z["Sw"], 0, 1)

                # ---- NET PAY ----
                z["Net"] = ((z["Vsh"] <= vsh_cutoff) & (z["PHIE"] >= phi_cutoff) & (z["Sw"] <= sw_cutoff))
                z["Zone"] = zone["Zone Name"]
                results.append(z)

            result_df = pd.concat(results)
            if results:
                result_df = pd.concat(results)
            else:
                result_df = pd.DataFrame()

            st.success("✅ Petrophysical calculations completed")

    # ============================================================
    # TAB 3 – LOG PLOTS
    # ============================================================
    with tab3:
        st.header("📈 Log & Interpretation Plots")
        
        if uploaded_file and not result_df.empty:
            fig, ax = plt.subplots(1, 7, figsize=(18, 100), sharey=True)

            # 👉 Set depth ticks every 10 m
            depth_locator = MultipleLocator(10)

            # ---- GR ----
            ax[0].plot(df["GR"], df["Depth"], color="green")
            ax[0].set_xlabel("GR (API)")
            ax[0].set_xlim(0, 150)

            # ---- RHOB ----
            ax[1].plot(df["RHOB"], df["Depth"], color="red")
            ax[1].set_xlabel("RHOB (g/cc)")
            ax[1].set_xlim(1.95, 2.95)

            # ---- NPHI ----
            ax[2].plot(df["NPHI"], df["Depth"], color="blue")
            ax[2].set_xlabel("NPHI (v/v)")
            ax[2].set_xlim(0.45, -0.15)

            # ---- RT10 ----
            ax[3].plot(df["RT"], df["Depth"], color="black")
            ax[3].set_xlabel("RT (ohm.m)")
            ax[3].set_xscale("log")
            ax[3].set_xlim(0.2, 2000)

            # ---- Vsh ----
            if not result_df.empty:
                ax[4].plot(result_df["Vsh"], result_df["Depth"], color="green")
                ax[4].set_xlabel("Vsh")
                ax[4].set_xlim(0, 1)

            # ---- PHIE ----
            if not result_df.empty:
                ax[5].plot(result_df["PHIE"], result_df["Depth"], color="blue")
                ax[5].set_xlabel("PHIE")
                ax[5].set_xlim(0, 1)
            
            # ---- Sw ----
            if not result_df.empty:
                ax[6].plot(result_df["Sw"], result_df["Depth"], color="purple")
                ax[6].set_xlabel("Sw")
                ax[6].set_xlim(0, 1)

            # ---- Common formatting ----
            for a in ax:
                a.invert_yaxis()
                a.grid(True, linestyle="--", alpha=0.5)
                a.yaxis.set_major_locator(depth_locator)

            plt.tight_layout()
            st.pyplot(fig)


    # ============================================================
    # TAB 4 – RESULTS & SUMMARY (ENHANCED)
    # ============================================================
    with tab4:
        st.header("📊 Zone & Reservoir Summary")

        if uploaded_file and not result_df.empty:

            summaries = []
            dz = df["Depth"].diff().median()

            for _, zone in zone_df.iterrows():
                zone_name = zone["Zone Name"]
                top_depth = zone["Top Depth"]
                base_depth = zone["Base Depth"]

                z = result_df[result_df["Zone"] == zone_name]
                if z.empty:
                    continue

                net_thickness = z["Net"].sum() * dz
                gross_thickness = base_depth - top_depth
                ntg = net_thickness / gross_thickness if gross_thickness > 0 else 0

                summaries.append({
                    "Zone Name": zone_name,
                    "Top Depth": top_depth,
                    "Bottom Depth": base_depth,
                    "Net Thickness": net_thickness,
                    "Net-to-Gross (NTG)": ntg,
                    "Avg Vsh": z["Vsh"].mean(),
                    "Avg PHIE": z["PHIE"].mean(),
                    "Avg Sw": z["Sw"].mean()
                })

            summary_df = pd.DataFrame(summaries)
            st.subheader("📋 Petrophysical Zone Summary")
            st.dataframe(summary_df.style.format({
                "Net Thickness": "{:.2f}",
                "Net-to-Gross (NTG)": "{:.2f}",
                "Avg Vsh": "{:.2f}",
                "Avg PHIE": "{:.2f}",
                "Avg Sw": "{:.2f}"
            }))

            st.success("✅ Zone-level petrophysical summary generated")

