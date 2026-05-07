import streamlit as st
import google.generativeai as genai
import PyPDF2
import pandas as pd

# 1. ضبط اتجاه الصفحة (من اليمين إلى اليسار) وتنسيق الخطوط
st.set_page_config(page_title="نظام بوشناف لإدارة المشاريع", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .stMarkdown {
        direction: RTL;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    .stTable { direction: RTL !important; text-align: right !important; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1E3A8A; color: white; }
    </style>
    <div style='text-align: center; background-color: #1E3A8A; padding: 20px; border-radius: 10px;'>
        <h1 style='color: white;'>🏗️ نظام إدارة المشاريع - مؤسسة بوشناف منذر</h1>
        <p style='color: #d1d5db;'>توليد وضعيات الأشغال وتحليل دفاتر الشروط (BPU/DQE)</p>
    </div>
    <hr>
""", unsafe_allow_html=True)

# 2. إعداد الاتصال بالذكاء الاصطناعي
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model = genai.GenerativeModel(models[0])
except:
    st.error("خطأ في الاتصال بالخادم. تأكد من مفتاح الـ API.")
    st.stop()

# 3. إدارة البيانات
if 'project_df' not in st.session_state:
    st.session_state.project_df = None

# --- القائمة الجانبية ---
st.sidebar.title("القائمة الرئيسية")
menu = st.sidebar.radio("", ["📁 استيراد مشروع جديد", "🚧 متابعة الورشة والتقدم", "📄 توليد وضعية الأشغال (Situation)"])

# --- المرحلة 1: استخراج BPU ---
if menu == "📁 استيراد مشروع جديد":
    st.header("📂 استخراج جدول الأسعار والكميات")
    file = st.file_uploader("ارفع دفتر الشروط (PDF)", type=["pdf"])
    if file and st.button("تحليل الدفتر واستخراج البيانات"):
        with st.spinner("جاري قراءة البيانات وتنسيق الجداول..."):
            reader = PyPDF2.PdfReader(file)
            text = "".join([p.extract_text() for p in reader.pages[:15]])
            
            prompt = f"استخرج جدول الأسعار (BPU) من هذا النص. أريد النتائج في جدول بأعمدة: الرقم، التعيين، الوحدة، الكمية، السعر الوحدوي. النص: {text}"
            response = model.generate_content(prompt)
            
            st.markdown("### الجدول المستخرج من دفتر الشروط:")
            st.write(response.text)
            st.info("ملاحظة: يمكنك نسخ هذا الجدول لاستخدامه في النظام.")

# --- المرحلة 2: متابعة التقدم ---
elif menu == "🚧 متابعة الورشة والتقدم":
    st.header("🚧 تحديث التقدم الميداني")
    st.info("هنا يقوم مسؤول المشروع بتحديث نسب الإنجاز الفعلية.")
    
    # نموذج تفاعلي لإدخال التقدم (يمكن ربطه بقاعدة بيانات لاحقاً)
    with st.form("progress_form"):
        st.subheader("إدخال الكميات المنجزة")
        c1, c2, c3 = st.columns(3)
        with c1: item_name = st.text_input("تعيين البند (مثال: حفر البئر)")
        with c2: total_qty = st.number_input("الكمية الكلية في العقد", min_value=0.0)
        with c3: done_qty = st.number_input("الكمية المنجزة حالياً", min_value=0.0)
        
        if st.form_submit_button("حفظ التقدم"):
            st.success(f"تم تسجيل {done_qty} من {total_qty} لبند {item_name}")

# --- المرحلة 3: وضعية الأشغال الاحترافية ---
elif menu == "📄 توليد وضعية الأشغال (Situation)":
    st.header("📄 كشف وضعية الأشغال رقم 01")
    st.write("**المشروع:** إنجاز ثقب مائي ببلدية بئر غبالو")
    st.write("**المقاول:** مؤسسة بوشناف منذر")
    
    # إنشاء نموذج جدول وضعية أشغال جزائري احترافي
    data = {
        "رقم البند": ["01", "02", "03"],
        "تعيين الأشغال": ["تنصيب الورشة", "الحفر الميكانيكي (Forage)", "التجهيز بالأنابيب"],
        "الوحدة": ["F", "ML", "ML"],
        "السعر الوحدوي (DA)": [150000, 8000, 4500],
        "الكمية المتعاقد عليها": [1, 120, 120],
        "الكمية المنجزة (سابقاً)": [0, 0, 0],
        "الكمية المنجزة (حالياً)": [1, 45, 0],
    }
    
    df = pd.DataFrame(data)
    # حساب المبالغ تلقائياً
    df["المبلغ الحالي (HT)"] = df["الكمية المنجزة (حالياً)"] * df["السعر الوحدوي (DA)"]
    df["نسبة الإنجاز %"] = (df["الكمية المنجزة (حالياً)"] / df["الكمية المتعاقد عليها"]) * 100
    
    st.table(df)
    
    total_amount = df["المبلغ الحالي (HT)"].sum()
    st.metric("إجمالي المبلغ المستحق (بدون رسوم)", f"{total_amount:,.2f} د.ج")
    
    if st.button("تصدير الوضعية إلى Excel"):
        st.write("جاري التحميل...")
