import streamlit as st
import requests
from firebase_admin import firestore

# ✅ Firebase setup
FIREBASE_API_KEY = st.secrets["FIREBASE_CONFIG"]["apiKey"]
db = firestore.client()

st.set_page_config(page_title="Email Verification", page_icon="✅")

params = st.query_params

if "oobCode" not in params:
    st.error("⚠️ No verification code found. Please check your email link again.")
else:
    try:
        oob_code = params["oobCode"]

        # 🔑 Call Firebase REST API to apply action code
        resp = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FIREBASE_API_KEY}",
            json={"oobCode": oob_code}
        )
        data = resp.json()

        if "email" in data:
            email = data["email"]

            # 🔎 Lookup Firestore for username
            docs = db.collection("users").where("email", "==", email).get()
            if docs:
                username = docs[0].id  # Firestore document ID

                # ✅ Store both username and first_name in session
                st.session_state["username"] = username
                st.session_state["first_name"] = username.split()[0]

                st.success(f"✅ Welcome {st.session_state['first_name']}! Redirecting to app...")

                # Auto-redirect (HTML meta refresh)
                st.markdown(
                    """
                    <meta http-equiv="refresh" content="2;url=/app" />
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.error("❌ User record not found in Firestore.")
        else:
            st.error(f"❌ Verification failed: {data.get('error', {}).get('message', 'Unknown error')}")

    except Exception as e:
        st.error(f"❌ Verification failed: {str(e)}")
