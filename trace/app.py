import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from data_loader import load_all

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="TRACE", layout="wide", page_icon="📡")

st.title("📡 TRACE")
st.subheader("Trending & RF Analysis for Cyclotron Engineering")
st.caption("HCY0110 — The Christie NHS Foundation Trust")

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_all()

with st.spinner("Loading clinical and ISM data..."):
    clinical, ism = get_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controls")

    date_min = clinical["date"].min().date()
    date_max = clinical["date"].max().date()

    date_range = st.date_input(
        "Date range",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max,
    )

    show_ism = st.toggle("Show ISM maintenance events", value=True)

    st.divider()
    st.markdown("**Data summary**")
    st.markdown(f"Clinical snapshots: **{len(clinical)}**")
    st.markdown(f"ISM sessions: **{len(ism)}**")
    st.markdown(f"Date range: **{date_min}** → **{date_max}**")

# ── Filter by date ────────────────────────────────────────────────────────────
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = clinical["date"].min(), clinical["date"].max()

mask     = (clinical["date"] >= start) & (clinical["date"] <= end)
cl       = clinical[mask].copy()
ism_mask = (ism["date"] >= start) & (ism["date"] <= end)
ism_filt = ism[ism_mask].copy()

# ── Helper: add ISM markers to a figure ──────────────────────────────────────
def add_ism_markers(fig, ism_df, y_ref=0):
    if not show_ism:
        return
    for _, row in ism_df.iterrows():
        fig.add_vline(
            x=row["date"].timestamp() * 1000,
            line_dash="dash",
            line_color="rgba(255,200,0,0.4)",
            line_width=1,
        )

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ RF Power", "⚖️ Field Balance", "📏 Stem Positions", "🌡️ Thermal & Events"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — RF Power
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Forward & Reflected Power")

    fig_pwr = go.Figure()
    fig_pwr.add_trace(go.Scatter(
        x=cl["date"], y=cl["forward_power_1_mW"],
        name="Forward Power Ch1", mode="lines",
        line=dict(color="#7F77DD", width=1.5)
    ))
    fig_pwr.add_trace(go.Scatter(
        x=cl["date"], y=cl["reflected_power_1_mW"],
        name="Reflected Power Ch1", mode="lines",
        line=dict(color="#FF6B6B", width=1.5)
    ))
    add_ism_markers(fig_pwr, ism_filt)
    fig_pwr.update_layout(template="plotly_dark", height=350,
                          yaxis_title="Power", xaxis_title="Date",
                          legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_pwr, use_container_width=True)

    st.markdown("### Reflected Power Ratio (Ch1)")
    fig_ratio = go.Figure()
    fig_ratio.add_trace(go.Scatter(
        x=cl["date"], y=cl["reflected_ratio_1"],
        name="Reflected Ratio Ch1", mode="lines",
        line=dict(color="#FF9F43", width=1.5)
    ))
    add_ism_markers(fig_ratio, ism_filt)
    fig_ratio.update_layout(template="plotly_dark", height=300,
                             yaxis_title="Reflected / Forward",
                             xaxis_title="Date")
    st.plotly_chart(fig_ratio, use_container_width=True)

    st.markdown("### ASUM")
    fig_asum = go.Figure()
    fig_asum.add_trace(go.Scatter(
        x=cl["date"], y=cl["asum_V"],
        name="ASUM", mode="lines",
        line=dict(color="#00D2D3", width=1.5)
    ))
    add_ism_markers(fig_asum, ism_filt)
    fig_asum.update_layout(template="plotly_dark", height=300,
                            yaxis_title="V", xaxis_title="Date")
    st.plotly_chart(fig_asum, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Field Balance
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Dee Field Balance — Top")
    fig_top = go.Figure()
    colors = ["#7F77DD", "#00D2D3", "#FF6B6B", "#FF9F43"]
    for i, col in enumerate(["dee_balance_top_1_pct", "dee_balance_top_2_pct",
                               "dee_balance_top_3_pct", "dee_balance_top_4_pct"]):
        fig_top.add_trace(go.Scatter(
            x=cl["date"], y=cl[col],
            name=f"Dee Top {i+1}", mode="lines",
            line=dict(color=colors[i], width=1.5)
        ))
    add_ism_markers(fig_top, ism_filt)
    fig_top.add_hline(y=0, line_dash="dot", line_color="white", line_width=0.8)
    fig_top.update_layout(template="plotly_dark", height=350,
                           yaxis_title="Balance %", xaxis_title="Date",
                           legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("### Dee Field Balance — Bottom")
    fig_bot = go.Figure()
    for i, col in enumerate(["dee_balance_bot_1_pct", "dee_balance_bot_2_pct",
                               "dee_balance_bot_3_pct", "dee_balance_bot_4_pct"]):
        fig_bot.add_trace(go.Scatter(
            x=cl["date"], y=cl[col],
            name=f"Dee Bot {i+1}", mode="lines",
            line=dict(color=colors[i], width=1.5)
        ))
    add_ism_markers(fig_bot, ism_filt)
    fig_bot.add_hline(y=0, line_dash="dot", line_color="white", line_width=0.8)
    fig_bot.update_layout(template="plotly_dark", height=350,
                           yaxis_title="Balance %", xaxis_title="Date",
                           legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_bot, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Stem Positions
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Upper Stem Positions")
    fig_su = go.Figure()
    for i, col in enumerate(["stem_1_upper_mm", "stem_2_upper_mm",
                               "stem_3_upper_mm", "stem_4_upper_mm"]):
        fig_su.add_trace(go.Scatter(
            x=cl["date"], y=cl[col],
            name=f"Stem {i+1} Upper", mode="lines",
            line=dict(color=colors[i], width=1.5)
        ))
    add_ism_markers(fig_su, ism_filt)
    fig_su.update_layout(template="plotly_dark", height=350,
                          yaxis_title="Position (mm)", xaxis_title="Date",
                          legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_su, use_container_width=True)

    st.markdown("### Lower Stem Positions")
    fig_sl = go.Figure()
    for i, col in enumerate(["stem_1_lower_mm", "stem_2_lower_mm",
                               "stem_3_lower_mm", "stem_4_lower_mm"]):
        fig_sl.add_trace(go.Scatter(
            x=cl["date"], y=cl[col],
            name=f"Stem {i+1} Lower", mode="lines",
            line=dict(color=colors[i], width=1.5)
        ))
    add_ism_markers(fig_sl, ism_filt)
    fig_sl.update_layout(template="plotly_dark", height=350,
                          yaxis_title="Position (mm)", xaxis_title="Date",
                          legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_sl, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — Thermal & Events
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### RF Window & Coupling Loop Temperature")
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=cl["date"], y=cl["rf_window_temp_C"],
        name="RF Window Temp", mode="lines",
        line=dict(color="#FF6B6B", width=1.5)
    ))
    fig_temp.add_trace(go.Scatter(
        x=cl["date"], y=cl["coupling_loop_temp_C"],
        name="Coupling Loop Temp", mode="lines",
        line=dict(color="#FF9F43", width=1.5)
    ))
    add_ism_markers(fig_temp, ism_filt)
    fig_temp.update_layout(template="plotly_dark", height=300,
                            yaxis_title="°C", xaxis_title="Date",
                            legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_temp, use_container_width=True)

    st.divider()
    st.markdown("### RF Health Indicators (daily event rates)")
    st.caption("Slow drift signals — rising trends here precede acute faults")

    fig_health = go.Figure()
    fig_health.add_trace(go.Scatter(
        x=cl["date"], y=cl["high_reflected_pwr_count_daily"],
        name="High Reflected Power", mode="lines",
        line=dict(color="#FF6B6B", width=1.5)
    ))
    fig_health.add_trace(go.Scatter(
        x=cl["date"], y=cl["p_out_clip_count_daily"],
        name="P Out Clip", mode="lines",
        line=dict(color="#FF9F43", width=1.5)
    ))
    fig_health.add_trace(go.Scatter(
        x=cl["date"], y=cl["hom_reflected_count_daily"],
        name="HOM Reflected", mode="lines",
        line=dict(color="#FFC312", width=1.5)
    ))
    fig_health.add_trace(go.Scatter(
        x=cl["date"], y=cl["discharge_count_daily"],
        name="Discharge Events", mode="lines",
        line=dict(color="#A29BFE", width=1.5)
    ))
    fig_health.add_trace(go.Scatter(
        x=cl["date"], y=cl["ecur_count_daily"],
        name="Electron Current Events", mode="lines",
        line=dict(color="#00D2D3", width=1.5)
    ))
    add_ism_markers(fig_health, ism_filt)
    fig_health.update_layout(template="plotly_dark", height=350,
                              yaxis_title="Daily Event Count",
                              xaxis_title="Date",
                              legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_health, use_container_width=True)

    st.divider()
    st.markdown("### Trip & Fault Events (daily event rates)")
    st.caption("Acute events — these are the faults, not the precursors")

    fig_trips = go.Figure()
    fig_trips.add_trace(go.Scatter(
        x=cl["date"], y=cl["rf_off_trips_count_daily"],
        name="RF Off Trips", mode="lines",
        line=dict(color="#FF6B6B", width=1.5)
    ))
    fig_trips.add_trace(go.Scatter(
        x=cl["date"], y=cl["llrf_fault_count_daily"],
        name="LLRF Faults", mode="lines",
        line=dict(color="#FF9F43", width=1.5)
    ))
    fig_trips.add_trace(go.Scatter(
        x=cl["date"], y=cl["rf_not_reduced_count_daily"],
        name="RF Not Reduced", mode="lines",
        line=dict(color="#A29BFE", width=1.5)
    ))
    fig_trips.add_trace(go.Scatter(
        x=cl["date"], y=cl["il_en_rf_on_count_daily"],
        name="Interlock While RF On", mode="lines",
        line=dict(color="#00D2D3", width=1.5)
    ))
    fig_trips.add_trace(go.Scatter(
        x=cl["date"], y=cl["asum_deviation_count_daily"],
        name="ASUM Deviation", mode="lines",
        line=dict(color="#FFC312", width=1.5)
    ))
    add_ism_markers(fig_trips, ism_filt)
    fig_trips.update_layout(template="plotly_dark", height=350,
                             yaxis_title="Daily Event Count",
                             xaxis_title="Date",
                             legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_trips, use_container_width=True)