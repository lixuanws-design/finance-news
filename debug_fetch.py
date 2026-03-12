import requests, json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.eastmoney.com/",
}

# Test 1: 东方财富资讯
print("=== 东方财富资讯 ===")
try:
    url = "https://np-anotice-stock.eastmoney.com/api/security/ann?page_size=20&page_index=1&ann_type=A&client_source=web&f_node=0&s_node=0"
    r = requests.get(url, headers=HEADERS, timeout=10)
    print(f"Status: {r.status_code}, Length: {len(r.text)}")
    print(r.text[:500])
except Exception as e:
    print(f"Failed: {e}")

# Test 2: 新浪
print("\n=== 新浪财经 ===")
try:
    url = "https://finance.sina.com.cn/stock/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    print(f"Status: {r.status_code}, Length: {len(r.text)}")
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select("a")
    count = 0
    for a in links:
        t = a.get_text(strip=True)
        if len(t) > 10 and ("股" in t or "涨" in t or "跌" in t or "市场" in t or "板块" in t or "基金" in t):
            print(f"  {t[:60]}")
            count += 1
            if count >= 10: break
except Exception as e:
    print(f"Failed: {e}")

# Test 3: 东方财富热榜
print("\n=== 东方财富热闻 ===")
try:
    url = "https://np-anotice-stock.eastmoney.com/api/security/ann"
    params = {"page_size": 10, "page_index": 1, "ann_type": "A", "client_source": "web"}
    r = requests.get(url, params=params, headers=HEADERS, timeout=10)
    print(f"Status: {r.status_code}")
    data = r.json()
    print(json.dumps(data, ensure_ascii=False, indent=2)[:800])
except Exception as e:
    print(f"Failed: {e}")
