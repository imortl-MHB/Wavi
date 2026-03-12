from __future__ import annotations

import httpx

from .config import settings


API_URL = f"https://api.telegram.org/bot{settings.telegram_bot_token}"


async def telegram_request(method: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(f"{API_URL}/{method}", json=payload)
        response.raise_for_status()
        return response.json()


async def send_message(chat_id: int, text: str, reply_markup: dict | None = None) -> None:
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    await telegram_request("sendMessage", payload)


async def answer_callback_query(callback_query_id: str, text: str | None = None) -> None:
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    await telegram_request("answerCallbackQuery", payload)


async def set_webhook() -> dict:
    return await telegram_request(
        "setWebhook",
        {
            "url": f"{settings.public_base_url}/webhook/telegram",
            "secret_token": settings.telegram_secret_token,
            "drop_pending_updates": True,
        },
    )


async def set_menu_button() -> dict:
    return await telegram_request(
        "setChatMenuButton",
        {
            "menu_button": {
                "type": "web_app",
                "text": "Открыть Wavi",
                "web_app": {"url": settings.miniapp_url},
            }
        },
    )
