import streamlit as st
import sqlite3
import requests
import os
from datetime import datetime

# ==================================================
# إعداد برهان
# ==================================================
st.set_page_config(
    page_title="بُرهان | المرافق الذكي للباحث",
    page_icon="🔎",
    layout="wide"
)

DB_PATH = "burhan_database.db"

# ==================================================
# التصميم - أزرق بارد وأبيض - بدون فرض عرض Sidebar
# ==================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], input, textarea, button {
    font-family: 'Cairo', sans-serif !important;
}

.stApp {
    background: #FFFFFF !important;
    color: #000000 !important;
    direction: rtl;
}

/* Sidebar: لا نفرض عرضًا ولا min-width ولا max-width */
section[data-testid="stSidebar"] {
    background-color: #183B5B !important;
    border: none !important;
}

section[data-testid="stSidebar"] > div {
    background-color: #183B5B !important;
    border: none !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* المحتوى */
.block-container {
    max-width: 1200px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* العناوين */
h1, h2, h3, h4 {
    color: #183B5B !important;
    font-weight: 800 !important;
}

/* النص */
p, label, .stMarkdown {
    color: #000000;
}

/* خانات الإدخال */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #183B5B !important;
    border-radius: 10px !important;
    caret-color: #183B5B !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #555555 !important;
    opacity: 1 !important;
}

/* القوائم */
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #000000 !important;
}

/* الأزرار */
.stButton > button,
.stDownloadButton > button {
    background-color: #183B5B !important;
    color: #FFFFFF !important;
    border: 1px solid #183B5B !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background-color: #28577D !important;
    color: #FFFFFF !important;
}

/* البطاقات */
div[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #B8D0E5 !important;
    border-radius: 12px !important;
    padding: 15px !important;
}

/* الرسائل */
div[data-testid="stAlert"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #183B5B !important;
    border-radius: 10px !important;
}

/* الفواصل */
hr {
    border-color: #B8D0E5 !important;
}

/* الهاتف: لا نتحكم في sidebar بعرض ثابت */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.7rem 2rem 0.7rem !important;
    }

    h1 {
        font-size: 1.65rem !important;
    }

    h2 {
        font-size: 1.35rem !important;
    }

    h3 {
        font-size: 1.15rem !important;
    }

    div[data-testid="stMetric"] {
        padding: 10px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# قاعدة البيانات
# ==================================================
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            field TEXT,
            description TEXT,
            created_at TEXT,
            analysis TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

def get_projects():
    conn = get_connection()
    rows = conn.execute("""
        SELECT id, title, field, description, created_at, analysis
        FROM projects
        ORDER BY id DESC
    """).fetchall()
    conn.close()
    return rows

def create_project(title, field, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO projects (title, field, description, created_at, analysis)
        VALUES (?, ?, ?, ?, ?)
    """, (
        title, field, description,
        datetime.now().strftime("%Y-%m-%d %H:%M"), ""
    ))
    project_id = cur.lastrowid
    conn.commit()
    conn.close()
    return project_id

def update_analysis(project_id, analysis):
    conn = get_connection()
    conn.execute(
        "UPDATE projects SET analysis=? WHERE id=?",
        (analysis, project_id)
    )
    conn.commit()
    conn.close()

def delete_project(project_id):
    conn = get_connection()
    conn.execute("DELETE FROM projects WHERE id=?", (project_id,))
    conn.commit()
    conn.close()

init_db()

# ==================================================
# الذكاء الاصطناعي
# ==================================================
def get_api_key():
    try:
        return st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")

def get_model():
    try:
        return st.secrets.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    except Exception:
        return os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

def call_ai(messages):
    key = get_api_key()
    if not key:
        return "لم يتم إعداد مفتاح الذكاء الاصطناعي في إعدادات التطبيق (Secrets)."

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            },
            json={
                "model": get_model(),
                "messages": messages,
                "temperature": 0.5,
                "max_tokens": 3000
            },
            timeout=90
        )

        if response.status_code != 200:
            return (
                f"حدث خطأ من خدمة الذكاء الاصطناعي "
                f"({response.status_code}).\n{response.text[:800]}"
            )

        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "انتهت مدة الاتصال. حاول مرة أخرى."

    except Exception as e:
        return f"تعذر الاتصال: {str(e)}"

# ==================================================
# مراحل البحث
# ==================================================
research_stages = [
    ("01", "اختيار موضوع البحث",
     "اختيار موضوع واضح، قابل للدراسة، ومرتبط باهتمام الباحث."),
    ("02", "تحديد المشكلة",
     "اكتشاف المشكلة البحثية وتحديد أبعادها ومن يتأثر بها."),
    ("03", "صياغة الإشكالية",
     "صياغة سؤال رئيسي وأسئلة فرعية توجه الدراسة."),
    ("04", "بناء الفرضيات",
     "اقتراح إجابات مؤقتة قابلة للاختبار عند الحاجة."),
    ("05", "تحديد الأهداف",
     "تحديد ما يسعى البحث إلى تحقيقه بوضوح."),
    ("06", "الدراسات السابقة",
     "استكشاف الأدبيات، وفهم ما تم بحثه وتحديد فجوات محتملة."),
    ("07", "المنهجية",
     "اختيار المنهج والأدوات ومجتمع الدراسة والعينة."),
    ("08", "التحليل والنتائج",
     "تحليل البيانات، ومناقشة النتائج، واستخلاص التوصيات.")
]

# ==================================================
# القائمة الجانبية
# ==================================================
st.sidebar.title("🔎 بُرهان")
st.sidebar.caption("من الفكرة إلى الدليل")
st.sidebar.divider()

page = st.sidebar.radio(
    "التنقل",
    [
        "الرئيسية",
        "إنشاء مشروع",
        "المساعد الذكي",
        "مشاريعي",
        "مراحل البحث",
        "الإعدادات"
    ],
    key="navigation"
)

st.sidebar.divider()
st.sidebar.caption("المرافق الذكي للباحث")
st.sidebar.caption("نسخة MVP الأولية")

# ==================================================
# الصفحة الرئيسية
# ==================================================
if page == "الرئيسية":
    projects = get_projects()

    st.title("بُرهان")
    st.subheader("المرافق الذكي للباحث")
    st.write("من الفكرة إلى الدليل — رحلة بحثية أكثر وضوحًا وتنظيمًا.")

    st.info(
        "ابدأ فكرتك البحثية، وحوّلها إلى مشروع علمي منظم "
        "بمساعدة الذكاء الاصطناعي."
    )

    st.markdown("## لوحة الباحث")
    c1, c2, c3 = st.columns(3)
    c1.metric("مشاريعك", len(projects))
    c2.metric("مراحل البحث", 8)
    c3.metric("المساعد الذكي", "متاح")

    st.divider()
    st.markdown("## كيف يساعدك بُرهان؟")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### تطوير الأفكار")
        st.write("تحليل الأفكار الأولية وتحديد قابليتها للتطوير.")
        st.markdown("### بناء الإشكالية")
        st.write("اقتراح إشكاليات وأسئلة بحثية.")

    with c2:
        st.markdown("### تنظيم البحث")
        st.write("متابعة مراحل البحث العلمي الثمانية.")
        st.markdown("### المساعدة الأكاديمية")
        st.write("دعم الأهداف والفرضيات والمنهجية والكتابة.")

    st.divider()
    st.markdown("## أحدث المشاريع")
    if projects:
        for p in projects[:5]:
            st.markdown(f"**{p[1]}**")
            st.caption(f"{p[2] or 'غير محدد'} · {p[4]}")
    else:
        st.info("لم تنشئ أي مشروع بعد.")

# ==================================================
# إنشاء مشروع
# ==================================================
elif page == "إنشاء مشروع":
    st.title("إنشاء مشروع بحث")
    st.write("أنشئ مساحة خاصة لتنظيم بحثك.")

    with st.form("project_form"):
        title = st.text_input("عنوان البحث")
        field = st.selectbox(
            "التخصص",
            [
                "إدارة الأعمال", "اقتصاد", "علوم التسيير",
                "مالية ومحاسبة", "تسويق", "علوم اجتماعية",
                "علوم إنسانية", "علوم طبيعية", "علوم تقنية", "أخرى"
            ]
        )
        description = st.text_area(
            "وصف فكرة البحث",
            placeholder="اشرح فكرتك والمشكلة التي تريد دراستها...",
            height=160
        )
        submitted = st.form_submit_button("إنشاء المشروع")

    if submitted:
        if not title.strip():
            st.warning("أدخل عنوان البحث.")
        else:
            create_project(title.strip(), field, description.strip())
            st.success("تم إنشاء المشروع بنجاح.")
            st.rerun()

# ==================================================
# المساعد الذكي
# ==================================================
elif page == "المساعد الذكي":
    st.title("المساعد البحثي الذكي")
    st.write("حلّل فكرتك، طوّر إشكاليتك، وناقش بحثك مع بُرهان.")

    projects = get_projects()
    project_options = {"بدون ربط بمشروع": None}
    for p in projects:
        project_options[f"{p[1]} (#{p[0]})"] = p[0]

    selected_name = st.selectbox("ربط التحليل بمشروع", list(project_options.keys()))
    selected_project_id = project_options[selected_name]

    idea = st.text_area(
        "فكرة البحث",
        placeholder="اكتب موضوع أو فكرة بحثك...",
        height=150,
        key="research_idea"
    )

    assistance = st.selectbox(
        "نوع المساعدة",
        [
            "تحليل شامل للفكرة",
            "صياغة الإشكالية والأسئلة",
            "بناء الفرضيات والأهداف",
            "اقتراح المنهجية",
            "تطوير عنوان البحث",
            "تقييم الفجوة البحثية",
            "مناقشة مفتوحة"
        ]
    )

    prompts = {
        "تحليل شامل للفكرة": """
حلل الفكرة من حيث:
فهم الفكرة، المشكلة، الأهمية، نقاط القوة والضعف،
القابلية للدراسة، المخاطر، والجوانب التي تحتاج توضيحًا.
قدم نقدًا بنّاءً وأسئلة تطويرية.
""",
        "صياغة الإشكالية والأسئلة": """
اشرح المشكلة البحثية، ثم اقترح إشكالية رئيسية وأسئلة فرعية،
ووضح حدود الصياغة وما يجب التحقق منه.
""",
        "بناء الفرضيات والأهداف": """
اقترح أهدافًا عامة وخاصة وفرضيات مناسبة إن كان البحث يحتاجها،
وحدد المتغيرات المحتملة والعلاقة بينها.
""",
        "اقتراح المنهجية": """
ناقش المناهج الممكنة، واقترح الأنسب مع التبرير،
وأدوات جمع البيانات والمجتمع والعينة المحتملة وحدود المنهج.
""",
        "تطوير عنوان البحث": """
اقترح خمسة عناوين أكاديمية واضحة وغير مبالغ فيها،
ثم وضح الفروق بينها واختر العنوان الأكثر دقة مبدئيًا.
""",
        "تقييم الفجوة البحثية": """
حدد فجوات محتملة فقط، وما يجب فحصه في الدراسات السابقة.
لا تدّع أن الفجوة مؤكدة دون مراجعة المصادر.
""",
        "مناقشة مفتوحة": """
ناقش الباحث كمشرف علمي نقدي وبنّاء،
واطرح أسئلة مهمة واقترح تطويرات عملية.
"""
    }

    if st.button("تحليل الفكرة"):
        if not idea.strip():
            st.warning("اكتب فكرة البحث أولًا.")
        else:
            system = """
أنت بُرهان، المرافق الذكي للباحث.
تساعد الباحثين من مختلف المستويات باللغة العربية.
كن دقيقًا، نقديًا، ومنظمًا.
لا تختلق مراجع أو بيانات أو نتائج.
وضح حدود المعرفة، ووجّه الباحث ولا تتخذ قراراته بدلًا عنه.
تجنب الحشو والنصائح العامة.
"""
            messages = [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": f"فكرة البحث:\n{idea}\n\nالمهمة:\n{prompts[assistance]}"
                }
            ]

            with st.spinner("برهان يحلل الفكرة..."):
                result = call_ai(messages)

            st.markdown("---")
            st.markdown("## نتيجة التحليل")
            st.markdown(result)

            st.session_state.last_analysis = result
            st.session_state.last_idea = idea

            if selected_project_id is not None:
                update_analysis(selected_project_id, result)
                st.success("تم حفظ التحليل في المشروع.")

            st.download_button(
                "تحميل نتيجة التحليل",
                data=result,
                file_name="burhan_analysis.txt",
                mime="text/plain"
            )

    # محادثة
    st.divider()
    st.markdown("## محادثة مع برهان")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    chat_input = st.chat_input("اكتب سؤالك البحثي...")

    if chat_input:
        st.session_state.chat_history.append(
            {"role": "user", "content": chat_input}
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "أنت بُرهان، مساعد بحثي أكاديمي. "
                    "ناقش المستخدم بالعربية، كن دقيقًا ولا تختلق مصادر."
                )
            }
        ]
        messages += st.session_state.chat_history[-12:]

        with st.spinner("برهان يفكر..."):
            answer = call_ai(messages)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )
        st.rerun()

    if st.button("مسح المحادثة"):
        st.session_state.chat_history = []
        st.rerun()

# ==================================================
# المشاريع
# ==================================================
elif page == "مشاريعي":
    st.title("مشاريعي البحثية")
    projects = get_projects()

    if not projects:
        st.info("لا توجد مشاريع. أنشئ مشروعك الأول.")
    else:
        project_map = {f"{p[1]} | #{p[0]}": p for p in projects}
        selected = st.selectbox("اختر مشروعًا", list(project_map.keys()))
        p = project_map[selected]

        st.divider()
        st.header(p[1])
        st.write("**التخصص:**", p[2] or "غير محدد")
        st.write("**تاريخ الإنشاء:**", p[4])

        st.markdown("### وصف المشروع")
        st.write(p[3] or "لا يوجد وصف.")

        st.markdown("### تحليل المشروع")
        if p[5]:
            st.markdown(p[5])
            st.download_button(
                "تحميل التحليل",
                data=p[5],
                file_name=f"burhan_project_{p[0]}.txt",
                mime="text/plain"
            )
        else:
            st.info("لم يتم تحليل هذا المشروع بعد.")

        st.divider()
        if st.button("حذف المشروع"):
            delete_project(p[0])
            st.success("تم حذف المشروع.")
            st.rerun()

# ==================================================
# مراحل البحث
# ==================================================
elif page == "مراحل البحث":
    st.title("مراحل البحث العلمي")
    st.write("مسار إرشادي يساعدك على فهم وتنظيم مراحل بحثك.")

    for number, name, description in research_stages:
        with st.expander(f"{number} — {name}"):
            st.write(description)

            guidance = {
                "اختيار موضوع البحث": [
                    "ما الموضوع الذي يثير اهتمامك؟",
                    "هل الموضوع قابل للدراسة؟",
                    "هل توجد بيانات يمكن الوصول إليها؟"
                ],
                "تحديد المشكلة": [
                    "ما المشكلة الفعلية؟",
                    "من يتأثر بها؟",
                    "ما حدود المشكلة؟"
                ],
                "صياغة الإشكالية": [
                    "ما السؤال الرئيسي؟",
                    "ما الأسئلة الفرعية؟"
                ],
                "بناء الفرضيات": [
                    "ما العلاقة المتوقع اختبارها؟",
                    "هل يمكن اختبارها علميًا؟"
                ],
                "تحديد الأهداف": [
                    "ما الهدف العام؟",
                    "ما الأهداف الخاصة؟"
                ],
                "الدراسات السابقة": [
                    "ماذا توصلت إليه الدراسات؟",
                    "ما الذي يحتاج إلى بحث إضافي؟"
                ],
                "المنهجية": [
                    "ما المنهج المناسب؟",
                    "كيف سيتم جمع البيانات؟"
                ],
                "التحليل والنتائج": [
                    "ماذا تظهر البيانات؟",
                    "هل تجيب عن أسئلة البحث؟"
                ]
            }

            st.markdown("**أسئلة تساعدك:**")
            for q in guidance[name]:
                st.write(f"- {q}")

# ==================================================
# الإعدادات
# ==================================================
elif page == "الإعدادات":
    st.title("إعدادات بُرهان")

    st.markdown("## معلومات المنصة")
    st.write("**الاسم:** بُرهان")
    st.write("**الوصف:** المرافق الذكي للباحث")
    st.write("**الشعار:** من الفكرة إلى الدليل")
    st.write("**الإصدار:** MVP الأولي")

    st.divider()
    st.markdown("## حالة الذكاء الاصطناعي")

    if get_api_key():
        st.success("مفتاح API موجود.")
    else:
        st.warning("لم يتم إضافة مفتاح API بعد.")

    st.markdown("## قاعدة البيانات")
    st.write("تستخدم المنصة SQLite لحفظ المشاريع.")

    st.divider()
    st.write(
        "بُرهان أداة مساعدة بحثية. يجب التحقق من المعلومات "
        "والمراجع والنتائج قبل اعتمادها علميًا."
)
