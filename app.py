import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import requests

# --- הגדרות עמוד ---
st.set_page_config(page_title="YouTube Summarizer", page_icon="📺", layout="centered")

# --- הזן את הכתובת שלך כאן (בתוך המרכאות!) ---
webhook_url = "https://cloud.activepieces.com/api/v1/webhooks/HDSgK2B66mVb6nQSsNFVx"

# --- עיצוב ---
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3, p, div, label { text-align: right; }
    .stTextInput > div > div > input { text-align: right; direction: rtl; }
    .stTextArea > div > div > textarea { text-align: right; direction: rtl; }
    .stSelectbox > div > div > div { direction: rtl; text-align: right; }
    
    .stButton>button {
        width: 100%;
        background-color: #FF0000;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        padding: 10px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

st.title("📺 סיכום סרטונים חכם")

# --- הטופס ---
with st.form("summary_form"):
    url = st.text_input("🔗 קישור לסרטון יוטיוב")
    
    col1, col2 = st.columns(2)
    with col1:
        length = st.selectbox("📏 אורך", ["תמציתי", "מפורט", "נקודות"])
    with col2:
        style = st.selectbox("🎨 סגנון", ["מקצועי", "קליל", "לימודי"])
    
    notes = st.text_area("✍️ הערות (אופציונלי)")
    email = st.text_input("📧 לאן לשלוח? (המייל שלך)")
    
    submitted = st.form_submit_button("🚀 סכם ושלח")

if submitted:
    if not url or not email:
        st.warning("⚠️ נא למלא את כל הפרטים")
    else:
        with st.spinner('⏳ מחלץ תמלול...'):
            try:
                # חילוץ ה-ID של הסרטון
                video_id = None
                if "v=" in url:
                    video_id = url.split("v=")[1].split("&")[0]
                elif "youtu.be" in url:
                    video_id = url.split("/")[-1]

                if video_id:
                    # התיקון: שימוש בפקודה הישירה והפ
