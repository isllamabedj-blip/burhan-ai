import streamlit as st

st.set_page_config(
    page_title="بُرهان | المرافق الذكي للباحث",
    page_icon="🔎",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
}
.stApp {
    background: #f4f7fb;
    direction: rtl;
}
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🔎 بُرهان")
st.sidebar.caption("من الفكرة إلى الدليل")
page = st.sidebar.radio(
    "التنقل",
    ["الرئيسية", "مشروع بحث جديد", "المساعد البحثي", "مشاريعي"]
)

if page == "الرئيسية":
    st.title("بُرهان")
    st.subheader("المرافق الذكي للباحث")
    st.write("من الفكرة إلى الدليل — رحلة بحثية أكثر وضوحًا وتنظيمًا.")
    st.info("ابدأ فكرتك البحثية، وساعد نفسك على تحويلها إلى مشروع علمي منظم.")

    c1, c2, c3 = st.columns(3)
    c1.metric("مراحل البحث", "8")
    c2.metric("مساعد بحثي", "متاح")
    c3.metric("مساحة العمل", "منظمة")

    st.markdown("### كيف يساعدك بُرهان؟")
    st.write("💡 تطوير الأفكار البحثية")
    st.write("🧩 صياغة الإشكاليات والفرضيات")
    st.write("📚 تنظيم مراحل البحث")
    st.write("📝 دعم الكتابة الأكاديمية")

elif page == "مشروع بحث جديد":
    st.title("إنشاء مشروع بحث")
    title = st.text_input("عنوان البحث")
    field = st.text_input("التخصص")
    description = st.text_area("وصف فكرة البحث")

    if st.button("إنشاء المشروع"):
        if title:
            st.session_state["project"] = {
                "title": title,
                "field": field,
                "description": description
            }
            st.success("تم إنشاء المشروع بنجاح!")
        else:
            st.warning("يرجى إدخال عنوان البحث.")

elif page == "المساعد البحثي":
    st.title("المساعد البحثي")
    st.write("ناقش فكرتك البحثية وابدأ في تطويرها.")

    idea = st.text_area("ما فكرة بحثك؟")

    if st.button("تحليل الفكرة"):
        if idea.strip():
            st.subheader("تحليل أولي")
            st.write("**فكرة البحث:**", idea)
            st.write("**الإشكالية المقترحة:**")
            st.write(f"ما طبيعة المشكلة المرتبطة بـ {idea}؟")            
            st.write("**أهداف البحث:**")
            st.write("- فهم الموضوع وتحليل أبعاده.")
            st.write("- تحديد المتغيرات والعوامل المؤثرة.")
            st.write("- الوصول إلى نتائج وتوصيات.")
            st.write("**المنهج المقترح:**")
            st.write("المنهج الوصفي التحليلي، ويُحدد بدقة بعد ضبط الإشكالية.")
        else:
            st.warning("أدخل فكرة البحث أولاً.")

elif page == "مشاريعي":
    st.title("مشاريعي البحثية")
    project = st.session_state.get("project")

    if project:
        st.subheader(project["title"])
        st.write("التخصص:", project["field"])
        st.write(project["description"])
    else:
        st.info("لا توجد مشاريع بعد. ابدأ بإنشاء مشروع جديد.")
