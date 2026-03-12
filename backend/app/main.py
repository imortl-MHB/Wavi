from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .data import PLACES
from .recommender import find_places
from .telegram import answer_callback_query, send_message, set_menu_button, set_webhook

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WELCOME_TEXT = (
    "<b>Wavi</b> — подберу, где поесть в Воронеже за 30 секунд.\n\n"
    "Напиши, что ты хочешь. Например:\n"
    "• кофе и десерт рядом\n"
    "• завтрак в центре\n"
    "• ужин для свидания\n"
    "• обед до 1000\n\n"
    "Или нажми кнопку ниже."
)


def build_main_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "☕ Что рядом", "callback_data": "preset:кофе рядом"},
                {"text": "🍳 Завтрак", "callback_data": "preset:завтрак центр"},
            ],
            [
                {"text": "💘 Свидание", "callback_data": "preset:ужин свидание"},
                {"text": "💸 До 1000 ₽", "callback_data": "preset:обед до 1000"},
            ],
            [
                {"text": "📱 Открыть mini app", "web_app": {"url": settings.miniapp_url}},
            ],
        ]
    }


def format_place(place: dict) -> str:
    return (
        f"<b>{place['name']}</b>\n"
        f"{place['description']}\n"
        f"📍 {place['district']}, {place['address']}\n"
        f"💳 Средний чек: {place['avg_check']} ₽\n"
        f"🏷 {', '.join(place['tags'])}"
    )


def places_keyboard(place_id: int) -> dict:
    return {
        "inline_keyboard": [
            [
                {
                    "text": "📱 Открыть в mini app",
                    "web_app": {"url": f"{settings.miniapp_url}?place_id={place_id}"},
                }
            ],
            [{"text": "🔁 Подобрать ещё", "callback_data": "restart"}],
        ]
    }


async def process_user_query(chat_id: int, text: str) -> None:
    places = find_places(text)
    if not places:
        await send_message(chat_id, "Пока не нашёл подходящие места. Попробуй другой запрос.")
        return

    intro = f"Нашёл варианты по запросу: <b>{text}</b>"
    await send_message(chat_id, intro)

    for place in places:
        await send_message(chat_id, format_place(place), reply_markup=places_keyboard(place["id"]))


@app.get("/")
async def root() -> dict:
    return {"ok": True, "service": "wavi-backend"}


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


@app.get("/api/places")
async def get_places(q: str | None = None, district: str | None = None, max_price: int | None = None) -> dict:
    results = PLACES

    if q:
        q_lower = q.lower()
        results = [
            p for p in results
            if q_lower in p["name"].lower()
            or q_lower in p["description"].lower()
            or any(q_lower in tag.lower() for tag in p["tags"])
        ]

    if district:
        results = [p for p in results if p["district"].lower() == district.lower()]

    if max_price is not None:
        results = [p for p in results if p["avg_check"] <= max_price]

    return {"items": results}


@app.get("/api/places/{place_id}")
async def get_place(place_id: int) -> dict:
    place = next((p for p in PLACES if p["id"] == place_id), None)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@app.get("/setup")
async def setup(key: str = Query(...)) -> dict:
    if key != settings.admin_setup_key:
        raise HTTPException(status_code=403, detail="Forbidden")

    webhook_result = await set_webhook()
    menu_button_result = await set_menu_button()

    return {
        "ok": True,
        "webhook": webhook_result,
        "menu_button": menu_button_result,
    }


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, x_telegram_bot_api_secret_token: str | None = Header(default=None)):
    if x_telegram_bot_api_secret_token != settings.telegram_secret_token:
        raise HTTPException(status_code=403, detail="Invalid secret token")

    update = await request.json()

    message = update.get("message")
    callback_query = update.get("callback_query")

    if message:
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text == "/start":
            await send_message(chat_id, WELCOME_TEXT, reply_markup=build_main_keyboard())
        else:
            await process_user_query(chat_id, text)

    elif callback_query:
        callback_id = callback_query["id"]
        chat_id = callback_query["message"]["chat"]["id"]
        data = callback_query.get("data", "")

        await answer_callback_query(callback_id)

        if data == "restart":
            await send_message(chat_id, WELCOME_TEXT, reply_markup=build_main_keyboard())
        elif data.startswith("preset:"):
            preset_text = data.replace("preset:", "", 1)
            await process_user_query(chat_id, preset_text)

    return JSONResponse({"ok": True})
