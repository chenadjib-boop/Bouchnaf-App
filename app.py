import streamlit as st
import google.generativeai as genai
import PyPDF2
import pandas as pd
from datetime import datetime

# 1. إعدادات الهوية والواجهة
st.set_page_config(page_title="نظام بوشناف لإدارة المشاريع", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    <h1 style='text-align: center; color: #1E3A8A;'>🏗️ نظام إدارة تنفيذ المشاريع - مؤسسة بوشناف</h1>
    <p style='text-align: center;'>تحليل دفاتر الشروط ومتابعة ورشات (بئر غبالو / حريملة)</p>
    <hr>
""", unsafe_allow_html=True)

# 2. إعداد الاتصال واكتشاف الموديل تلقائياً (لحل خطأ 404 للأبد)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # البحث عن أول موديل متاح في حسابك يدعم توليد المحتوى
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if not models:
        st.error("لا يوجد محرك متاح في حسابك.")
        st.stop()
    
    model = genai.GenerativeModel(models[0])
    st.sidebar.success(f"المحرك النشط: {models[0]}")
except Exception as e:
    st.error(f"خطأ في الاتصال: {e}")
    st.stop()

# 3. مخزن البيانات المؤقت (لربط المهام بتقدم الأشغال)
if 'tasks_df' not in st.session_state:
    st.session_state.tasks_df = None

# --- القائمة الجانبية ---
menu = st.sidebar.radio("القائمة الرئيسية", ["📂 استيراد مشروع (PDF)", "👷 متابعة الأشغال اليومية", "📊 وضعية المشروع"])

# --- المرحلة 1: التحليل الذكي ---
if menu == "📂 استيراد مشروع (PDF)":
    st.subheader("رفع وتحليل دفتر الشروط")
    uploaded_file = st.file_uploader("ارفع ملف PDF لمشروع الحفر أو البناء", type=["pdf"])
    
    if uploaded_file and st.button("تحليل واستخراج المهام"):
        with st.spinner("جاري قراءة الملف وتوليد خطة العمل..."):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = "".join([p.extract_text() for p in pdf_reader.pages[:10]])
            
            prompt = f"""أنت مهندس جزائري خبير. استخرج من هذا النص قائمة بالمهام الرئيسية للتنفيذ (بند الحفر، الأنابيب، إلخ).
            أعطني النتيجة كقائمة مهام فقط، كل مهمة في سطر منفصل وبدون أرقام.
            النص: {text}"""
            
            response = model.generate_content(prompt)
            lines = response.text.strip().split('\n')
            
            # بناء جدول المهام الابتدائي
            data = {
                "المهمة": [line.strip() for line in lines if line.strip()],
                "نسبة الإنجاز %": [0] * len([line for line in lines if line.strip()]),
                "الحالة": ["منتظرة"] * len([line for line in lines if line.strip()])
            }
            st.session_state.tasks_df = pd.DataFrame(data)
            st.success("تم تحليل المشروع بنجاح! توجه لقسم متابعة الأشغال.")

# --- المرحلة 2: واجهة مسؤول المشروع (التحديث اليومي) ---
elif menu == "👷 متابعة الأشغال اليومية":
    st.subheader("تحديث التقدم الميداني")
    if st.session_state.tasks_df is not None:
        for index, row in st.session_state.tasks_df.iterrows():
            col1, col2 = st.columns([3, 2])
            with col1:
                st.write(f"🔹 {row['المهمة']}")
            with col2:
                # تحديث النسبة
                new_val = st.slider("نسبة الإنجاز", 0, 100, int(row['نسبة الإنجاز %']), key=f"s_{index}")
                st.session_state.tasks_df.at[index, 'نسبة الإنجاز %'] = new_val
                # تحديث الحالة تلقائياً
                if new_val == 100: st.session_state.tasks_df.at[index, 'الحالة'] = "مكتملة"
                elif new_val > 0: st.session_state.tasks_df.at[index, 'الحالة'] = "جارية"
        st.success("يتم حفظ التغييرات تلقائياً في الجلسة الحالية.")
    else:
        st.info("يرجى رفع ملف المشروع أولاً من القائمة الجانبية.")

# --- المرحلة 3: وضعية الأشغال (التقرير النهائي) ---
elif menu == "📊 وضعية المشروع":
    st.subheader("وضعية الأشغال (Situation)")
    if st.session_state.tasks_df is not None:
        df = st.session_state.tasks_df
        
        # عرض المقاييس الكلية
        total_p = df['نسبة الإنجاز %'].mean()
        st.metric("النسبة الإجمالية لتقدم المشروع", f"{total_p:.2f} %")
        st.progress(total_p / 100)
        
        # عرض الجدول التفصيلي
        st.table(df)
        
        # زر التحميل (Export)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("تحميل تقرير الوضعية (CSV)", csv, "situation_report.csv", "text/csv")
    else:
        st.warning("لا توجد بيانات مشروع لعرضها.")

st.sidebar.markdown("---")
st.sidebar.info("مؤسسة بوشناف منذر للأشغال\nسوق أهراس - الجزائر")
