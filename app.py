import streamlit as st
import google.generativeai as genai
import tempfile
import os

# إعداد واجهة البرنامج الاحترافية
st.set_page_config(page_title="مؤسسة بوشناف منذر لأشغال البناء", layout="wide")

st.markdown("""
    <div style="text-align: center;">
        <h1>🏗️ نظام تحليل دفاتر الشروط الذكي</h1>
        <h3>مؤسسة بوشناف منذر لأشغال البناء والري</h3>
    </div>
    <hr>
""", unsafe_allow_html=True)

# استدعاء مفتاح API بأمان من إعدادات النظام
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# تعليمات المهندس الرقمي (عقل البرنامج)
system_instruction = """أنت مهندس متخصص في الصفقات العمومية والري في الجزائر. 
عند رفع دفتر شروط، قم بإنتاج تقرير منظم يحتوي على:
1. جدول الأسعار الوحدوية (BPU) بالكامل (رقم البند، البيان، الوحدة، الكمية).
2. جدول المخطط الزمني (Planning) مقسم لأسابيع (مثلاً لمشروع 90 يوم).
3. قائمة العتاد (المعدات) والعمالة المطلوبة في الموقع."""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# منطقة رفع الملفات
uploaded_file = st.file_uploader("ارفع دفتر الشروط (PDF) الخاص بالمشروع هنا", type=["pdf"])

if uploaded_file:
    with st.spinner("جاري تحليل المشروع وتوليد جداول الأسعار والمهام..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            # رفع الملف لجوجل ومعالجته
            gen_file = genai.upload_file(path=tmp_path)
            response = model.generate_content([gen_file, "حلل هذا المشروع وأعطني الجداول كاملة"])
            
            # عرض النتائج في تبويبات منظمة
            tab1, tab2 = st.tabs(["📊 التحليل والجداول", "📋 قائمة المهام التنفيذية"])
            with tab1:
                st.markdown(response.text)
            with tab2:
                st.info("نصيحة: يمكنك نسخ هذه الجداول مباشرة لملفات Excel.")
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
