import streamlit as st
import google.generativeai as genai
import PyPDF2
import pandas as pd

# --- 1. إعدادات الهوية البصرية ودعم اللغة العربية ---
st.set_page_config(page_title="Bouchnaf ERP", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .stMarkdown, .stTable, .stDataFrame {
        direction: RTL;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    .main-header {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-right: 5px solid #1E3A8A;
        text-align: center;
    }
    </style>
    <div class="main-header">
        <h1>🏗️ نظام بوشناف لإدارة المشاريع والوضعيات</h1>
        <p>مؤسسة بوشناف منذر للأشغال - سوق أهراس</p>
    </div>
""", unsafe_allow_html=True)

# --- 2. الربط مع الذكاء الاصطناعي ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # اكتشاف الموديل تلقائياً لتجنب خطأ 404
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model = genai.GenerativeModel(available_models[0])
except:
    st.error("خطأ: يرجى التحقق من مفتاح API في الإعدادات.")
    st.stop()

# --- 3. القائمة الجانبية للتنقل ---
st.sidebar.title("🛠️ لوحة التحكم")
menu = st.sidebar.radio("", ["📊 لوحة القيادة (Dashboard)", "📝 تحليل العقود (BPU)", "🚧 متابعة الميدان", "📄 وضعية الأشغال (Situation)"])

# --- القسم الأول: لوحة القيادة ---
if menu == "📊 لوحة القيادة (Dashboard)":
    st.subheader("🏠 ملخص أداء المؤسسة")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='card'><h4>إجمالي قيمة المشاريع</h4><h2 style='color:#1E3A8A;'>18.5M د.ج</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='card'><h4>نسبة الإنجاز الكلية</h4><h2 style='color:#10B981;'>72%</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='card'><h4>الورشات النشطة</h4><h2 style='color:#F59E0B;'>03</h2></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📈 تقدم مشروع بئر غبالو (حريملة)")
    chart_data = pd.DataFrame({
        "البند": ["تنصيب الورشة", "حفر (Forage)", "التجهيز", "التجارب"],
        "النسبة %": [100, 85, 40, 0]
    })
    st.bar_chart(chart_data, x="البند", y="النسبة %")

# --- القسم الثاني: تحليل BPU ---
elif menu == "📝 تحليل العقود (BPU)":
    st.header("📄 تحليل ذكي لدفتر الشروط")
    file = st.file_uploader("ارفع ملف PDF لمشروع جديد", type=["pdf"])
    if file and st.button("بدء الاستخراج"):
        with st.spinner("جاري قراءة البيانات..."):
            reader = PyPDF2.PdfReader(file)
            text = "".join([p.extract_text() for p in reader.pages[:10]])
            response = model.generate_content(f"استخرج جدول الأسعار (BPU) من النص التالي بجدول Markdown: {text}")
            st.markdown(response.text)

# --- القسم الثالث: متابعة الميدان ---
elif menu == "🚧 متابعة الميدان":
    st.header("👷 تحديثات مسؤول الموقع")
    with st.container():
        st.info("قم بتحديث الكميات المنجزة فعلياً ليتم حساب الوضعية المالية تلقائياً.")
        item = st.text_input("اسم البند (مثال: حفر ميكانيكي 120م)")
        qty = st.number_input("الكمية المنجزة اليوم", min_value=0.0)
        st.multiselect("العتاد المستخدم", ["حفارة هيدروليكية", "شاحنة صهريج", "ضاغط هواء"])
        if st.button("حفظ التقرير"):
            st.success("تم تسجيل البيانات بنجاح.")

# --- القسم الرابع: وضعية الأشغال (الموديل الرسمي) ---
elif menu == "📄 وضعية الأشغال (Situation)":
    st.header("📄 كشف وضعية الأشغال رقم 01")
    st.write("**المشروع:** إنجاز ثقب مائي ببلدية بئر غبالو")
    
    # محاكاة لبيانات وضعية أشغال حقيقية
    data = {
        "رقم البند": ["01", "02", "03"],
        "تعيين الأشغال": ["تنصيب الورشة", "الحفر الميكانيكي", "تجهيز البئر بالأنابيب"],
        "الوحدة": ["جزافي", "ML", "ML"],
        "السعر (د.ج)": [200000, 9500, 4800],
        "الكمية المتعاقد عليها": [1, 120, 120],
        "الكمية المنجزة": [1, 105, 40]
    }
    df = pd.DataFrame(data)
    df["المبلغ الحالي (HT)"] = df["الكمية المنجزة"] * df["السعر (د.ج)"]
    
    st.table(df.style.format({"السعر (د.ج)": "{:,.2f}", "المبلغ الحالي (HT)": "{:,.2f}"}))
    
    total = df["المبلغ الحالي (HT)"].sum()
    st.markdown(f"<div style='background:#f1f5f9; padding:15px; border-radius:5px; text-align:left;'><h3>المبلغ المستحق الإجمالي: {total:,.2f} د.ج</h3></div>", unsafe_allow_html=True)
