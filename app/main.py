from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Инициализация приложения с метаданными для Swagger-документации
app = FastAPI(
    title="КакДостатьСоседа API",
    description="API приложения для поиска идеального соседа",
    version="0.1.0"
)

# Настройка CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Порт локального сервера Vite (React)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Базовый эндпоинт для проверки работоспособности (Health Check)
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "ok", 
        "message": "Бэкенд успешно запущен и готов к работе"
    }