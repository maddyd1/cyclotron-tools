import pandas as pd
from pathlib import Path
from dateutil import parser as dateparser

# ── Config ────────────────────────────────────────────────────────────────────
ISM_FILE = Path("ism-scraper/HCY0110_cyclotron_characterization_v06.xlsx")
OUTPUT_FILE = Path("ism-scraper/ism_history.csv")

SKIP_SHEETS = {"Sheet1", "Sheet4", "training",
               "BC post CYC maint template",
               "BC post ISM maint template"}

# Label fragments to search for in column A (case-insensitive, partial match)
# Each field lists multiple possible label variants across template versions
LABEL_MAP = {
    "chimney_angle_deg":     ["chimney angle"],
    "h2_flow_sccm":          ["h2 flow"],
    "arc_current_mA":        ["arc current for max", "is arc current"],
    "max_beam_current_nA":   ["max beam current used", "max beam current for cli"],
    "ps1_position_mm":       ["position ps1"],
    "ps1_width_mm":          ["slit width ps1", "width ps1"],
    "ps2_position_mm":       ["position ps2"],
    "ps2_width_mm":          ["slit width ps2", "width ps2"],
    "asum_V":                ["asum"],
    "forward_power_kW":      ["p forward", "forward power"],
    "magnet_current_A":      ["magnet current"],
    "itr_amplitude_G":       ["inner trim rods amplitude", "inner trim rod amplitude"],
    "itr_phase_deg":         ["inner trim rods phase", "inner trim rod phase"],
    "itr_offset_G":          ["inner trim rods offset", "inner trim rod offset"],
    "otr_amplitude_G":       ["outer trim rods amplitude", "outer trim rod amplitude"],
    "otr_phase_deg":         ["outer trim rods phase", "outer trim rod phase"],
    "otr_offset_G":          ["outer trim rods offset", "outer trim rod offset"],
    "beam_x_mm":             ["m1:10 - x", "m1:10-x"],
    "beam_y_mm":             ["m1:10 - y", "m1:10-y"],
    "monpic_x_mm":           ["monpic - x", "monpic-x"],
    "monpic_y_mm":           ["monpic - y", "monpic-y"],
    "ps_beam_current_nA":    ["max beam current ps1", "beam current ps1 + ps2"],
    "wincc_beam_current_nA": ["wincc", "max beam current shown"],
    "extraction_efficiency": ["extraction efficiency", "efficiency %", "efficiency%"],
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def parse_date_from_sheet_name(name):
    clean = name.split("(")[0].strip()
    clean = clean.replace("post op", "").replace("CYC PMI", "").strip()
    clean = clean.replace("- ", "-").replace(" -", "-").strip()
    try:
        return dateparser.parse(clean, dayfirst=True)
    except Exception:
        return None

def find_value_by_label(df, label_fragments):
    """Search col A for a label, return numeric value from col B on same row."""
    col_a = df.iloc[:, 0].astype(str).str.strip().str.lower()
    for fragment in label_fragments:
        matches = col_a[col_a.str.contains(fragment.lower(), na=False)]
        for row_idx in matches.index:
            try:
                val = df.iloc[row_idx, 1]
                if pd.notna(val) and str(val).strip() not in ("", "hh:mm", "MM/DD/YYYY"):
                    return float(val)
            except (ValueError, TypeError):
                continue
    return None

# ── Scraper ───────────────────────────────────────────────────────────────────
def scrape_ism_workbook(filepath):
    print(f"Loading {filepath}...")
    wb = pd.read_excel(filepath, sheet_name=None, engine="openpyxl", header=None)

    records = []
    skipped = []

    for sheet_name, df in wb.items():
        if sheet_name.strip() in SKIP_SHEETS:
            skipped.append(sheet_name)
            continue

        date = parse_date_from_sheet_name(sheet_name)
        record = {"sheet": sheet_name, "date": date}

        for field, labels in LABEL_MAP.items():
            record[field] = find_value_by_label(df, labels)

        records.append(record)

    print(f"Skipped {len(skipped)} template/blank sheets: {skipped}")
    return pd.DataFrame(records)

if __name__ == "__main__":
    df = scrape_ism_workbook(ISM_FILE)
    df = df.sort_values("date").reset_index(drop=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nDone — {len(df)} sessions scraped")
    print(f"Date range: {df['date'].min()} → {df['date'].max()}")
    print(f"Missing dates: {df['date'].isna().sum()}")
    print()
    print(df[["sheet", "date", "chimney_angle_deg", "arc_current_mA", "extraction_efficiency"]].to_string())