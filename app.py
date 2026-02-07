import streamlit as st
# שימוש בכינוי (alias) כדי למנוע בלבול בשמות
from youtube_transcript_api import YouTubeTranscriptApi as YTApi
from youtube_transcript_api.formatters import TextFormatter
import requests

# --- הגדרות עמוד ---
st.set_page_config(page_title="YouTube Summarizer", page_icon="📺", layout="centered")

# --- הזן את הכתובת שלך כאן ---
webhook_url = "https://cloud.activepieces.com/api/v1/webhooks/HDSgK2B66mVb6nQSsNFVx"

# --- עיצוב ---
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
                    # שימוש בשם החדש והפשוט (YTApi)
                    transcript = YTApi.get_transcript(video_id, languages=['he', 'en'])
                    
                    formatter = TextFormatter()
                    text_data = formatter.format_transcript(transcript)
                    
                    # שליחה ל-Activepieces
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
                        st.success(f"✅ הצלחנו! הסיכום בדרך למייל: {email}")
                        st.balloons()
                    else:
                        st.error(f"שגיאה בשליחה לאוטומציה: {response.status_code}")
                else:
                    st.error("❌ הקישור לא תקין")
            
            except Exception as e:
                st.error("😓 שגיאה בחילוץ התמלול:")
                st.code(str(e)) # יציג את השגיאה המדויקת באנגלית
                st.info("טיפ: וודא שלסרטון יש כתוביות (CC) זמינות ביוטיוב.")
