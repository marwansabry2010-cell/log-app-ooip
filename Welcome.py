import streamlit as st
import pandas as pd
from datetime import date

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Log-App | Petrophysical Analysis",
    page_icon="🛢️",
    layout="wide"
)

# =========================
# HEADER
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    st.title("🛢️ Log-App")
    st.subheader(
        ":blue[Petrophysical Analysis & Volumetric Evaluation Platform]"
    )
    st.markdown(
        """
        - **Well Log Interpretation (CSV)**
        - **Fluid Evaluation**
        - **Porosity, Saturation & Net Pay**
        - **Clean, Fast & Interactive Visualizations**
        """
    )

with col2:
    st.image(
    "https://eco-cdn.iqpc.com/eco/images/channel_content/images/offshore_platform.webp",
    width="stretch"
    )


st.divider()

# =========================
# INFO SECTION
# =========================
st.info(
    "🚀 **Easy-to-use web application** designed for **petrophysical evaluation**, "
    "**formation analysis**, and **volumetric calculations**."
)

st.write(
    ":grey[Developed by **Dr. Marwan Sabry** | Petrophysicist & Data Analyst]"
)

st.caption(f"📅 Today: {date.today()}")

st.divider()

# =========================
# LOGIN SECTION
# =========================
st.markdown("## 🔐 User Login")

USERNAME = "admin"
PASSWORD = "12345"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

login_col1, login_col2 = st.columns([1, 2])

with login_col1:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

with login_col2:
    st.markdown(
        """
        **Access Features After Login**
        - Upload CSV well logs
        - Interactive log plots
        - Petrophysical calculations
        - Export results & figures
        """
    )

if login_btn:
    if username == USERNAME and password == PASSWORD:
        st.session_state["authenticated"] = True
        st.success("✅ Login successful")
    else:
        st.error("❌ Invalid username or password")

# =========================
# POST-LOGIN MESSAGE
# =========================
if st.session_state["authenticated"]:
    st.success("🎉 Welcome to **Log-App** – Start your petrophysical workflow from the sidebar.")
