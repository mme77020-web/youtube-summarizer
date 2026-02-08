import streamlit as st
import yt_dlp
import google.generativeai as genai
import os

# --- הגדרות עיצוב ---
st.set_page_config(page_title="Gemini Video Summarizer", page_icon="✨", layout="centered")

st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3, p, div, span, label, .stMarkdown { text-align: right; }
    .stTextInput > div > div > input { text-align: right; direction: rtl; }
    .stTextArea > div > div > textarea { text-align: right; direction: rtl; }
    .stSelectbox > div > div > div { direction: rtl; text-align: right; }
    .stButton>button {
        background-color: #ff4b4b; color: white; border-radius: 10px; padding: 10px; border: none; width: 100%; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ סיכום סרטונים (מנוע yt-dlp)")

# --- פונקציית העל: הורדת כתוביות ---
def download_subs_clean(url):
    # הגדרות למנוע ההורדה: רק כתוביות, בלי וידאו
    ydl_opts = {
        'skip_download': True,      # לא להוריד את הסרטון עצמו
        'writesubtitles': True,     # כן להוריד כתוביות רגילות
        'writeautomaticsub': True,  # כן להוריד כתוביות אוטומטיות
        'subtitleslangs': ['he', 'en'], # עדיפות לעברית, ואז אנגלית
        'outtmpl': 'temp_subs_%(id)s',  # שם הקובץ הזמני
        'quiet': True,
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_id = info['id']
            
            # ביצוע ההורדה בפועל
            ydl.download([url])
            
            # חיפוש הקובץ שנוצר (יכול להיות עם סיומות שונות)
            generated_files = [f for f in os.listdir('.') if f.startswith(f"temp_subs_{video_id}") and f.endswith('.vtt')]
            
            if not generated_files:
                return None
            
            filename = generated_files[0]
            
            # קריאת הטקסט מתוך הקובץ
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # ניקוי הקובץ מהמחשב (לא להשאיר זבל)
            os.remove(filename)
            
            # ניקוי בסיסי של הטקסט (הסרת זמנים ותגיות)
            clean_lines = []
            for line in content.splitlines():
                if '-->' in line: continue         # דילוג על זמנים
                if line.strip() == '': continue    # דילוג על שורות ריקות
                if line.strip() == 'WEBVTT': continue
                if line.strip().isdigit(): continue
                # הסרת תגיות עיצוב אם יש
                line = line.replace('&nbsp;', ' ').replace('align:start', '').replace('position:0%', '')
                if line not in clean_lines[-2:]: # מניעת כפילויות רצופות
                    clean_lines.append(line)
                    
            return " ".join(clean_lines)

    except Exception as e:
        return f"Error: {str(e)}"

# --- הגדרות מפתח ---
with st.sidebar:
    st.header("🔑 הגדרות")
    api_key = st.text_input("Gemini API Key", type="password")

# --- הטופס ---
with st.form("my_form"):
    url = st.text_input("🔗 קישור לסרטון יוטיוב")
    col1, col2 = st.columns(2)
    with col1:
        length = st.selectbox("📏 אורך", ["פסקה אחת", "סיכום מפורט", "נקודות עיקריות"])
    with col2:
        style = st.selectbox("🎨 סגנון", ["מקצועי", "קליל", "לימודי"])
    prompt_text = st.text_area("✍️ בקשות מיוחדות")
    submitted = st.form_submit_button("🚀 סכם לי")

# --- הלוגיקה ---
if submitted:
    if not api_key:
        st.error("חסר מפתח API (בצד ימין)")
    elif not url:
        st.warning("חסר קישור")
    else:
        status = st.empty()
        status.info("🚜 מפעיל מנוע yt-dlp להורדת טקסט...")
        
        # שימוש במנוע החדש
        text = download_subs_clean(url)
        
        if text and "Error:" not in text:
            status.info("✨ ג'מיני מסכם...")
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                ai_prompt = f"""
                סכם את הטקסט הבא מסרטון יוטיוב בעברית.
                הטקסט גולמי ומכיל שגיאות תמלול - התעלם מהן והתמקד בתוכן.
                
                תוכן: {text[:30000]}
                
                הנחיות: אורך: {length}, סגנון: {style}. {prompt_text}
                """
                
                response = model.generate_content(ai_prompt)
                
                status.empty()
                st.success("הסיכום מוכן!")
                st.markdown("### 📝 התוצאה:")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"שגיאה בג'מיני: {e}")
        else:
            status.empty()
            st.error("לא הצלחנו להוריד כתוביות.")
            if text:
                st.error(f"פרטים טכניים: {text}")
            st.warning("טיפ: וודא שלסרטון יש כתוביות (CC) פעילות ביוטיוב.")
