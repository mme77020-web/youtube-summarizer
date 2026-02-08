import streamlit as st
import os
import sys
import shutil

# --- הגדרות עמוד ---
st.set_page_config(page_title="Gemini Video Summarizer", page_icon="✨", layout="centered")

# --- חלק 1: ניקוי עצמי ותיקון אוטומטי ---
# הקוד הזה רץ לפני הכל ובודק אם יש קבצים שמפריעים
if os.path.exists("youtube_transcript_api.py"):
    try:
        os.remove("youtube_transcript_api.py")
        st.toast("🗑️ קובץ מתנגש נמחק אוטומטית!", icon="✅")
    except:
        st.error("יש קובץ בשם youtube_transcript_api.py שחוסם אותנו. אנא מחק אותו ידנית.")

# --- חלק 2: ייבוא חכם ---
try:
    # מנסים לייבא מהמקום הכי עמוק וישיר בספרייה כדי לעקוף בלבולים
    from youtube_transcript_api._api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
except ImportError:
    # אם זה נכשל, מנסים להתקין מחדש תוך כדי ריצה
    st.warning("מתקן את ההתקנה... (זה ייקח רגע)")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-transcript-api"])
    from youtube_transcript_api._api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter

import google.generativeai as genai

# --- חלק 3: עיצוב האתר ---
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3, p, div, span, label, .stMarkdown { text-align: right; }
    .stTextInput > div > div > input { text-align: right; direction: rtl; }
    .stTextArea > div > div > textarea { text-align: right; direction: rtl; }
    .stSelectbox > div > div > div { direction: rtl; text-align: right; }
    .stButton>button {
        background-color: #4b8bf5; color: white; border-radius: 10px; padding: 10px; border: none; width: 100%; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ סיכום סרטונים עם Gemini")

# --- חלק 4: הגדרות (Sidebar) ---
with st.sidebar:
    st.header("🔑 הגדרות")
    api_key = st.text_input("Gemini API Key", type="password")

# --- חלק 5: הטופס ---
with st.form("my_form"):
    url = st.text_input("🔗 קישור לסרטון יוטיוב")
    email = st.text_input("📧 אימייל (אופציונלי)")
    
    col1, col2 = st.columns(2)
    with col1:
        length = st.selectbox("📏 אורך", ["פסקה אחת", "סיכום מפורט", "נקודות עיקריות"])
    with col2:
        style = st.selectbox("🎨 סגנון", ["מקצועי", "קליל", "לימודי"])
        
    prompt_text = st.text_area("✍️ הערות")
    submitted = st.form_submit_button("🚀 סכם לי")

# --- חלק 6: הלוגיקה ---
if submitted:
    if not api_key:
        st.error("❌ חסר מפתח API. נא להזין אותו בתפריט בצד.")
    elif not url:
        st.warning("⚠️ נא להכניס קישור.")
    else:
        status = st.empty()
        try:
            status.info("📥 מחלץ כתוביות...")
            
            # חילוץ מזהה הסרטון
            video_id = None
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be" in url:
                video_id = url.split("/")[-1]
            else:
                video_id = url

            if video_id:
                # שימוש בפונקציה שיבאנו בצורה ישירה
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['he', 'en'])
                
                formatter = TextFormatter()
                full_text = formatter.format_transcript(transcript)
                
                status.info("✨ ג'מיני חושב...")
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                ai_prompt = f"""
                סכם את הטקסט הבא מסרטון יוטיוב בעברית.
                טקסט: {full_text[:30000]}
                הנחיות: אורך: {length}, סגנון: {style}. {prompt_text}
                """
                
                response = model.generate_content(ai_prompt)
                summary = response.text
                
                status.empty()
                st.success("הסיכום מוכן!")
                st.markdown("### 📝 התוצאה:")
                st.write(summary)
                
                if email:
                    subject = "סיכום סרטון: " + video_id
                    safe_body = summary.replace('\n', '%0D%0A').replace('"', "'")
                    mailto = f"mailto:{email}?subject={subject}&body={safe_body}"
                    st.markdown(f'<a href="{mailto}" target="_blank"><button style="background-color:green;color:white;padding:10px;border-radius:5px;border:none;width:100%;cursor:pointer;">📧 שלח למייל שלי</button></a>', unsafe_allow_html=True)
            else:
                st.error("קישור לא תקין")

        except Exception as e:
            # דיאגנוסטיקה: אם זה נכשל שוב, נדפיס בדיוק מה יש בתוך הספרייה
            st.error("אירעה שגיאה:")
            st.code(str(e))
            
            if "get_transcript" in str(e):
                st.warning("🔧 בדיקת מערכת:")
                st.write(f"הספרייה נטענה מתוך: {YouTubeTranscriptApi}")
                st.write("אנא שלח צילום מסך של הודעה זו כדי שנוכל לפתור את זה.")
            elif "TranscriptsDisabled" in str(e):
                st.warning("לסרטון הזה אין כתוביות זמינות ביוטיוב.")
