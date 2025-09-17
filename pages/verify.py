import streamlit as st
import firebase_admin
from firebase_admin import auth, credentials
import time

# Initialize Firebase Admin (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)

st.set_page_config(page_title="Email Verification", page_icon="✅")

# ✅ Use the new query params API
params = st.query_params

if "oobCode" not in params:
    st.error("⚠️ No verification code found. Please check your email link again.")
else:
    try:
        oob_code = params["oobCode"]

        # Verify email with Firebase
        auth.apply_action_code(oob_code)

        st.success("✅ Your email has been verified! Redirecting to app...")
        time.sleep(2)

        # ✅ Redirect without clearing query params manually
        st.switch_page("pages/app.py")

    except Exception as e:
        st.error(f"❌ Verification failed: {str(e)}")
