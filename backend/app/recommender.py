from __future__ import annotations

from typing import List, Tuple

from .data import PLACES


SCENARIO_KEYWORDS = {
    "кофе": ["кофе", "капучино", "латте"],
    "десерт": ["десерт", "сладкое", "торт"],
    "завтрак": ["завтрак"],
    "обед": ["обед", "ланч"],
    "ужин": ["ужин"],
    "свидание": ["свидание", "романтично", "девушк"],
    "семья": ["семья", "дети", "ребен"],
    "бар": ["бар", "коктейл"],
    "быстро": ["быстро"],
    "до 1000": ["до 1000", "недорого", "дешево", "бюджет"],
    "с друзьями": ["друзья", "компания"],
    "красиво": ["красиво", "эстетично", "атмосферно"],
    "рядом": ["рядом", "поблизости"],
}

DISTRICTS = ["центр", "северный", "левый берег"]


def normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def extract_preferences(text: str) -> Tuple[list[str], str | None, int | None]:
    normalized = normalize_text(text)
    matched_scenarios: list[str] = []

    for scenario, words in SCENARIO_KEYWORDS.items():
        if any(word in normalized for word in words):
            matched_scenarios.append(scenario)

    district = next((d.title() if d != "центр" else "Центр" for d in DISTRICTS if d in normalized), None)

    budget_limit = None
    if "1000" in normalized:
        budget_limit = 1000
    elif "1500" in normalized:
        budget_limit = 1500

    return matched_scenarios, district, budget_limit


def score_place(place: dict, scenarios: list[str], district: str | None, budget_limit: int | None) -> int:
    score = 0

    if place["open_now"]:
        score += 3

    for scenario in scenarios:
        if scenario in place["scenarios"] or scenario in place["tags"]:
            score += 4

    if district and place["district"] == district:
        score += 3

    if budget_limit is not None and place["avg_check"] <= budget_limit:
        score += 3

    return score


def find_places(user_text: str, limit: int = 3) -> list[dict]:
    scenarios, district, budget_limit = extract_preferences(user_text)

    ranked = sorted(
        PLACES,
        key=lambda place: score_place(place, scenarios, district, budget_limit),
        reverse=True,
    )

    return ranked[:limit]
