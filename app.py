import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

st.set_page_config(page_title="Gemini Video Summarizer", page_icon="✨", layout="centered")

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

with st.form("my_form"):
    url = st.text_input("🔗 קישור לסרטון יוטיוב")
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
            video_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1]
            
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['he', 'en'])
            full_text = " ".join([d['text'] for d in transcript_list])
            
            status.info("✨ ג'מיני חושב...")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(f"סכם בעברית: {full_text[:30000]}. אורך: {length}, סגנון: {style}. {prompt_text}")
            
            status.empty()
            st.success("הסיכום מוכן!")
            st.write(response.text)
            
        except Exception as e:
            st.error(f"שגיאה: {e}")
