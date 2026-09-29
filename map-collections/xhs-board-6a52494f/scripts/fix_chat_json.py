# -*- coding: utf-8 -*-
import json
from pathlib import Path

raw = Path(r"D:\2_Projects\github\StoneChan00\my-skills\chat-all-messages.json").read_text(encoding="utf-8")
print("repr head:", repr(raw[:80]))

j = None
try:
    j = json.loads(raw)
    print("direct loads OK:", type(j).__name__)
except Exception as e:
    print("direct fail:", e)
    # 双重解码: 文件内容可能是 JSON 字符串字面量
    try:
        j = json.loads(raw.encode().decode("unicode_escape"))
        print("unescape OK:", type(j).__name__)
    except Exception as e2:
        print("unescape fail:", e2)

if isinstance(j, str):
    try:
        j = json.loads(j)
        print("second-level loads OK:", type(j).__name__)
    except Exception as e3:
        print("second fail:", e3)

if isinstance(j, list):
    print("messages:", len(j))
    Path(r"D:\2_Projects\github\StoneChan00\my-skills\map-collections\xhs-board-6a52494f\chat-messages-clean.json").write_text(
        json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
    print("saved clean copy")
