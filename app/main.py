"""Точка входа FastAPI приложения"""
from datetime import datetime
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import get_settings
from app.api.routes import departments_router, employees_router
from app.exceptions import AppException
from app.database import check_db_connection

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
settings = get_settings()

# Создание приложения
app = FastAPI(
    title=settings.app_name,
    description="API для управления организационной структурой компании",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Обработчик кастомных исключений
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Обработка кастомных исключений приложения"""
    logger.warning(f"App exception: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


# Обработчик ошибок валидации Pydantic
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработка ошибок валидации"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Ошибка валидации данных",
            "errors": exc.errors()
        },
    )


# Обработчик всех остальных исключений
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Обработка непредвиденных ошибок"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )


# Подключение роутов с префиксом API версии
API_PREFIX = "/api/v1"
app.include_router(departments_router, prefix=API_PREFIX)
app.include_router(employees_router, prefix=API_PREFIX)


@app.get("/", tags=["health"])
async def health_check():
    """Проверка работоспособности API"""
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "version": "1.0.0",
        "message": "FastAPI Organization API is running"
    }


@app.get("/health", tags=["health"])
async def detailed_health_check():
    """Детальная проверка работоспособности"""
    health_status = {
        "status": "healthy",
        "app": settings.app_name,
        "debug": settings.debug,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Проверка БД
    try:
        db_ok = check_db_connection()
        health_status["database"] = "connected" if db_ok else "error"
        if not db_ok:
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name} in {'debug' if settings.debug else 'production'} mode")
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )