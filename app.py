import streamlit as st
import google.generativeai as genai
import PyPDF2
import pandas as pd
from datetime import datetime

# 1. إعدادات الهوية البصرية
st.set_page_config(page_title="نظام بوشناف لإدارة المشاريع", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏗️ نظام إدارة وتنفيذ المشاريع - مؤسسة بوشناف</h1>", unsafe_allow_html=True)

# 2. إعداد قاعدة بيانات بسيطة في ذاكرة البرنامج (Session State)
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# 3. ربط الذكاء الاصطناعي (العقل المدبر)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
except:
    st.error("يرجى ضبط مفتاح API أولاً.")
    st.stop()

# --- القائمة الجانبية للتنقل ---
menu = st.sidebar.radio("القائمة الرئيسية", ["تحليل دفتر شروط جديد", "متابعة تقدم الأشغال اليومية", "وضعية المشروع (Situations)"])

# --- المرحلة 1: تحليل دفتر الشروط وخلق المهام ---
if menu == "تحليل دفتر شروط جديد":
    st.header("📂 استيراد مشروع جديد")
    uploaded_file = st.file_uploader("ارفع ملف PDF (بئر غبالو، حريملة، إلخ)", type=["pdf"])
    
    if uploaded_file and st.button("بدء المعالجة الذكية"):
        with st.spinner("جاري استخراج البيانات وبناء خطة العمل..."):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = "".join([p.extract_text() for p in pdf_reader.pages[:10]])
            
            prompt = f"حلل هذا النص واستخرج المهام الكبرى للمشروع في شكل قائمة مفصولة بفاصلة فقط. النص: {text}"
            response = model.generate_content(prompt)
            
            # تحويل النص إلى قائمة مهام في قاعدة البيانات
            extracted_tasks = response.text.split(",")
            st.session_state.tasks = [{"المهمة": t.strip(), "التقدم": 0, "الحالة": "لم تبدأ"} for t in extracted_tasks]
            st.success("تم استخراج المهام بنجاح! انتقل الآن لصفحة متابعة الأشغال.")

# --- المرحلة 2: واجهة مسؤول المشروع (تحديث التقدم) ---
elif menu == "متابعة تقدم الأشغال اليومية":
    st.header("👷 لوحة تحكم مسؤول الموقع")
    if not st.session_state.tasks:
        st.warning("لا توجد مهام حالية. يرجى رفع دفتر الشروط أولاً.")
    else:
        st.subheader("تحديث نسبة الإنجاز اليومية")
        for i, task in enumerate(st.session_state.tasks):
            cols = st.columns([3, 2, 1])
            with cols[0]:
                st.write(f"**{task['المهمة']}**")
            with cols[1]:
                new_progress = st.slider("نسبة الإنجاز %", 0, 100, task['التقدم'], key=f"slider_{i}")
                st.session_state.tasks[i]['التقدم'] = new_progress
            with cols[2]:
                if new_progress == 100: st.success("مكتملة")
                elif new_progress > 0: st.info("جارية")
                else: st.dark_content("منتظرة")

# --- المرحلة 3: وضعية الأشغال والتقارير ---
elif menu == "وضعية المشروع (Situations)":
    st.header("📊 وضعية الأشغال الحالية")
    if st.session_state.tasks:
        df = pd.DataFrame(st.session_state.tasks)
        st.table(df)
        
        # حساب النسبة الكلية للمشروع
        total_progress = df['التقدم'].mean()
        st.metric("نسبة تقدم المشروع الكلية", f"{total_progress:.2f}%")
        st.progress(total_progress / 100)
        
        if st.button("توليد تقرير للمدير"):
            st.write(f"تقرير يوم: {datetime.now().strftime('%Y-%m-%d')}")
            st.write("المشروع يسير وفق الخطة (مثال) - يرجى توفير عتاد الحفر للمرحلة القادمة.")
    else:
        st.error("لا توجد بيانات لعرضها.")
