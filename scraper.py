import json
import requests
from playwright.sync_api import sync_playwright
import time

# あなたのGASのURL
GAS_URL = "https://script.google.com/a/macros/cartahd.com/s/AKfycbx45-XFXuhhRUU6b4oycBI26iFQSfqrDNocmYIJaDpP4eTvWiMWkBs5c7z9xsdkAUc2kA/exec"

# 各媒体のURLと、テキストを待つための「目印（セレクタ）」
TARGETS = [
    {
        "name": "Meta", 
        "url": "https://www.facebook.com/business/ads-guide/update/image?locale=ja_JP",
        "wait_for": "h1" # H1タグ（タイトル）が出るまで待つ
    },
    {
        "name": "X", 
        "url": "https://business.x.com/ja/help/campaign-setup/creative-ad-specifications",
        "wait_for": "main" # メインコンテンツが出るまで待つ
    },
    {
        "name": "TikTok", 
        "url": "https://ads.tiktok.com/help/category?id=6dGs4bNMAZSdPr4pQ0KFuX",
        "wait_for": "div"
    },
    {
        "name": "LINE", 
        "url": "https://www.lycbiz.com/jp/manual/line-ads/policy_009/",
        "wait_for": ".main-content, article" # 記事部分が出るまで待つ
    }
]

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # JSがちゃんと動くように、人間のブラウザのフリをする設定
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for target in TARGETS:
            print(f"[{target['name']}] の取得を開始します...")
            try:
                # ページ移動
                page.goto(target['url'], timeout=60000, wait_until="domcontentloaded")
                
                # ページのJSが完全にレンダリングされるまで、指定した要素を待つ
                try:
                    page.wait_for_selector(target['wait_for'], timeout=15000)
                except:
                    print(f"待機タイムアウト: {target['name']}")

                # さらに念押しで3秒待つ（アニメーション等の完了待ち）
                time.sleep(3)

                # 本文（表示されているテキストのみ）を抽出
                text = page.evaluate('''() => {
                    return document.body.innerText;
                }''')

                # 改行や空白を整えて、冒頭10000文字に制限
                clean_text = ' '.join(text.split())[:10000]

                # GASへデータを送信
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
