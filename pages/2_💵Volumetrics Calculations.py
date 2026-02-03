import streamlit as st 
import pandas as pd

if not st.session_state.get("authenticated"):
    st.warning("Please login first")
    st.switch_page("Welcome.py")

if st.session_state.get("authenticated"):

    
    st.title("💸 Volumetric Calculations")
    st.write("________________________")
    st.title(" OOIP & OGIP ")

    st.write("________________________")

    Hydrocarbon_Type = st.selectbox('**Choose Type**', ["Oil", "Gas"])
    st.write("________________________")

    if Hydrocarbon_Type == 'Oil' :
        Area_A_Acres = st.number_input('**Area_A_Acres**', value=100)
        Net_Pay_Thickness_H_ft =  st.number_input('**Net_Pay_Thickness_H_ft**', value=10)
        Effective_Porosity_PHIE_fraction =  st.number_input('**Effective_Porosity_PHIE_fraction**', value=0.1)
        Water_Saturation_SW_fraction =  st.number_input('**Water_Saturation_SW_fraction**', value=0.2)
        Oil_formation_volume_factor_Bo =  st.number_input('**Oil_formation_volume_factor_Bo**' , format="%.2f" ,value=1.5)
        Conversion_factor =  st.number_input('**Conversion_factor (7758)**', value=7758)
        st.write("________________________")
        OOIP_STB = Conversion_factor * Area_A_Acres * Net_Pay_Thickness_H_ft * Effective_Porosity_PHIE_fraction * (1-Water_Saturation_SW_fraction) /Oil_formation_volume_factor_Bo
        Compute_Button = st.button(":red[**OOIP_STB**]")
        st.write("**OOIP_STB**: ", OOIP_STB)
        st.write("________________________")
        Recovery_Factor_fraction = st.number_input('**Recovery_Factor_fraction**', value=0.1)
        st.write("________________________")
        Recoverable_Oil = OOIP_STB * Recovery_Factor_fraction 
        Compute_Button = st.button(":red[**Recoverable_Oil**]")
        st.write("**Recoverable_Oil**: ", Recoverable_Oil)


    if Hydrocarbon_Type == 'Gas' :
        Area_A_Acres = st.number_input('**Area_A_Acres**', value=100)
        Net_Pay_Thickness_H_ft =  st.number_input('**Net_Pay_Thickness_H_ft**', value=10)
        Effective_Porosity_PHIE_fraction =  st.number_input('**Effective_Porosity_PHIE_fraction**', value=0.1)
        Water_Saturation_SW_fraction =  st.number_input('**Water_Saturation_SW_fraction**', value=0.2)
        Gas_formation_volume_factor_Bg =  st.number_input('**Gas_formation_volume_factor_Bg**' , format="%.5f" ,value=0.005)
        Conversion_factor =  st.number_input('**Conversion_factor (43560)**', value=43560)
        st.write("________________________")
        OGIP_SCF = Conversion_factor * Area_A_Acres * Net_Pay_Thickness_H_ft * Effective_Porosity_PHIE_fraction * (1-Water_Saturation_SW_fraction) /Gas_formation_volume_factor_Bg
        Compute_Button = st.button(":red[OGIP_SCF]")
        st.write("**OGIP_SCF**: ", OGIP_SCF)
        st.write("________________________")
        Recovery_Factor_fraction = st.number_input('**Recovery_Factor_fraction**', value=0.5)
        st.write("________________________")
        Recoverable_Gas = OGIP_SCF * Recovery_Factor_fraction 
        Compute_Button = st.button(":red[**Recoverable_Gas**]")
        st.write("**Recoverable_Gas**: ", Recoverable_Gas)
    




  






