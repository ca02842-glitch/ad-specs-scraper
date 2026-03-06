import json
import requests
from playwright.sync_api import sync_playwright

# あなたのGASのURL
GAS_URL = "https://script.google.com/a/macros/cartahd.com/s/AKfycbx45-XFXuhhRUU6b4oycBI26iFQSfqrDNocmYIJaDpP4eTvWiMWkBs5c7z9xsdkAUc2kA/exec"

# 取得する媒体のリスト（まずはJSの壁が厚い4媒体をセット）
TARGETS = [
    {"name": "Meta", "url": "https://www.facebook.com/business/ads-guide/update/image?locale=ja_JP"},
    {"name": "X", "url": "https://business.x.com/ja/help/campaign-setup/creative-ad-specifications"},
    {"name": "TikTok", "url": "https://ads.tiktok.com/help/category?id=6dGs4bNMAZSdPr4pQ0KFuX"},
    {"name": "LINE", "url": "https://www.lycbiz.com/jp/manual/line-ads/policy_009/"}
]

def run():
    with sync_playwright() as p:
        # 裏側でChromeブラウザを起動
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for target in TARGETS:
            print(f"[{target['name']}] の取得を開始します...")
            try:
                # ページを開き、ネットワーク通信が落ち着く（JSが描画される）まで待つ
                page.goto(target['url'], timeout=60000, wait_until="networkidle")

                # 余計なタグ（メニューや裏側のコード）を消して、本文だけを抽出
                text = page.evaluate('''() => {
                    const elementsToRemove = document.querySelectorAll('script, style, noscript, iframe, svg, nav, footer, header');
                    elementsToRemove.forEach(el => el.remove());
                    return document.body.innerText;
                }''')

                # 改行や空白を綺麗に整えて、冒頭10000文字に制限
                clean_text = ' '.join(text.split())[:10000]

                # GASへデータを送信（POST）
                payload = {
                    "pfName": target['name'],
                    "rawText": clean_text
                }
                response = requests.post(GAS_URL, json=payload)
                print(f"GASからの返答: {response.text}")

            except Exception as e:
                print(f"エラー発生 ({target['name']}): {e}")

        browser.close()

if __name__ == "__main__":
    run()
