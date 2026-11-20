
import streamlit as st
import sqlite3
import requests
import json
from datetime import datetime

# =========================
# إعداد المنصة
# =========================
st.set_page_config(
    page_title="بُرهان | المرافق الذكي للباحث",
    page_icon="🔎",
    layout="wide"
)

DB = "burhan.db"

# =========================
# التصميم
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #F5F8FC;
    color: #101820;
}
header[data-testid="stHeader"] {
    background: transparent;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}
h1, h2, h3 {
    color: #163B5C !important;
}
p, label, li {
    color: #182B3A;
}
div[data-testid="stSelectbox"] {
    background: white;
    border-radius: 10px;
}
div[data-testid="stForm"] {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #DCE6F0;
}
div.stButton > button {
    background: #174B75;
    color: white;
    border-radius: 9px;
    border: none;
    min-height: 42px;
}
div.stButton > button:hover {
    background: #22658F;
    color: white;
}
div[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border: 1px solid #DCE6F0;
    border-radius: 12px;
}
div[data-testid="stChatMessage"] {
    border-radius: 12px;
}
hr {
    border-color: #DCE6F0;
}
</style>
""", unsafe_allow_html=True)

# =========================
# قاعدة البيانات
# =========================
def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            topic TEXT,
            field TEXT,
            problem TEXT,
            methodology TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_project(title, topic, field, problem, methodology):
    conn = sqlite3.connect(DB)
    conn.execute("""
        INSERT INTO projects
        (title, topic, field, problem, methodology, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        title, topic, field, problem, methodology,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()

def get_projects():
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return rows

def delete_project(project_id):
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM projects WHERE id=?", (project_id,))
    conn.commit()
    conn.close()

init_db()

# =========================
# الذكاء الاصطناعي
# =========================
def ask_ai(prompt, system_prompt=None):
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        return "⚠️ لم يتم إعداد GROQ_API_KEY في إعدادات Secrets."

    if not system_prompt:
        system_prompt = """
أنت بُرهان، مساعد ذكي متخصص في البحث العلمي.
تساعد الباحثين والطلبة في:
- اختيار وصياغة موضوعات البحث
- تحليل المشكلات البحثية
- صياغة الإشكالية والأسئلة والفرضيات
- اقتراح المنهجيات
- شرح المفاهيم العلمية
- تنظيم البحث

تحدث باللغة التي يستخدمها الباحث.
كن دقيقاً، أكاديمياً، واضحاً ومنظماً.
لا تختلق مراجع أو مصادر علمية.
إذا لم تكن متأكداً من معلومة فصرّح بذلك.
"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5
            },
            timeout=90
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]

        return f"خطأ من خدمة الذكاء الاصطناعي: {response.status_code}\n{response.text}"

    except Exception as e:
        return f"حدث خطأ أثناء الاتصال: {e}"

# =========================
# رأس المنصة والتنقل
# =========================
st.markdown("""
<div style="
    background:#173F63;
    padding:24px;
    border-radius:16px;
    margin-bottom:15px;
">
    <h1 style="color:white !important;margin:0;">🔎 بُرهان</h1>
    <p style="color:#FFFFFF !important;margin:6px 0 0 0;">
        المرافق الذكي للباحث | من الفكرة إلى الدليل
    </p>
</div>
""", unsafe_allow_html=True)

pages = [
    "الرئيسية",
    "إنشاء مشروع",
    "المساعد الذكي",
    "مشاريعي",
    "مراحل البحث",
    "الإعدادات"
]

page = st.selectbox(
    "انتقل إلى القسم",
    pages,
    key="main_navigation"
)

st.divider()

# =========================
# الصفحة الرئيسية
# =========================
if page == "الرئيسية":

    st.title("مرحباً بك في بُرهان")

    st.write("""
    مساحة ذكية ترافقك في رحلتك البحثية، من بلورة الفكرة
    إلى بناء بحث منظم وأكثر وضوحاً.
    """)

    projects = get_projects()

    c1, c2 = st.columns(2)

    with c1:
        st.metric("مشاريعك البحثية", len(projects))

    with c2:
        st.metric("المرافق البحثي", "متاح")

    st.markdown("### ماذا يمكنك أن تفعل؟")

    st.markdown("""
    **إنشاء مشروع بحث**  
    ابدأ بتنظيم فكرتك وتحويلها إلى مشروع بحث.

    **المساعد الذكي**  
    ناقش موضوعك، حلل إشكاليتك، واطلب المساعدة في مختلف مراحل البحث.

    **مشاريعي**  
    استعرض مشاريعك المحفوظة وارجع إليها.

    **مراحل البحث**  
    تعرّف على مراحل إنجاز البحث العلمي وتنظيم العمل.
    """)

    st.info("بُرهان مساعد لك، وليس بديلاً عن تفكيرك أو التحقق العلمي من المعلومات.")

# =========================
# إنشاء مشروع
# =========================
elif page == "إنشاء مشروع":

    st.title("إنشاء مشروع بحث جديد")

    with st.form("new_project_form"):

        title = st.text_input("عنوان المشروع")

        field = st.text_input(
            "التخصص أو المجال",
            placeholder="مثال: إدارة الأعمال، اقتصاد، علوم..."
        )

        topic = st.text_area(
            "فكرة البحث",
            placeholder="اشرح فكرتك البحثية باختصار..."
        )

        problem = st.text_area(
            "المشكلة التي تريد دراستها",
            placeholder="ما المشكلة التي يحاول البحث فهمها أو حلها؟"
        )

        methodology = st.text_input(
            "المنهج (إن وجد)",
            placeholder="يمكنك تركه فارغاً إذا لم تحدده بعد"
        )

        submitted = st.form_submit_button("حفظ المشروع")

        if submitted:
            if title.strip() and topic.strip():
                add_project(title, topic, field, problem, methodology)
                st.success("تم حفظ مشروعك بنجاح.")
            else:
                st.warning("يرجى إدخال عنوان المشروع وفكرة البحث.")

    st.divider()
    st.markdown("### هل تحتاج مساعدة في تطوير فكرتك؟")

    idea = st.text_area(
        "اكتب فكرة البحث لتحليلها بالذكاء الاصطناعي",
        key="idea_analysis_input"
    )

    if st.button("تحليل الفكرة"):
        if idea.strip():
            with st.spinner("يجري تحليل الفكرة..."):
                result = ask_ai(
                    f"""
حلل فكرة البحث التالية تحليلاً أكاديمياً:

{idea}

قدم:
1. تقييم الفكرة
2. نقاط القوة والضعف
3. إمكانية تطويرها
4. مشكلة بحثية محتملة
5. أسئلة بحث مقترحة
6. عنوان أكاديمي مناسب
"""
                )
            st.markdown("### نتيجة التحليل")
            st.markdown(result)
        else:
            st.warning("أدخل فكرة البحث أولاً.")

# =========================
# المساعد الذكي
# =========================
elif page == "المساعد الذكي":

    st.title("المساعد البحثي الذكي")

    st.write("اطرح سؤالاً، ناقش موضوعاً، أو اطلب مساعدة في بحثك.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("اكتب سؤالك البحثي هنا...")

    if user_input:

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("بُرهان يفكر..."):
                conversation = ""
                for msg in st.session_state.chat_history[-10:]:
                    role = "الباحث" if msg["role"] == "user" else "بُرهان"
                    conversation += f"{role}: {msg['content']}\n"

                answer = ask_ai(conversation)
                st.markdown(answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })

    if st.button("مسح المحادثة"):
        st.session_state.chat_history = []
        st.rerun()

# =========================
# مشاريعي
# =========================
elif page == "مشاريعي":

    st.title("مشاريعي البحثية")

    projects = get_projects()

    if not projects:
        st.info("لا توجد مشاريع محفوظة بعد. ابدأ بإنشاء مشروع جديد.")
    else:
        for project in projects:

            with st.expander(f"📘 {project[1]}"):

                st.markdown(f"**المجال:** {project[3] or 'غير محدد'}")
                st.markdown("**فكرة البحث:**")
                st.write(project[2] or "لم تتم إضافة الفكرة")

                st.markdown("**المشكلة البحثية:**")
                st.write(project[4] or "لم يتم تحديد المشكلة")

                st.markdown("**المنهج:**")
                st.write(project[5] or "لم يتم تحديده")

                st.caption(f"تاريخ الإنشاء: {project[6]}")

                if st.button("حذف المشروع", key=f"del_{project[0]}"):
                    delete_project(project[0])
                    st.rerun()

# =========================
# مراحل البحث
# =========================
elif page == "مراحل البحث":

    st.title("مراحل البحث العلمي")

    stages = [
        ("1 — اختيار الموضوع",
         "اختيار موضوع واضح ومناسب، يثير اهتمام الباحث وقابل للدراسة."),
        ("2 — تحديد المشكلة",
         "تحديد المشكلة البحثية وصياغتها بشكل واضح ودقيق."),
        ("3 — صياغة الأسئلة والفرضيات",
         "تحديد الأسئلة التي يسعى البحث للإجابة عنها، والفرضيات عند الحاجة."),
        ("4 — مراجعة الأدبيات",
         "الاطلاع على الدراسات السابقة والمراجع ذات الصلة."),
        ("5 — تحديد المنهج",
         "اختيار المنهج والأدوات المناسبة لطبيعة المشكلة."),
        ("6 — جمع البيانات",
         "جمع البيانات وفق أدوات ومنهجية واضحة."),
        ("7 — تحليل البيانات",
         "تنظيم البيانات وتحليلها للوصول إلى نتائج."),
        ("8 — النتائج والمناقشة",
         "عرض النتائج وتفسيرها ومقارنتها بالدراسات السابقة."),
        ("9 — الخاتمة والتوصيات",
         "تلخيص أهم النتائج وتقديم توصيات ومقترحات."),
        ("10 — التوثيق والمراجعة",
         "توثيق المصادر ومراجعة البحث لغوياً ومنهجياً.")
    ]

    for title, description in stages:
        st.markdown(f"### {title}")
        st.write(description)
        st.divider()

# =========================
# الإعدادات
# =========================
elif page == "الإعدادات":

    st.title("الإعدادات")

    st.markdown("### حول بُرهان")

    st.write("""
    بُرهان هو مرافق ذكي للباحث، يهدف إلى تسهيل رحلة البحث العلمي
    ومساعدة الباحث في التفكير والتحليل والتنظيم.
    """)

    st.markdown("**الاسم:** بُرهان (Burhan)")
    st.markdown("**الشعار:** من الفكرة إلى الدليل")
    st.markdown("**اللغة الأساسية:** العربية")
    st.markdown("**الإصدار:** MVP")

    st.divider()

    st.markdown("### إدارة المحادثة")

    if st.button("إعادة ضبط المحادثة"):
        st.session_state.chat_history = []
        st.success("تمت إعادة ضبط المحادثة.")
