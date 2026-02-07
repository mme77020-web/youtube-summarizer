import streamlit as st
# שימוש בייבוא המלא והבטוח ביותר
import youtube_transcript_api
from youtube_transcript_api.formatters import TextFormatter
import google.generativeai as genai

# הגדרת העמוד
st.set_page_config(page_title="Gemini Video Summarizer", page_icon="✨", layout="centered")

# עיצוב לימין-שמאל
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3, p, div, span, label, .stMarkdown { text-align: right; }
    .stTextInput > div > div > input { text-align: right; direction: rtl; }
    .stTextArea > div > div > textarea { text-align: right; direction: rtl; }
    .stSelectbox > div > div > div { direction: rtl; text-align: right; }
    .stButton>button {
        width: 100%;
        background-color: #4b8bf5;
        color: white;
        border-radius: 10px;
        padding: 10px;
        font-weight: bold;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ סיכום סרטונים עם Gemini")

# תפריט צד למפתח
with st.sidebar:
    st.header("הגדרות")
    api_key = st.text_input("Gemini API Key", type="password")

# הטופס
with st.form("my_form"):
    url = st.text_input("🔗 קישור לסרטון יוטיוב")
    email = st.text_input("📧 אימייל לשליחת הסיכום (אופציונלי)")
    
    col1, col2 = st.columns(2)
    with col1:
        length = st.selectbox("📏 אורך", ["פסקה אחת", "סיכום מפורט", "נקודות"])
    with col2:
        style = st.selectbox("🎨 סגנון", ["מקצועי", "קליל", "לימודי"])
        
    prompt_text = st.text_area("✍️ בקשות מיוחדות")
    submitted = st.form_submit_button("🚀 סכם לי!")

if submitted:
    if not api_key:
        st.error("❌ חסר מפתח API בצד ימין (בהגדרות).")
    elif not url:
        st.warning("⚠️ נא להכניס קישור.")
    else:
        status = st.empty()
        try:
            status.info("📥 מחלץ טקסט...")
            
            # חילוץ מזהה סרטון בצורה בטוחה
            video_id = None
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be" in url:
                video_id = url.split("/")[-1]
            
            if video_id:
                # הקריאה הבטוחה ביותר לספרייה
                transcript_list = youtube_transcript_api.YouTubeTranscriptApi.get_transcript(video_id, languages=['he', 'en'])
                
                # המרת הרשימה לטקסט
                formatter = TextFormatter()
                full_text = formatter.format_transcript(transcript_list)
                
                status.info("✨ ג'מיני חושב...")
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # הבקשה ל-AI
                prompt = f"""
                תפקידך לסכם את הטקסט הבא מסרטון יוטיוב בעברית.
                
                הטקסט:
                {full_text[:30000]}
                
                הנחיות:
                1. אורך: {length}
                2. סגנון: {style}
                3. הערות: {prompt_text}
                4. חשוב: כתוב את התשובה בעברית בלבד.
                """
                
                response = model.generate_content(prompt)
                summary_text = response.text
                
                status.empty()
                st.success("הסיכום מוכן!")
                
                # הצגה על המסך
                st.markdown("### 📝 התוצאה:")
                st.write(summary_text)
                
                # כפתור ליצירת מייל (כי אין לנו שרת מייל לשליחה אוטומטית)
                if email:
                    subject = "סיכום סרטון יוטיוב"
                    body = summary_text.replace('\n', '%0D%0A') # התאמה למייל
                    mailto_link = f"mailto:{email}?subject={subject}&body={body}"
                    st.markdown(f'<a href="{mailto_link}" target="_blank" style="text-decoration:none;"><button style="background-color:green;color:white;padding:10px;border-radius:5px;width:100%;border:none;cursor:pointer;">📧 לחץ כאן לפתיחת המייל עם הסיכום</button></a>', unsafe_allow_html=True)

            else:
                st.error("לא הצלחנו לזהות את ה-ID של הסרטון.")
                
        except Exception as e:
            st.error("שגיאה:")
            st.write(e)
            if "NoTranscriptFound" in str(e):
                st.warning("טיפ: לסרטון הזה אין כתוביות זמינות ביוטיוב.")
