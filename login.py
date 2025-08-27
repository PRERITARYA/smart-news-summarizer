import json
import streamlit as st
import pyrebase
import firebase_admin
import time
from firebase_admin import credentials, firestore


#  Firebase config
firebaseConfig = {
    "apiKey": "AIzaSyA7BkX0feIuMHzDh4Q112_w5SVFcmeBHXo",
    "authDomain": "smart-newz-summarizer.firebaseapp.com",
    "projectId": "smart-newz-summarizer",
    "storageBucket": "smart-newz-summarizer.firebasestorage.app",
    "messagingSenderId": "810605592735",
    "appId": "1:810605592735:web:5116b5a9d16fcb411c62aa",
    "measurementId": "G-RKH4TTT0TJ",
    "databaseURL": ""
}

# ----- Pyrebase (client) -----
firebaseConfig = st.secrets["FIREBASE_CONFIG"]
firebase = pyrebase.initialize_app(firebaseConfig)
pb_auth = firebase.auth()

# ----- Firebase Admin (server) -----
if not firebase_admin._apps:
    firebase_config = st.secrets["FIREBASE"]
    
    # Fix multiline private_key for Firebase Admin
    firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")
    
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# ---------------- CSS ----------------
st.set_page_config(page_title="Smart News Auth", page_icon="📰", layout="centered")

st.markdown("""
    <style>
    body {
        background: radial-gradient(circle at top left, #0f2027, #203a43, #2c5364);
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Glassmorphic Card */
    .glass-card {
        background: rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 30px;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0px 8px 32px rgba(0,0,0,0.6);
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        transform: scale(1.02);
        box-shadow: 0px 12px 40px rgba(0,0,0,0.7);
    }

    /* Gradient Animated Text */
    .gradient-text {
        background: linear-gradient(90deg, #00DBDE, #FC00FF, #00DBDE);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientMove 5s ease infinite;
        font-weight: bold;
        font-size: 2.2em;
        text-align: center;
    }

    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px;
        font-size: 16px;
        font-weight: bold;
        letter-spacing: 0.5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #fc6076, #ff9a44);
        transform: scale(1.05);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.5);
    }

    /* Radio buttons customization */
    .stRadio>div {
        display: flex;
        justify-content: center;
        gap: 20px;
    }

    </style>
""", unsafe_allow_html=True)

# ---------------- AUTH FUNCTIONS ----------------

def show_loader(message="⚡ Please wait..."):
    loader_placeholder = st.empty()
    loader_placeholder.markdown(
        f"""
        <style>
        .loading-overlay {{
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.85);
            backdrop-filter: blur(8px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }}
        .loader {{
            width: 80px;
            height: 80px;
            border: 5px solid rgba(255,255,255,0.2);
            border-top: 5px solid #00f7ff;
            border-radius: 50%;
            animation: spin 1.3s linear infinite;
            box-shadow: 0 0 30px #00f7ff88;
            margin: auto;
        }}
        .loading-text {{
            margin-top: 20px;
            font-size: 18px;
            font-weight: 500;
            color: #fff;
            text-align: center;
            font-family: 'Poppins', sans-serif;
            animation: pulse 1.5s infinite;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg);}}
            100% {{ transform: rotate(360deg);}}
        }}
        @keyframes pulse {{
            0%,100% {{ opacity: 0.6; }}
            50% {{ opacity: 1; }}
        }}
        </style>

        <div class="loading-overlay">
            <div>
                <div class="loader"></div>
                <div class="loading-text">{message}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    return loader_placeholder


def signup(email, username, password):
    try:
        show_loader("Creating your account...")
        time.sleep(1.5)
        if db.collection("users").document(username).get().exists:
            st.error("❌ Username already taken.")
            return
        user = pb_auth.create_user_with_email_and_password(email, password)
        pb_auth.send_email_verification(user['idToken'])
        db.collection("users").document(username).set({"email": email})
        st.success("✅ Account created! Please check your inbox to verify email.")
    except Exception as e:
        st.error(f"❌ Signup failed: {e}")


def login(username, password):
    loader = None
    try:
        loader = show_loader("🔐 Logging you in...")
        time.sleep(1.5)

        user_doc = db.collection("users").document(username).get()
        if not user_doc.exists:
            loader.empty()   # ❌ remove loader
            st.error("❌ Username not found.")
            return None

        email = user_doc.to_dict()["email"]
        user = pb_auth.sign_in_with_email_and_password(email, password)
        info = pb_auth.get_account_info(user['idToken'])

        if not info['users'][0]['emailVerified']:
            loader.empty()   # ❌ remove loader
            st.warning("⚠️ Please verify your email first.")
            return None

        # ✅ success
        loader.empty()
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        st.success(f"✨ Welcome {username}!")
        time.sleep(1)
        st.switch_page("pages/app.py")
        return user

    except Exception as e:
        if loader:  
            loader.empty()   # ❌ remove loader even if error
        st.error(f"❌ Login failed: {e}")
        return None


def reset_password(email):
    loader = show_loader("📩 Sending reset link...")
    try:
        pb_auth.send_password_reset_email(email)
        loader.empty()
        st.success("✅ Password reset email sent! Check your Inbox/Spam Folder.")
    except Exception as e:
        loader.empty()
        st.error(f"❌ Failed to reset password: {e}")


# ---------------- LOGIN UI ----------------
def login_page():
    st.markdown(
        "<h1 class='gradient-text' style='text-align:center;'>🚀 Smart News Summarizer</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center; font-size:18px; color: #bbb;'>AI Powered · Fast · Personalized</p>",
        unsafe_allow_html=True
    )

    #  Style (no black box issue)
    st.markdown(
        """
        <style>
        .glass-card-form {
            background: rgba(0,0,0,0.55);
            padding: 0px;
            border-radius: 0px;
            box-shadow: 0px 6px 25px rgba(0,0,0,0.6);
            backdrop-filter: blur(12px);
            color: white;
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ✅ Radio outside (so switching works instantly)
    option = st.radio(
        "🔑 Select Option",
        ["Login", "Signup", "Forgot Password"],
        horizontal=True
    )

    # ✅ Card wraps only when content exists
    with st.container():
        if option == "Signup":
            with st.form("signup_form"):
                st.markdown('<div class="glass-card-form">', unsafe_allow_html=True)
                email = st.text_input("📧 Email", placeholder="Enter your email")
                username = st.text_input("👤 Username", placeholder="Choose a username")
                password = st.text_input("🔑 Password", type="password", placeholder="Create a password")
                submit = st.form_submit_button("✨ Create Account")
                st.markdown("</div>", unsafe_allow_html=True)
                if submit:
                    signup(email, username, password)

        elif option == "Login":
            with st.form("login_form"):
                st.markdown('<div class="glass-card-form">', unsafe_allow_html=True)
                username = st.text_input("👤 Username", placeholder="Enter your username")
                password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("🚀 Login")
                st.markdown("</div>", unsafe_allow_html=True)
                if submit:
                    login(username, password)

        else:  # Forgot Password
            with st.form("reset_form"):
                st.markdown('<div class="glass-card-form">', unsafe_allow_html=True)
                email = st.text_input("📧 Registered Email", placeholder="Enter your email")
                submit = st.form_submit_button("🔄 Reset Password")
                st.markdown("</div>", unsafe_allow_html=True)
                if submit:
                    reset_password(email)

# 🚀 Run
if __name__ == "__main__":
    login_page()
