import streamlit as st
from firebase_admin import auth

st.title("🔐 Email Verification")

query_params = st.query_params
mode = query_params.get("mode", [None])[0]
oob_code = query_params.get("oobCode", [None])[0]

if mode == "verifyEmail" and oob_code:
    try:
        auth.apply_action_code(oob_code)
        st.success("✅ Your email has been verified! You can now log in.")
        st.page_link("pages/app.py", label="Go to App 🚀")
    except Exception as e:
        st.error(f"❌ Verification failed: {e}")
else:
    st.warning("No verification code found. Please check your email again.")
