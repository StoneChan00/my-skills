# -*- coding: utf-8 -*-
import json
from pathlib import Path

d = json.loads(Path(r"D:\2_Projects\github\StoneChan00\my-skills\map-collections\xhs-board-6a52494f\osm_geocoded_final.json").read_text(encoding="utf-8"))
for x in d:
    if x.get("source") in ("douyin", "douyin+xhs"):
        print(f"{x['display'][:30]:34s} osm={str(x.get('osm_name'))[:28]:30s} {x['lat']:.5f},{x['lon']:.5f} [{x.get('precision')}]")
