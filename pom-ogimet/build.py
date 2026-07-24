#!/usr/bin/env python3
"""Build a self-contained static HTML map for Argentina SYNOP → AEROMET.

Run once (requires Python + requests), then share ``index.html`` with colleagues.
They only need a web browser — no Python or server required.

Usage:
    python build.py
    python build.py --hours 6
    python build.py --output /path/to/index.html
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

OGIMET_STATIONS_URL = "http://ogimet.com/cgi-bin/gsynres"
OGIMET_SYNOP_URL = "http://www.ogimet.com/cgi-bin/getsynop"
HERE = Path(__file__).resolve().parent


def _dms_to_decimal(deg: str, minutes: str, seconds: str | None, hemisphere: str) -> float:
    seconds = seconds or "0"
    value = int(deg) + int(minutes) / 60 + int(seconds) / 3600
    return -value if hemisphere in {"S", "W"} else value


def fetch_stations_argentina(country: str = "Argentina", date_query: date | None = None) -> list[dict]:
    """Fetch SYNOP station coordinates from OGIMET (same logic as cloudVis notebook)."""
    if date_query is None:
        date_query = date.today()

    url = (
        f"{OGIMET_STATIONS_URL}?lang=en&state={country.replace(' ', '+')}"
        f"&osum=no&fmt=html&ord=REV&ano={date_query.strftime('%Y')}"
        f"&mes={date_query.strftime('%m')}&day={date_query.strftime('%d')}"
        f"&hora=12&ndays=1&Send=send"
    )
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    html = response.text

    lat_re = re.compile(r"Lat=(\d+)-(\d+)(?:-(\d+))?([NS])")
    lon_re = re.compile(r"Lon=(\d+)-(\d+)(?:-(\d+))?([EW])")
    alt_re = re.compile(r"Alt=(\d+)")
    meta_re = re.compile(r"'(\d{5}) \(.*? - (.+?)\)'")

    records: list[dict] = []
    for chunk in html.split("Decoded synops since")[1:]:
        lat_m = lat_re.search(chunk)
        lon_m = lon_re.search(chunk)
        meta_m = meta_re.search(chunk)
        if not (lat_m and lon_m and meta_m):
            continue

        alt_m = alt_re.search(chunk)
        records.append(
            {
                "wmo_id": meta_m.group(1),
                "name": meta_m.group(2).strip(),
                "lat": round(_dms_to_decimal(*lat_m.groups()), 5),
                "lon": round(_dms_to_decimal(*lon_m.groups()), 5),
                "alt": int(alt_m.group(1)) if alt_m else None,
            }
        )

    return records


def _parse_ogimet_csv_line(line: str) -> dict | None:
    """Parse one OGIMET getsynop CSV row into a SYNOP record."""
    parts = line.split(",", 6)
    if len(parts) < 7:
        return None
    wmo_id, year, month, day, hour, minute, report = parts
    report = report.strip()
    if "NIL" in report or not report.startswith("AAXX"):
        return None
    return {
        "wmo_id": wmo_id,
        "year": int(year),
        "month": int(month),
        "day": int(day),
        "hour": int(hour),
        "minute": int(minute),
        "report": report,
    }


def fetch_synops_argentina(hours: int, station_ids: set[str]) -> dict[str, list[dict]]:
    """Download recent SYNOP bulletins for Argentina (one bulk OGIMET request)."""
    end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(hours=hours)

    params = {
        "begin": start.strftime("%Y%m%d%H%M"),
        "end": end.strftime("%Y%m%d%H%M"),
        "state": "Argen",
        "header": "yes",
        "lang": "eng",
    }
    response = requests.get(OGIMET_SYNOP_URL, params=params, timeout=180)
    response.raise_for_status()

    by_station: dict[str, list[dict]] = {sid: [] for sid in station_ids}
    for line in response.text.splitlines()[1:]:
        row = _parse_ogimet_csv_line(line)
        if row is None or row["wmo_id"] not in station_ids:
            continue
        by_station[row["wmo_id"]].append(
            {
                "year": row["year"],
                "month": row["month"],
                "day": row["day"],
                "hour": row["hour"],
                "minute": row["minute"],
                "report": row["report"],
            }
        )

    for sid in by_station:
        by_station[sid].sort(
            key=lambda r: (r["year"], r["month"], r["day"], r["hour"], r["minute"]),
            reverse=True,
        )
    return by_station


def build_html(
    stations: list[dict],
    default_hours: int,
    embed_hours: int,
    embedded_synops: dict[str, list[dict]],
    built_at_iso: str,
    auto_reload_page: bool,
    template_path: Path,
    decoder_path: Path,
) -> str:
    template = template_path.read_text(encoding="utf-8")
    decoder_js = decoder_path.read_text(encoding="utf-8")

    stations_json = json.dumps(stations, ensure_ascii=False)
    synops_json = json.dumps(embedded_synops, ensure_ascii=False)

    html = template.replace("/*__DECODER_JS__*/", decoder_js)
    html = html.replace("__STATIONS_JSON__", stations_json)
    html = html.replace("__EMBEDDED_SYNOPS_JSON__", synops_json)
    html = html.replace("__DEFAULT_HOURS__", str(default_hours))
    html = html.replace("__EMBED_HOURS__", str(embed_hours))
    html = html.replace("__BUILT_AT__", built_at_iso)
    html = html.replace("__STATION_COUNT__", str(len(stations)))
    html = html.replace("__AUTO_RELOAD_PAGE__", "true" if auto_reload_page else "false")
    return html


def main() -> None:
    parser = argparse.ArgumentParser(description="Build pom-ogimet static HTML")
    parser.add_argument("--hours", type=int, default=3, help="Default lookback hours in the UI slider")
    parser.add_argument(
        "--embed-hours",
        type=int,
        default=24,
        help="Hours of SYNOP data to embed in HTML (max lookback available offline)",
    )
    parser.add_argument("--auto-reload-page", action="store_true", help="Reload browser page every 2 min (for gh-pages)")
    parser.add_argument("--no-embed-synops", action="store_true", help="Skip embedding recent SYNOP data")
    parser.add_argument("--output", type=Path, default=HERE / "index.html")
    parser.add_argument("--template", type=Path, default=HERE / "template.html")
    parser.add_argument("--decoder", type=Path, default=HERE / "synop_aeromet.js")
    args = parser.parse_args()

    print("Fetching Argentina SYNOP stations from OGIMET...")
    stations = fetch_stations_argentina()
    print(f"  {len(stations)} stations")

    station_ids = {s["wmo_id"] for s in stations}
    embedded: dict[str, list[dict]] = {}
    if not args.no_embed_synops:
        print(f"Downloading SYNOP (últimas {args.embed_hours} h, Argentina) para embeber en HTML...")
        embedded = fetch_synops_argentina(args.embed_hours, station_ids)
        with_data = sum(1 for rows in embedded.values() if rows)
        print(f"  {with_data} estaciones con al menos un SYNOP embebido")

    built_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = build_html(
        stations,
        args.hours,
        args.embed_hours,
        embedded,
        built_at,
        args.auto_reload_page,
        args.template,
        args.decoder,
    )
    args.output.write_text(html, encoding="utf-8")
    print(f"Wrote {args.output} ({len(html) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
