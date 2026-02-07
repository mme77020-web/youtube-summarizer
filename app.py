import streamlit as st
import google.generativeai as genai
# ייבוא בטוח עם בדיקה
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi

st.set_page_config(page_title="Gemini Video Summarizer", page_icon="✨", layout="centered")

st.title("✨ סיכום סרטונים עם Gemini")

# --- בדיקת מערכת (רק אם יש שגיאה) ---
try:
    # בדיקה שהספרייה תקינה
    test = YouTubeTranscriptApi.get_transcript
except AttributeError:
    st.error("⚠️ אזהרת מערכת: נטען קובץ לא נכון!")
    st.code(f"הקובץ שנטען: {youtube_transcript_api.__file__}")
    st.stop()

# --- הגדרות ---
with st.sidebar:
    st.header("🔑 הגדרות")
    api_key = st.text_input("Gemini API Key", type="password")

# --- הטופס ---
with st.form("my_form"):
    url = st.text_input("🔗 קישור לסרטון יוטיוב")
    email = st.text_input("📧 אימייל (אופציונלי)")
    col1, col2 = st.columns(2)
    with col1:
        length = st.selectbox("📏 אורך", ["פסקה אחת", "מפורט", "נקודות"])
    with col2:
        style = st.selectbox("🎨 סגנון", ["מקצועי", "קליל", "לימודי"])
    prompt_text = st.text_area("✍️ הערות")
    submitted = st.form_submit_button("🚀 סכם לי")

if submitted:
    if not api_key:
        st.error("חסר מפתח API")
    elif not url:
        st.warning("חסר קישור")
    else:
        with st.spinner('✨ ג\'מיני עובד...'):
            try:
                video_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1]
                
                # הפקודה שנופלת
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['he', 'en'])
                formatter = youtube_transcript_api.formatters.TextFormatter()
                text = formatter.format_transcript(transcript)
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"סכם בעברית: {text[:30000]}. {length}, {style}. {prompt_text}")
                
                st.success("מוכן!")
                st.write(response.text)
                
            except Exception as e:
                st.error("שגיאה:")
                st.write(e)
