import streamlit as st
# שינוי קריטי: ייבוא הפונקציה הספציפית ישירות
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import requests

st.set_page_config(page_title="YouTube Summarizer", layout="centered")

# --- שים כאן את הכתובת שלך ---
webhook_url = "PASTE_YOUR_WEBHOOK_URL_HERE"

st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3, p, div, span, label { text-align: right; }
    .stTextInput > div > div > input { text-align: right; direction: rtl; }
    .stSelectbox > div > div > div { direction: rtl; text-align: right; }
    .stTextArea > div > div > textarea { text-align: right; direction: rtl; }
    .stButton>button {
        width: 100%;
        background-color: #FF0000;
        color: white;
        border-radius: 10px;
        padding: 10px;
        border: none;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("📺 סיכום סרטונים חכם")

with st.form("summary_form"):
    url = st.text_input("🔗 קישור ליוטיוב")
    col1, col2 = st.columns(2)
    with col1:
        length = st.selectbox("📏 אורך", ["תמציתי", "מפורט", "נקודות"])
    with col2:
        style = st.selectbox("🎨 סגנון", ["מקצועי", "קליל", "לימודי"])
    notes = st.text_area("✍️ הערות")
    email = st.text_input("📧 אימייל")
    submitted = st.form_submit_button("🚀 סכם ושלח")

if submitted:
    if not url or not email:
        st.error("נא למלא את כל הפרטים")
    else:
        with st.spinner('מחלץ תמלול...'):
            try:
                video_id = None
                if "v=" in url:
                    video_id = url.split("v=")[1].split("&")[0]
                elif "youtu.be" in url:
                    video_id = url.split("/")[-1]

                if video_id:
                    # שימוש בפונקציה הישירה שיבאנו למעלה
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['he', 'en'])
                    
                    formatter = TextFormatter()
                    text_data = formatter.format_transcript(transcript)
                    
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
                        st.success("נשלח בהצלחה!")
                        st.balloons()
                    else:
                        st.error(f"שגיאה: {response.status_code}")
                else:
                    st.error("קישור לא תקין")
            except Exception as e:
                st.error("שגיאה בחילוץ התמלול:")
                st.write(e)
