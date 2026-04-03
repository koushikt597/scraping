import json
import re
import time
from typing import Dict, List, Optional

from playwright.sync_api import Locator, TimeoutError, sync_playwright


PRICE_RE = re.compile(r"(?:\u20b9|Rs\.?)\s*\d+(?:\.\d+)?", re.IGNORECASE)
RATING_RE = re.compile(r"\b[1-5](?:\.\d)?\b")
QTY_RE = re.compile(r"\b\d+(?:\.\d+)?\s?(?:ml|l|g|kg|gm|pcs|pack)\b", re.IGNORECASE)
DELIVERY_RE = re.compile(r"\b\d+\s*(?:min|mins|minute|minutes)\b", re.IGNORECASE)


def _first_text_match(text_list: List[str], pattern: re.Pattern[str]) -> str:
    for text in text_list:
        match = pattern.search(text)
        if match:
            return match.group(0)
    return ""


def _first_non_empty(card: Locator, selectors: List[str], attribute: Optional[str] = None) -> str:
    for selector in selectors:
        try:
            locator = card.locator(selector).first
            if locator.count() == 0:
                continue
            value = locator.get_attribute(attribute) if attribute else locator.inner_text()
            if value:
                cleaned = value.strip()
                if cleaned:
                    return cleaned
        except Exception:
            continue
    return ""


def _extract_card_data(card: Locator, query: str) -> Optional[Dict[str, str]]:
    raw_text = card.inner_text()
    text_list = [line.strip() for line in raw_text.splitlines() if line.strip()]

    name = _first_non_empty(
        card,
        [
            "h2",
            "h3",
            "[data-testid*='name']",
            "[class*='name']",
            "a[title]",
        ],
    )
    if not name and text_list:
        name = max(text_list, key=len)

    if not name or query.lower() not in name.lower():
        return None

    price = _first_text_match(text_list, PRICE_RE)
    rating = _first_non_empty(card, ["[aria-label*='rating']", "[class*='rating']"])
    if not rating:
        rating = _first_text_match(text_list, RATING_RE)

    quantity = _first_non_empty(
        card,
        [
            "[data-testid*='weight']",
            "[data-testid*='variant']",
            "[class*='weight']",
            "[class*='quantity']",
        ],
    )
    if not quantity:
        quantity = _first_text_match(text_list, QTY_RE)

    delivery_time = _first_non_empty(
        card,
        [
            "[data-testid*='delivery']",
            "[class*='delivery']",
            "[class*='eta']",
        ],
    )
    if not delivery_time:
        delivery_time = _first_text_match(text_list, DELIVERY_RE)

    image = _first_non_empty(card, ["img[src]"], attribute="src")

    return {
        "name": name,
        "price": price,
        "rating": rating,
        "quantity": quantity,
        "delivery_time": delivery_time,
        "image": image,
    }


def scrape_blinkit(query: str = "milk") -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
            permissions=["geolocation"],
            geolocation={"latitude": 12.9716, "longitude": 77.5946},
        )
        page = context.new_page()
        page.goto(f"https://blinkit.com/s/?q={query}", wait_until="domcontentloaded")

        try:
            page.locator("text=Detect my location").first.click(timeout=3000)
        except Exception:
            pass

        page.wait_for_selector("text=ADD", timeout=25000)

        for _ in range(6):
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(1200)

        cards = page.locator("div:has-text('ADD')")
        count = cards.count()
        print("Total candidate cards:", count)

        seen = set()
        for index in range(count):
            try:
                item = _extract_card_data(cards.nth(index), query=query)
                if not item:
                    continue

                dedupe_key = (item["name"], item["quantity"], item["price"])
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)

                results.append(item)
                print(item)
            except TimeoutError:
                continue
            except Exception:
                continue

        browser.close()

    return results


if __name__ == "__main__":
    result = scrape_blinkit("milk")
    with open("milk_products.json", "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
    time.sleep(2)