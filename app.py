import streamlit as st

st.set_page_config(
    page_title="بُرهان | المرافق الذكي للباحث",
    page_icon="🔎",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

/* الخط العام */
html, body, [class*="css"], input, textarea, button {
    font-family: 'Cairo', sans-serif !important;
}

/* الخلفية الرئيسية */
.stApp {
    background-color: #FFFFFF;
    color: #000000;
    direction: rtl;
}

/* القائمة الجانبية */
section[data-testid="stSidebar"] {
    background-color: #183B5B;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* العناوين */
h1, h2, h3, h4 {
    color: #183B5B !important;
    font-weight: 800 !important;
}

/* النصوص */
p, label, .stMarkdown {
    color: #000000;
}

/* خانات الكتابة */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #183B5B !important;
    border-radius: 9px !important;
    caret-color: #183B5B !important;
}

/* النص الإرشادي داخل الخانات */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #555555 !important;
    opacity: 1 !important;
}

/* القوائم المنسدلة */
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #000000 !important;
}

/* الأزرار */
.stButton > button {
    background-color: #183B5B !important;
    color: #FFFFFF !important;
    border: 1px solid #183B5B !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
}

.stButton > button:hover {
    background-color: #28577D !important;
    color: #FFFFFF !important;
}

/* البطاقات */
div[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #B8D0E5;
    border-radius: 12px;
    padding: 18px;
}

/* الرسائل */
div[data-testid="stAlert"] {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #183B5B;
    border-radius: 10px;
}

/* المسافات */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
        <style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], input, textarea, button {
    font-family: 'Cairo', sans-serif !important;
}

.stApp {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    direction: rtl;
}

/* إلغاء الخط الفاصل للقائمة */
section[data-testid="stSidebar"] {
    background-color: #183B5B !important;
    border-right: none !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] > div {
    border-right: none !important;
    box-shadow: none !important;
}

[data-testid="stSidebarContent"] {
    background-color: #183B5B !important;
}

/* القائمة */
section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

/* المحتوى */
.block-container {
    max-width: 1200px !important;
    padding: 1.5rem 1rem 3rem 1rem !important;
}

/* العناوين */
h1, h2, h3, h4 {
    color: #183B5B !important;
    font-weight: 800 !important;
}

/* النصوص */
p, label, .stMarkdown {
    color: #000000;
}

/* خانات الكتابة */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #183B5B !important;
    border-radius: 9px !important;
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
.stButton > button {
    background-color: #183B5B !important;
    color: #FFFFFF !important;
    border: 1px solid #183B5B !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
}

.stButton > button:hover {
    background-color: #28577D !important;
    color: #FFFFFF !important;
}

/* البطاقات */
div[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #B8D0E5 !important;
    border-radius: 12px !important;
    padding: 18px !important;
}

/* الرسائل */
div[data-testid="stAlert"] {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #183B5B !important;
    border-radius: 10px !important;
}

/* تحسين الهاتف */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.6rem !important;
    }

    h1 {
        font-size: 1.8rem !important;
    }

    h2, h3 {
        font-size: 1.3rem !important;
    }

    div[data-testid="stMetric"] {
        padding: 12px !important;
    }

    [data-testid="stAlert"] {
        width: 100% !important;
        overflow-wrap: break-word !important;
    }
}
</style>
