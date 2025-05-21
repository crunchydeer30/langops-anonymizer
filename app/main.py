from fastapi import FastAPI
import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings, configure_logging
from app.routers import analysis, health, anonymization
from app.services.analyzer import AnalyzerService
from app.services.anonymizer import AnonymizerService

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
    """Pre-load services on startup to avoid first-request lag."""
    logger.info("Pre-loading analyzer engine...")
    app.state.analyzer = AnalyzerService(get_settings())
    logger.info("Analyzer engine loaded successfully")
    
    logger.info("Pre-loading anonymizer engine...")
    app.state.anonymizer = AnonymizerService()
    logger.info("Anonymizer engine loaded successfully")

app.include_router(health.router)
app.include_router(analysis.router)
app.include_router(anonymization.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=settings.port, 
        reload=True,
        log_level=settings.log_level.lower(),
    )
