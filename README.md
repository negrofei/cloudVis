# cloudVis

Visualize SYNOP cloud observations over Argentina in Google Colab.

## Quick start (Google Colab)

1. Upload or open [`notebooks/argentina_synop_cloud_retrieval.ipynb`](notebooks/argentina_synop_cloud_retrieval.ipynb) in [Google Colab](https://colab.research.google.com/).
2. Run all cells.
3. Adjust `START_UTC` / `END_UTC` in the configuration cell.

The notebook downloads Argentina SYNOP data from [OGIMET](http://www.ogimet.com/) and extracts **cloud base height**:

| Field | Meaning | Units |
|-------|---------|-------|
| `cloud_base_m` / `HKm` | Lowest cloud base height | meters / km |
| `cloud_base_ft` | Same value | feet (`m × 3.28084`) |

If OGIMET decoded tables are empty (common for the current day), the notebook automatically falls back to the raw SYNOP API.

## Data sources

- **OGIMET** (`state=Argen`, WMO block `87xxx`) — free raw SYNOP bulletins
- **atmofetch** — Python helper for decoded hourly SYNOP + station coordinates

## Roadmap

- [x] Basic SYNOP retrieval for Argentina
- [ ] Map plotting with consistent styling
- [ ] Spatial interpolation over Argentina territory
- [ ] Time slider / latest-observation mode
