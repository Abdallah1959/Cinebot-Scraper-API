from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="Cinebot Scraper API 🍿")

# السماح للواجهة بتاعتنا (Netlify) بالاتصال بالسيرفر بدون مشاكل CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Cinebot API is running 🚀"}

@app.get("/scrape/{tmdb_id}")
async def scrape_movie(tmdb_id: str):
    """
    هذه الدالة تقوم بدور الوسيط (Proxy)
    تتصل بسيرفرات السحب من الخلفية (Backend) لتخطي قيود المتصفح
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # محاولة السحب من API خارجي عبر السيرفر الخاص بنا
            # السيرفرات لا تتأثر بقيود CORS الموجودة في المتصفحات
            response = await client.get(
                f"https://api.consumet.org/meta/tmdb/info/{tmdb_id}?type=movie", 
                headers=headers, 
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if "sources" in data and len(data["sources"]) > 0:
                    # اختيار أعلى جودة متاحة
                    auto_source = next((s for s in data["sources"] if s.get("quality") == "auto"), data["sources"][0])
                    return {"success": True, "stream_url": auto_source["url"]}
            
            return {"success": False, "error": "لم يتم العثور على رابط مباشر لهذا الفيلم حالياً"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))