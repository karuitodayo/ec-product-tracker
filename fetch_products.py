import json
import os
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"
HEADERS = {"User-Agent": "Mozilla/5.0"}
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "products_config.json")


def load_target_products():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_one(client_id, target):
    params = {
        "appid": client_id,
        "seller_id": target["seller_id"],
        "jan_code": target["jan_code"],
        "results": 10,
    }
    response = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    data = response.json()
    hits = data.get("hits", [])
    match = next((h for h in hits if h.get("code") == target["code"]), None)

    if match is None:
        return {
            "商品名": target.get("memo", "(不明)"),
            "商品コード": target["code"],
            "価格": None,
            "在庫有無": None,
            "商品URL": None,
            "取得日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "取得結果": "見つかりませんでした",
        }

    return {
        "商品名": match.get("name"),
        "商品コード": match.get("code"),
        "価格": match.get("price"),
        "在庫有無": "あり" if match.get("inStock") else "なし",
        "商品URL": match.get("url"),
        "取得日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "取得結果": "OK",
    }


def fetch_all_products():
    client_id = os.getenv("YAHOO_CLIENT_ID")
    targets = load_target_products()
    results = []

    for i, target in enumerate(targets):
        result = fetch_one(client_id, target)
        results.append(result)
        if i < len(targets) - 1:
            time.sleep(1)  # レート制限(1クエリ/秒)を守るための待機

    return results


if __name__ == "__main__":
    for row in fetch_all_products():
        print(row)
