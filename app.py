import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import requests

# --- הגדרות עמוד ועיצוב ---
st.set_page_config(page_title="YouTube Summarizer", page_icon="📺", layout="centered")

# --- כאן מדביקים את הכתובת מ-Activepieces ---
webhook_url = "PASTE_YOUR_WEBHOOK_URL_HERE"

# --- עיצוב CSS מותאם אישית ---
st.markdown("""
<style>
    /* יישור לימין לכל האתר */
    .stApp {
        direction: rtl;
        text-align: right;
    }
    
    /* כותרות */
    h1, h2, h3 {
        text-align: right; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* תיבות קלט */
    .stTextInput input {
        text-align: right;
        direction: rtl;
    }

    /* כפתור ראשי מעוצב */
    .stButton>button {
        width: 100%;
        background-color: #FF0000;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        padding: 10px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #cc0000;
        color: white;
    }

    /* כרטיסייה למרכז המסך */
    div[data-testid="stForm"] {
        background-color: #f9f9f9;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #ddd;
    }
    
    /* התאמה למצב לילה (אם המשתמש במצב כהה) */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stForm"] {
            background-color: #262730;
            border: 1px solid #444;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- כותרת ראשית ---
st.markdown("<h1 style='text-align: center; color: #FF0000;'>📺 סיכום סרטונים חכם</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em;'>הדבק קישור, קבל סיכום למייל, וחסוך זמן יקר.</p>", unsafe_allow_html=True)
st.write("---")

# --- הטופס המעוצב ---
with st.form("summary_form"):
    st.markdown("### 📝 פרטי הבקשה")
    
    url = st.text_input("🔗 קישור לסרטון יוטיוב")
    
    col1, col2 = st.columns(2)
    with col1:
        length = st.selectbox("📏 אורך הסיכום", ["תמציתי (פסקה)", "מפורט (כולל דוגמאות)", "נקודות עיקריות (Bullepoints)"])
    with col2:
        style = st.selectbox("🎨 סגנון כתיבה", ["מקצועי וענייני", "קליל והומוריסטי", "לימודי (כמו סיכום שיעור)", "לילדים"])
    
    notes = st.text_area("✍️ הערות מיוחדות (אופציונלי)", placeholder="למשל: תתמקד רק בחלק שמדבר על AI...")
    
    st.markdown("### 📧 לאן לשלוח?")
    email = st.text_input("כתובת המייל שלך")
    
    submitted = st.form_submit_button("🚀 סכם ושלח למייל")

# --- לוגיקה (מה קורה כשלוחצים) ---
if submitted:
    if not url or not email:
        st.warning("⚠️ נא למלא קישור וכתובת מייל.")
    else:
        with st.spinner('⏳ מחלץ תמלול ושולח למעבדת ה-AI...'):
            try:
                # חילוץ ID
                video_id = None
                if "v=" in url:
                    video_id = url.split("v=")[1].split("&")[0]
                elif "youtu.be" in url:
                    video_id = url.split("/")[-1]

                if video_id:
                    # משיכת תמלול
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['he', 'en'])
                    formatter = TextFormatter()
                    text_data = formatter.format_transcript(transcript)
                    
                    # הכנת המידע
                    payload = {
                        "transcript": text_data,
                        "user_email": email,
                        "summary_length": length,
                        "style": style,
                        "special_instructions": notes,
                        "video_url": url
                    }
                    
                    # שליחה ל-Webhook
                    response = requests.post(webhook_url, json=payload)
                    
                    if response.status_code == 200:
                        st.balloons()
                        st.success(f"✅ מעולה! הסיכום נשלח לעיבוד ויגיע ל-{email} בדקות הקרובות.")
                    else:
                        st.error(f"שגיאה בשליחה: {response.status_code}")
                else:
                    st.error("❌ הקישור שהזנת אינו תקין.")
                    
            except Exception as e:
                st.error("😓 לא הצלחנו לחלץ את הטקסט מהסרטון. ייתכן שאין לו כתוביות.")
                st.info(f"פרטי שגיאה טכניים: {e}")
