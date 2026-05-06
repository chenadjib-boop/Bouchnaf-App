import streamlit as st
import google.generativeai as genai
import PyPDF2

# 1. إعدادات الواجهة الاحترافية
st.set_page_config(page_title="مؤسسة بوشناف منذر", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stTable { background-color: white; }
    </style>
    <h1 style='text-align: center; color: #1E3A8A;'>🏗️ لوحة تحكم المشاريع - مؤسسة بوشناف</h1>
    <hr>
""", unsafe_allow_html=True)

# 2. إعداد الاتصال التلقائي
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model = genai.GenerativeModel(available_models[0])
except Exception as e:
    st.error(f"خطأ في الإعدادات: {e}")
    st.stop()

# 3. رفع ومعالجة الملف
uploaded_file = st.file_uploader("ارفع دفتر الشروط (PDF) لتحويله إلى جداول تنفيذية", type=["pdf"])

if uploaded_file:
    with st.spinner("جاري تحويل نص دفتر الشروط إلى جداول منظمة..."):
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_content = ""
            for page in pdf_reader.pages[:15]: # زيادة عدد الصفحات لضمان شمولية البيانات
                text_content += page.extract_text()

            # تطوير الطلب للحصول على جداول حقيقية
            prompt = f"""
            بصفتك مهندس إدارة مشاريع، حلل النص التالي المستخرج من دفتر شروط في الجزائر.
            يجب أن تكون المخرجات دقيقة وفي شكل جداول Markdown فقط كما يلي:

            1. **جدول الأسعار الوحدوية (BPU)**: (الرقم، بيان الأعمال، الوحدة، الكمية التقديرية).
            2. **جدول المخطط الزمني**: (المرحلة، مدة الإنجاز المتوقعة، الأسبوع المستهدف).
            3. **قائمة الاحتياجات الميدانية**: (نوع العتاد، عدد العمال المطلوبين).

            النص:
            {text_content}
            """
            
            response = model.generate_content(prompt)
            
            # 4. عرض النتائج في تبويبات (Tabs) لتنظيم العرض
            tab1, tab2, tab3 = st.tabs(["📊 جداول الأسعار (BPU)", "📅 المخطط الزمني", "🔧 العتاد والعمالة"])
            
            # تقسيم الاستجابة (محاولة بسيطة لعرض كل جزء في تبويبه)
            results = response.text.split("###") # يفترض أن الذكاء الاصطناعي يستخدم العناوين
            
            with tab1:
                st.markdown("### نتائج تحليل الأسعار")
                st.markdown(response.text) # سيعرض الجداول بشكل أنيق هنا
            
            with tab2:
                st.info("نصيحة: يمكنك نسخ هذه الجداول مباشرة ولصقها في ملف Excel للعمل عليها.")
                
        except Exception as e:
            st.error(f"حدث خطأ أثناء التنظيم: {e}")

st.markdown("<br><hr><center>مؤسسة بوشناف منذر للأشغال - برنامج إدارة المشاريع الذكي © 2026</center>", unsafe_allow_html=True)
