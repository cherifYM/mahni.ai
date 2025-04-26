import streamlit as st
import json
from sqlalchemy import create_engine, Column, String, Integer, MetaData, Table
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="اختبار الشخصية – مهني.ai", page_icon="🧠")

# إعداد قاعدة البيانات
engine = create_engine("sqlite:///mahni_data.db", echo=False)
metadata = MetaData()

results_table = Table(
    "personality_results", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("mbti_type", String, nullable=False),
    Column("timestamp", String, nullable=False)
)
metadata.create_all(engine)

def calculate_mbti(questions, answers):
    scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    for q, ans in zip(questions, answers):
        if ans.startswith("A"):
            scores[q["key_A"]] += 1
        else:
            scores[q["key_B"]] += 1
    return "".join([
        "E" if scores["E"] > scores["I"] else "I",
        "S" if scores["S"] > scores["N"] else "N",
        "T" if scores["T"] > scores["F"] else "F",
        "J" if scores["J"] > scores["P"] else "P"
    ])

def run_test():
    st.title("🧠 اختبار نمط الشخصية – مهني.ai")
    user_name = st.text_input("🧾 أدخل اسمك الكامل لاختبار الشخصية:")

    with open("questions_mbti.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    answers = []
    progress = st.progress(0)

    for i, q in enumerate(questions, 1):
        st.markdown(f"### {q['text']}")
        answer = st.radio("", q["options"], key=f"q_{i}")
        answers.append(answer)
        progress.progress(i / len(questions))

    if st.button("🔍 إظهار النتيجة") and user_name.strip():
        mbti_type = calculate_mbti(questions, answers)
        with engine.connect() as conn:
            conn.execute(results_table.insert().values(
                name=user_name.strip(),
                mbti_type=mbti_type,
                timestamp=datetime.utcnow().isoformat()
            ))
            conn.commit()

        with open("personality_profiles.json", "r", encoding="utf-8") as f:
            profiles = json.load(f)

        profile = profiles.get(mbti_type)
        if profile:
            st.subheader(f"👤 {mbti_type} – {profile['label']}")
            st.markdown(f"#### 🧠 الوصف:\n{profile['description']}")
            st.markdown("### 💼 التوصيات المهنية:")
            for role in profile["roles"]:
                st.write(f"- {role}")
        else:
            st.warning("⚠️ لم يتم العثور على وصف لهذا النمط.")

# شغل الصفحة تلقائيًا
run_test()
