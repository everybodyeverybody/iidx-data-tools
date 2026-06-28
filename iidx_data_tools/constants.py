#!/usr/bin/env python3
import os
from pathlib import Path
# from .local_dataclasses import NumberArea

BASE_DIR = Path(os.getenv("PWD", default="./"))
DATA_DIR = BASE_DIR / Path("data")

KAMAITACHI_SONG_LIST_URL = "https://raw.githubusercontent.com/zkldi/Tachi/refs/heads/main/db/seeds/songs-iidx.json"
KAMAITACHI_SP_CHART_LIST_URL = "https://raw.githubusercontent.com/zkldi/Tachi/refs/heads/main/db/seeds/charts-iidx-sp.json"
KAMAITACHI_DP_CHART_LIST_URL = "https://raw.githubusercontent.com/zkldi/Tachi/refs/heads/main/db/seeds/charts-iidx-dp.json"
EAMUSE_REFERER_URL = "https://p.eagate.573.jp/gate/p/eamusement/coop/mall.html?fromlist&dt=%2FIIDX%20INFINITAS%2F%E6%A5%BD%E6%9B%B2%E3%83%91%E3%83%83%E3%82%AF%2F&pid=320"
INFINITAS_MUSIC_HTML = DATA_DIR / Path("music_index.html")
INFINITAS_SONG_PACK_JSON = DATA_DIR / Path("pack_index.json")
EAMUSE_SONG_PACK_URL = "https://p.eagate.573.jp/gate/p/eamusement/coop/api/getdata.html"
INFINITAS_MUSIC_URL = "https://p.eagate.573.jp/game/infinitas/2/music/index.html"
KAMAITACHI_SONG_LIST = DATA_DIR / Path("kamaitachi-iidx-songs.json")
KAMAITACHI_SP_CHART_LIST = DATA_DIR / Path("kamaitachi-iidx-sp-charts.json")
KAMAITACHI_DP_CHART_LIST = DATA_DIR / Path("kamaitachi-iidx-dp-charts.json")
