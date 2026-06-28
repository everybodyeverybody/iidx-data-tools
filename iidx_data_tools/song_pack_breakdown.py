#!/usr/bin/env python3
import re
import json
import time
import logging
import argparse
import datetime
from pathlib import Path
from typing import Any, Optional

import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

from . import constants as CONSTANTS

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def download_song_pack_price_data() -> Path:
    headers = {"Referer": CONSTANTS.EAMUSE_REFERER_URL}
    url = CONSTANTS.EAMUSE_SONG_PACK_URL
    local_file = CONSTANTS.INFINITAS_SONG_PACK_JSON
    log.info(f"downloading {url} to {local_file}")
    response = requests.post(url, headers=headers)
    with open(local_file, "wt") as writer:
        writer.write(response.text)
    return local_file


def download_konami_song_data() -> Path:
    url = CONSTANTS.INFINITAS_MUSIC_URL
    local_file = CONSTANTS.INFINITAS_MUSIC_HTML
    log.info(f"downloading {url} to {local_file}")
    response = requests.get(url)
    with open(local_file, "wt") as writer:
        writer.write(response.text)
    return local_file


def parse_json(song_pack_json_file: Path) -> dict[str, dict[str, Any]]:
    pack_info: dict[str, dict[str, Any]] = {}
    with open(song_pack_json_file, "rt") as reader:
        pack_json = json.load(reader)
        for p in pack_json["product"]:
            if "content_keyword" in p and p["content_keyword"] == "IIDX INFINITAS":
                if p["display_tree"] == "/楽曲パック/":
                    fixed_name = re.sub("(<br>|<BR>)", " ", p["product_name"])
                    price_in_yen = p["payment"]["6"]["price"]
                    is_on_sale = p["sale_id"] != 1

                    sale_ends = int(
                        pack_json["sale"][str(p["sale_id"])]["end_datetime"] / 1000
                    )
                    pack_info[fixed_name] = {
                        "price_in_yen": price_in_yen,
                        "is_on_sale": is_on_sale,
                        "sale_ends": sale_ends,
                    }
    return pack_info


def normalize_konami_data_to_kamaitachi(song: tuple[str, str]) -> tuple[str, str]:
    """
    Song titles listed on Konami's site for infinitas do not match with the
    song values provided by Tachi's iidx seeds files. Rather than do any
    regex insanity, we keep map the artists/titles we know don't match
    to the values in kamaitachi's json.
    """
    normalizer: dict[tuple, tuple[str, str]] = {
        ("DE DE MOUSE", "Bitter & Lucky"): ("DÉ DÉ MOUSE", "Bitter & Lucky"),
        ('BEMANI Sound Team "TAG"', "Euphoric Lagoon"): (
            "BEMANI Sound Team TAG",
            "Euphoric Lagoon",
        ),
        ('BEMANI Sound Team "Trance Liquid"', "X-ray binary"): (
            "BEMANI Sound Team Trance Liquid",
            "X-ray binary",
        ),
        ('BEMANI Sound Team "HuΣeR" respect for D.J.Amuro', "∀"): (
            "BEMANI Sound Team HuΣeR respect for D.J.Amuro",
            "∀",
        ),
        ('BEMANI Sound Team "あさき隊"', "ここからよろしく大作戦143"): (
            "BEMANI Sound Team あさき隊",
            "ここからよろしく大作戦143",
        ),
        ("Snail's House", "魔法のかくれんぼ"): ("Snails House", "魔法のかくれんぼ"),
        ('BEMANI Sound Team "Akhuta Works" feat. mami', "乱膳の舞姫"): (
            "BEMANI Sound Team Akhuta Works feat. mami",
            "乱膳の舞姫",
        ),
        ('BEMANI Sound Team "Sota Fujimori"', "Breakin' Rules"): (
            "BEMANI Sound Team Sota Fujimori",
            "Breakin Rules",
        ),
        ('BEMANI Sound Team "Trance Liquid"', "of the first magnitude"): (
            "BEMANI Sound Team Trance Liquid",
            "of the first magnitude",
        ),
        ('BEMANI Sound Team "DARK TRAIN"', "S-Bahn"): (
            "BEMANI Sound Team DARK TRAIN",
            "S-Bahn",
        ),
        ("Remixed by Snail's House", "smooooch・∀・ (Snail's House Remix)"): (
            "Remixed by Snails House",
            "smooooch・∀・ (Snails House Remix)",
        ),
        ('Yuta Imai Vs. BEMANI Sound Team "L.E.D.-G"', "THE PEERLESS UNDER HEAVEN"): (
            "Yuta Imai Vs. BEMANI Sound Team L.E.D.-G",
            "THE PEERLESS UNDER HEAVEN",
        ),
        ('BEMANI Sound Team "Yvya"', "Vitrum"): ("BEMANI Sound Team Yvya", "Vitrum"),
        ('BEMANI Sound Team "Coyaan"', "水鏡の異界"): (
            "BEMANI Sound Team Coyaan",
            "水鏡の異界",
        ),
        ('BEMANI Sound Team "劇団レコード" feat.Risa Yuzuki', "霧幻メモリア"): (
            "BEMANI Sound Team 劇団レコード feat.Risa Yuzuki",
            "霧幻メモリア",
        ),
        ('BEMANI Sound Team "L.E.D."', "PHASE SHIFT MANEUVER"): (
            'BEMANI Sound Team "L.E.D." ',
            "PHASE SHIFT MANEUVER",
        ),
        (
            "噂の怪盗少女ぷらずま★彡Prim@休業中～( _ _ ).。",
            "がっつり陰キャ!? 怪盗いいんちょの億劫^^;",
        ): (
            "噂の怪盗少女ぷらずま★彡Prim@休業中〜( _ _ ).。",
            "がっつり陰キャ!? 怪盗いいんちょの億劫^^;",
        ),
        ('BEMANI Sound Team "Sota F."', "BEMANI PRO LEAGUE Theme"): (
            "BEMANI Sound Team Sota F.",
            "BEMANI PRO LEAGUE Theme",
        ),
        ("かめりあ feat. ななひら", "Amor De Verào"): (
            "かめりあ feat. ななひら",
            "Amor De Verão",
        ),
        ('BEMANI Sound Team "Coyaan"', "Amabie"): (
            "BEMANI Sound Team “Coyaan”",
            "Amabie",
        ),
        ("D-Evoke（与那嶺雅人/小日向翔）", "共犯ヘヴンズコード"): (
            "D-Evoke（与那嶺雅人/小日向翔）",
            "共犯へヴンズコード",
        ),
        ("Ryu*", "!Viva!"): ("Ryu*", "¡Viva!"),
        ("RoughSkreamZ feat.楽天斎", "火影"): ("RoughSkreamZ feat.楽天斎", "焱影"),
        (
            "海の底からマーメイド Prim by ARM×狐夢想",
            "ギョギョっと人魚♨爆婚ブライダル",
        ): (
            "海の底からマーメイド Prim by ARM×狐夢想",
            "ギョギョっと人魚 爆婚ブライダル",
        ),
        ("◇◆噂の怪盗少女 ぷらずま★彡Prim◇◆", "表裏一体！？怪盗いいんちょの悩み❤"): (
            "◇◆噂の怪盗少女 ぷらずま★彡Prim◇◆",
            "表裏一体！？怪盗いいんちょの悩み♥",
        ),
        ("楓璃夢＝ジークフリード＝ファイエルローゼン", "旋律のドグマ～Miserables～"): (
            "楓璃夢＝ジークフリード＝ファイエルローゼン",
            "旋律のドグマ～Misérables～",
        ),
        ("ななひら", "超!!遠距離らぶメ～ル"): ("ななひら", "超!!遠距離らぶ♡メ〜ル"),
        ("あさき大監督", "野球の遊び方 そしてその歴史 ～決定版～"): (
            "あさき大監督",
            "野球の遊び方　そしてその歴史　～決定版～",
        ),
        ("猫叉Master", "Reflection Into the EDEN"): (
            "猫叉Master",
            "Reflection into the EDEN",
        ),
        ("TËЯRA", "LETHEBOLG ～双神威に斬り咲けり～"): (
            "ＴЁЯＲＡ",
            "LETHEBOLG ～双神威に斬り咲けり～",
        ),
        ("CANVAS feat. Quimar", "Out of Control"): (
            "CANVAS feat. Quimär",
            "Out of Control",
        ),
        ("高田 雅史", "WaterCube Pf.(RX-Ver.S.P.L.)"): (
            "高田雅史",
            "WaterCube Pf.(RX-Ver.S.P.L.)",
        ),
        ('BEMANI Sound Team "L.E.D.-G"', "THE ANCIENT KING IS BACK"): (
            "L.E.D.-G",
            "THE ANCIENT KING IS BACK",
        ),
        ("Juggernaut.", "GO!"): ("Juggernaut", "GO!"),
        ("Yuta Imai", "SμG@R RU$#"): ("Yuta Imai", "SµG@R RU$#"),
        ("くにたけみゆき", "Destiny Lovers"): ("くにたけみゆき", "Destiny lovers"),
        ("cosMo@暴走P", "Hopeful Daybreak!!!"): ("cosMo＠暴走P", "Hopeful Daybreak!!!"),
        (
            "SOUND HOLIC Vs. BEMANI Sound Team “T.Kakuta” feat. Nana Takahashi",
            "鬼華-修羅の舞-",
        ): (
            'SOUND HOLIC Vs. BEMANI Sound Team "T.Kakuta" feat. Nana Takahashi',
            "鬼華-修羅の舞-",
        ),
    }

    if song not in normalizer:
        return song
    return normalizer[song]


def parse_html(local_file: Path) -> dict:
    songs_by_pack: dict[str, dict] = {}
    with open(local_file, "rt") as reader:
        html = "".join(reader.readlines())
    soup = BeautifulSoup(html, "html.parser")
    for t in soup.find_all("table"):
        prev = t.find_previous_siblings("div", limit=1)
        if not prev:
            continue
        title_div = prev[0]
        label_tag = None
        is_song_pack_label = False
        for child in title_div.contents:
            if child.name == "strong" and child.contents:
                label_tag = child.contents[0].strip()
                if re.match(".*楽曲パック.*", label_tag):
                    is_song_pack_label = True
                break
        prev_is_right_class = "cat" in title_div.attrs["class"]

        if prev_is_right_class and label_tag and is_song_pack_label:
            sublabel_match = re.findall(r"(.*)\((.*)\)", label_tag)
            if sublabel_match:
                product_name = str.strip(sublabel_match[0][0])
                sublabel = str.strip(sublabel_match[0][1])
            else:
                product_name = label_tag.strip()
                sublabel = ""
            if product_name not in songs_by_pack:
                songs_by_pack[product_name] = {}
                songs_by_pack[product_name]["PRODUCT_NAME_SUBLABEL"] = sublabel
                songs_by_pack[product_name]["SONGS"] = []

            for rows in t.find_all("tr"):
                columns = rows.find_all("td")
                if not columns or len(columns) != 2:
                    continue
                title = columns[0].contents[0].strip()
                artist = columns[1].contents[0].strip()
                song = (artist, title)
                normed_song = normalize_konami_data_to_kamaitachi(song)
                songs_by_pack[product_name]["SONGS"].append(normed_song)
    return songs_by_pack


def download_kamaitachi_song_list() -> tuple[Path, Path, Path]:
    songs_json_file = CONSTANTS.KAMAITACHI_SONG_LIST
    chart_sp_json_file = CONSTANTS.KAMAITACHI_SP_CHART_LIST
    chart_dp_json_file = CONSTANTS.KAMAITACHI_DP_CHART_LIST
    with (
        open(songs_json_file, "wt") as json_writer,
        open(chart_sp_json_file, "wt") as sp_chart_writer,
        open(chart_dp_json_file, "wt") as dp_chart_writer,
    ):
        log.info(
            f"Downloading kamaitachi song list {CONSTANTS.KAMAITACHI_SONG_LIST_URL} "
            f"to {songs_json_file}"
        )
        song_list_json_response = requests.get(CONSTANTS.KAMAITACHI_SONG_LIST_URL)
        if song_list_json_response.status_code == 200:
            json_writer.write(song_list_json_response.text)
        else:
            raise RuntimeError(
                f"could not download kamaitachi source from "
                "{CONSTANTS.KAMAITACHI_SONG_LIST_URL} "
                f"code: {song_list_json_response.status_code} "
                f"error: {song_list_json_response.text}"
            )

        log.info(
            f"Downloading kamaitachi SP difficulty data {CONSTANTS.KAMAITACHI_SP_CHART_LIST_URL} "
            f"to {chart_sp_json_file}"
        )
        chart_list_json_response = requests.get(CONSTANTS.KAMAITACHI_SP_CHART_LIST_URL)
        if chart_list_json_response.status_code == 200:
            sp_chart_writer.write(chart_list_json_response.text)
        else:
            raise RuntimeError(
                f"could not download kamaitachi source from "
                "{CONSTANTS.KAMAITACHI_SP_CHART_LIST_URL} "
                f"code: {chart_list_json_response.status_code} "
                f"error: {chart_list_json_response.text}"
            )

        log.info(
            f"Downloading kamaitachi DP difficulty data {CONSTANTS.KAMAITACHI_DP_CHART_LIST_URL} "
            f"to {chart_dp_json_file}"
        )
        chart_list_json_response = requests.get(CONSTANTS.KAMAITACHI_DP_CHART_LIST_URL)
        if chart_list_json_response.status_code == 200:
            dp_chart_writer.write(chart_list_json_response.text)
        else:
            raise RuntimeError(
                f"could not download kamaitachi source from "
                "{CONSTANTS.KAMAITACHI_DP_CHART_LIST_URL} "
                f"code: {chart_list_json_response.status_code} "
                f"error: {chart_list_json_response.text}"
            )

    return songs_json_file, chart_sp_json_file, chart_dp_json_file


def combine_kamaitachi_data(
    songs: Path, sp_charts: Path, dp_charts: Path
) -> dict[tuple, dict[tuple, dict[str, Any]]]:
    with open(songs, "rt") as reader:
        songs_json = json.load(reader)

    songs_by_kamaitachi_id = {
        entry["id"]: {
            "artist": entry["artist"],
            "title": entry["title"],
        }
        for entry in songs_json
    }

    with open(sp_charts, "rt") as reader:
        sp_charts_json = json.load(reader)

    with open(dp_charts, "rt") as reader:
        dp_charts_json = json.load(reader)

    charts_by_kamaitachi_id: dict[int, dict[tuple, dict[str, Any]]] = {}

    for chart_json, is_sp in [(sp_charts_json, True), (dp_charts_json, False)]:
        for c in chart_json:
            if "inf" not in c["versions"]:
                continue
            if c["songID"] not in charts_by_kamaitachi_id:
                charts_by_kamaitachi_id[c["songID"]] = {}
            if c["levelNum"] == 0:
                continue
            level = c["levelNum"]
            nc_tier_label = None
            hc_tier_label = None

            if level >= 11 and "ncTier" in c["data"]:
                if c["data"]["ncTier"]["individualDifference"]:
                    tier_type = "個"
                else:
                    tier_type = "地"
                nc_tier_label = f"{tier_type}{c['data']['ncTier']['text']}"

            if level >= 11 and "hcTier" in c["data"]:
                if c["data"]["hcTier"]["individualDifference"]:
                    tier_type = "個"
                else:
                    tier_type = "地"
                hc_tier_label = f"{tier_type}{c['data']['hcTier']['text']}"

            if is_sp:
                playtype = "SP"
            else:
                playtype = "DP"
            entry = (playtype, c["difficulty"])
            value = {"level": level, "nc_tier": nc_tier_label, "hc_tier": hc_tier_label}
            charts_by_kamaitachi_id[c["songID"]][entry] = value

    combined_data: dict = {}
    for song_id in songs_by_kamaitachi_id.keys():
        artist = songs_by_kamaitachi_id[song_id]["artist"]
        title = songs_by_kamaitachi_id[song_id]["title"]
        combined_key = (artist, title)
        if song_id not in charts_by_kamaitachi_id:
            log.debug(f"SKIPPING song_id {song_id} {combined_key}: not in inf")
            continue
        combined_data[combined_key] = charts_by_kamaitachi_id[song_id]
    return combined_data


def generate_community_tables(
    songs: dict[tuple[str, str], dict[tuple[str, str], dict[str, Any]]],
) -> str:
    not_available = "N/A"
    nc_ranks = {}
    hc_ranks = {}
    for song, diffs in songs.items():
        for diff in diffs:
            nc_tier = songs[song][diff]["nc_tier"]
            hc_tier = songs[song][diff]["hc_tier"]
            song_metadata = song + diff + (songs[song][diff]["level"],)
            if diff[0] == "SP":
                if not nc_tier:
                    nc_ranks[song_metadata] = not_available
                else:
                    nc_ranks[song_metadata] = songs[song][diff]["nc_tier"]
                if not hc_tier:
                    hc_ranks[song_metadata] = not_available
                else:
                    hc_ranks[song_metadata] = songs[song][diff]["hc_tier"]

    community_sections = []
    for level in [12, 11]:
        section = f"<div class='community'><h3>SP☆{level} Ranks</h3>"
        table_header = (
            "<table class='community'>\n"
            "<tr>"
            "<th class='shorttitle'>Rank</th>"
            "<th class='n num'>NC</th>"
            "<th class='a num'>HC</th>"
            "</tr>"
        )
        table_footer = "</table></div>"
        individual_order = ["個", "地"]
        rank_order = ["F", "E", "D", "C", "B", "B+", "A", "A+", "S", "S+"]
        order: list[str] = []
        for rank in rank_order:
            for ind in individual_order:
                order.append(f"{ind}{level}{rank}")
        order.insert(0, not_available)
        nc_rank_count: list[int] = [0] * len(order)
        hc_rank_count: list[int] = [0] * len(order)
        for index, rank in nc_ranks.items():
            if index[4] != level:
                continue
            count_index = order.index(rank)
            nc_rank_count[count_index] += 1

        for index, rank in hc_ranks.items():
            if index[4] != level:
                continue
            count_index = order.index(rank)
            hc_rank_count[count_index] += 1

        table_body_rows = []
        for i, r in enumerate(order):
            nc_count = str(nc_rank_count[i])
            hc_count = str(hc_rank_count[i])
            if nc_count == "0":
                nc_count = ""
            if hc_count == "0":
                hc_count = ""
            row = (
                f"<tr><td class='rank'>{r}</td>"
                f"<td class='num n'>{nc_count}</td>"
                f"<td class='num a'>{hc_count}</td>"
                "</tr>"
            )
            table_body_rows.append(row)
        table_body = "\n".join(table_body_rows)
        table = "\n".join([section, table_header, table_body, table_footer])
        community_sections.append(table)
    community_tables_html = "\n".join(community_sections)
    return community_tables_html


def generate_dp_table(
    songs: dict[tuple[str, str], dict[tuple[str, str], dict[str, Any]]],
) -> str:
    section = "<div class='dp_table'><h3>DP Songs</h3>"
    table_header = (
        "<table>\n"
        "<tr>"
        "<th class='shorttitle'>Lv.</th>"
        "<th class='num n'>N</th>"
        "<th class='num h'>H</th>"
        "<th class='num a'>A</th>"
        "<th class='num l'>L</th>"
        "<th class='num total'>Total</th>"
        "</tr>"
    )

    row_template = (
        "<tr>"
        "<td class='num'>{}</td>"
        "<td class='num n'>{}</td>"
        "<td class='num h'>{}</td>"
        "<td class='num a'>{}</td>"
        "<td class='num l'>{}</td>"
        "<td class='num total'>{}</td>"
        "</tr>"
    )
    footer = "</table></div>"
    empty_2d_array = [[0] * 4 for x in range(13)]
    for song, diff in songs.items():
        sorted_diffs = sort_difficulties(diff)
        sp_sorted_diffs = sorted_diffs[5:]
        for diff_x, level_y in enumerate(sp_sorted_diffs):
            if level_y and level_y["level"]:
                empty_2d_array[level_y["level"]][diff_x] += 1
    level_rows = []
    for index, row in enumerate(empty_2d_array):
        if index == 0:
            continue
        html_row_data = [index]
        html_row_data.extend(row)
        total = sum(row)
        html_row_data.append(total)

        bold_html_row_data = [f"{x}" if x != 0 else "" for x in html_row_data]

        html_row = row_template.format(*bold_html_row_data)
        level_rows.append(html_row)
    table_body = "\n".join(level_rows)
    dp_table = "\n".join([section, table_header, table_body, footer])
    return dp_table


def generate_sp_table(
    songs: dict[tuple[str, str], dict[tuple[str, str], dict[str, Any]]],
) -> str:
    section = "<div class='sp_table'><h3>SP Songs</h3>"
    table_header = (
        "<table>"
        "<tr>"
        "<th class='shorttitle'>Lv.</th>"
        "<th class='num b'>B</th>"
        "<th class='num n'>N</th>"
        "<th class='num h'>H</th>"
        "<th class='num a'>A</th>"
        "<th class='num l'>L</th>"
        "<th class='num total'>Total</th>"
        "</tr>"
    )

    row_template = (
        "<tr>"
        "<td class='num'>{}</td>"
        "<td class='num b'>{}</td>"
        "<td class='num n'>{}</td>"
        "<td class='num h'>{}</td>"
        "<td class='num a'>{}</td>"
        "<td class='num l'>{}</td>"
        "<td class='num total'>{}</td>"
        "</tr>"
    )
    footer = "</table></div>"

    empty_2d_array = [[0] * 5 for x in range(13)]
    for song, diff in songs.items():
        sorted_diffs = sort_difficulties(diff)
        sp_sorted_diffs = sorted_diffs[0:5]
        for diff_x, level_y in enumerate(sp_sorted_diffs):
            if level_y and level_y["level"]:
                empty_2d_array[level_y["level"]][diff_x] += 1
    level_rows = []
    for index, row in enumerate(empty_2d_array):
        if index == 0:
            continue
        html_row_data = [index]
        html_row_data.extend(row)
        total = sum(row)
        html_row_data.append(total)
        bold_html_row_data = [f"{x}" if x != 0 else "" for x in html_row_data]
        html_row = row_template.format(*bold_html_row_data)
        level_rows.append(html_row)
    table_body = "\n".join(level_rows)
    sp_table = "\n".join([section, table_header, table_body, footer])
    return sp_table


def sort_difficulties(
    difficulty_list: dict[tuple[str, str], dict[str, Any]],
) -> list[Optional[dict[str, Any]]]:
    ordering = [
        ("SP", "BEGINNER"),
        ("SP", "NORMAL"),
        ("SP", "HYPER"),
        ("SP", "ANOTHER"),
        ("SP", "LEGGENDARIA"),
        ("DP", "NORMAL"),
        ("DP", "HYPER"),
        ("DP", "ANOTHER"),
        ("DP", "LEGGENDARIA"),
    ]
    ordered_diffs: list[Optional[dict[str, Any]]] = []
    for difficulty in ordering:
        if difficulty in difficulty_list:
            ordered_diffs.append(difficulty_list[difficulty])
        else:
            ordered_diffs.append(None)
    return ordered_diffs


def generate_song_table(
    songs: dict[tuple[str, str], dict[tuple[str, str], dict[str, Any]]],
    pack_name: str,
    pack_info: dict[str, Any],
) -> tuple[str, str, str]:
    if pack_info["sublabel"]:
        pack_title = f"{pack_name} ( {pack_info['sublabel']} )"
    else:
        pack_title = f"{pack_name}"

    if pack_info["is_on_sale"]:
        sale_ends_datetime = datetime.datetime.fromtimestamp(
            pack_info["sale_ends"]
        ).date()
        on_sale = f"<span class='sale'>ON SALE TIL {sale_ends_datetime}</span> "
    else:
        on_sale = ""
    pack_price = f"￥{pack_info['price_in_yen']}"
    song_count = len(list(songs.keys()))
    price_per_song = int(pack_info["price_in_yen"] / song_count)

    section = (
        f"<div class='pack_header'>{pack_title}</div>\n"
        f"<div class='pack_price b'>{on_sale}{song_count} songs {pack_price} (about ￥{price_per_song} per song)</div>\n"
        f"<div class='song_table'><h3>Songlist</h3>\n"
    )

    table_header = (
        "<table>"
        "<tr>"
        "<th class='title'>Title</th>"
        "<th class='num b'>SPB</th>"
        "<th class='num n'>SPN</th>"
        "<th class='num h'>SPH</th>"
        "<th class='num a'>SPA</th>"
        "<th class='num l'>SPL</th>"
        "<th class='num n'>DPN</th>"
        "<th class='num h'>DPH</th>"
        "<th class='num a'>DPA</th>"
        "<th class='num l'>DPL</th>"
        "</tr>"
    )
    row_template = (
        "<tr>"
        "<td class='title'>{}</td>"
        "<td class='num b'>{}</td>"
        "<td class='num n'>{}</td>"
        "<td class='num h'>{}</td>"
        "<td class='num a'>{}</td>"
        "<td class='num l'>{}</td>"
        "<td class='num n'>{}</td>"
        "<td class='num h'>{}</td>"
        "<td class='num a'>{}</td>"
        "<td class='num l'>{}</td>"
        "</tr>"
    )
    footer = "</table></div>\n"
    difficulty_rows = []
    for song, diffs in songs.items():
        row = [song[1]]
        sorted_diffs = [
            sorted_diff["level"] if sorted_diff else None
            for sorted_diff in sort_difficulties(diffs)
        ]
        for diff in sorted_diffs:
            if diff:
                row.append(str(diff))
            else:
                row.append("")
        formatted_row = row_template.format(*row)
        difficulty_rows.append(formatted_row)
    joined_rows = "\n".join(difficulty_rows)
    table = "\n".join([section, table_header, joined_rows, footer])
    return on_sale, pack_title, table


def get_css() -> str:
    return """

body {
    font-family: sans-serif;
    color: #000000;
}

.pack {
    padding-top:1em;
    padding-bottom:1em;
    display: grid;
    grid-template-columns: repeat(3,2fr,1fr,1fr);
    gap: 0.25em;
}

.song_table {
  grid-row:3;
  border: 1px solid #000000;
}

.by_play_style {
    grid-row: 3;
    border: 1px solid #000000;
}

.by_community_rank {
    grid-row: 3;
    border: 1px solid #000000;
}

.pack_header {
    padding:1em;
    font-size:1.5em;
    font-weight: bold;
    color:#ffffff;
    background-color:#0000ff;
    grid-row:1;
    grid-column: 1 / span 3;
}

.pack_price {
    padding:0.5em;
    font-weight: bold;
    grid-row:2;
    grid-column: 1 / span 3;
}

.rank {
   font-weight: bold;
    font-size:0.75em;
}

.title {
    text-align: left;
}

th.title {
    width: 24em;
    font-weight: bold;
    color: #ffffff;
    background-color:#000000;
}

th.shorttitle {
    text-align: left;
    font-weight: bold;
    color: #ffffff;
    background-color:#000000;
}

.num {
    font-weight: bold;
    text-align:left;
    font-family: monospace;
    width: 2em;
}

h3  {
    font-weight: bold;
    color:#ffffff;
    background-color:#000000;
    padding: 1em;
    margin: 0em;
}
/* colors for difficulties */
.b {
    background-color:#ADF798;
}
.n {
    background-color:#66ffff;
}
.h {
    background-color:#ffff45;
}
.a {
    background-color:#F89B86;
}
.l {
    background-color:#EC98F7;
}
.total {
    background-color:#000000;
    color:#ffffff;
}
.sale {
    color:#ff0000;
    font-weight:bold;
}
    """


def generate_and_write_html(song_difficulties_by_pack, pack_info) -> None:
    last_update = datetime.datetime.now()
    css = get_css()
    header = (
        f"<html><title>INFINITAS Song Pack Value Breakdown</title>"
        f"<style>{css}</style>"
        f"<body><h1>INFINITAS Song Pack Value Breakdown</h1>"
        f"<div>Last Updated: <b>{last_update} {time.tzname[1]}</b></div>"
    )
    footer = "</body></html>"
    analysis_list = []
    toc_links = []
    for index, pack in enumerate(song_difficulties_by_pack.keys()):
        on_sale, pack_title, song_table = generate_song_table(
            song_difficulties_by_pack[pack], pack, pack_info[pack]
        )
        pack_id = f"pack{index}"
        pack_link = f"<li><a href='#{pack_id}'>{on_sale}{pack_title}</a></li>"
        toc_links.append(pack_link)
        pack_container = f"<div id='{pack_id}' class='pack'>"
        pack_footer = "</div>"
        play_style_header = "<div class='by_play_style'>"
        play_style_footer = "</div>"
        community_header = "<div class='by_community_rank'>"
        community_footer = "</div>"
        sp_table = generate_sp_table(song_difficulties_by_pack[pack])
        dp_table = generate_dp_table(song_difficulties_by_pack[pack])
        community_tables = generate_community_tables(song_difficulties_by_pack[pack])
        pack_body = "\n".join(
            [
                pack_container,
                song_table,
                community_header,
                community_tables,
                community_footer,
                play_style_header,
                sp_table,
                dp_table,
                play_style_footer,
                pack_footer,
            ]
        )
        analysis_list.append(pack_body)
    toc = "<ul>" + "\n".join(toc_links) + "</ul>"
    body = "\n".join(analysis_list)
    output_html = "\n".join([header, toc, body, footer])
    output_file = "index.html"
    with open("index.html", "wt") as writer:
        writer.write(output_html)
    log.info(f"wrote updated list to {output_file}")
    return


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-download",
        action="store_true",
        dest="skip_download",
        help="If set, will skip redownloading data from kamaitachi and e-amuse. Defaults to False.",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.skip_download:
        infinitas_music_html = CONSTANTS.INFINITAS_MUSIC_HTML
        infinitas_song_pack_json = CONSTANTS.INFINITAS_SONG_PACK_JSON
        ksongs = CONSTANTS.KAMAITACHI_SONG_LIST
        k_sp_charts = CONSTANTS.KAMAITACHI_SP_CHART_LIST
        k_dp_charts = CONSTANTS.KAMAITACHI_DP_CHART_LIST
    else:
        infinitas_music_html = download_konami_song_data()
        infinitas_song_pack_json = download_song_pack_price_data()
        ksongs, k_sp_charts, k_dp_charts = download_kamaitachi_song_list()
    songs_by_pack = parse_html(infinitas_music_html)
    pack_info = parse_json(infinitas_song_pack_json)
    combined_kamaitachi_data = combine_kamaitachi_data(ksongs, k_sp_charts, k_dp_charts)
    song_difficulties_by_pack = {}
    for pack in songs_by_pack:
        pack_info[pack]["sublabel"] = songs_by_pack[pack]["PRODUCT_NAME_SUBLABEL"]
        if pack not in song_difficulties_by_pack:
            song_difficulties_by_pack[pack] = {}
        for song in songs_by_pack[pack]["SONGS"]:
            if song not in combined_kamaitachi_data:
                raise RuntimeError(f"Could not find {song} in kamaitachi data.")
            song_difficulties_by_pack[pack][song] = combined_kamaitachi_data[song]
    generate_and_write_html(song_difficulties_by_pack, pack_info)
    return


if __name__ == "__main__":
    main()
