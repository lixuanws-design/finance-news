import requests
r = requests.get("http://127.0.0.1:8899/api/news?force=1", timeout=60)
data = r.json()
print(f"Total: {data.get('total_news')} | Analyzed: {data.get('analyzed_news')}")
print("\n--- All News ---")
for n in data.get("all_news", [])[:20]:
    print(f"[{n['source']}] {n['title'][:60]}")
if data.get("news"):
    print("\n--- With Stocks ---")
    for n in data["news"][:5]:
        stocks = [s["name"] for s in n.get("stocks", [])]
        print(f"  {n['title'][:40]} -> {stocks}")
