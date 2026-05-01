from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
import asyncio

app = FastAPI(title="Cinebot Master Extractor 🍿")

# السماح للواجهة بالاتصال بالسيرفر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Master Extractor is ONLINE and ready to intercept 🚀"}

@app.get("/scrape/{tmdb_id}")
async def scrape_movie(tmdb_id: str):
    async with async_playwright() as p:
        # هنا التعديل السحري: هنقفل كل الإضافات والجرافيكس عشان نوفر الـ RAM للسيرفر المجاني
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--disable-setuid-sandbox",
                "--no-sandbox",
            ]
        )
        
        # انتحال شخصية متصفح حقيقي (User-Agent)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}, # صغرنا الشاشة لتوفير الرام
            java_script_enabled=True
        )
        
        page = await context.new_page()
        extracted_m3u8 = None

        # دالة المراقبة: اعتراض الشبكة لخطف الرابط
        async def intercept_request(request):
            nonlocal extracted_m3u8
            if ".m3u8" in request.url:
                extracted_m3u8 = request.url

        # تشغيل المراقبة
        page.on("request", intercept_request)

        try:
            # الدخول للموقع مع وقت انتظار كافي
            await page.goto(f"https://vidsrc.me/embed/movie?tmdb={tmdb_id}", timeout=60000)
            
            # الانتظار حتى تستقر الشبكة
            await page.wait_for_load_state("networkidle", timeout=60000)
            
            # محاكاة ضغطة بشرية في منتصف الشاشة (بناءً على الشاشة الجديدة 1280x720)
            await page.mouse.click(640, 360)
            
            # الانتظار 5 ثواني لضمان خروج طلب الـ m3u8
            await asyncio.sleep(5)
            
        except Exception as e:
            print("Scraping Warning/Error:", e)
        finally:
            # التنظيف ضروري جداً في السيرفر المجاني
            await context.close()
            await browser.close()

        # تقييم النتيجة وإرسالها
        if extracted_m3u8:
            return {"success": True, "stream_url": extracted_m3u8}
        else:
            return {"success": False, "error": "فشل استخراج الرابط. السيرفر المجاني مضغوط."}
