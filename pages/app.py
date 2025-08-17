import streamlit as st
from transformers import pipeline
from textblob import TextBlob
import trafilatura
import requests
from datetime import datetime, timedelta
from gtts import gTTS
import io
from deep_translator import GoogleTranslator

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
def read_text(summary, lang_code="en"):
    tts = gTTS(text=summary, lang=lang_code)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    st.audio(audio_buffer, format="audio/mp3")

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

# ---------- Sentiment Interpretation Functions ----------
def interpret_polarity(score):
    if score < -0.3:
        return "Negative 😞"
    elif score > 0.3:
        return "Positive 🙂"
    else:
        return "Neutral 😐"

def interpret_subjectivity(score):
    if score < 0.4:
        return "Objective 📊"
    elif score > 0.6:
        return "Subjective 💬"
    else:
        return "Mixed 🌓"

# ---------- APP TABS ----------
tab1, tab2 = st.tabs(["📄 Summarizer", "📈 News Pulse"])

# ---------- TAB 1: Summarizer ----------
with tab1:
    st.subheader("📥 Enter a News Article URL")
    url = st.text_input("Paste your article link here:")

    # New feature: summary length choice
    length_choice = st.selectbox(
        "Select Summary Length:",
        ["One Line", "Short Paragraph", "Detailed"]
    )

    # New feature: language choice
    language_choice = st.selectbox(
        "Choose Output Language:",
        ["English", "Hindi"]
    )
    lang_code = "en" if language_choice == "English" else "hi"

    if st.button("Summarize"):
        if url:
            with st.spinner("🔄 Fetching and summarizing the article..."):
                try:
                    downloaded = trafilatura.fetch_url(url)
                    article_text = trafilatura.extract(downloaded)

                    if not article_text:
                        st.error("Could not extract article content. Try another link.")
                        st.stop()

                    # Adjust length
                    if length_choice == "One Line":
                        min_len, max_len = 15, 25
                    elif length_choice == "Short Paragraph":
                        min_len, max_len = 40, 80
                    else:
                        min_len, max_len = 80, 150

                    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
                    summary = summarizer(article_text, max_length=max_len, min_length=min_len, do_sample=False)[0]["summary_text"]

                    # Translate if Hindi selected
                    if language_choice == "Hindi":
                        summary = GoogleTranslator(source="en", target="hi").translate(summary)

                    sentiment = TextBlob(article_text).sentiment

                    # Store in session
                    st.session_state["summary"] = summary
                    st.session_state["lang_code"] = lang_code

                    # Display results
                    st.subheader("📝 Summary")
                    st.text_area("Summary", summary, height=150)

                    st.subheader("📊 Sentiment Analysis")
                    st.write(f"**Polarity:** {interpret_polarity(sentiment.polarity)} ({sentiment.polarity:.2f})")
                    st.write(f"**Subjectivity:** {interpret_subjectivity(sentiment.subjectivity)} ({sentiment.subjectivity:.2f})")

                    st.subheader("📌 Additional Insights")
                    st.write(f"**Original Word Count:** {len(article_text.split())}")
                    st.write(f"**Estimated Reading Time:** {len(article_text.split()) // 200} min")

                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.warning("Please enter a valid article URL.")

    # Audio summary (always available if summary exists)
    if "summary" in st.session_state:
        if st.button("🔊 Listen to Summary"):
            read_text(st.session_state["summary"], st.session_state.get("lang_code", "en"))

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
