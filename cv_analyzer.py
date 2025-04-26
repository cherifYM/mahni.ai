import streamlit as st
import pdfplumber
import json
import os
import datetime
from fpdf import FPDF
from sqlalchemy import create_engine, text

st.set_page_config(page_title="تحليلك المهني الكامل – مهني.ai", layout="wide")
st.title("🔍 منصة مهني.ai – تحليلك المهني الكامل")

# إعداد قاعدة البيانات
engine = create_engine("sqlite:///mahni_data.db", echo=False)

def get_mbti_by_name(user_name):
    if not user_name.strip():
        return None
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT mbti_type FROM personality_results WHERE name = :name ORDER BY id DESC LIMIT 1"),
            {"name": user_name.strip()}
        )
        row = result.fetchone()
        return row[0] if row else None

# إدخال الاسم
name = st.text_input("🧾 أدخل اسمك الكامل:")

# إدخال السيرة الذاتية
option = st.radio("اختر طريقة الإدخال:", ["✍️ كتابة", "📁 رفع PDF", "📄 الاثنين"])
cv_text = ""

if option in ["✍️ كتابة", "📄 الاثنين"]:
    cv_input = st.text_area("📝 أدخل سيرتك الذاتية هنا", height=200)
    cv_text += cv_input + "\n"

if option in ["📁 رفع PDF", "📄 الاثنين"]:
    pdf_file = st.file_uploader("📁 ارفع ملف سيرتك الذاتية PDF", type="pdf")
    if pdf_file:
        with pdfplumber.open(pdf_file) as pdf:
            extracted = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
            cv_text += extracted
        st.success("✅ تم استخراج النص بنجاح")

# تحليل السيرة الذاتية
def analyze_resume(text):
    strengths, weaknesses = [], []
    if "python" in text.lower():
        strengths.append("إجادة Python")
    else:
        weaknesses.append("ينقصك Python")

    if "sql" in text.lower():
        strengths.append("خبرة في SQL")
    else:
        weaknesses.append("ينقصك SQL")

    if "project" in text.lower():
        strengths.append("إدارة المشاريع")
    else:
        weaknesses.append("قلة خبرة في إدارة المشاريع")

    return strengths, weaknesses

def get_recommendations(text):
    roles = []
    if "data" in text.lower():
        roles.append("Data Analyst")
    if "ai" in text.lower() or "machine learning" in text.lower():
        roles.append("AI Engineer")
    if "project" in text.lower():
        roles.append("Project Manager")
    return roles

if cv_text.strip():
    strengths, weaknesses = analyze_resume(cv_text)
    recommendations = get_recommendations(cv_text)
else:
    strengths, weaknesses, recommendations = [], [], []

# وظائف افتراضية
jobs = [
    {"title": "Data Analyst", "company": "TechBridge", "location": "Toronto", "apply": "https://example.com"},
    {"title": "AI Developer", "company": "SmartAI", "location": "Remote", "apply": "https://example.com"},
    {"title": "Business Analyst", "company": "FinTechX", "location": "Vancouver", "apply": "https://example.com"}
]

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.add_font('Amiri', '', './assets/fonts/Amiri-Regular.ttf', uni=True)
        self.set_font('Amiri', '', 14)

    def rtl(self, text):
        return text[::-1]

    def chapter_title(self, title):
        self.cell(0, 10, self.rtl(str(title)), ln=True, align='R')

    def chapter_body(self, body):
        self.multi_cell(0, 10, self.rtl(str(body)))

def export_to_pdf(name, strengths, weaknesses, recommendations, jobs):
    pdf = PDF()
    pdf.chapter_title(f"تحليل مهني – {str(name)}")
    pdf.ln(10)

    pdf.chapter_body("نقاط القوة:")
    for s in strengths:
        pdf.chapter_body(f"- {str(s)}")
    pdf.ln(5)

    pdf.chapter_body("نقاط الضعف:")
    for w in weaknesses:
        pdf.chapter_body(f"- {str(w)}")
    pdf.ln(5)

    pdf.chapter_body("التوصيات المهنية:")
    for r in recommendations:
        pdf.chapter_body(f"- {str(r)}")
    pdf.ln(5)

    pdf.chapter_body("وظائف مقترحة:")
    for j in jobs:
        pdf.chapter_body(f"- {str(j['title'])} في {str(j['company'])} – {str(j['location'])}")

    file_path = f"{name}_career_report.pdf"
    pdf.output(file_path)
    return file_path

# واجهة التبويبات
tabs = st.tabs(["💪 نقاط القوة", "⚠️ نقاط الضعف", "🎯 التوصيات المهنية", "💼 الوظائف المقترحة", "🎭 اختبار الشخصية", "📄 تحميل التقرير"])

with tabs[0]:
    st.subheader("💪 نقاط القوة")
    if strengths:
        for s in strengths:
            st.success(f"✅ {s}")
    else:
        st.info("🤷‍♂️ لا توجد نقاط قوة واضحة.")

with tabs[1]:
    st.subheader("⚠️ نقاط الضعف")
    if weaknesses:
        for w in weaknesses:
            st.error(f"🔻 {w}")
    else:
        st.info("👏 لا توجد نقاط ضعف واضحة.")

with tabs[2]:
    st.subheader("🎯 التوصيات المهنية")
    if recommendations:
        for r in recommendations:
            st.markdown(f"- 🔹 {r}")
    else:
        st.info("🤔 لم يتم العثور على توصيات بناءً على سيرتك الذاتية.")

with tabs[3]:
    st.subheader("💼 الوظائف المقترحة")
    for job in jobs:
        st.markdown(f"""**{job['title']}** – {job['company']}  
📍 {job['location']}  
🔗 [قدّم الآن]({job['apply']})
---""")

with tabs[4]:
    st.subheader("🎭 اختبار الشخصية")
    st.link_button("🎭 ابدأ اختبار شخصيتك", "🎭 اختبار الشخصية")

with tabs[5]:
    st.subheader("📄 تحميل تقرير التحليل المهني")
    if st.button("⬇️ تحميل التقرير"):
        if not name.strip():
            st.warning("⚠️ من فضلك أدخل اسمك الكامل أولاً.")
        else:
            try:
                filename = export_to_pdf(name, strengths, weaknesses, recommendations, jobs)
                with open(filename, "rb") as f:
                    st.download_button("📥 اضغط هنا لتحميل التقرير", f, file_name=filename)
            except Exception as e:
                st.error(f"🚨 حصل خطأ أثناء توليد التقرير: {e}")
