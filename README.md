# cloudVis

Visualize SYNOP cloud observations over Argentina in Google Colab.

## Quick start (Google Colab)

1. Upload or open [`notebooks/argentina_synop_cloud_retrieval.ipynb`](notebooks/argentina_synop_cloud_retrieval.ipynb) in [Google Colab](https://colab.research.google.com/).
2. Run all cells.
3. Adjust `START_UTC` / `END_UTC` in the configuration cell.

The notebook downloads Argentina SYNOP data from [OGIMET](http://www.ogimet.com/) and extracts **cloud base height** from SYNOP Section 3 groups `8NChh`:

| Field | Meaning | Units |
|-------|---------|-------|
| `cloud_base_hh` | Height code from group `8NChh` | hundreds of feet |
| `cloud_base_ft` | `hh × 100` | feet |
| `cloud_base_m` | Derived from feet | meters |

Cloud base is parsed from raw SYNOP bulletins. OGIMET decoded hourly tables are only used as a fallback when no Section 3 cloud layers are present.

Station map coordinates are parsed directly from OGIMET `Lat=DD-MM-SS` / `Lon=DDD-MM-SS` metadata. The `atmofetch.stations_ogimet()` helper mis-parses these strings and can place stations tens of km off (sea / neighboring countries).

## Data sources

- **OGIMET** (`state=Argen`, WMO block `87xxx`) — free raw SYNOP bulletins
- **atmofetch** — Python helper for decoded hourly SYNOP + station coordinates

## Roadmap

- [x] Basic SYNOP retrieval for Argentina
- [x] Correct station coordinates from OGIMET DMS metadata
- [x] Time selector (default: latest available UTC hour)
- [x] Spatial interpolation (`contourf`) clipped to Argentina
- [ ] Kriging / finer grid options
