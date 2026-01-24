import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as plt
import plotly.express as px

if not st.session_state.get("authenticated"):
    st.warning("Please login first")
    st.switch_page("Welcome.py")

if st.session_state.get("authenticated"):


    st.set_page_config(page_title="Petrophysical Evaluation", layout="wide")

    st.title(" Full Petrophysical Evaluation ")
    st.header("📂 Upload Well Log Data (CSV)")
    file = st.file_uploader("Upload CSV file", type=["csv"])


    # ======================================================
    # Upload Data
    # ======================================================

    if file:
        df = pd.read_csv(file)
        st.subheader("📊 Raw Log Data")
        #st.dataframe(df.head())
        n_rows = st.slider('**Choose the number of rows to display** : ', min_value=5 , max_value=len(df),step=1)
        st.write("____________________________")
        Columns_to_show=st.multiselect("**Select coloumns to show** : ", df.columns.to_list() , default=df.columns.to_list())
        numerical_columns = df.select_dtypes(include=np.number).columns.to_list()
        st.write("____________________________")
        st.write(df[:n_rows][Columns_to_show])
        


        # ======================================================
        # Sidebar Parameters
        # ======================================================
        st.sidebar.header("⚙️ Petrophysical Parameters")

        GR_clean = st.sidebar.number_input("GR Clean (API)", value=20.0)
        GR_shale = st.sidebar.number_input("GR Shale (API)", value=120.0)

        rho_matrix = st.sidebar.number_input("Matrix Density (g/cc)", value=2.65)
        rho_shale = st.sidebar.number_input("Bulk Density shale (g/cc)", value=2.4)

        rho_fluid = st.sidebar.number_input("Fluid Density (g/cc)", value=1.0)

        m = st.sidebar.number_input("Archie m", value=2.0)
        n = st.sidebar.number_input("Archie n", value=2.0)
        a = st.sidebar.number_input("Archie a", value=1.0)
        Rw = st.sidebar.number_input("Rw (ohm.m)", value=0.05)

        phi_cut = st.sidebar.number_input("Porosity Cutoff", value=0.10)
        sw_cut = st.sidebar.number_input("Sw Cutoff", value=0.6)
        vsh_cut = st.sidebar.number_input("Vsh Cutoff", value=0.35)

        # ======================================================
        # Vsh Calculation
        # ======================================================
        st.subheader("🟫 Shale Volume (Vsh)")

        df["Vsh"] = (df["GR"] - GR_clean) / (GR_shale - GR_clean)
        df["Vsh"] = df["Vsh"].clip(0, 1)
        st.write(df["Vsh"])
        
        
            
        # ======================================================
        # Porosity Calculation (Density-Neutron)
        # ======================================================
        st.subheader("🟦 Effective Porosity (PHIE)")

        df["PHIT_D"] = (rho_matrix - df["RHOB"]) / (rho_matrix - rho_fluid)
        df["PHIT_sh"] = (rho_matrix - rho_shale) / (rho_matrix - rho_fluid)
        df["PHIE_D"] = df["PHIT_D"] - (df["PHIT_sh"] * df["Vsh"]) 
        st.write(df["PHIE_D"])

        #df["PHI_E"] = (df["PHI_D"] + df["NPHI"]) / 2
        #df["PHI_E"] = df["PHI_E"].clip(0, 0.4)


        

        
        # ======================================================
        # Water Saturation (Archie)
        # ======================================================
        st.subheader("💧 Water Saturation (SW)")

        df["Sw"] = ((a * Rw) / (df["RT"] * (df["PHIE_D"] ** m))) ** (1 / n)
        df["Sw"] = df["Sw"].clip(0, 1)
        st.write(df["Sw"])

        # ======================================================
        # Net Pay Flag
        # ======================================================
        st.subheader("🟩 Net Pay")

        df["NetPay"] = np.where(
            (df["PHIE_D"] >= phi_cut) &
            (df["Sw"] <= sw_cut) &
            (df["Vsh"] <= vsh_cut), 1, 0
        )

        net_pay_thickness = df["NetPay"].sum() * (df["DEPTH"].iloc[1] - df["DEPTH"].iloc[0])
        st.write(net_pay_thickness)

        # ======================================================
        # Visualization
        # ======================================================
        st.subheader("📈 Log Visualization")
        
        tab1 , tab2 =st.tabs(["**Scatter Plot**" , "**Histogram**"])
        with tab1:
            col1 , col2 , col3 = st.columns(3)
            with col1:
                x_column = st.selectbox('**Select coloumn on x axis** :' , numerical_columns)
            with col2:
                y_column = st.selectbox('**Select coloumn on y axis** :' , numerical_columns)
            with col3:
                color = st.selectbox('**Select coloumn to be color** :' , df.columns)
            fig_scatter =px.scatter(df , x= x_column , y= y_column , color=color)
            st.plotly_chart(fig_scatter)
        


        with tab2:
            Histogram_Feature =st.selectbox('**Select feature to histogram** :' , numerical_columns)
            fig_hist =px.histogram(df , x= 'GR')
            st.plotly_chart(fig_hist)





        #fig, ax = plt.subplots(figsize=(4, 8))
        #ax.plot(df["GR"], df["DEPTH"], label="GR")
        #ax.plot(df["PHIE_D"] * 100, df["DEPTH"], label="PHIE_D (%)")
        #ax.plot(df["Sw"] * 100, df["DEPTH"], label="Sw (%)")

        #ax.invert_yaxis()
        #ax.set_xlabel("Value")
        #ax.set_ylabel("Depth (m)")
        #ax.legend()
        #st.pyplot(fig)

        # ======================================================
        # Export Results
        # ======================================================
        st.subheader("📥 Download Results")

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Petrophysical Results", csv, "petrophysics_results.csv")

    else:
        st.info("⬅️ Upload a CSV file to start evaluation")

    

