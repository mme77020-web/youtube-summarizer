import streamlit as st
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi # ניסיון ייבוא ישיר
from youtube_transcript_api.formatters import TextFormatter
import requests

# --- הגדרות עמוד ועיצוב ---
st.set_page_config(page_title="YouTube Summarizer", page_icon="📺", layout="centered")

# --- וודא שאתה שם כאן את הכתובת שלך! ---
webhook_url = "PASTE_YOUR_WEBHOOK_URL_HERE"

# --- עיצוב CSS ---
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3, p, div { text-align: right; }
    .stTextInput input { text-align: right; direction: rtl; }
    .stButton>button {
        width: 100%;
        background-color: #FF0000;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        padding: 10px;
        border: none;
    }
    div[data-testid="stForm"] {
        background-color: #f9f9f9;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #FF0000;'>📺 סיכום סרטונים חכם</h1>", unsafe_allow_html=True)

# --- הטופס ---
with st.form("summary_form"):
    st.markdown("### 📝 פרטי הבקשה")
    url = st.text_input("🔗 קישור לסרטון יוטיוב")
    
    col1, col2 = st.columns(2)
    with col1:
        length = st.selectbox("📏 אורך", ["תמציתי", "מפורט", "נקודות"])
    with col2:
        style = st.selectbox("🎨 סגנון", ["מקצועי", "קליל", "לימודי"])
    
    notes = st.text_area("✍️ הערות")
    email = st.text_input("📧 לאן לשלוח? (כתובת המייל שלך)")
    
    submitted = st.form_submit_button("🚀 סכם ושלח למייל")

if submitted:
    if not url or not email:
        st.warning("⚠️ נא למלא קישור ומייל")
    else:
        with st.spinner('⏳ עובד על זה...'):
            try:
                # חילוץ ID
                if "v=" in url:
                    video_id = url.split("v=")[1].split("&")[0]
                elif "youtu.be" in url:
                    video_id = url.split("/")[-1]
                else:
                    video_id = None

                if video_id:
                    # --- התיקון נמצא כאן ---
                    # שימוש בייבוא המלא והבטוח ביותר
                    transcript = youtube_transcript_api.YouTubeTranscriptApi.get_transcript(video_id, languages=['he', 'en'])
                    
                    formatter = TextFormatter()
                    text_data = formatter.format_transcript(transcript)
                    
                    # שליחה
                    payload = {
                        "transcript": text_data,
                        "user_email": email,
                        "summary_length": length,
                        "style": style,
                        "special_instructions": notes,
                        "video_url": url
                    }
                    
                    response = requests.post(webhook_url, json=payload)
                    
                    if response.status_code == 200:
                        st.balloons()
                        st.success(f"✅ נשלח בהצלחה ל-{email}!")
                    else:
                        st.error(f"שגיאה בשליחה: {response.status_code}")
                else:
                    st.error("קישור לא תקין")
                    
            except Exception as e:
                st.error(f"תקלה: {e}")
                st.info("טיפ: נסה לוודא שלסרטון יש כתוביות.")
