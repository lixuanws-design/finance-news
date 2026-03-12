#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""财经热点日报 - Financial News Digest"""
import os, sys, json, time, re, threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/json", "Accept-Language": "zh-CN,zh;q=0.9"}

def fetch_eastmoney_news():
    news = []
    try:
        r = requests.get("https://www.eastmoney.com/", headers=HEADERS, timeout=10)
        r.encoding = "utf-8"
        for m in re.finditer(r'href="(https?://finance\.eastmoney\.com/a/\d+\.html)"[^>]*>([^<]{5,})<', r.text):
            link, title = m.group(1), m.group(2).strip()
            if len(title) > 5 and not any(x["title"] == title for x in news):
                news.append({"title": title, "url": link, "source": "东方财富", "time": ""})
    except: pass
    return news[:20]

def fetch_eastmoney_7x24():
    news = []
    try:
        url = "https://np-anotice-stock.eastmoney.com/api/security/ann"
        params = {"page_size": 20, "page_index": 1, "ann_type": "A", "client_source": "web"}
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = r.json()
        for item in data.get("data", {}).get("list", []):
            title = item.get("title", "")
            if title:
                news.append({"title": title, "url": f'https://notice.eastmoney.com/{item.get("art_code","")}.html',
                             "source": "公司公告", "time": item.get("display_time", "")[:16]})
    except: pass
    return news

def fetch_cls_telegraph():
    news = []
    try:
        url = "https://www.cls.cn/nodeapi/updateTelegraphList"
        params = {"app": "CailianpressWeb", "sv": "7.7.5", "os": "web"}
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = r.json()
        for item in data.get("data", {}).get("roll_data", []):
            content = re.sub(r'<[^>]+>', '', item.get("content", "")).strip()
            if content:
                ts = item.get("ctime", 0)
                t = datetime.fromtimestamp(ts).strftime("%H:%M") if ts else ""
                news.append({"title": content[:120], "url": "", "source": "财联社", "time": t})
    except: pass
    return news[:20]

def fetch_sina_finance():
    news = []
    try:
        r = requests.get("https://finance.sina.com.cn/roll/", headers=HEADERS, timeout=10)
        r.encoding = "utf-8"
        for m in re.finditer(r'href="(https?://finance\.sina\.com\.cn/[^"]+\.shtml)"[^>]*>([^<]{5,})<', r.text):
            link, title = m.group(1), m.group(2).strip()
            if len(title) > 8 and not any(x["title"] == title for x in news):
                news.append({"title": title, "url": link, "source": "新浪", "time": ""})
    except: pass
    return news[:15]

def fetch_10jqka_hot():
    stocks = []
    try:
        url = "https://q.10jqka.com.cn/index/index/board/all/field/zdf/order/desc/page/1/ajax/1/"
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        for tr in soup.select("table.m-table tbody tr")[:15]:
            tds = tr.select("td")
            if len(tds) >= 5:
                stocks.append({"name": tds[1].get_text(strip=True), "code": tds[0].get_text(strip=True),
                               "price": tds[2].get_text(strip=True), "change_pct": tds[3].get_text(strip=True)})
    except: pass
    return stocks

def fetch_market_index():
    indices = []
    try:
        url = "https://push2.eastmoney.com/api/qt/ulist/get"
        params = {"fltt": 2, "secids": "1.000001,0.399001,0.399006,1.000688,1.000300",
                  "fields": "f2,f3,f4,f12,f14", "ut": "bd1d9ddb04089700cf9c27f6f7426281"}
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = r.json() or {}
        for item in (data.get("data") or {}).get("diff") or []:
            indices.append({"name": item.get("f14",""), "code": item.get("f12",""),
                            "price": item.get("f2",0), "change_pct": item.get("f3",0)})
    except: pass
    return indices

def fetch_hot_sectors():
    sectors = []
    try:
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {"pn":1,"pz":15,"po":1,"np":1,"ut":"bd1d9ddb04089700cf9c27f6f7426281",
                  "fltt":2,"invt":2,"fid":"f3","fs":"m:90+t:2","fields":"f2,f3,f4,f12,f14"}
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = r.json() or {}
        for item in (data.get("data") or {}).get("diff") or []:
            sectors.append({"name": item.get("f14",""), "change_pct": item.get("f3",0)})
    except: pass
    return sectors

def fetch_article_content(url):
    if not url or "mp.weixin.qq.com" in url: return ""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.encoding = r.apparent_encoding or "utf-8"
        html = r.text
        for pat in [r'<div[^>]*id="ContentBody"[^>]*>([\s\S]*?)</div>', r'<div[^>]*class="art_context"[^>]*>([\s\S]*?)</div>']:
            m = re.search(pat, html)
            if m:
                text = re.sub(r'<[^>]+>', '', m.group(1))
                text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace(r"&#\d+;", "")
                text = re.sub(r'\n{3,}', '\n\n', text).strip()
                if len(text) > 50: return text[:3000]
    except: pass
    return ""

KEYWORD_STOCKS = {
    "石油": [("中国石油","601857"),("中国石化","600028")], "原油": [("中国石油","601857"),("中远海能","600026")],
    "油价": [("中国石油","601857")], "航运": [("中远海能","600026"),("招商南油","601975")],
    "人工智能": [("科大讯飞","002230"),("寒武纪","688256")], "AI": [("寒武纪","688256"),("科大讯飞","002230")],
    "芯片": [("中芯国际","688981"),("北方华创","002371")], "半导体": [("中芯国际","688981"),("北方华创","002371")],
    "算力": [("中科曙光","603019"),("浪潮信息","000977"),("工业富联","601138")],
    "新能源": [("比亚迪","002594"),("宁德时代","300750"),("隆基绿能","601012")],
    "光伏": [("隆基绿能","601012"),("通威股份","600438")], "锂电池": [("宁德时代","300750"),("比亚迪","002594")],
    "储能": [("宁德时代","300750"),("阳光电源","300274")], "汽车": [("比亚迪","002594"),("长安汽车","000625")],
    "房地产": [("万科A","000002"),("保利发展","600048")], "银行": [("工商银行","601398"),("招商银行","600036")],
    "保险": [("中国平安","601318")], "券商": [("中信证券","600030"),("东方财富","300059")],
    "白酒": [("贵州茅台","600519"),("五粮液","000858")], "医药": [("恒瑞医药","600276"),("迈瑞医疗","300760")],
    "军工": [("中航沈飞","600760"),("航发动力","600893")], "煤炭": [("中国神华","601088"),("陕西煤业","601225")],
    "黄金": [("紫金矿业","601899"),("山东黄金","600547")], "机器人": [("汇川技术","300124"),("埃斯顿","002747")],
    "华为": [("赛力斯","601127"),("欧菲光","002456")], "5G": [("中兴通讯","000063"),("烽火通信","600498")],
    "低空经济": [("中信海直","000099"),("万丰奥威","002085")], "电力": [("长江电力","600900")],
    "稀土": [("北方稀土","600111")], "农业": [("牧原股份","002714"),("温氏股份","300498")],
    "游戏": [("三七互娱","002555")], "基建": [("中国中铁","601390"),("中国交建","601800")],
    "固态电池": [("宁德时代","300750"),("赣锋锂业","002460")], "数据要素": [("易华录","300212"),("人民网","603000")],
}

def analyze_stocks(text):
    matched, seen = [], set()
    for kw, stocks in KEYWORD_STOCKS.items():
        if kw in text:
            for name, code in stocks:
                if code not in seen:
                    seen.add(code)
                    matched.append({"name": name, "code": code, "keyword": kw})
    return matched[:5]

def analyze_sentiment(text):
    bull = sum(1 for w in ["涨","利好","增长","突破","上涨","看多","强势","飙升","扭亏","盈利","创新高"] if w in text)
    bear = sum(1 for w in ["跌","利空","下滑","下跌","看空","亏损","暴跌","风险","危机","承压"] if w in text)
    if bull > bear + 1: return "bullish"
    if bear > bull + 1: return "bearish"
    return "neutral"

def get_openrouter_key():
    auth_path = os.path.join(os.path.expanduser("~"), ".openclaw", "agents", "main", "agent", "auth-profiles.json")
    if os.path.exists(auth_path):
        try:
            with open(auth_path, "r") as f:
                auth = json.load(f)
            return auth.get("profiles", {}).get("openrouter:default", {}).get("key", "")
        except: pass
    return os.environ.get("OPENROUTER_API_KEY", "")

def ai_analyze_news(title, content=""):
    api_key = get_openrouter_key()
    text = title + " " + content
    stocks = analyze_stocks(text)
    sentiment = analyze_sentiment(text)
    if not api_key:
        return {"summary": title, "sentiment": sentiment, "stocks": stocks, "industries": [s["keyword"] for s in stocks[:3]],
                "risk_factors": ["地缘政治风险", "市场波动风险"], "ai_generated": False}
    try:
        prompt = f"""分析财经新闻。只输出JSON。标题:{title} 内容:{content[:1500] if content else ""}
JSON:{{"summary":"3 句摘要","sentiment":"bullish/bearish/neutral","industries":[],"stocks_mentioned":[{{"name":"","code":"","reason":""}}],"risk_factors":[],"time_horizon":"short/medium/long","confidence":0.8}}"""
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "google/gemini-2.5-flash-preview", "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.3, "max_tokens": 1500}, timeout=30)
        data = r.json()
        content_str = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        m = re.search(r'\{[\s\S]*\}', content_str)
        if m:
            result = json.loads(m.group(0))
            result["ai_generated"] = True
            return result
    except: pass
    return {"summary": title, "sentiment": sentiment, "stocks": stocks, "ai_generated": False}

def get_cache(name, max_age_min=15):
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(CACHE_DIR, f"{name}_{today}.json")
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < max_age_min * 60:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    return None

def set_cache(name, data):
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(CACHE_DIR, f"{name}_{today}.json")
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)

# Template folder setup
if getattr(sys, 'frozen', False):
    TPL_DIR = os.path.join(sys._MEIPASS, 'templates')
    STA_DIR = os.path.join(sys._MEIPASS, 'static')
else:
    TPL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    STA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

app = Flask(__name__, template_folder=TPL_DIR, static_folder=STA_DIR)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/dashboard")
def api_dashboard():
    force = request.args.get("force", "0") == "1"
    cached = None if force else get_cache("dashboard", max_age_min=10)
    if cached: return jsonify(cached)
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch_eastmoney_news): "em_news", pool.submit(fetch_eastmoney_7x24): "em_7x24",
                   pool.submit(fetch_cls_telegraph): "cls", pool.submit(fetch_sina_finance): "sina",
                   pool.submit(fetch_market_index): "indices", pool.submit(fetch_hot_sectors): "sectors"}
        results = {}
        for f in as_completed(futures):
            name = futures[f]
            try: results[name] = f.result(timeout=15)
            except: results[name] = []
    all_news = results.get("em_news", []) + results.get("em_7x24", []) + results.get("cls", []) + results.get("sina", [])
    seen = set()
    unique_news = [n for n in all_news if (key := n["title"][:20]) not in seen and len(key) > 4 and not seen.add(key)]
    analyzed = [{**n, "stocks": analyze_stocks(n["title"]), "sentiment": analyze_sentiment(n["title"])} for n in unique_news[:30]]
    result = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "indices": results.get("indices", []),
              "sectors": results.get("sectors", [])[:10], "hot_stocks": fetch_10jqka_hot()[:10],
              "total_news": len(unique_news), "analyzed_news": len([x for x in analyzed if x["stocks"]]),
              "news_with_stocks": [x for x in analyzed if x["stocks"]], "all_news": unique_news[:50]}
    set_cache("dashboard", result)
    return jsonify(result)

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.json
    title = data.get("title", "")
    url = data.get("url", "")
    content = fetch_article_content(url) if url else ""
    return jsonify(ai_analyze_news(title, content))

@app.route("/api/fetch-article")
def api_fetch_article():
    url = request.args.get("url", "")
    content = fetch_article_content(url)
    return jsonify({"url": url, "content": content, "length": len(content)})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8899, debug=False, use_reloader=False)
