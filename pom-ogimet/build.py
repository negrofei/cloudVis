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
from datetime import date
from pathlib import Path

import requests

OGIMET_STATIONS_URL = "http://ogimet.com/cgi-bin/gsynres"
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


def build_html(stations: list[dict], default_hours: int, template_path: Path, decoder_path: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    decoder_js = decoder_path.read_text(encoding="utf-8")

    stations_json = json.dumps(stations, ensure_ascii=False)
    built_at = date.today().isoformat()

    html = template.replace("/*__DECODER_JS__*/", decoder_js)
    html = html.replace("__STATIONS_JSON__", stations_json)
    html = html.replace("__DEFAULT_HOURS__", str(default_hours))
    html = html.replace("__BUILT_AT__", built_at)
    html = html.replace("__STATION_COUNT__", str(len(stations)))
    return html


def main() -> None:
    parser = argparse.ArgumentParser(description="Build pom-ogimet static HTML")
    parser.add_argument("--hours", type=int, default=3, help="Default SYNOP lookback hours")
    parser.add_argument("--output", type=Path, default=HERE / "index.html")
    parser.add_argument("--template", type=Path, default=HERE / "template.html")
    parser.add_argument("--decoder", type=Path, default=HERE / "synop_aeromet.js")
    args = parser.parse_args()

    print("Fetching Argentina SYNOP stations from OGIMET...")
    stations = fetch_stations_argentina()
    print(f"  {len(stations)} stations")

    html = build_html(stations, args.hours, args.template, args.decoder)
    args.output.write_text(html, encoding="utf-8")
    print(f"Wrote {args.output} ({len(html) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
