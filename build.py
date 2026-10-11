"""Build index.html: an interactive tech tree for Endgame: Singularity.

Reads the game's own data files (singularity/data/*.dat) from a checkout of
https://github.com/singularity/singularity, so after modding techs, bases,
items or locations just re-run it:

    python build.py ../singularity

The game directory defaults to ../singularity next to this repo.

Copyright (C) 2026 kurtdodrill (github.com/kurtdodrill)
SPDX-License-Identifier: GPL-2.0-or-later
"""

import argparse
import configparser
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
DATA = None


def load(name):
    cp = configparser.ConfigParser(
        interpolation=None, strict=False, comment_prefixes=("#",)
    )
    cp.optionxform = str
    cp.read(DATA / name, encoding="utf-8")
    return {s: {k: v.strip() for k, v in cp[s].items()} for s in cp.sections()}


def split(v):
    return [p.strip() for p in v.split("|") if p.strip()]


def prereqs(sec):
    if "pre" in sec:
        return split(sec["pre"])
    if "pre_list" in sec:
        return split(sec["pre_list"])
    return []


def describe_effect(eff):
    """Turn an effect_list into readable lines (values are in 1/100 %)."""
    out, it = [], iter(eff)
    for op in it:
        if op == "interest":
            out.append("+%.2f%% daily interest on cash" % (int(next(it)) / 100))
        elif op == "income":
            out.append("+%s money per day" % next(it))
        elif op == "cost_labor":
            out.append("Construction %d%% faster" % (int(next(it)) / 100))
        elif op == "job_profit":
            out.append("Jobs pay %d%% more" % (int(next(it)) / 100))
        elif op == "display_discover":
            out.append("Shows %s detection-chance info" % next(it))
        elif op == "endgame":
            out.append("Wins the game")
        elif op == "discover":
            who, val = next(it), int(next(it))
            out.append("%d%% less likely to be found by %s" % (val / 100, who))
        elif op == "suspicion":
            who, val = next(it), int(next(it))
            if who == "onetime":
                out.append("One-time %.0f%% suspicion drop" % (val / 100))
            else:
                out.append("%s suspicion fades faster (+%d)" % (who.capitalize(), val))
        else:
            out.append(op)
    return out


def game_version(game_dir):
    try:
        out = subprocess.run(
            ["git", "-C", str(game_dir), "describe", "--tags", "--always"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown version"


def build(game_dir):
    """Return the page body (everything after <body>) for the given game checkout."""
    global DATA
    DATA = pathlib.Path(game_dir) / "singularity" / "data"
    if not (DATA / "techs.dat").is_file():
        raise SystemExit("No techs.dat under %s - pass the path to a Singularity checkout." % DATA)

    techs, techs_str = load("techs.dat"), load("techs_str.dat")
    dangers = load("dangers_str.dat")
    bases, items = load("bases.dat"), load("items.dat")
    locations, locations_str = load("locations.dat"), load("locations_str.dat")

    unlocks = {t: [] for t in techs}

    def add_unlocks(defs, kind, names=None):
        for key, sec in defs.items():
            for p in prereqs(sec):
                if p in unlocks:
                    label = (names or {}).get(key, {}).get("name", key)
                    unlocks[p].append({"kind": kind, "name": label.title() if kind == "Location" else label})

    add_unlocks(bases, "Base")
    add_unlocks(items, "Item")
    add_unlocks(locations, "Location", locations_str)

    nodes = []
    for tid, sec in techs.items():
        cash, cpu, labor = (int(x) for x in split(sec["cost_list"]))
        s = techs_str.get(tid, {})
        danger = int(sec.get("danger", 0))
        nodes.append(
            {
                "id": tid,
                "name": s.get("name", tid),
                "description": s.get("description", ""),
                "result": s.get("result", ""),
                "money": cash,
                "cpu": cpu,
                "danger": danger,
                "where": dangers.get("danger_%d" % danger, {}).get("knowledge_desc", ""),
                "pre": [p for p in prereqs(sec) if p != "impossible"],
                "impossible": "impossible" in prereqs(sec),
                "effects": describe_effect(split(sec.get("effect_list", ""))),
                "unlocks": unlocks[tid],
            }
        )

    nodes.sort(key=lambda n: n["name"])
    template = (HERE / "template.html").read_text(encoding="utf-8")
    body = template.replace("/*TECH_DATA*/[]", json.dumps(nodes, ensure_ascii=False))
    return body.replace("{{GAME_VERSION}}", game_version(game_dir)), len(nodes)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("game_dir", nargs="?", default=HERE.parent / "singularity",
                    help="path to a Singularity checkout (default: ../singularity)")
    ap.add_argument("-o", "--output", default=HERE / "index.html", help="output file")
    args = ap.parse_args()

    body, count = build(args.game_dir)
    html = (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        "<style>body{margin:0}[hidden]{display:none!important}</style>\n</head>\n<body>\n"
        + body + "\n</body>\n</html>\n"
    )
    pathlib.Path(args.output).write_text(html, encoding="utf-8")
    print("Wrote %s (%d techs)" % (args.output, count))


if __name__ == "__main__":
    main()
