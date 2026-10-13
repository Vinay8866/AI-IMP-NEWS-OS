"""
AI IMP NEWS OS
FastAPI Server Entry Point
Version: 3.0 Buffer Edition - Fixed /api prefix
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.settings import APP_PORT, MEDIA_DIR
from app.api.routes import router


app = FastAPI(
    title="AI IMP NEWS OS API",
    description="Free Autonomous Multi-Agent Content Operating System + Buffer Clone",
    version="3.0"
)

# CORS Policy for Frontend Access (Port 5500 / file://)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount Static Media Directory (Images Preview)
if MEDIA_DIR.exists():
    app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

# Include Routes WITH /api prefix - THIS FIXES 404 for /api/social/stats
app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "system": "AI IMP NEWS OS",
        "version": "3.0 Buffer Edition",
        "status": "online",
        "docs_url": "http://127.0.0.1:8000/docs",
        "buffer_endpoints": [
            "/api/social/queue",
            "/api/social/calendar",
            "/api/social/stats",
            "/api/social/schedule",
            "/api/social/auto-schedule-all"
        ]
    }


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 AI IMP NEWS OS - FASTAPI SERVER STARTING v3.0 Buffer")
    print(f"📡 API Base URL : http://127.0.0.1:{APP_PORT}/api")
    print(f"📖 Swagger Docs : http://127.0.0.1:{APP_PORT}/docs")
    print(f"📱 Buffer Stats : http://127.0.0.1:{APP_PORT}/api/social/stats")
    print("=" * 60 + "\n")

    uvicorn.run("app.server:app", host="127.0.0.1", port=APP_PORT, reload=True)
