import streamlit as st
import google.generativeai as genai
import os

# 1. إعدادات الواجهة (هوية مؤسسة بوشناف)
st.set_page_config(page_title="مؤسسة بوشناف منذر للأشغال", layout="wide")

st.markdown("""
    <div style="text-align: center;">
        <h1 style="color: #1E1E1E;">🏗️ نظام تحليل دفاتر الشروط</h1>
        <h3 style="color: #4A4A4A;">مؤسسة بوشناف منذر لأشغال البناء والري</h3>
    </div>
    <hr>
""", unsafe_allow_html=True)

# 2. جلب المفتاح السري من الإعدادات
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("خطأ: لم يتم العثور على مفتاح API في الإعدادات (Secrets).")
    st.stop()

# 3. إعداد المحرك الكلاسيكي (الأكثر توافقاً لضمان عدم ظهور خطأ 404)
# استخدمنا gemini-pro لأنه يدعم معظم المفاتيح القديمة والجديدة
model = genai.GenerativeModel('gemini-pro')

# 4. واجهة رفع الملفات
uploaded_file = st.file_uploader("ارفع ملف دفتر الشروط بصيغة PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("جاري قراءة البيانات وتنظيم الجداول..."):
        try:
            # قراءة النص من ملف PDF المرفوع مباشرة
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text()

            # إرسال النص للمحرك مع التعليمات
            prompt = f"""
            أنت مهندس متخصص في الصفقات العمومية بالجزائر. 
            بناءً على النص التالي من دفتر الشروط، استخرج ما يلي في جداول منظمة:
            1. جدول الأسعار (BPU) مع الكميات والبيان.
            2. المخطط الزمني للتنفيذ (Planning).
            3. قائمة المعدات والعمالة المطلوبة.
            
            النص المستخرج:
            {text_content[:15000]} 
            """
            
            response = model.generate_content(prompt)
            
            # 5. عرض النتائج النهائية
            st.success("تم التحليل بنجاح!")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"عذراً، حدث خطأ: {str(e)}")
            st.info("نصيحة: تأكد من أن مفتاح API صحيح ونشط في حسابك على Google AI Studio.")

st.markdown("<br><hr><center>جميع الحقوق محفوظة لمؤسسة بوشناف منذر © 2026</center>", unsafe_allow_html=True)
