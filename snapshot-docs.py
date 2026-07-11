#!/usr/bin/env python3
"""
TinyTapeout 정적 문서 페이지 -> 로컬 마크다운 스냅샷.
Antigravity workspace의 docs/ 폴더에 .md로 저장하면, 에이전트가 이걸
인덱싱해서 자체 검색(=RAG)합니다. NotebookLM MCP 없이 동일 효과 + 원문 보존.

사용법:
    pip install requests beautifulsoup4 markdownify
    python snapshot-docs.py

결과:
    ./docs/*.md   (각 파일 상단에 출처 URL + 스냅샷 날짜)

주의:
    - tinytapeout.com/specs, /guides, /faq 등은 정적(Hugo) 페이지라 잘 됨.
    - app.tinytapeout.com 계열(계산기/제출)은 JS SPA라 본문이 안 잡히므로 제외.
      (어차피 이건 '문서'가 아니라 브라우저에서 클릭하는 '도구'임)
"""
import datetime
import pathlib
import re
import sys

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

DOCS = {
    "analog-specs":           "https://tinytapeout.com/specs/analog/",
    "pinouts":                "https://tinytapeout.com/specs/pinouts/",
    "gpio":                   "https://tinytapeout.com/specs/gpio/",
    "clock":                  "https://tinytapeout.com/specs/clock/",
    "pcb":                    "https://tinytapeout.com/specs/pcb/",
    "guide-local-hardening":  "https://tinytapeout.com/guides/local-hardening/",
    "guide-magic-layout":     "https://tinytapeout.com/guides/laying-standard-cells-with-magic/",
    "guide-analog-discovery": "https://tinytapeout.com/guides/analog-discovery/",
    "guide-demoboard":        "https://tinytapeout.com/guides/get-started-demoboard/",
    "guide-documentation":    "https://tinytapeout.com/guides/documentation/",
    "making-asics":           "https://tinytapeout.com/making_asics/",
    "faq":                    "https://tinytapeout.com/faq/",
    "zta-analog-course":      "https://www.zerotoasiccourse.com/analog/",
    "zta-terminology":        "https://zerotoasiccourse.com/terminology/",
}

OUT = pathlib.Path("docs")
OUT.mkdir(exist_ok=True)
HEADERS = {"User-Agent": "Mozilla/5.0 (personal doc-snapshot)"}
today = datetime.date.today().isoformat()


def extract_main(soup):
    """본문 영역만 골라내서 nav/사이드바 중복 제거."""
    for sel in ["main", "article", '[role="main"]', ".td-content",
                ".content", "#content", ".post"]:
        node = soup.select_one(sel)
        if node and len(node.get_text(strip=True)) > 200:
            return node
    return soup.body or soup


ok, fail = 0, 0
for slug, url in DOCS.items():
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else slug
        for tag in soup(["script", "style", "nav", "header", "footer", "form", "svg"]):
            tag.decompose()
        markdown = md(str(extract_main(soup)), heading_style="ATX", strip=["img"])
        markdown = re.sub(r"\n{3,}", "\n\n", markdown).strip()
        (OUT / f"{slug}.md").write_text(
            f"---\ntitle: {title}\nsource: {url}\nsnapshot: {today}\n---\n\n{markdown}\n",
            encoding="utf-8",
        )
        print(f"OK   {slug:24s} <- {url}")
        ok += 1
    except Exception as e:
        print(f"FAIL {slug:24s} <- {url}  ({e})", file=sys.stderr)
        fail += 1

print(f"\n완료: {ok}개 저장, {fail}개 실패 -> ./docs/")
