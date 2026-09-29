#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量读取小红书合集笔记。

用法:
  python read_notes.py --board-url "<合集链接>"          # 第一步: 拉合集笔记列表 → board.json
  python read_notes.py --board-url "<合集链接>" --read   # 第二步: 逐篇读取 → notes/<id>.json

特性: 可断点续跑(跳过已有文件)、间隔 3.5s 防风控、连续 3 次失败自动中止、
      board.json 结构自适应解析(递归收集 note_id + xsec_token)。
"""
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import _common
BASE = _common.base_from_argv()  # --dir <collection目录> 可指定，缺省取最新
NOTES_DIR = BASE / "notes"
BOARD_FILE = BASE / "board.json"
CONFIG = _common.config_path()

NOTE_ID_RE = re.compile(r"^[0-9a-f]{24}$")
SLEEP_S = 3.5
MAX_CONSEC_FAIL = 3


def get_cookie() -> str:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    return cfg["redbook_cookie"]


def run_redbook(args: list) -> str:
    """运行 redbook，返回 stdout。node 直调 cli.js（.cmd 垫片会切坏 cookie 分号）。"""
    p = subprocess.run(_common.redbook_cmd() + args, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=180)
    out = (p.stdout or "") + (p.stderr or "")
    return out


def extract_json(text: str):
    """从 redbook 输出中提取 JSON（用 raw_decode 兼容 JSON 后有尾随文本的情况）"""
    dec = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch in "{[":
            try:
                obj, _ = dec.raw_decode(text[i:])
                return obj
            except json.JSONDecodeError:
                continue
    return None


def collect_notes(obj, found: dict):
    """递归收集 note_id -> {xsec_token, title}（结构自适应）"""
    if isinstance(obj, dict):
        nid = tok = title = None
        for k, v in obj.items():
            kl = k.lower()
            if kl in ("note_id", "noteid", "id") and isinstance(v, str) and NOTE_ID_RE.match(v):
                nid = v
            if kl == "xsec_token" and isinstance(v, str):
                tok = v
            if kl in ("title", "display_title", "name") and isinstance(v, str):
                title = v
        if nid:
            ent = found.setdefault(nid, {})
            if tok:
                ent["xsec_token"] = tok
            if title and "title" not in ent:
                ent["title"] = title
        for v in obj.values():
            collect_notes(v, found)
    elif isinstance(obj, list):
        for v in obj:
            collect_notes(v, found)


def fetch_board(url: str, cookie: str) -> int:
    print(f"[1/2] 拉取合集列表: {url}")
    out = run_redbook(["board", url, "--cookie-string", cookie, "--json"])
    data = extract_json(out)
    if data is None:
        print("[FAIL] 无法解析 board 输出。原始输出前 800 字符:")
        print(out[:800])
        return 1
    BOARD_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    found: dict = {}
    collect_notes(data, found)
    # 兜底: 从原始文本正则收集
    for nid in set(re.findall(r"(?:explore/|note_id[\"'=:\s]+)([0-9a-f]{24})", out)):
        found.setdefault(nid, {})

    NOTES_DIR.mkdir(exist_ok=True)
    (BASE / "note_list.json").write_text(
        json.dumps([{"note_id": k, **v} for k, v in found.items()], ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"[OK] board.json 已保存; 共发现 {len(found)} 篇笔记 → note_list.json")
    if 0 < len(found) < 5:
        print("     (数量偏少，可能只拿到第一页，需要检查 board.json 是否有分页)")
    return 0


def read_all(cookie: str) -> int:
    nl = BASE / "note_list.json"
    if not nl.exists():
        print("[ERROR] 缺少 note_list.json，请先不带 --read 运行")
        return 1
    notes = json.loads(nl.read_text(encoding="utf-8"))
    print(f"[2/2] 开始读取 {len(notes)} 篇笔记 (间隔 {SLEEP_S}s，可断点续跑)")
    NOTES_DIR.mkdir(exist_ok=True)

    consec_fail, ok, skip = 0, 0, 0
    for i, n in enumerate(notes, 1):
        nid = n["note_id"]
        dest = NOTES_DIR / f"{nid}.json"
        if dest.exists() and dest.stat().st_size > 100:
            skip += 1
            continue
        url = f"https://www.xiaohongshu.com/explore/{nid}"
        if n.get("xsec_token"):
            url += f"?xsec_token={n['xsec_token']}&xsec_source=pc_feed"
        out = run_redbook(["read", url, "--cookie-string", cookie, "--json"])
        data = extract_json(out)
        if not isinstance(data, dict) or not any(k in data for k in ("note_id", "title", "desc", "user")):
            print(f"  [{i}/{len(notes)}] FAIL {nid}: {out[:120].strip()}")
            consec_fail += 1
            if consec_fail >= MAX_CONSEC_FAIL:
                print(f"[ABORT] 连续 {MAX_CONSEC_FAIL} 次失败，疑似 cookie 失效或被风控。已完成 {ok} 篇。")
                return 2
            time.sleep(SLEEP_S)
            continue
        consec_fail = 0
        dest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        ok += 1
        title = ""
        try:
            t = data if isinstance(data, dict) else {}
            title = t.get("title") or t.get("note", {}).get("title") or n.get("title") or ""
        except Exception:
            pass
        print(f"  [{i}/{len(notes)}] OK {nid} 《{title[:30]}》")
        time.sleep(SLEEP_S)

    print(f"\n完成: 新读 {ok}, 跳过(已有) {skip}, 剩余失败 {len(notes)-ok-skip}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--board-url", default=None)
    ap.add_argument("--read", action="store_true", help="读取全部笔记（默认只拉列表）")
    ap.add_argument("--read-only", action="store_true", help="跳过拉列表，直接按 note_list.json 读取")
    ap.add_argument("--cookie", default=None, help="覆盖 config.json 中的 cookie")
    args = ap.parse_args()

    cookie = args.cookie or get_cookie()
    if not args.read_only:
        if not args.board_url:
            ap.error("需要 --board-url（或用 --read-only）")
        rc = fetch_board(args.board_url, cookie)
        if rc != 0:
            return rc
    if args.read or args.read_only:
        rc = read_all(cookie)
    return rc


if __name__ == "__main__":
    sys.exit(main())
