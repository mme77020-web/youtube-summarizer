import streamlit as st
import google.generativeai as genai

# --- התיקון הגדול: ייבוא דרך "דלת השירות" ---
# במקום לייבא מהתיקייה הראשית, אנחנו נכנסים ישר לתוך המנוע
try:
    from youtube_transcript_api._api import YouTubeTranscriptApi
except ImportError:
    # גיבוי למקרה שהשם שונה בגרסאות אחרות
    from youtube_transcript_api import YouTubeTranscriptApi

from youtube_transcript_api.formatters import TextFormatter

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
            status.info("📥 מחלץ כתוביות...")
            
            # חילוץ מזהה הסרטון
            video_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1]
            
            # השימוש בפונקציה הישירה
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
                
        except Exception as e:
            st.error("שגיאה:")
            st.code(e)
            if "TranscriptsDisabled" in str(e):
                st.warning("לסרטון הזה אין כתוביות ולכן אי אפשר לסכם אותו.")
