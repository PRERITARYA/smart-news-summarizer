import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time

st.set_page_config(page_title="Login - Smart News Summarizer", page_icon="🔐", layout="centered")

# Load Lottie animation from URL
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Your Lottie animation (loader)
lottie_loader = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_usmfx6bp.json")

# CSS for full-screen overlay
st.markdown("""
    <style>
    .overlay {
        position: fixed;
        top: 0; left: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(0, 0, 0, 0.85);
        z-index: 9999;
        display: none;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    .overlay.visible {
        display: flex;
    }
    </style>
    <div id="custom-overlay" class="overlay">
        <div id="lottie-loader"></div>
        <p style='color:white;font-size:18px;'>Redirecting, please wait...</p>
    </div>
    <script>
    const overlay = window.parent.document.getElementById('custom-overlay');
    function showOverlay() {
        if (overlay) {
            overlay.classList.add('visible');
        }
    }
    </script>
""", unsafe_allow_html=True)

st.title("🔐 Login to Smart News Summarizer")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

with st.form("login_form"):
    name = st.text_input("👤 Name")
    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")
    submit = st.form_submit_button("Login")

    if submit:
        if name and email and password:
            # Trigger JavaScript overlay
            st.components.v1.html("""
                <script>
                    showOverlay();
                </script>
            """, height=0)

            # Show Streamlit Lottie animation while waiting
            with st.spinner("Loading..."):
                st_lottie(lottie_loader, speed=1, height=200, key="loader")
                time.sleep(3)

            st.session_state.authenticated = True
            st.session_state.name = name
            st.switch_page("pages/app.py")
        else:
            st.error("❌ Please fill all fields!")
