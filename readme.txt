eTir backend (FastAPI + PostgreSQL)

1. cp .env.example .env и заполните DB_* значения.
2. Активировать окружение: .etir_database\Scripts\Activate.ps1
3. Перейти в backend: cd backend
4. Создать БД (если нет): python -m source.create_db
5. Применить миграции: python -m migrations.runner
6. Запустить API: uvicorn main:app --reload
7. Тесты: python -m pytest
