import streamlit as st
import time

st.set_page_config(page_title="Login - Smart News Summarizer", page_icon="🔐", layout="centered")

# Public Lottie JSON URL
public_lottie_url = "https://lottie.host/2ebcb20e-2fec-4996-a24e-ef3d57cd566b/2QHGJiJWM8.json"

# Inject CSS & HTML for overlay (hidden by default)
st.markdown(f"""
    <style>
    #overlay {{
        position: fixed;
        top: 0; left: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(0, 0, 0, 0.85);
        z-index: 9999;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        visibility: hidden;
    }}
    #overlay.visible {{
        visibility: visible;
    }}
    </style>

    <div id="overlay">
        <div id="lottie-container"></div>
        <p style='color:white;font-size:18px;'>Redirecting, please wait...</p>
    </div>

    <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
    <script>
    function showOverlay() {{
        const overlay = window.parent.document.querySelector('#overlay');
        if (overlay) {{
            overlay.innerHTML = `
                <lottie-player 
                    src="{public_lottie_url}" 
                    background="transparent"  
                    speed="1"  
                    style="width: 300px; height: 300px;"  
                    loop autoplay></lottie-player>
                <p style='color:white;font-size:18px;'>Redirecting, please wait...</p>
            `;
            overlay.classList.add('visible');
        }}
    }}
    </script>
""", unsafe_allow_html=True)

st.title("🔐 Login to Smart News Summarizer")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# State to handle animation
if "show_loading" not in st.session_state:
    st.session_state.show_loading = False

# Login form
if not st.session_state.show_loading:
    with st.form("login_form"):
        name = st.text_input("👤 Name")
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if name and email and password:
                st.session_state.name = name
                st.session_state.show_loading = True
                st.rerun()
            else:
                st.error("❌ Please fill all fields!")

# Show animation before redirect
if st.session_state.show_loading:
    st.components.v1.html("<script>showOverlay();</script>", height=0)
    time.sleep(3)
    st.session_state.authenticated = True
    st.session_state.show_loading = False
    st.switch_page("pages/app.py")
