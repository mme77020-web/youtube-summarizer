import streamlit as st
import google.generativeai as genai
import subprocess # ספרייה להרצת פקודות מערכת
import json
import sys

st.set_page_config(page_title="Gemini Video Summarizer", page_icon="✨", layout="centered")

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

# --- הגדרות ---
with st.sidebar:
    st.header("🔑 הגדרות")
    api_key = st.text_input("Gemini API Key", type="password")

# --- פונקציית עקיפה (Bypass) ---
def get_transcript_via_cli(video_id):
    """
    מריץ את תמלול היוטיוב כפקודת מערכת נפרדת
    כדי לעקוף את בעיות ה-Cache וה-Import בתוך פייתון
    """
    try:
        # הרצת הפקודה מבחוץ
        cmd = [
            sys.executable, "-m", "youtube_transcript_api",
            video_id,
            "--languages", "he", "en",
            "--format", "json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"שגיאה חיצונית: {result.stderr}")
            
        # המרת התשובה מ-JSON לטקסט רגיל
        transcript_json = json.loads(result.stdout)
        full_text = " ".join([item['text'] for item in transcript_json])
        return full_text
        
    except Exception as e:
        raise e

# --- הטופס ---
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

if submitted:
    if not api_key:
        st.error("❌ חסר מפתח API. נא להזין אותו בתפריט בצד.")
    elif not url:
        st.warning("⚠️ נא להכניס קישור.")
    else:
        status = st.empty()
        try:
            status.info("📥 מחלץ כתוביות (בשיטה חיצונית)...")
            
            # חילוץ ID
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be" in url:
                video_id = url.split("/")[-1]
            else:
                video_id = url # נסיון למקרה שהזינו רק ID
            
            # שימוש בפונקציה החדשה שעוקפת את הבעיה
            full_text = get_transcript_via_cli(video_id)
            
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

        except Exception as e:
            st.error("אירעה שגיאה:")
            st.code(str(e))
            if "Could not retrieve a transcript" in str(e):
                st.warning("הסרטון הזה לא מכיל כתוביות זמינות.")
