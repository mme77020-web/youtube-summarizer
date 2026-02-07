import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import requests
import re

# --- כאן מדביקים את הכתובת מ-Activepieces ---
webhook_url = "https://cloud.activepieces.com/api/v1/webhooks/HDSgK2B66mVb6nQSsNFVx" 

def get_video_id(url):
    # פונקציה פשוטה לחילוץ מזהה סרטון
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("/")[-1]
    return None

st.title("סיכום סרטוני יוטיוב במייל 📧")

# קבלת נתונים מהמשתמש
url = st.text_input("הכנס קישור ליוטיוב:")
email = st.text_input("לאיזה מייל לשלוח את הסיכום?")
length = st.selectbox("אורך הסיכום", ["קצר", "בינוני", "ארוך"])
style = st.selectbox("סגנון", ["רשמי", "קליל", "לסיכום שיעור"])
notes = st.text_area("הערות מיוחדות (אופציונלי)")

if st.button("סכם לי את הסרטון!"):
    if not url or not email:
        st.error("חובה להכניס קישור ומייל")
    else:
        video_id = get_video_id(url)
        if not video_id:
            st.error("קישור לא תקין")
        else:
            st.info("מחלץ תמלול... אנא המתן")
            try:
                # משיכת התמלול
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['he', 'en'])
                formatter = TextFormatter()
                text_data = formatter.format_transcript(transcript)

                st.success("התמלול חולץ! שולח ל-Activepieces לעיבוד...")

                # שליחת הנתונים לאוטומציה
                payload = {
                    "transcript": text_data,
                    "user_email": email,
                    "summary_length": length,
                    "style": style,
                    "special_instructions": notes
                }

                requests.post(webhook_url, json=payload)
                st.balloons()
                st.success(f"הבקשה נשלחה! בדוק את המייל {email} בעוד דקה.")

            except Exception as e:
                st.error(f"שגיאה: {e}")
                st.warning("הערה: סרטונים ללא כתוביות לא יעבדו.")
