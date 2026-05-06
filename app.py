import streamlit as st
import google.generativeai as genai
import PyPDF2

# 1. إعدادات الواجهة
st.set_page_config(page_title="مؤسسة بوشناف منذر", layout="wide")
st.markdown("<h1 style='text-align: center;'>🏗️ نظام بوشناف لتحليل المشاريع</h1><hr>", unsafe_allow_html=True)

# 2. جلب المفتاح وتحديد الموديل المتاح تلقائياً
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # هذه الخطوة تبحث في حسابك عن الموديل الذي يدعم توليد المحتوى وتختاره
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if not available_models:
        st.error("لم يتم العثور على أي موديل متاح في حسابك. تأكد من إعدادات API Key.")
        st.stop()
    
    # اختيار أول موديل متاح (سواء كان pro أو flash أو غيره)
    model_to_use = available_models[0]
    model = genai.GenerativeModel(model_to_use)
    st.sidebar.success(f"تم الاتصال بالمحرك: {model_to_use}")

except Exception as e:
    st.error(f"خطأ في الاتصال بجوجل: {e}")
    st.stop()

# 3. معالجة الملف
uploaded_file = st.file_uploader("ارفع ملف دفتر الشروط (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner("جاري استخراج جداول الأسعار والمهام..."):
        try:
            # استخراج النص من PDF
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_content = ""
            for page in pdf_reader.pages[:10]: # نأخذ أول 10 صفحات لضمان السرعة
                text_content += page.extract_text()

            prompt = f"أنت خبير صفقات عمومية جزائري. من النص التالي، استخرج جدول الأسعار (BPU) وجدول المهام التنفيذية:\n\n{text_content}"
            
            response = model.generate_content(prompt)
            st.markdown("### 📊 نتائج تحليل المشروع")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء التحليل: {e}")

st.markdown("<hr><center>مؤسسة بوشناف منذر للأشغال - سوق أهراس</center>", unsafe_allow_html=True)
