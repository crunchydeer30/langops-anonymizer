from fastapi import FastAPI
import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings, configure_logging
from app.routers import analysis, health, anonymization, translation
from app.services.analyzer import AnalyzerService
from app.services.anonymizer import AnonymizerService
from app.services.translation_anonymizer import TranslationAnonymizerService

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.on_event("startup")
def startup_event():
    logger.info("Pre-loading analyzer engine...")
    app.state.analyzer = AnalyzerService(get_settings())
    logger.info("Analyzer engine loaded successfully")
    
    logger.info("Pre-loading anonymizer engine...")
    app.state.anonymizer = AnonymizerService()
    logger.info("Anonymizer engine loaded successfully")

    logger.info("Pre-loading translation anonymizer service...")
    app.state.translation_anonymizer = TranslationAnonymizerService()
    logger.info("Translation anonymizer loaded successfully")

app.include_router(health.router)
app.include_router(analysis.router)
app.include_router(anonymization.router)
app.include_router(translation.router)

if __name__ == "__main__":
    import uvicorn
    import argparse
    parser = argparse.ArgumentParser(description="Run LangOps NER API")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=settings.port, help="Port to listen on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()
    uvicorn.run(
        "app.main:app", 
        host=args.host, 
        port=args.port, 
        reload=args.reload,
        log_level=settings.log_level.lower(),
    )
