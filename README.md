# КакДостатьСоседа - Backend

Бэкенд приложения для поиска соседа, написанный на FastAPI.

## Локальный запуск
1. Создайте виртуальное окружение: `python -m venv venv`
2. Активируйте его: 
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
3. Установите зависимости: `pip install -r requirements.txt`
4. Запустите сервер: `uvicorn app.main:app --reload`

## API Документация (Контракты)
После запуска сервера интерактивная документация (Swagger UI) доступна по адресу: 
[http://localhost:8000/docs](http://localhost:8000/docs)