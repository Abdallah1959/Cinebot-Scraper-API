# استخدام حاوية مايكروسوفت الرسمية المجهزة بكل ملفات المتصفحات
FROM mcr.microsoft.com/playwright/python:v1.59.0-jammy

# تحديد مجلد العمل داخل السيرفر
WORKDIR /app

# نسخ ملف المكتبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي كود المشروع (main.py)
COPY . .

# أمر التشغيل الذكي اللي بياخد البورت من Render تلقائياً
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"
