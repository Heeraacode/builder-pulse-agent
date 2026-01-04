import os, re, html
from datetime import datetime, timezone
import feedparser

FEEDS = [
    ("HackerNews", "https://hnrss.org/newest?q=vibe%20coding"),
    ("Reddit", "https://www.reddit.com/search.rss?q=vibe%20coding&sort=new"),
]

KEYWORDS = [
    ("AI Agents", ["agent", "agents", "agentic"]),
    ("No-code Builders", ["no-code", "nocode", "app builder", "builder"]),
    ("Other", []),
]

def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def tag_text(text: str):
    t = text.lower()
    for name, keys in KEYWORDS:
        if keys and any(k in t for k in keys):
            return name
    return "Other"

def main():
    now = datetime.now(timezone.utc)
    day = now.strftime("%Y-%m-%d")
    items = []

    for source, url in FEEDS:
        d = feedparser.parse(url)
        for e in d.entries[:20]:
            title = clean(getattr(e, "title", ""))
            link = clean(getattr(e, "link", ""))
            summary = clean(re.sub("<.*?>", "", getattr(e, "summary", "")))[:200]
            items.append({
                "source": source,
                "title": title,
                "link": link,
                "summary": summary,
                "tag": tag_text(f"{title} {summary}")
            })

    os.makedirs("docs", exist_ok=True)
    os.makedirs("docs/archive", exist_ok=True)

    def esc(x): return html.escape(x)

    cards = []
    for it in items[:25]:
        cards.append(f"""
        <div class="card">
          <div class="meta">{esc(it['source'])} • {esc(it['tag'])}</div>
          <div class="title"><a href="{esc(it['link'])}" target="_blank" rel="noreferrer">{esc(it['title'])}</a></div>
          <div class="summary">{esc(it['summary'])}</div>
        </div>
        """)

    page = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Builder Pulse — {day}</title>
  <style>
    body {{ font-family: system-ui; margin:0; background:#0b0f1a; color:#e7ecff; }}
    .wrap {{ max-width: 980px; margin: 0 auto; padding: 28px; }}
    .sub {{ color:#aab3d6; font-size: 13px; }}
    .box {{ background:#111936; border:1px solid #1c2a5a; border-radius:16px; padding:16px; margin-top:16px; }}
    .grid {{ display:grid; grid-template-columns: 1fr; gap:12px; margin-top: 14px; }}
    .card {{ background:#0f1630; border:1px solid #1c2a5a; border-radius:16px; padding:14px; }}
    .meta {{ color:#98a6d9; font-size: 12px; margin-bottom: 6px; }}
    .title a {{ color:#e7ecff; text-decoration:none; }}
    .title a:hover {{ text-decoration:underline; }}
    .summary {{ color:#c7d0ff; font-size: 13px; margin-top:8px; }}
    a {{ color:#9db2ff; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Builder Pulse — {day}</h1>
    <div class="sub">Auto-built from live RSS • Updated: {now.strftime("%H:%M UTC")}</div>

    <div class="box">
      <b>Live mentions (click for receipts)</b>
      <div class="grid">
        {''.join(cards)}
      </div>
    </div>

    <div class="box">
      <a href="archive/{day}.html">Archive copy for {day}</a>
    </div>
  </div>
</body>
</html>
"""

    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(page)
    with open(f"docs/archive/{day}.html", "w", encoding="utf-8") as f:
        f.write(page)

if __name__ == "__main__":
    main()
