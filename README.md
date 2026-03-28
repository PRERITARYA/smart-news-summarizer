<!-- ANIMATED HEADER -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0040ff,50:3399ff,100:66ccff&height=200&section=header&text=Smart%20News%20Summarizer&fontSize=48&fontColor=ffffff&fontAlignY=38&desc=AI-Powered%20%C2%B7%20Fast%20%C2%B7%20Personalized&descAlignY=58&descSize=18" width="100%"/>

<!-- BADGES -->
<p>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-1.47.1-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black"/>
  <img src="https://img.shields.io/badge/Firebase-Auth%20%26%20Firestore-FFCA28?style=for-the-badge&logo=firebase&logoColor=black"/>
  <img src="https://img.shields.io/badge/NLP-distilBART-8B5CF6?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-00C853?style=for-the-badge"/>
</p>

<p>
  <img src="https://img.shields.io/badge/Internship-Sopra%20Steria%2C%20Noida-E63946?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Duration-July%20–%20Sept%202025-0040ff?style=for-the-badge"/>
</p>

<br/>

> **"Stop drowning in news. Start understanding it."**
>
> An intelligent full-stack web application that summarizes news articles using state-of-the-art NLP,
> analyzes their sentiment, reads them aloud, and tracks breaking stories over time — all behind a secure, personalized login.

<br/>

[🚀 Live Demo](https://smart-news-summarizer.streamlit.app) &nbsp;·&nbsp;
[🐛 Report Bug](https://github.com/PRERITARYA/smart-news-summarizer/issues) &nbsp;·&nbsp;
[✨ Request Feature](https://github.com/PRERITARYA/smart-news-summarizer/issues)

</div>

---

## 📸 Screenshots

<div align="center">

| 🔐 Login Page | 📝 Summarizer | 📈 News Pulse |
|:---:|:---:|:---:|
| <img width="400" src="https://github.com/user-attachments/assets/ec0c3aa3-602a-43c6-8d76-6bafb756f841" /> | <img width="400" src="https://github.com/user-attachments/assets/05467a57-cec8-4c2d-8177-a64cd7956ae0" /> | <img width="400" src="https://github.com/user-attachments/assets/1981db0c-cc99-4be1-af8e-7054bba42329" /> |

> 💡 *Replace the placeholder images above with actual screenshots from your app.*

</div>

---

## 🌟 Why Smart News Summarizer?

The average person encounters **hundreds of news articles** daily. Reading them all is impossible. Smart News Summarizer solves this by giving you **the essence of any article in seconds** — with AI that actually understands what it's reading.

Built during a real-world internship at **Sopra Steria, Noida**, this is not a toy project. It's a production-ready, full-stack application with secure authentication, real NLP models, live news APIs, and text-to-speech — deployed on Streamlit Cloud.

---

## ✨ Features

### 🧠 AI-Powered Summarization
- Paste a **URL** or raw article text and get an intelligent summary instantly
- Powered by **`distilbart-cnn-12-6`** from Hugging Face Transformers — a state-of-the-art extractive/abstractive NLP model
- Choose from **3 summary lengths**: One Line · Short Paragraph · Detailed

### 📊 Sentiment & Insight Analysis
- **Polarity score** (Positive / Neutral / Negative) via TextBlob
- **Subjectivity score** (Objective / Mixed / Subjective)
- **Word count** and **estimated reading time** for every article

### 🌐 Multilingual Output
- Translate summaries to **Hindi** using Google Translate API (Deep Translator)
- More languages can be easily added

### 🔊 Text-to-Speech (Listen Mode)
- Hit **"Listen to Summary"** and hear the summary read aloud via **gTTS**
- Works in both English and Hindi

### 📈 News Pulse — Timeline Tracker
- Enter any topic (e.g. *"Climate Change"*, *"ISRO"*, *"Budget 2025"*)
- Get a **7-day chronological timeline** of top headlines from **NewsAPI**
- Expand any headline for its description, timestamp, and source link

### 🔐 Secure Firebase Authentication
- **Email + Password** signup with mandatory **email verification**
- Username-based login backed by **Firestore** database
- **Forgot Password** with reset email flow
- Animated loading overlay during all auth actions
- Session-based logout with full state cleanup

---

## 🏗️ Architecture

```
smart-news-summarizer/
│
├── login.py                  # 🔐 Entry point — Firebase Auth (Login / Signup / Reset)
│
├── pages/
│   ├── app.py                # 🧠 Main app — Summarizer + News Pulse tabs
│   └── verify.py             # ✅ Email verification handler (Firebase oobCode)
│
├── .streamlit/
│   └── config.toml           # 🎨 Streamlit theme config
│
├── requirements.txt          # 📦 All dependencies
└── README.md
```

**Data Flow:**
```
User → login.py → Firebase Auth → Email Verification
     → pages/app.py → [URL Input] → Trafilatura/Newspaper3k → Text Extraction
                    → HuggingFace distilBART → Summary
                    → TextBlob → Sentiment Analysis
                    → gTTS → Audio Output
                    → Deep Translator → Hindi Translation
                    → NewsAPI → News Pulse Timeline
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend & Backend** | Streamlit 1.47.1 |
| **NLP / Summarization** | HuggingFace Transformers (`distilbart-cnn-12-6`), PyTorch |
| **Sentiment Analysis** | TextBlob, NLTK |
| **Text Extraction** | Trafilatura, Newspaper3k, BeautifulSoup4 |
| **Translation** | Deep Translator (Google Translate) |
| **Text-to-Speech** | gTTS (Google Text-to-Speech) |
| **Authentication** | Firebase Auth (Pyrebase4) + Firebase Admin SDK |
| **Database** | Firestore (Firebase) |
| **News Data** | NewsAPI (`/v2/everything`) |
| **Environment** | Python-dotenv, Streamlit Secrets |

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/PRERITARYA/smart-news-summarizer.git
cd smart-news-summarizer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure secrets

Create a `.streamlit/secrets.toml` file with the following:

```toml
NEWS_API_KEY = "your_newsapi_key_here"

[FIREBASE_CONFIG]
apiKey = "your_firebase_api_key"
authDomain = "your-project.firebaseapp.com"
databaseURL = "https://your-project.firebaseio.com"
projectId = "your-project-id"
storageBucket = "your-project.appspot.com"
messagingSenderId = "your_sender_id"
appId = "your_app_id"

[FIREBASE]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your_private_key_id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-...@your-project.iam.gserviceaccount.com"
client_id = "your_client_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
```

### 4. Run the app
```bash
streamlit run login.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔑 Getting API Keys

| Service | How to get it |
|---|---|
| **NewsAPI** | Sign up free at [newsapi.org](https://newsapi.org/) |
| **Firebase** | Create a project at [console.firebase.google.com](https://console.firebase.google.com/) → Enable Email/Password Auth → Create Firestore DB → Generate Admin SDK key |

---

## 📦 Key Dependencies

```txt
streamlit==1.47.1          # UI framework
transformers==4.54.1       # HuggingFace NLP models
torch==2.7.1               # PyTorch backend
textblob==0.17.1           # Sentiment analysis
trafilatura==2.0.0         # Article text extraction
newspaper3k==0.2.8         # Article scraping
deep-translator==1.11.4    # Google Translate API
gTTS==2.5.4                # Text-to-speech
firebase-admin==6.6.0      # Firebase Admin SDK
pyrebase4 @ git+...        # Firebase client SDK
requests==2.32.4           # HTTP requests
```

---

## 🚀 Deployment (Streamlit Cloud)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo — set **main file** to `login.py`
4. Add all secrets in the **Secrets** section of the app settings
5. Deploy 🎉

---

## 🎯 Use Cases

| 👤 Who | 💡 How they use it |
|---|---|
| **Journalists & Researchers** | Rapidly review dozens of articles to extract key facts |
| **Business Professionals** | Track competitor news and industry trends via News Pulse |
| **Students** | Summarize long articles for assignments and research |
| **General Public** | Stay informed in minutes, not hours |

---

## 🙏 Acknowledgements

This project was built during an internship at **Sopra Steria India, Noida** (July – September 2025).

Special thanks to **Mr. Chandramouli Vashisth** (Sr. Technical Lead, Sopra Steria Group) for his continuous guidance, invaluable feedback, and technical mentorship throughout the development of this project.

---

## 👨‍💻 Author

<div align="center">

**Prerit Arya**
B.Tech Computer Science & Engineering

[![GitHub](https://img.shields.io/badge/GitHub-PRERITARYA-181717?style=for-the-badge&logo=github)](https://github.com/PRERITARYA)

</div>

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:66ccff,50:3399ff,100:0040ff&height=120&section=footer" width="100%"/>

**⭐ If you found this project useful, please consider giving it a star!**

*Built with ❤️ during internship at Sopra Steria · 2025*

</div>
