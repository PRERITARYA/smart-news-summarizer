import streamlit as st
import requests
import time

FIREBASE_API_KEY = st.secrets["FIREBASE_CONFIG"]["apiKey"]  # get from Firebase console

st.set_page_config(page_title="Email Verification", page_icon="✅")

params = st.query_params

if "oobCode" not in params:
    st.error("⚠️ No verification code found. Please check your email link again.")
else:
    try:
        oob_code = params["oobCode"]

        # Call Firebase REST API to apply action code
        resp = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FIREBASE_API_KEY}",
            json={"oobCode": oob_code}
        )
        data = resp.json()

        if "email" in data:
            st.success(f"✅ {data['email']} verified! Redirecting to app...")

            # Auto-redirect with HTML
            st.markdown(
                """
                <meta http-equiv="refresh" content="2;url=/app" />
                """,
                unsafe_allow_html=True,
            )
        else:
            st.error(f"❌ Verification failed: {data.get('error', {}).get('message', 'Unknown error')}")

    except Exception as e:
        st.error(f"❌ Verification failed: {str(e)}")
