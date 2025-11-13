import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    data: Dict[str, Any]
    themeId: str

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """
    Lightweight prompt-to-landing generator (no external AI).
    Heuristic: extract product name and keywords and craft copy + features.
    """
    prompt = (req.prompt or "").strip()
    # Fallbacks
    name = "Your Product"
    subtitle_bits: List[str] = []
    theme = "fintech"

    lower = prompt.lower()
    # Theme heuristic
    if any(k in lower for k in ["bank", "fintech", "saas", "analytics", "ai", "ml"]):
        theme = "fintech"
    if any(k in lower for k in ["sunset", "creative", "design", "marketing", "brand", "portfolio"]):
        theme = "sunset"
    if any(k in lower for k in ["health", "calm", "wellness", "eco", "green", "garden"]):
        theme = "mint"

    # Try to extract a product/app name (first capitalized phrase or first 3 words title-cased)
    tokens = [t for t in prompt.replace("\n", " ").split(" ") if t]
    if tokens:
        # Take first 3 tokens as name candidate
        cand = " ".join(tokens[:3]).strip()
        if cand:
            name = cand.title()
    
    # Build simple feature bullets based on keywords
    feature_bank: List[str] = []
    def add_feat(text: str):
        if text and text not in feature_bank:
            feature_bank.append(text)

    if any(k in lower for k in ["ai", "ml", "gpt", "chat"]):
        add_feat("AI-assisted workflows that learn from your usage")
        subtitle_bits.append("AI-powered")
    if any(k in lower for k in ["analytics", "insight", "metric", "dashboard"]):
        add_feat("Real-time analytics dashboards with actionable insights")
        subtitle_bits.append("analytics")
    if any(k in lower for k in ["team", "collab", "share"]):
        add_feat("Team collaboration with comments and shared libraries")
        subtitle_bits.append("collaboration")
    if any(k in lower for k in ["mobile", "ios", "android", "responsive"]):
        add_feat("Responsive by default — perfect on mobile and desktop")
    if any(k in lower for k in ["secure", "privacy", "gdpr", "auth"]):
        add_feat("Enterprise-grade security and role-based access")
    if any(k in lower for k in ["api", "integrations", "zapier", "slack", "notion"]):
        add_feat("One-click integrations with your favorite tools")
    if not feature_bank:
        feature_bank = [
            "Clean, modern UI built for conversion",
            "Lightning-fast performance and SEO",
            "Effortless setup — launch in minutes",
        ]

    subtitle = f"{', '.join(dict.fromkeys(subtitle_bits))} platform to help you move faster" if subtitle_bits else "A minimal landing that explains your value clearly."

    data = {
        "hero": {
            "title": f"{name}: launch faster with clarity",
            "subtitle": subtitle,
            "cta": "Get Started",
        },
        "features": {
            "items": feature_bank,
        },
        "cta": {
            "title": "Ready to launch your landing?",
            "button": "Generate Page",
        },
    }

    return {"data": data, "themeId": theme}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
