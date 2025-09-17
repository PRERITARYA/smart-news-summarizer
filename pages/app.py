from dotenv import load_dotenv
load_dotenv()
import os
import io
import requests
import streamlit as st
from datetime import datetime, timedelta
from transformers import pipeline
from textblob import TextBlob
import trafilatura
from newspaper import Article
from deep_translator import GoogleTranslator
from gtts import gTTS

# ---------------- CONFIG ----------------
NEWS_API_KEY = os.getenv("NEWS_API_KEY") or st.secrets["NEWS_API_KEY"]
st.set_page_config(page_title="Smart News Summarizer", page_icon="📰", layout="wide")

# --------------- THEME ------------------
# ✅ Take first name from session (set in login.py)
# --------------- THEME ------------------
# ✅ Take username from session (set in login.py)
if "username" in st.session_state:
    first_name = st.session_state["username"].strip().split(" ")[0]
elif "name" in st.session_state:
    first_name = st.session_state["name"].strip().split(" ")[0]
else:
    first_name = "Guest"

st.markdown(
    f"""
    <style>
    @keyframes gradientAnimation {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    .hello-text {{
        font-size: 42px;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        text-align: center;
        margin-top: 20px;
    }}

    .name-gradient {{
        background: linear-gradient(270deg, #0040ff, #3399ff, #66ccff);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientAnimation 6s ease infinite;
    }}
    </style>

    <div class="hello-text">
         <span class="name-gradient">Hello, {first_name}</span>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------- HELPERS ----------------
@st.cache_resource(show_spinner=False)
def load_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

@st.cache_data(show_spinner=False, ttl=3600)
def extract_text(url: str) -> str:
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            result = trafilatura.extract(downloaded)
            if result:
                return result
    except Exception:
        pass
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception:
        pass
    return ""

@st.cache_data(show_spinner=False, ttl=3600)
def get_news_pulse(query: str):
    today = datetime.now().date()
    last_week = today - timedelta(days=7)
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={requests.utils.quote(query)}&from={last_week}&to={today}"
        f"&sortBy=publishedAt&pageSize=20&language=en&apiKey={NEWS_API_KEY}"
    )
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 429:
            st.error("🚨 API quota exceeded. Try again later.")
            return []
        if r.status_code != 200:
            return []
        return r.json().get("articles", []) or []
    except Exception:
        return []

def interpret_polarity(score: float):
    if score < -0.3: return "<span style='color:#ff4b4b'>Negative 😞</span>"
    if score > 0.3:  return "<span style='color:#00c853'>Positive 🙂</span>"
    return "<span style='color:#ffb300'>Neutral 😐</span>"

def interpret_subjectivity(score: float):
    if score < 0.4: return "<span style='color:#29b6f6'>Objective 📊</span>"
    if score > 0.6: return "<span style='color:#ab47bc'>Subjective 💬</span>"
    return "<span style='color:#ffee58'>Mixed 🌓</span>"

def tts_audio(summary_text: str, lang_code: str = "en"):
    tts = gTTS(text=summary_text, lang=lang_code)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf

# ------------------ UI ------------------
tab1, tab2 = st.tabs(["📄 Summarizer", "📈 News Pulse"])

# ===== TAB 1: SUMMARIZER =====
with tab1:
    st.subheader("📥 Enter a News Article URL or Paste Text")
    url = st.text_input("Paste your article link here:")
    manual_text = st.text_area("Or paste article text directly:")

    colA, colB = st.columns(2)
    with colA:
        length_choice = st.selectbox(
            "Select Summary Length:",
            ["One Line", "Short Paragraph", "Detailed"],
            index=1
        )
    with colB:
        language_choice = st.selectbox(
            "Choose Output Language:",
            ["English", "Hindi"],
            index=0
        )

    lang_code = "en" if language_choice == "English" else "hi"

    length_map = {
        "One Line": (15, 25),
        "Short Paragraph": (40, 80),
        "Detailed": (80, 150)
    }

    if st.button("Summarize"):
        if not url and not manual_text.strip():
            st.warning("Please enter a valid article URL or paste text.")
        else:
            with st.spinner("🔄 Fetching and summarizing the article..."):
                # Select source
                if manual_text.strip():
                    article_text = manual_text.strip()
                else:
                    article_text = extract_text(url)

                if not article_text or len(article_text.strip()) < 50:
                    st.error("❌ Could not extract article content. Try another link or paste text.")
                else:
                    words = article_text.split()
                    if len(words) > 1200:
                        article_text = " ".join(words[:1200])

                    min_len, max_len = length_map[length_choice]

                    # Adjust dynamically based on input size
                    input_word_count = len(article_text.split())
                    max_allowed = max(30, input_word_count // 2)
                    max_len = min(max_len, max_allowed)
                    min_len = min(min_len, max_len - 10) if max_len > 20 else 15

                    summarizer = load_summarizer()

                    try:
                        summary_outputs = summarizer(
                            article_text,
                            max_length=max_len,
                            min_length=min_len,
                            num_beams=4,
                            do_sample=False,
                            truncation=True
                        )

                        if not summary_outputs or "summary_text" not in summary_outputs[0]:
                            raise ValueError("Empty summary returned.")

                        summary = summary_outputs[0]["summary_text"]

                    except Exception as e:
                        sentences = article_text.split(". ")
                        summary = ". ".join(sentences[:3]).strip()
                        st.warning(f"Summarizer fallback used. ({e})")

                    if lang_code == "hi":
                        try:
                            summary = GoogleTranslator(source="en", target="hi").translate(summary)
                        except Exception:
                            st.warning("Translation failed; showing English summary.")

                    sentiment = TextBlob(article_text).sentiment

                    st.session_state["summary"] = summary
                    st.session_state["lang_code"] = lang_code

                    st.subheader("📝 Summary")
                    st.text_area("Summary", summary, height=150)

                    st.subheader("📊 Sentiment Analysis")
                    st.markdown(f"**Polarity:** {interpret_polarity(sentiment.polarity)} ({sentiment.polarity:.2f})", unsafe_allow_html=True)
                    st.markdown(f"**Subjectivity:** {interpret_subjectivity(sentiment.subjectivity)} ({sentiment.subjectivity:.2f})", unsafe_allow_html=True)

                    st.subheader("📌 Additional Insights")
                    st.write(f"**Original Word Count:** {len(words)}")
                    st.write(f"**Estimated Reading Time:** {len(words) // 200} min")

    if "summary" in st.session_state:
        if st.button("🔊 Listen to Summary"):
            audio = tts_audio(st.session_state["summary"], st.session_state.get("lang_code", "en"))
            st.audio(audio, format="audio/mp3")

# ===== TAB 2: NEWS PULSE (TIMELINE) =====
with tab2:
    st.subheader("🔍 Track News Timeline")
    topic = st.text_input("Enter topic to track:")
    if st.button("Show News Timeline"):
        if not topic:
            st.warning("Please enter a topic to track.")
        else:
            with st.spinner("Fetching recent articles..."):
                articles = get_news_pulse(topic)
            if not articles:
                st.info("No news found for this topic in the last 7 days.")
            else:
                for art in articles:
                    title = art.get("title") or "(no title)"
                    date = art.get("publishedAt") or ""
                    desc = art.get("description") or ""
                    link = art.get("url") or "#"
                    with st.expander(f"📰 {title}"):
                        st.write(f"📅 {date}")
                        st.write(desc)
                        st.markdown(f"[Read more]({link})")

# --------- LOGOUT ----------
st.markdown("---")
if st.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
            