# Wavi starter

## Структура
- `backend` — FastAPI webhook для Telegram и API заведений
- `miniapp` — React/Vite мини-приложение

## Что нужно сделать
1. Скопировать содержимое архива в репозиторий `wavi`
2. В Vercel у проекта `wavi-backend` поставить Root Directory = `backend`
3. В Vercel у проекта `wavi-miniapp` поставить Root Directory = `miniapp`
4. В Environment Variables backend добавить значения из `.env.example`
5. В Environment Variables miniapp добавить `VITE_API_BASE_URL`
6. Сделать redeploy обоих проектов
7. Открыть `https://<backend-domain>/setup?key=<ADMIN_SETUP_KEY>` один раз
8. Написать `/start` боту
