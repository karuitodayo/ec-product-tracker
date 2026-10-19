import os

import gspread
from dotenv import load_dotenv

from fetch_products import fetch_all_products

load_dotenv()

HEADER = ["商品コード", "商品名", "価格", "前回価格", "価格差分", "在庫有無", "商品URL", "取得日時", "前回取得日時"]
WORKSHEET_NAME = "シート1"


def get_worksheet():
    key_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    sheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")
    gc = gspread.service_account(filename=key_path)
    sh = gc.open_by_key(sheet_id)
    return sh.worksheet(WORKSHEET_NAME)


def load_previous_data(ws):
    """既存シートから 商品コード -> (価格, 取得日時) の対応表を作る（1回目実行時は空）"""
    rows = ws.get_all_values()
    if len(rows) <= 1:
        return {}
    previous = {}
    for row in rows[1:]:
        if len(row) >= 8 and row[0]:
            try:
                previous[row[0]] = (int(row[2]), row[7])
            except (ValueError, IndexError):
                pass
    return previous


def build_rows(products, previous_data):
    rows = []
    for p in products:
        code = p["商品コード"]
        price = p["価格"]
        prev_price, prev_timestamp = previous_data.get(code, (None, None))
        diff = (price - prev_price) if (price is not None and prev_price is not None) else ""
        rows.append([
            code,
            p["商品名"],
            price if price is not None else "",
            prev_price if prev_price is not None else "",
            diff,
            p["在庫有無"] or "",
            p["商品URL"] or "",
            p["取得日時"],
            prev_timestamp if prev_timestamp is not None else "",
        ])
    return rows


def update_spreadsheet():
    ws = get_worksheet()
    previous_data = load_previous_data(ws)

    products = fetch_all_products()
    rows = build_rows(products, previous_data)

    ws.clear()
    ws.update([HEADER] + rows)
    return rows


if __name__ == "__main__":
    updated_rows = update_spreadsheet()
    print(f"{len(updated_rows)}件の商品データをスプレッドシートに反映しました。")
    for row in updated_rows:
        print(row)
