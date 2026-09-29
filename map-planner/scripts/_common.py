#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""map-planner 共享工具：仓库根定位 / 凭据配置 / collection 目录解析 / redbook 命令。

兼容三种安装形态（symlink / junction / 直接拷贝）——通过向上搜索 .git 或
map-collections/ 定位仓库根，不依赖 __file__ 的相对层级。
"""
import json
import os
import sys
from pathlib import Path


def repo_root() -> Path:
    p = Path(__file__).resolve()
    for anc in p.parents:
        if (anc / ".git").exists() or (anc / "map-collections").is_dir():
            return anc
    return p.parents[2]


def config_path() -> Path:
    """凭据配置（与 travel-planner skill 共享，位于 gitignored 区域）。"""
    return repo_root() / ".opencode" / "skills" / "travel-planner" / "config.json"


def config() -> dict:
    return json.loads(config_path().read_text(encoding="utf-8"))


def base_from_argv() -> Path:
    """从 sys.argv 预扫描 --dir <collection目录>（并从 argv 移除，避免干扰各脚本自身的 argparse）。
    未指定时默认取 map-collections/ 下最新的 collection。"""
    d = None
    if "--dir" in sys.argv:
        i = sys.argv.index("--dir")
        if i + 1 < len(sys.argv):
            d = sys.argv[i + 1]
            del sys.argv[i:i + 2]
    if d:
        p = Path(d).resolve()
        if not p.is_dir():
            raise SystemExit(f"[ERROR] --dir 指定的目录不存在: {p}")
        return p
    mc = repo_root() / "map-collections"
    if mc.is_dir():
        dirs = sorted(x for x in mc.iterdir() if x.is_dir())
        if dirs:
            return dirs[-1]
    return Path.cwd()


def redbook_cmd() -> list:
    """构造 redbook CLI 调用命令。Windows 下必须 node 直调 cli.js——
    .cmd 垫片会把 cookie 里的分号当参数分隔符切坏参数。"""
    appdata = os.environ.get("APPDATA", "")
    cli = Path(appdata) / "npm" / "node_modules" / "@lucasygu" / "redbook" / "dist" / "cli.js"
    if cli.exists():
        return ["node", str(cli)]
    if os.name != "nt":
        return ["redbook"]
    raise SystemExit("[ERROR] redbook CLI 未安装 (npm i -g @lucasygu/redbook)")
