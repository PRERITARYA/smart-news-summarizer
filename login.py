import streamlit as st
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
import time

# ---------------- Streamlit Config ----------------
st.set_page_config(page_title="Smart News Auth", page_icon="📰", layout="centered")

# ---------------- Pyrebase ----------------
pb_config = dict(st.secrets["FIREBASE_CONFIG"])
firebase = pyrebase.initialize_app(pb_config)
pb_auth = firebase.auth()

API_KEY = pb_config["apiKey"]
OOB_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"

# ---------------- Firebase Admin ----------------
if not firebase_admin._apps:
    admin_config = dict(st.secrets["FIREBASE"])
    admin_config["private_key"] = admin_config["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(admin_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------- Session Defaults ----------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "show_resend_signup" not in st.session_state:
    st.session_state["show_resend_signup"] = False
if "show_resend_login" not in st.session_state:
    st.session_state["show_resend_login"] = False

# ---------------- CSS ----------------
st.markdown("""
    <style>
    body {
        background: radial-gradient(circle at top left, #0f2027, #203a43, #2c5364);
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
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
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #fc6076, #ff9a44);
        transform: scale(1.05);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.5);
    }
    .stRadio>div { display: flex; justify-content: center; gap: 20px; }
    </style>
""", unsafe_allow_html=True)

# ---------------- Loader ----------------
def show_loader(message="⚡ Please wait..."):
    placeholder = st.empty()
    placeholder.markdown(f"""
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
        @keyframes spin {{0% {{transform: rotate(0deg);}}100%{{transform: rotate(360deg);}}}}
        @keyframes pulse {{0%,100%{{opacity:0.6;}}50%{{opacity:1;}}}}
        </style>
        <div class="loading-overlay">
            <div>
                <div class="loader"></div>
                <div class="loading-text">{message}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    return placeholder

# ---------------- Signup ----------------
def signup(email, username, password):
    loader = show_loader("Creating your account...")
    try:
        if db.collection("users").document(username).get().exists:
            st.error("❌ Username already taken.")
            return None

        user = pb_auth.create_user_with_email_and_password(email, password)

        # Send verification email
        payload = {"requestType": "VERIFY_EMAIL", "idToken": user["idToken"]}
        requests.post(OOB_URL, json=payload)

        db.collection("users").document(username).set({"email": email})

        st.success("✅ Account created! Please verify your email before login.")

        # Save idToken for dynamic resend button
        st.session_state["last_signup_user"] = user["idToken"]
        st.session_state["show_resend_signup"] = True

        return user["idToken"]

    except Exception as e:
        st.error(f"❌ Signup failed: {e}")
        return None
    finally:
        loader.empty()

# ---------------- Login ----------------
def login(username, password):
    loader = show_loader("Logging you in...")
    try:
        # 1️⃣ Get user document from Firestore
        user_doc = db.collection("users").document(username).get()
        if not user_doc.exists:
            st.error("❌ Username not found.")
            return

        email = user_doc.to_dict()["email"]

        # 2️⃣ Sign in with Firebase
        user = pb_auth.sign_in_with_email_and_password(email, password)

        # 3️⃣ Check if email is verified
        info = pb_auth.get_account_info(user['idToken'])
        verified = info["users"][0].get("emailVerified", False)

        if not verified:
            st.warning("⚠️ Please verify your email before logging in.")

            # Save idToken for dynamic resend button
            st.session_state["last_login_user"] = user["idToken"]
            st.session_state["show_resend_login"] = True
            return

        # 4️⃣ ✅ Verified → set username in session and redirect
        st.session_state["username"] = username
        st.success(f"✨ Welcome {username}!")
        time.sleep(0.5)
        st.switch_page("pages/app.py")

    except Exception as e:
        st.error(f"❌ Login failed: {e}")
    finally:
        loader.empty()

# ---------------- Reset Password ----------------
def reset_password(email):
    loader = show_loader("Sending reset link...")
    try:
        user_docs = db.collection("users").where("email", "==", email).get()
        if not user_docs:
            st.error("❌ No account found with this email.")
        else:
            pb_auth.send_password_reset_email(email)
            st.success("✅ Password reset email sent! Check Inbox/Spam.")
    except Exception as e:
        st.error(f"❌ Failed to reset password: {e}")
    finally:
        loader.empty()

# ---------------- UI ----------------
def login_page():
    st.markdown("<h1 class='gradient-text'>🚀 Smart News Summarizer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:18px; color: #bbb;'>AI Powered · Fast · Personalized</p>", unsafe_allow_html=True)

    option = st.radio("🔑 Select Option", ["Login", "Signup", "Forgot Password"], horizontal=True)

    # ---------------- Signup ----------------
    if option == "Signup":
        with st.form("signup_form"):
            email = st.text_input("📧 Email")
            username = st.text_input("👤 Username")
            password = st.text_input("🔑 Password", type="password")

            col1, col2 = st.columns([2, 1])
            submit = col1.form_submit_button("✨ Create Account")
            
            if submit:
                signup(email, username, password)
                st.session_state["first_name"] = username.split()[0]

        # Dynamic Resend Verification Button (appears after signup)
        if st.session_state.get("show_resend_signup", False):
            col1, col2 = st.columns([2, 1])
            if col2.button("📧 Resend Email"):
                user_id_token = st.session_state["last_signup_user"]
                payload = {"requestType": "VERIFY_EMAIL", "idToken": user_id_token}
                requests.post(OOB_URL, json=payload)
                st.info("✅ Verification email resent! Please check your inbox.")

    # ---------------- Login ----------------
    elif option == "Login":
        with st.form("login_form"):
            username_input = st.text_input("👤 Username")
            password_input = st.text_input("🔑 Password", type="password")
            submit = st.form_submit_button("🚀 Login")

        if submit:
            login(username_input, password_input)
            st.session_state["first_name"] = username.split()[0]
        # Dynamic Resend Verification Button for unverified login
        if st.session_state.get("show_resend_login", False):
            col1, col2 = st.columns([2, 1])
            if col2.button("📧 Resend Email"):
                user_id_token = st.session_state["last_login_user"]
                payload = {"requestType": "VERIFY_EMAIL", "idToken": user_id_token}
                requests.post(OOB_URL, json=payload)
                st.info("✅ Verification email resent! Please check your inbox.")

    # ---------------- Reset Password ----------------
    else:
        with st.form("reset_form"):
            email = st.text_input("📧 Registered Email")
            submit = st.form_submit_button("🔄 Reset Password")
            if submit: reset_password(email)

if __name__ == "__main__":
    login_page()
