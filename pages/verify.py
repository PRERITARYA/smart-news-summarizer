import streamlit as st
import requests
import time

st.set_page_config(page_title="Verify Email", page_icon="✅")

API_KEY = st.secrets["FIREBASE_CONFIG"]["apiKey"]

def verify_email_action(oob_code):
    """Call Firebase REST API to apply email verification code."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={API_KEY}"
    payload = {"oobCode": oob_code}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return True, None
    else:
        return False, res.json().get("error", {}).get("message", "Unknown error")

# Get query params from URL
query_params = st.experimental_get_query_params()
mode = query_params.get("mode", [None])[0]
oob_code = query_params.get("oobCode", [None])[0]

if mode == "verifyEmail" and oob_code:
    success, err = verify_email_action(oob_code)
    if success:
        st.success("✅ Your email has been verified! Redirecting to app...")
        time.sleep(2)
        st.switch_page("pages/app.py")  # redirect to your main app
    else:
        st.error(f"❌ Verification failed: {err}")
else:
    st.warning("⚠️ No verification code found. Please check your email link again.")
