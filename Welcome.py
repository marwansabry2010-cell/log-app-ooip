import streamlit as st
import pandas as pd

st.set_page_config(page_title="Welcome", layout="wide")

st.title(" 🛢️ Welcome to Log-App ")


st.info(' :blue[**Easy Application** for **petrophysical Evaluation** and **Volumetrics Calcultaions**]')
st.write(":grey[Created By :-  Dr. Marwan Sabry] ")
st.date_input("**Today**")
st.image('https://eco-cdn.iqpc.com/eco/images/channel_content/images/offshore_platform.webp',width=200)


USERNAME = "admin"
PASSWORD = "12345"

st.title("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if username == USERNAME and password == PASSWORD:
        st.success("Login successful")
        st.session_state["authenticated"] = True
    else:
        st.error("Invalid username or password")

if st.session_state.get("authenticated"):
    st.write(":blue[Welcome Log App] ")