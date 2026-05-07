import streamlit as st
import google.generativeai as genai
import PyPDF2
import pandas as pd

# 1. إعدادات النظام الاحترافي
st.set_page_config(page_title="Bouchnaf Construction ERP", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: #1E3A8A;'>🏗️ نظام بوشناف لإدارة الأشغال والري</h1>
    <p style='text-align: center; font-weight: bold;'>التحول الرقمي لمتابعة المشاريع (بئر غبالو / حريملة)</p>
    <hr>
""", unsafe_allow_html=True)

# 2. ربط الذكاء الاصطناعي (المحرك الذكي)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # اختيار الموديل تلقائياً لتجنب أخطاء 404
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model = genai.GenerativeModel(models[0])
except:
    st.error("خطأ في الربط التقني بمحرك جوجل.")
    st.stop()

# 3. إدارة الجلسة وتخزين البيانات
if 'project_data' not in st.session_state:
    st.session_state.project_data = None

# --- القائمة الرئيسية للمقاول ---
menu = st.sidebar.radio("لوحة التحكم", ["📊 استخراج بيانات الصفقة (BPU)", "🚧 متابعة الورشة اليومية", "💰 الوضعية المالية (Situation)"])

# --- المرحلة 1: استخراج البيانات ---
if menu == "📊 استخراج بيانات الصفقة (BPU)":
    st.header("تفكيك دفتر الشروط (Extraction)")
    file = st.file_uploader("ارفع دفتر الشروط PDF", type=["pdf"])
    if file and st.button("تحليل الصفقة"):
        with st.spinner("جاري تحويل النصوص إلى أرقام وكميات..."):
            reader = PyPDF2.PdfReader(file)
            text = "".join([p.extract_text() for p in reader.pages[:15]]) # قراءة صفحات أكثر
            
            # طلب استخراج جدول احترافي
            prompt = f"""حلل هذا الدفتر واستخرج جدول الأسعار (BPU) بالصيغة التالية فقط:
            البند | البيان | الوحدة | الكمية | السعر الوحدوي
            النص المستخرج: {text}"""
            
            response = model.generate_content(prompt)
            st.markdown("### جدول الأسعار والكميات المستخرج:")
            st.write(response.text)
            st.info("قم بنسخ هذه البيانات إلى قسم المتابعة أدناه للبدء.")

# --- المرحلة 2: متابعة الورشة (هنا يتدخل مسؤول المشروع) ---
elif menu == "🚧 متابعة الورشة اليومية":
    st.header("👷 سجل المتابعة اليومي - مسؤول الموقع")
    st.subheader("تحديث حالة تنفيذ البنود")
    
    # مثال لجدول تفاعلي (يمكن تطويره ليرتبط بالبيانات المستخرجة)
    items = ["حفر البئر (Forage)", "التجهيز بالأنابيب", "تجارب الضخ", "بناء الغرفة التقنية"]
    for item in items:
        with st.expander(f"بند: {item}"):
            c1, c2, c3 = st.columns(3)
            with c1: st.slider("نسبة الإنجاز %", 0, 100, key=f"p_{item}")
            with c2: st.number_input("الكمية المنجزة اليوم", key=f"q_{item}")
            with c3: st.multiselect("العتاد المستخدم", ["حفارة", "شاحنة رافعة", "ضاغط هواء"], key=f"e_{item}")

# --- المرحلة 3: الوضعية المالية (لب المشروع) ---
elif menu == "💰 الوضعية المالية (Situation)":
    st.header("📉 كشف وضعية الأشغال (Situation N°)")
    st.write("هنا يتم حساب المبالغ المالية المستحقة للمؤسسة بناءً على ما تم إنجازه فعلياً.")
    
    # عرض رسم بياني لتقدم المشروع
    chart_data = pd.DataFrame({"البند": ["حفر", "أنابيب", "بناء"], "الإنجاز": [80, 40, 10]})
    st.bar_chart(chart_data, x="البند", y="الإنجاز")
    
    st.button("توليد ملف الوضعية المالية")
