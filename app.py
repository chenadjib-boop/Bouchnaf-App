import streamlit as st
import google.generativeai as genai
import tempfile
import os

# إعداد واجهة البرنامج
st.set_page_config(page_title="مؤسسة بوشناف منذر لأشغال البناء", layout="wide")

st.markdown("""
    <div style="text-align: center;">
        <h1>🏗️ نظام تحليل دفاتر الشروط الذكي</h1>
        <h3>مؤسسة بوشناف منذر لأشغال البناء والري</h3>
    </div>
    <hr>
""", unsafe_allow_html=True)

# استدعاء مفتاح API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("يرجى إضافة GOOGLE_API_KEY في إعدادات Secrets في Streamlit")
    st.stop()

api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# تعليمات المهندس الرقمي
system_instruction = """أنت مهندس متخصص في الصفقات العمومية والري في الجزائر. 
عند رفع دفتر شروط، قم بإنتاج تقرير منظم يحتوي على:
1. جدول الأسعار الوحدوية (BPU) بالكامل (رقم البند، البيان، الوحدة، الكمية).
2. جدول المخطط الزمني (Planning) مقسم لأسابيع.
3. قائمة العتاد (المعدات) والعمالة المطلوبة في الموقع."""

# اختيار النموذج بشكل صحيح لتجنب خطأ 404
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# منطقة رفع الملفات
uploaded_file = st.file_uploader("ارفع دفتر الشروط (PDF) الخاص بالمشروع هنا", type=["pdf"])

if uploaded_file:
    with st.spinner("جاري تحليل المشروع..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            # رفع الملف لجوجل
            gen_file = genai.upload_file(path=tmp_path)
            # توليد المحتوى
            response = model.generate_content([gen_file, "حلل هذا المشروع وأعطني الجداول كاملة"])
            
            # عرض النتائج
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء المعالجة: {e}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
