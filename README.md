# 📡 TRACE — Trending & RF Analysis for Cyclotron Engineering

TRACE is a locally-hosted engineering dashboard for trending historical operational data from Varian ProBeam / ProBeam360 proton therapy cyclotrons. It ingests daily clinical parameter logs and ion source maintenance (ISM) characterisation records to produce interactive time-series visualisations of RF system health across the full operational history of a site.

Built and maintained by a field service engineer at HCY0110 — The Christie NHS Foundation Trust, Manchester.

---

## The Problem It Solves

ProBeam cyclotrons generate hundreds of parameters per daily snapshot. The PCS provides real-time monitoring but no built-in longitudinal trending. Identifying slow drifts, correlating RF anomalies with maintenance events, or spotting patterns that only become visible over months of data requires either manual spreadsheet work or tools that don't exist out of the box.

TRACE fills that gap — turning years of operational logs into an interactive, queryable engineering picture.

---

## Current Capabilities

- **RF Power Trending** — forward and reflected power (both channels), reflected power ratio, and ASUM over the full operational history
- **Dee Field Balance** — all 8 Dee segments (Top 1–4, Bottom 1–4) plotted as continuous time series with a zero-balance reference line
- **Stem Positions** — upper and lower stem positions for all 4 stems, revealing tuning adjustments over time
- **Thermal & Event Monitoring** — RF window temperature, coupling loop temperature, and LLRF event counters (high reflected power, discharge events, ASUM deviation)
- **ISM Event Overlay** — ion source maintenance sessions marked as vertical markers across all charts, enabling before/after comparison of RF parameters following maintenance interventions
- **Date range filtering** — zoom into any time window across the full dataset
- **Fully local** — no data leaves the machine, no cloud dependency, runs on a MacBook in the equipment room if needed

---

## Roadmap

TRACE is in active development. Planned capabilities include:

- **Anomaly detection** — rolling statistical flagging of parameters drifting outside their historical envelope, surfaced as alerts rather than requiring manual inspection
- **Predictive indicators** — identifying leading signals that precede known fault modes (RF trips, vacuum events, ISM requirements)
- **Cross-parameter correlation** — quantifying relationships between RF parameters, thermal signatures, and ion source condition
- **Multi-site support** — architecture designed to support any ProBeam / ProBeam360 site with access to the standard clinical log format
- **Automated reporting** — pre-maintenance briefing reports generated from the latest trend data

---

## Who This Is For

Any field service engineer or applications engineer working on a Varian ProBeam or ProBeam360 site. The tool expects the standard `Daily Clinical` sheet format from the Varian OPC parameter history workbook and the standard ISM characterisation sheet format. No modification to the PCS or clinical systems is required.

---

## Data Requirements

TRACE requires two local data files (not included in the repository — clinical data stays on site):

- `HCY0110_cyclotron_parameter_history_vX.X.xlsm` — the OPC parameter history workbook containing the `Daily Clinical` sheet
- `HCY0110_cyclotron_characterization_vXX.xlsx` — the ISM characterisation workbook (one sheet per maintenance session)

Place both files in the `ism-scraper/` directory. Run the ISM scraper first to generate `ism_history.csv` before launching TRACE.

---

## Installation

```bash
# Clone the repo
git clone https://github.com/maddyd1/cyclotron-tools.git
cd cyclotron-tools

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install streamlit pandas plotly openpyxl python-dateutil

# Generate ISM history from characterisation workbook
python3 ism-scraper/scraper.py

# Launch TRACE
cd trace
streamlit run app.py
```

Or on macOS, double-click `trace/Start_TRACE.command` after the first install.

---

## Project Structure

```
cyclotron-tools/
├── ism-scraper/
│   ├── scraper.py              # ISM characterisation workbook parser
│   └── ism_history.csv         # Generated output (local only, gitignored)
└── trace/
    ├── data_loader.py          # Clinical log + ISM data ingestion layer
    ├── app.py                  # Streamlit dashboard
    └── Start_TRACE.command     # macOS double-click launcher
```

---

## Tech Stack

| Component | Library |
|---|---|
| Dashboard | Streamlit |
| Visualisation | Plotly |
| Data processing | pandas, NumPy |
| Excel parsing | openpyxl |
| Date parsing | python-dateutil |

---

## Author

Built by [Maddy](https://github.com/maddyd1) — field service engineer specialising in proton therapy cyclotron systems at The Christie NHS Foundation Trust, Manchester.

*Varian ProBeam / ProBeam360 — HCY0110*
