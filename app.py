import streamlit as st
import google.generativeai as genai
import PyPDF2
import pandas as pd

# --- إعدادات الصفحة والخطوط ---
st.set_page_config(page_title="Bouchnaf Construction ERP", layout="wide")

# تطبيق تنسيق RTL (من اليمين إلى اليسار) وتنسيق الهوية البصرية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .stMarkdown, .stTable, .stDataFrame {
        direction: RTL;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    .main-header {
        background-color: #1E3A8A;
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #ffffff;
        border-right: 5px solid #1E3A8A;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    div[data-testid="stExpander"] { text-align: right; direction: RTL; }
    </style>
""", unsafe_allow_html=True)

# --- الربط التقني ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model = genai.GenerativeModel(models[0])
except:
    st.error("يرجى ضبط مفتاح API في الإعدادات.")
    st.stop()

# --- واجهة البرنامج الرئيسية ---
st.markdown("<div class='main-header'><h1>🏗️ نظام بوشناف لإدارة المشاريع والوضعيات</h1><p>التحول الرقمي لمؤسسة بوشناف منذر للأشغال - سوق أهراس</p></div>", unsafe_allow_html=True)

# القائمة الجانبية
st.sidebar.title("🗂️ لوحة التحكم")
menu = st.sidebar.radio("", ["📊 لوحة القيادة (Dashboard)", "📝 تحليل الصفقات (BPU)", "🚧 متابعة الورشة اليومية", "📄 كشف وضعية الأشغال (Situation)"])

# 1. لوحة القيادة
if menu == "📊 لوحة القيادة (Dashboard)":
    st.subheader("📈 ملخص حالة المشاريع")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='metric-card'><h4>إجمالي قيمة المشاريع</h4><h3>18,500,000 د.ج</h3></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='metric-card'><h4>نسبة الإنجاز المتوسطة</h4><h3>72%</h3></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='metric-card'><h4>عدد الورشات النشطة</h4><h3>03</h3></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📅 الجدول الزمني والتقدم")
    df_chart = pd.DataFrame({
        "البند": ["تنصيب الورشة", "الحفر (Forage)", "التجهيز بالأنابيب", "تجارب الضخ"],
        "التقدم %": [100, 85, 40, 0]
    })
    st.bar_chart(df_chart, x="البند", y="التقدم %")

# 2. تحليل الصفقات
elif menu == "📝 تحليل الصفقات (BPU)":
    st.header("📄 استخراج البيانات من دفتر الشروط")
    uploaded_file = st.file_uploader("ارفع ملف PDF لمشروع (بئر غبالو أو غيره)", type=["pdf"])
    if uploaded_file:
        if st.button("بدء المعالجة الذكية"):
            with st.spinner("جاري تفكيك بنود العقد..."):
                reader = PyPDF2.PdfReader(uploaded_file)
                text = "".join([p.extract_text() for p in reader.pages[:10]])
                response = model.generate_content(f"استخرج جدول BPU من النص التالي بجدول منظم: {text}")
                st.markdown(response.text)

# 3. متابعة الورشة
elif menu == "🚧 متابعة الورشة اليومية":
    st.header("👷 سجل المتابعة الميداني")
    st.info("هنا يقوم مسؤول الموقع بإدخال التقدم اليومي للعتاد والعمالة.")
    with st.expander("📝 إضافة تقرير يومي جديد"):
        c1, c2 = st.columns(2)
        with c1: st.date_input("تاريخ اليوم")
        with c2: st.selectbox("المشروع", ["بئر غبالو", "حريملة", "مشروع آخر"])
        st.multiselect("العتاد المستخدم اليوم", ["حفارة هيدروليكية", "شاحنة رافعة", "ضاغط هواء", "مولد كهربائي"])
        st.text_area("ملاحظات تقنية (حالة التربة، معوقات)")
        st.button("حفظ التقرير اليومي")

# 4. وضعية الأشغال (النموذج الرسمي)
elif menu == "📄 كشف وضعية الأشغال (Situation)":
    st.header("📄 كشف وضعية الأشغال (Modèle Officiel)")
    st.write("**المصلحة المتعاقدة:** مديرية الموارد المائية")
    
    data = {
        "البند": ["01", "02", "03", "04"],
        "التعيين": ["تنصيب الورشة", "حفر ميكانيكي (120م)", "توريد أنابيب فولاذية", "تجارب الضخ"],
        "الوحدة": ["جزافي", "ML", "ML", "H"],
        "السعر (DA)": [200000.00, 9500.00, 4800.00, 3500.00],
        "الكمية الكلية": [1, 120, 120, 24],
        "المنجز حالياً": [1, 105, 50, 0]
    }
    df_sit = pd.DataFrame(data)
    df_sit["المبلغ المستحق (HT)"] = df_sit["المنجز حالياً"] * df_sit["السعر (DA)"]
    
    st.table(df_sit.style.format({"السعر (DA)": "{:,.2f}", "المبلغ المستحق (HT)": "{:,.2f}"}))
    
    total = df_sit["المبلغ المستحق (HT)"].sum()
    st.markdown(f"<div style='text-align: left; padding: 10px; background: #eee; border-radius: 5px;'><h3>المبلغ الإجمالي المنجز: {total:,.2f} د.ج</h3></div>", unsafe_allow_html=True)
    st.button("📥 تحميل ملف الوضعية (Excel)")
