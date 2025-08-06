import streamlit as st
from newspaper import Article
from transformers import pipeline
from textblob import TextBlob
import trafilatura
import time
import requests
import pyttsx3
from datetime import datetime, timedelta

# ---------- CONFIG ----------
NEWS_API_KEY = "35452938008a4d36b95ae0cff21ccf86"

st.set_page_config(page_title="Smart News Summarizer", page_icon="📰", layout="wide")

# ---------- CUSTOM DARK THEME ----------
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .stTextInput>div>div>input, .stTextArea>div>textarea {
        background-color: #1e1e1e; color: white; border: 1px solid #333; border-radius: 8px; padding: 0.75rem;
    }
    .stButton>button {
        background-color: #1a73e8; color: white; font-weight: bold; padding: 0.5rem 1.5rem;
        border-radius: 8px; border: none;
    }
    .stButton>button:hover { background-color: #1558b0; }
    </style>
""", unsafe_allow_html=True)

# ---------- WELCOME ----------
if "name" in st.session_state:
    st.markdown(f"### 👋 Hello, **{st.session_state.name}**!")
else:
    st.warning("User not logged in!")
    st.stop()

# ---------- AUDIO FUNCTION ----------
def read_text(summary):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Female voice (if available)
    engine.say(summary)
    engine.runAndWait()

# ---------- NEWS PULSE FUNCTION ----------
def get_news_pulse(query):
    today = datetime.now().date()
    last_week = today - timedelta(days=7)
    url = (f"https://newsapi.org/v2/everything?q={query}&from={last_week}&to={today}"
           f"&sortBy=publishedAt&apiKey={NEWS_API_KEY}")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("articles", [])
    else:
        return []

# ---------- APP TABS ----------
tab1, tab2 = st.tabs(["📄 Summarizer", "📈 News Pulse"])

# ---------- TAB 1: Summarizer ----------
with tab1:
    st.subheader("📥 Enter a News Article URL")
    url = st.text_input("Paste your article link here:")

    if st.button("Summarize"):
        if url:
            with st.spinner("🔄 Fetching and summarizing the article..."):
                try:
                    downloaded = trafilatura.fetch_url(url)
                    article_text = trafilatura.extract(downloaded)

                    if not article_text:
                        st.error("Could not extract article content. Try another link.")
                        st.stop()

                    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
                    summary = summarizer(article_text, max_length=130, min_length=30, do_sample=False)[0]["summary_text"]

                    sentiment = TextBlob(article_text).sentiment

                    # Display results
                    st.subheader("📝 Summary")
                    st.text_area("Summary", summary, height=150)

                    st.subheader("📊 Sentiment")
                    st.write(f"**Polarity:** `{sentiment.polarity:.2f}`")
                    st.write(f"**Subjectivity:** `{sentiment.subjectivity:.2f}`")

                    st.subheader("📌 Additional Insights")
                    st.write(f"**Original Word Count:** {len(article_text.split())}")
                    st.write(f"**Estimated Reading Time:** {len(article_text.split()) // 200} min")

                    # Audio summary button
                    if st.button("🔊 Listen to Summary"):
                        read_text(summary)
                        if st.button("⬅ Back"):
                            st.experimental_rerun()

                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.warning("Please enter a valid article URL.")

# ---------- TAB 2: News Pulse ----------
with tab2:
    st.subheader("🔍 Track News Timeline")
    topic = st.text_input("Enter topic to track:")
    if st.button("Show News Timeline"):
        if topic:
            articles = get_news_pulse(topic)
            if articles:
                for art in articles:
                    st.markdown(f"**{art['title']}**  \n"
                                f"📅 {art['publishedAt']}  \n"
                                f"{art['description'] or ''}  \n"
                                f"[Read more]({art['url']})")
                    st.markdown("---")
            else:
                st.info("No news found for this topic in the last 7 days.")
        else:
            st.warning("Please enter a topic to track.")

# ---------- LOGOUT ----------
st.markdown("---")
if st.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
