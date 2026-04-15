# Сервис объявлений купли/продажи на FastAPI.

## API Endpoints

- `POST /advertisement` - создание объявления
- `PATCH /advertisement/{id}` - обновление объявления
- `DELETE /advertisement/{id}` - удаление объявления
- `GET /advertisement/{id}` - получение объявления по ID
- `GET /advertisement?title=&author=&min_price=&max_price=` - поиск объявлений

## Запуск

```bash
# С использованием Docker Compose
docker-compose up --build