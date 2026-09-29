# -*- coding: utf-8 -*-
"""
后台守望：轮询聊天新笔记 → 自动读取 → 备好摘要。
- 每 5 分钟检查一次（免签名 IM API + config cookie）
- 发现新笔记: 并入 note_list.json → redbook 批量读取 → 重生成 notes_digest.json → 写 WATCH_STATUS.json
- 自终止: 达到 54 篇 或 运行超 12 小时 或 cookie 失效
"""
import json
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CFG = Path(__file__).resolve().parents[3] / ".opencode" / "skills" / "travel-planner" / "config.json"
STATUS_FILE = BASE / "WATCH_STATUS.json"
LOG_FILE = BASE / "watcher.log"
POLL_S = 300
MAX_HOURS = 12

CITY_CENTER_NOTES = 54  # 专辑总篇数


def log(msg: str):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def fetch_token_cards():
    cookie = json.loads(CFG.read_text(encoding="utf-8"))["redbook_cookie"]
    url = ("https://edith.xiaohongshu.com/api/im/web/messages/history?"
           "chat_user_id=61b6c78e000000001000ba5d&last_id=0&start_id=0&limit=100")
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        "Cookie": cookie, "Referer": "https://www.xiaohongshu.com/",
        "Origin": "https://www.xiaohongshu.com",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        j = json.loads(r.read().decode("utf-8"))
    msgs = (j.get("data") or {}).get("out_message_list") or []
    notes = {}
    for m in msgs:
        try:
            c = json.loads(m["content"])
            if c.get("content_type") != 3:
                continue
            inner = json.loads(c["content"]) if isinstance(c["content"], str) else (c["content"] or {})
            if inner.get("type") != "note" or not inner.get("id"):
                continue
            mt = re.search(r"xsec_token=([^&]+)", inner.get("link") or "")
            if mt:
                notes[inner["id"]] = {"note_id": inner["id"], "xsec_token": mt.group(1),
                                      "xsec_source": "app_share", "title": inner.get("title") or ""}
        except Exception:
            continue
    return notes


def write_status(state, total, new=0, msg=""):
    STATUS_FILE.write_text(json.dumps({
        "state": state, "token_cards_total": total, "target": CITY_CENTER_NOTES,
        "new_since_last_excel": new, "message": msg,
        "updated": datetime.now().isoformat(timespec="seconds"),
    }, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    start = time.time()
    log(f"守望启动: 每{POLL_S}s轮询, 目标{CITY_CENTER_NOTES}篇, 最长{MAX_HOURS}h")
    seen_at_start = set()
    first = True
    while True:
        try:
            cards = fetch_token_cards()
        except Exception as e:
            log(f"API异常: {e}")
            if "401" in str(e) or "403" in str(e):
                write_status("cookie_expired", 0, 0, "cookie 失效，需重新扫码/更新")
                log("cookie 失效，守望退出")
                return 1
            time.sleep(POLL_S)
            continue

        if first:
            seen_at_start = set(cards.keys())
            write_status("watching", len(cards), 0, "等待新笔记分享")
            log(f"初始: {len(cards)} 篇带token")
            first = False
            time.sleep(POLL_S)
            continue

        new = {k: v for k, v in cards.items() if k not in seen_at_start}
        if new:
            log(f"发现 {len(new)} 篇新笔记!")
            # 并入 note_list.json
            nl_path = BASE / "note_list.json"
            old_list = json.loads(nl_path.read_text(encoding="utf-8"))
            old_ids = {n["note_id"] for n in old_list}
            merged = old_list + [v for k, v in new.items() if k not in old_ids]
            nl_path.write_text(json.dumps(merged, ensure_ascii=False, indent=1), encoding="utf-8")
            # 批量读取（断点续跑，只会读新的）
            r = subprocess.run([sys.executable, str(BASE / "scripts" / "read_notes.py"), "--read-only"],
                               capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=1800, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
            log(f"读取完成 rc={r.returncode}: {r.stdout[-300:] if r.stdout else r.stderr[-300:]}")
            # 重生成摘要
            r2 = subprocess.run([sys.executable, str(BASE / "scripts" / "make_digest.py")],
                                capture_output=True, text=True, encoding="utf-8", errors="replace",
                                timeout=120, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
            log(f"摘要重生成 rc={r2.returncode}")
            write_status("awaiting_extraction", len(cards), len(new),
                         f"新到 {len(new)} 篇已自动读取，等待 LLM 提取地点 → 叫一声 agent 即可")
            log(f"状态: {len(cards)}/{CITY_CENTER_NOTES} 篇, 新增 {len(new)} 已就绪")
            seen_at_start = set(cards.keys())
            if len(cards) >= CITY_CENTER_NOTES:
                log("已达标 54 篇，守望退出")
                return 0
        else:
            write_status("watching", len(cards), 0, "等待新笔记分享")
            log(f"无新增 ({len(cards)}/{CITY_CENTER_NOTES})")

        if (time.time() - start) > MAX_HOURS * 3600:
            log("超时退出")
            write_status("timeout", len(cards), 0, "守望超时退出，可重启")
            return 0
        time.sleep(POLL_S)


if __name__ == "__main__":
    sys.exit(main())
