import pandas as pd
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
BASE  = Path(__file__).parent.parent
CLINICAL_FILE = BASE / "ism-scraper" / "HCY0110_cyclotron_parameter_history_v1.4.xlsm"
ISM_FILE      = BASE / "ism-scraper" / "ism_history.csv"

# RF parameters to extract from the daily clinical log
RF_PARAMS = {
    "CYC:RF:LLRF:GET_ASUM":               "asum_V",
    "CYC:RF:LLRF:GET_FORWARD_POWER_1":    "forward_power_1_mW",
    "CYC:RF:LLRF:GET_REFLECTED_POWER_1":  "reflected_power_1_mW",
    "CYC:RF:LLRF:GET_FORWARD_POWER_2":    "forward_power_2_mW",
    "CYC:RF:LLRF:GET_REFLECTED_POWER_2":  "reflected_power_2_mW",
    "CYC:RF:D1UP:GET_BALANCE":            "dee_balance_top_1_pct",
    "CYC:RF:D2UP:GET_BALANCE":            "dee_balance_top_2_pct",
    "CYC:RF:D3UP:GET_BALANCE":            "dee_balance_top_3_pct",
    "CYC:RF:D4UP:GET_BALANCE":            "dee_balance_top_4_pct",
    "CYC:RF:D1LO:GET_BALANCE":            "dee_balance_bot_1_pct",
    "CYC:RF:D2LO:GET_BALANCE":            "dee_balance_bot_2_pct",
    "CYC:RF:D3LO:GET_BALANCE":            "dee_balance_bot_3_pct",
    "CYC:RF:D4LO:GET_BALANCE":            "dee_balance_bot_4_pct",
    "CYC:RF:S1O:GET_POSITION":            "stem_1_upper_mm",
    "CYC:RF:S2O:GET_POSITION":            "stem_2_upper_mm",
    "CYC:RF:S3O:GET_POSITION":            "stem_3_upper_mm",
    "CYC:RF:S4O:GET_POSITION":            "stem_4_upper_mm",
    "CYC:RF:S1U:GET_POSITION":            "stem_1_lower_mm",
    "CYC:RF:S2U:GET_POSITION":            "stem_2_lower_mm",
    "CYC:RF:S3U:GET_POSITION":            "stem_3_lower_mm",
    "CYC:RF:S4U:GET_POSITION":            "stem_4_lower_mm",
    "CYC:AUX:RF_WINDOW:GET_TEMP":         "rf_window_temp_C",
    "CYC:AUX:WT_COUPLING_LOOP:GET_TEMP":  "coupling_loop_temp_C",
    "CYC:LLRF:PHASE_DIFF":                "phase_match",
    "CYC:LLRF:EVENT_PRFL:IS_ACT":         "high_reflected_pwr_count",
    "CYC:LLRF:EVENT_DISCHARGE:IS_ACT":    "discharge_count",
    "CYC:LLRF:EVENT_ASUM_OK:CNT":         "asum_deviation_count",
    "CYC:IS:PS:GET_CURRENT":              "arc_current_A",
    "CYC:1:GET_EXT_EFFICIENCY":           "extraction_efficiency_pct",
}

# ── Loaders ───────────────────────────────────────────────────────────────────
def load_clinical(filepath=CLINICAL_FILE):
    """Parse the daily clinical xlsm into a tidy dataframe."""
    print("Loading clinical log...")
    raw = pd.read_excel(filepath, sheet_name="Daily Clinical",
                        engine="openpyxl", header=None)

    # Row 0 = dates (col 7 onwards), Row 6 = PV names
    dates   = raw.iloc[0, 7:].values
    pv_names = raw.iloc[:, 6].values

    records = []
    for col_idx, date in enumerate(dates):
        if not isinstance(date, (pd.Timestamp,)) and not hasattr(date, 'year'):
            continue
        record = {"date": pd.Timestamp(date)}
        for row_idx, pv in enumerate(pv_names):
            if pv in RF_PARAMS:
                try:
                    val = raw.iloc[row_idx, col_idx + 7]
                    record[RF_PARAMS[pv]] = pd.to_numeric(val, errors="coerce")
                except Exception:
                    record[RF_PARAMS[pv]] = None
        records.append(record)

    df = pd.DataFrame(records)
    df = df.sort_values("date").reset_index(drop=True)

    # Derived: reflected power ratio
    df["reflected_ratio_1"] = df["reflected_power_1_mW"] / df["forward_power_1_mW"].replace(0, float("nan"))
    df["reflected_ratio_2"] = df["reflected_power_2_mW"] / df["forward_power_2_mW"].replace(0, float("nan"))

    print(f"Clinical log: {len(df)} snapshots, {df['date'].min().date()} → {df['date'].max().date()}")
    return df


def load_ism(filepath=ISM_FILE):
    """Load the scraped ISM session history."""
    print("Loading ISM history...")
    df = pd.read_csv(filepath, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    print(f"ISM history: {len(df)} sessions, {df['date'].min().date()} → {df['date'].max().date()}")
    return df


def load_all():
    """Load and return both datasets."""
    clinical = load_clinical()
    ism      = load_ism()
    return clinical, ism


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    clinical, ism = load_all()
    print("\nClinical columns:", clinical.columns.tolist())
    print("\nSample clinical data:")
    print(clinical[["date", "asum_V", "forward_power_1_mW", 
                     "dee_balance_bot_3_pct", "arc_current_A"]].head(10).to_string())
    print("\nSample ISM data:")
    print(ism[["date", "chimney_angle_deg", "arc_current_mA", 
               "extraction_efficiency"]].head(10).to_string())