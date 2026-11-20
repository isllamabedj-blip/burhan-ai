import streamlit as st
import sqlite3
import requests
import json
import os
from datetime import datetime
from io import BytesIO

# =====================================================
# 1. إعداد المنصة
# =====================================================

st.set_page_config(
    page_title="بُرهان | المرافق الذكي للباحث",
    page_icon="🔎",
    layout="wide"
)

DB_PATH = "burhan_database.db"

# =====================================================
# 2. التصميم
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], input, textarea, button, select {
    font-family: 'Cairo', sans-serif !important;
}

.stApp {
    background: #FFFFFF;
    color: #000000;
    direction: rtl;
}

/* إزالة الخط الفاصل للقائمة الجانبية */
section[data-testid="stSidebar"] {
    background: #183B5B !important;
    border: none !important;
}

section[data-testid="stSidebar"] > div {
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stSidebarContent"] {
    background: #183B5B !important;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* المحتوى الرئيسي */
.block-container {
    max-width: 1250px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

/* العناوين */
h1, h2, h3, h4 {
    color: #183B5B !important;
    font-weight: 800 !important;
}

/* النصوص */
p, label, .stMarkdown, li {
    color: #000000;
}

/* الخانات */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #FFFFFF !important;
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
    background: #FFFFFF !important;
    color: #000000 !important;
}

/* الأزرار */
.stButton > button,
.stDownloadButton > button {
    background: #183B5B !important;
    color: #FFFFFF !important;
    border: 1px solid #183B5B !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    min-height: 42px;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #28577D !important;
    color: #FFFFFF !important;
}

/* البطاقات */
div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #B8D0E5 !important;
    border-radius: 14px !important;
    padding: 15px !important;
}

/* التنبيهات */
div[data-testid="stAlert"] {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #183B5B !important;
    border-radius: 10px !important;
}

/* الخطوط والفواصل */
hr {
    border-color: #B8D0E5 !important;
}

/* تحسين عرض الهاتف */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.7rem 2rem 0.7rem !important;
    }

    h1 {
        font-size: 1.7rem !important;
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

    section[data-testid="stSidebar"] {
        min-width: 0 !important;
    }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. قاعدة البيانات
# =====================================================

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
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

init_db()

def get_projects():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, field, description, created_at, analysis
        FROM projects
        ORDER BY id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def create_project(title, field, description):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO projects (title, field, description, created_at, analysis)
        VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        field,
        description,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        ""
    ))
    conn.commit()
    project_id = cur.lastrowid
    conn.close()
    return project_id

def update_analysis(project_id, analysis):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE projects
        SET analysis = ?
        WHERE id = ?
    """, (analysis, project_id))
    conn.commit()
    conn.close()

def delete_project(project_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()

# =====================================================
# 4. إعداد الذكاء الاصطناعي
# =====================================================

def get_api_key():
    try:
        return st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        return os.getenv("GROQ_API_KEY", "")

def call_ai(messages, temperature=0.5):
    api_key = get_api_key()

    if not api_key:
        return "لم يتم إعداد مفتاح الذكاء الاصطناعي بعد. أضف GROQ_API_KEY في Secrets."

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 3000
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=90
        )

        if response.status_code != 200:
            return f"خطأ من خدمة الذكاء الاصطناعي ({response.status_code}):\n{response.text[:1000]}"

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "انتهت مدة الاتصال. حاول مرة أخرى."

    except Exception as e:
        return f"حدث خطأ أثناء الاتصال: {str(e)}"

# =====================================================
# 5. مراحل البحث
# =====================================================

research_stages = [
    ("01", "اختيار موضوع البحث", "تحديد مجال البحث واختيار موضوع واضح وقابل للدراسة."),
    ("02", "تحديد المشكلة", "اكتشاف المشكلة البحثية وتحديد أبعادها."),
    ("03", "صياغة الإشكالية", "تحويل المشكلة إلى سؤال علمي رئيسي وأسئلة فرعية."),
    ("04", "بناء الفرضيات", "اقتراح إجابات مؤقتة أو علاقات قابلة للاختبار."),
    ("05", "تحديد الأهداف", "تحديد ما يسعى البحث إلى تحقيقه."),
    ("06", "الدراسات السابقة", "استكشاف الأدبيات وتحديد الفجوة البحثية."),
    ("07", "المنهجية", "اختيار المنهج والأدوات والمجتمع والعينة."),
    ("08", "التحليل والنتائج", "تحليل البيانات واستخلاص النتائج والتوصيات.")
]

# =====================================================
# 6. الشريط الجانبي والتنقل
# =====================================================

st.sidebar.markdown("# 🔎 بُرهان")
st.sidebar.markdown("**من الفكرة إلى الدليل**")
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

# =====================================================
# 7. الرئيسية
# =====================================================

if page == "الرئيسية":

    projects = get_projects()

    st.title("بُرهان 🔎")
    st.subheader("المرافق الذكي للباحث")
    st.write("من الفكرة إلى الدليل — رحلة بحثية أكثر وضوحًا وتنظيمًا.")

    st.info(
        "ابدأ فكرتك البحثية، حلّلها، طوّر إشكاليتها، "
        "ونظّم مراحل بحثك في مساحة واحدة."
    )

    st.markdown("## لوحة الباحث")

    c1, c2, c3 = st.columns(3)

    c1.metric("مشاريعك", len(projects))
    c2.metric("مراحل البحث", "8")
    c3.metric("المساعد الذكي", "متاح")

    st.markdown("---")
    st.markdown("## ماذا يمكنك فعله ببُرهان؟")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 💡 تطوير الأفكار")
        st.write("تحويل الأفكار الأولية إلى مواضيع بحث قابلة للتطوير.")

        st.markdown("### 🧩 بناء الإشكالية")
        st.write("اقتراح إشكاليات وأسئلة بحثية مرتبطة بموضوعك.")

    with c2:
        st.markdown("### 📚 تنظيم البحث")
        st.write("متابعة مراحل البحث الثمانية بطريقة منظمة.")

        st.markdown("### 📝 المساعدة الأكاديمية")
        st.write("مساعدتك في الأهداف والفرضيات والمنهجية والكتابة.")

    st.markdown("---")
    st.markdown("## انطلق الآن")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### مشروع جديد")
        st.write("أنشئ مساحة خاصة لبحثك.")
        if st.button("إنشاء مشروع جديد", key="home_new_project"):
            st.session_state.navigation = "إنشاء مشروع"
            st.rerun()

    with c2:
        st.markdown("### المساعد الذكي")
        st.write("حلّل فكرة بحثك باستخدام الذكاء الاصطناعي.")
        if st.button("فتح المساعد", key="home_ai"):
            st.session_state.navigation = "المساعد الذكي"
            st.rerun()

    if projects:
        st.markdown("---")
        st.markdown("## آخر مشاريعك")

        for p in projects[:3]:
            st.markdown(f"**{p[1]}**")
            st.caption(f"التخصص: {p[2] or 'غير محدد'} | {p[4]}")

# =====================================================
# 8. إنشاء مشروع
# =====================================================

elif page == "إنشاء مشروع":

    st.title("إنشاء مشروع بحث")
    st.write("أنشئ مشروعًا جديدًا لتنظيم رحلة بحثك.")

    with st.form("new_project_form"):

        title = st.text_input("عنوان البحث")

        field = st.selectbox(
            "التخصص",
            [
                "إدارة الأعمال",
                "اقتصاد",
                "علوم التسيير",
                "مالية ومحاسبة",
                "تسويق",
                "علوم اجتماعية",
                "علوم إنسانية",
                "علوم طبيعية",
                "علوم تقنية",
                "أخرى"
            ]
        )

        description = st.text_area(
            "وصف فكرة البحث",
            placeholder="اشرح فكرتك، المشكلة التي تريد دراستها، أو المجال الذي تهتم به...",
            height=180
        )

        submitted = st.form_submit_button("إنشاء المشروع")

        if submitted:
            if not title.strip():
                st.warning("يرجى إدخال عنوان البحث.")
            else:
                new_id = create_project(title.strip(), field, description.strip())
                st.success("تم إنشاء المشروع بنجاح.")
                st.session_state.selected_project = new_id
                st.rerun()

# =====================================================
# 9. المساعد الذكي
# =====================================================

elif page == "المساعد الذكي":

    st.title("المساعد البحثي الذكي")
    st.write("ناقش فكرتك البحثية، وحوّلها إلى مشروع علمي قابل للتطوير.")

    projects = get_projects()

    project_options = {
        "بدون ربط بمشروع": None
    }

    for p in projects:
        project_options[f"{p[1]} (#{p[0]})"] = p[0]

    selected_name = st.selectbox(
        "ربط التحليل بمشروع",
        list(project_options.keys())
    )

    selected_project_id = project_options[selected_name]

    idea = st.text_area(
        "فكرة البحث أو الموضوع",
        placeholder="اكتب فكرتك هنا بالتفصيل...",
        height=160,
        key="ai_idea"
    )

    uploaded_file = st.file_uploader(
        "إرفاق ملف PDF لدعم التحليل (اختياري)",
        type=["pdf"]
    )

    file_text = ""

    if uploaded_file is not None:
        try:
            from pypdf import PdfReader

            reader = PdfReader(uploaded_file)
            pages_text = []

            for page_pdf in reader.pages[:20]:
                pages_text.append(page_pdf.extract_text() or "")

            file_text = "\n".join(pages_text)

            st.success("تم استخراج النص من الملف.")

        except Exception as e:
            st.error(f"تعذر قراءة الملف: {e}")

    st.markdown("### نوع المساعدة")

    assistance = st.selectbox(
        "اختر المهمة",
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

    if st.button("بدء التحليل الذكي", type="primary"):

        if not idea.strip() and not file_text.strip():
            st.warning("أدخل فكرة بحث أو أرفق ملفًا أولًا.")

        else:

            system_prompt = """
أنت بُرهان، مساعد بحثي أكاديمي ذكي.

دورك:
- مساعدة الباحثين من مختلف المستويات.
- تقديم إجابات علمية دقيقة ومنظمة.
- لا تختلق مراجع أو مصادر أو أرقامًا.
- إذا كانت المعلومات غير مؤكدة، وضّح ذلك.
- لا تعتبر الفكرة الجيدة بالضرورة فكرة جديدة.
- لا تفرض منهجًا قبل فهم المشكلة.
- لا تكتب كلامًا عامًا أو حشوًا.
- استخدم العربية الواضحة.
- ناقش الباحث ووجّهه بدل أن تتخذ القرارات عنه.
- كن نقديًا وبنّاءً، واذكر نقاط القوة والضعف.
"""

            task_prompts = {
                "تحليل شامل للفكرة": """
حلل الفكرة البحثية بعمق:
1. فهم الفكرة.
2. المشكلة التي تعالجها.
3. أهمية البحث.
4. نقاط القوة.
5. نقاط الضعف والمخاطر.
6. قابلية الدراسة.
7. جوانب تحتاج إلى تحديد.
8. أسئلة تطويرية للباحث.
""",

                "صياغة الإشكالية والأسئلة": """
ساعد في بناء الإشكالية:
1. شرح المشكلة.
2. خلفية مختصرة.
3. إشكالية رئيسية مقترحة.
4. أسئلة فرعية.
5. ملاحظات حول حدود الإشكالية.
لا تدّع أنها صياغة نهائية.
""",

                "بناء الفرضيات والأهداف": """
اقترح:
1. أهداف عامة وخاصة.
2. فرضيات مناسبة إن كان البحث يحتاج فرضيات.
3. توضيح العلاقة بين الأهداف والفرضيات.
4. المتغيرات المحتملة.
5. ما الذي يحتاج إلى مراجعة.
""",

                "اقتراح المنهجية": """
ناقش:
1. المناهج الممكنة.
2. المنهج الأقرب ولماذا.
3. المجتمع والعينة إن أمكن تحديدهما.
4. أدوات جمع البيانات.
5. حدود المنهج.
لا تفرض منهجًا واحدًا دون مبرر.
""",

                "تطوير عنوان البحث": """
اقترح 5 عناوين بديلة:
- واضحة.
- أكاديمية.
- غير مبالغ فيها.
- متناسبة مع الفكرة.
ثم اشرح الفرق بينها باختصار.
""",

                "تقييم الفجوة البحثية": """
ساعد الباحث في استكشاف الفجوة المحتملة:
1. ما الذي قد يكون مدروسًا؟
2. ما الجوانب التي تحتاج إلى بحث؟
3. ما المعلومات التي يجب التحقق منها في الأدبيات؟
4. لا تؤكد وجود فجوة حقيقية دون مراجعة مصادر علمية.
""",

                "مناقشة مفتوحة": """
ناقش الفكرة كأنك مشرف بحثي:
قدم رأيًا نقديًا، اسأل أسئلة مهمة،
اقترح تطويرات، وكن صريحًا في تقييمك.
"""
            }

            user_content = f"""
المهمة المطلوبة: {assistance}

فكرة الباحث:
{idea}

النص المستخرج من الملف إن وجد:
{file_text[:12000]}

تعليمات المهمة:
{task_prompts[assistance]}
"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]

            with st.spinner("برهان يحلل فكرتك..."):
                result = call_ai(messages)

            st.markdown("---")
            st.markdown("## نتيجة التحليل")
            st.markdown(result)

            st.session_state.last_analysis = result
            st.session_state.last_idea = idea
            st.session_state.last_task = assistance

            if selected_project_id is not None:
                update_analysis(selected_project_id, result)
                st.success("تم حفظ التحليل داخل المشروع المرتبط.")

            st.download_button(
                "تحميل نتيجة التحليل",
                data=result,
                file_name="burhan_analysis.txt",
                mime="text/plain"
            )

    st.markdown("---")
    st.markdown("## محادثة مع برهان")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    chat_input = st.chat_input("اكتب سؤالك أو ناقش فكرتك...")

    if chat_input:

        st.session_state.chat_history.append(
            {"role": "user", "content": chat_input}
        )

        chat_messages = [
            {
                "role": "system",
                "content": """
أنت برهان، مساعد بحثي أكاديمي.
ناقش الباحث بالعربية، وقدم معلومات دقيقة.
لا تخترع مصادر. كن نقديًا ومفيدًا.
"""
            }
        ]

        chat_messages.extend(st.session_state.chat_history[-12:])

        with st.spinner("برهان يفكر..."):
            answer = call_ai(chat_messages)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )

        st.rerun()

    if st.button("مسح المحادثة"):
        st.session_state.chat_history = []
        st.rerun()

# =====================================================
# 10. مشاريعي
# =====================================================

elif page == "مشاريعي":

    st.title("مشاريعي البحثية")

    projects = get_projects()

    if not projects:
        st.info("لا توجد مشاريع بعد. ابدأ بإنشاء مشروع جديد.")
    else:

        project_map = {
            f"{p[1]} | #{p[0]}": p
            for p in projects
        }

        selected = st.selectbox(
            "اختر مشروعًا",
            list(project_map.keys())
        )

        p = project_map[selected]

        st.markdown("---")
        st.markdown(f"# {p[1]}")

        st.write("**التخصص:**", p[2] or "غير محدد")
        st.write("**تاريخ الإنشاء:**", p[4])
        st.markdown("### وصف المشروع")
        st.write(p[3] or "لا يوجد وصف.")

        st.markdown("### تحليل المشروع")
        if p[5]:
            st.markdown(p[5])
        else:
            st.info("لم يتم حفظ تحليل لهذا المشروع بعد.")

        if p[5]:
            st.download_button(
                "تحميل تحليل المشروع",
                data=p[5],
                file_name=f"burhan_project_{p[0]}.txt",
                mime="text/plain"
            )

        st.markdown("---")

        if st.button("حذف المشروع", key=f"delete_{p[0]}"):
            delete_project(p[0])
            st.success("تم حذف المشروع.")
            st.rerun()

# =====================================================
# 11. مراحل البحث
# =====================================================

elif page == "مراحل البحث":

    st.title("مراحل البحث العلمي")
    st.write("مسار إرشادي يساعدك على فهم مراحل إنجاز البحث.")

    for number, name, description in research_stages:

        with st.expander(f"{number} — {name}"):

            st.write(description)

            if name == "اختيار موضوع البحث":
                st.write("**أسئلة تساعدك:**")
                st.write("- ما الموضوع الذي يثير اهتمامك؟")
                st.write("- هل يمكن دراسة هذا الموضوع؟")
                st.write("- هل توجد بيانات متاحة؟")

            elif name == "تحديد المشكلة":
                st.write("**أسئلة تساعدك:**")
                st.write("- ما المشكلة الفعلية؟")
                st.write("- من يتأثر بها؟")
                st.write("- ما حدودها؟")

            elif name == "صياغة الإشكالية":
                st.write("**أسئلة تساعدك:**")
                st.write("- ما السؤال الرئيسي؟")
                st.write("- ما الأسئلة الفرعية؟")

            elif name == "بناء الفرضيات":
                st.write("**أسئلة تساعدك:**")
                st.write("- ما العلاقة المتوقع اختبارها؟")
                st.write("- هل يمكن اختبارها؟")

            elif name == "تحديد الأهداف":
                st.write("**أسئلة تساعدك:**")
                st.write("- ما النتائج التي تريد الوصول إليها؟")
                st.write("- ما الهدف العام؟")

            elif name == "الدراسات السابقة":
                st.write("**أسئلة تساعدك:**")
                st.write("- ماذا قال الباحثون السابقون؟")
                st.write("- ما الجوانب غير المدروسة؟")

            elif name == "المنهجية":
                st.write("**أسئلة تساعدك:**")
                st.write("- ما المنهج المناسب؟")
                st.write("- كيف ستجمع البيانات؟")

            elif name == "التحليل والنتائج":
                st.write("**أسئلة تساعدك:**")
                st.write("- ماذا تظهر البيانات؟")
                st.write("- هل تجيب عن أسئلة البحث؟")

# =====================================================
# 12. الإعدادات
# =====================================================

elif page == "الإعدادات":

    st.title("إعدادات برهان")

    st.markdown("## معلومات المنصة")
    st.write("**الاسم:** بُرهان")
    st.write("**الوصف:** المرافق الذكي للباحث")
    st.write("**الشعار:** من الفكرة إلى الدليل")
    st.write("**الإصدار:** MVP الأولي")

    st.markdown("---")
    st.markdown("## الاتصال بالذكاء الاصطناعي")

    api_key = get_api_key()

    if api_key:
        st.success("مفتاح الذكاء الاصطناعي موجود.")
    else:
        st.warning("لم يتم إعداد المفتاح.")

    st.markdown("""
    لإضافة المفتاح:

    1. افتح تطبيقك في Streamlit Cloud.
    2. Settings.
    3. Secrets.
    4. أضف المفتاح بالشكل التالي:
    """)

    st.code("""
GROQ_API_KEY = "ضع_مفتاحك_هنا"
""", language="toml")

    st.markdown("---")
    st.markdown("## قاعدة البيانات")
    st.write("تُحفظ المشاريع باستخدام SQLite.")

    st.markdown("---")
    st.markdown("## ملاحظة")
    st.write(
        "برهان مساعد بحثي، ولا يغني عن مراجعة الباحث للمعلومات "
        "والتحقق من المراجع والنتائج العلمية."
    )

# =====================================================
# نهاية التطبيق
# =====================================================
