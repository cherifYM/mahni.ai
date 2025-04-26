import streamlit as st
st.set_page_config(page_title="منصة مهني – Mahni.ai", layout="centered")

# بعد التهيئة نبدأ الاستيرادات
import pdfplumber
import requests
from pages.personality_test import run_test
from profile_page import show_profile

# سايدبار للتنقل بين الصفحات
st.sidebar.title("🚀 القائمة")
page = st.sidebar.selectbox("اختر الصفحة", [
    "📄 محلل السيرة الذاتية",
    "🧠 اختبار الشخصية",
    "👤 صفحتي"
])

if page == "📄 محلل السيرة الذاتية":
    language = st.selectbox("اختر اللغة / Choose Language", ["العربية", "English"])
    st.title("📄 Mahni – محلل السيرة الذاتية")
    st.markdown("ارفع سيرتك الذاتية..." if language == "العربية" else "Upload your resume in PDF...")

    uploaded_file = st.file_uploader("⬆️ ارفع السيرة الذاتية هنا" if language == "العربية" else "Upload your Resume", type="pdf")
    text = ""
    if uploaded_file:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        st.success("تم استخراج النص ✅" if language == "العربية" else "Text extracted ✅")

    if text and st.button("🚀 ابدأ التحليل" if language == "العربية" else "🚀 Start Analysis"):
        prompt_ar = f"""هذا نص سيرة ذاتية:\n{text}\nحلل السيرة وقدم: نقاط القوة، نقاط الضعف، المجال المهني الأنسب، والمهارات الناقصة مع اقتراح دورات مناسبة."""
        prompt_en = f"""This is a resume:\n{text}\nAnalyze it and provide: strengths, weaknesses, best-fit career field, missing skills with recommended courses."""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": prompt_ar if language == "العربية" else prompt_en, "stream": False}
            )
            result = response.json()["response"]
            st.markdown("### ✅ التحليل:" if language == "العربية" else "### ✅ Analysis Result:")
            st.write(result)
        except Exception as e:
            st.error(f"❌ Error during analysis: {e}")

elif page == "🧠 اختبار الشخصية":
    run_test()

elif page == "👤 صفحتي":
    show_profile()
