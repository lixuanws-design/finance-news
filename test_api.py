import requests, json
r = requests.get("http://127.0.0.1:8899/api/dashboard", timeout=45)
d = r.json()
print(f"News: {d.get('total_news')} | Analyzed: {d.get('analyzed_news')}")
print(f"Indices: {len(d.get('indices',[]))} | Sectors: {len(d.get('sectors',[]))}")
print()
for n in d.get("news_with_stocks", [])[:8]:
    stocks = [f"{s['name']}({s['code']})" for s in n.get("stocks", [])]
    print(f"[{n['source']}] {n['title'][:50]}")
    print(f"  -> {stocks} | {n.get('sentiment','')}")
