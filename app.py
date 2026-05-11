import json
from datetime import datetime

import pandas as pd
import streamlit as st


# ---------------------------
# Page setup (must be first)
# ---------------------------
st.set_page_config(
    page_title="IC & Stock Calculator",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ---------------------------
# Minimal styling to fix header overlap + keep things clean
# ---------------------------
st.markdown(
    """
    <style>
      /* Prevent header/title from sitting under Streamlit toolbar */
      .block-container { padding-top: 2.75rem; padding-bottom: 2rem; max-width: 900px; }

      /* Slightly reduce sidebar crowding */
      section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }

      /* Make captions a little calmer */
      .stCaption { opacity: 0.85; }

      /* Keep metrics aligned nicely */
      div[data-testid="stMetric"] { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
        padding: 12px 14px; border-radius: 12px; }

      /* Slightly soften warning/info boxes */
      div[data-testid="stAlert"] { border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------
# Configuration & Mappings (based on your original file)
# ---------------------------
CURRENCIES = {
    "USD ($)": "$",
    "EUR (€)": "€",
    "GBP (£)": "£",
    "INR (₹)": "₹",
    "JPY (¥)": "¥",
    "CAD (C$)": "C$",
    "AUD (A$)": "A$",
    "Other": "",
}

# IC Percentages (Grade 1-25)
IC_MAPPING = {
    1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00,
    6: 0.00, 7: 0.00, 8: 0.00, 9: 0.00,
    10: 0.07, 11: 0.07,
    12: 0.13, 13: 0.18, 14: 0.25, 15: 0.30,
    16: 0.40, 17: 0.45, 18: 0.65, 19: 0.70,
    20: 0.75, 21: 0.80, 22: 0.90, 23: 0.95,
    24: 1.00, 25: 1.00,
}

# Stock Mapping (Grade 1-25)
STOCK_MAPPING = {
    1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00,
    6: 0.00, 7: 0.00, 8: 0.00, 9: 0.00,
    10: 0.00, 11: 0.00,
    12: 0.00, 13: 0.00, 14: 0.18, 15: 0.25,
    16: 0.30, 17: 0.40, 18: 0.60, 19: 0.70,
    20: 0.85, 21: 0.95, 22: 1.20, 23: 1.40,
    24: 1.60, 25: 1.75,
}


# ---------------------------
# Helpers
# ---------------------------
def fmt_money(amount: float, symbol: str) -> str:
    return f"{symbol}{amount:,.0f}" if symbol else f"{amount:,.0f}"


def fmt_pct(p: float) -> str:
    return f"{p * 100:.0f}%"


# ---------------------------
# Header (simple + not cramped)
# ---------------------------
st.header("💰 IC & Stock Calculator")
st.caption("Internal personal planning tool (estimation only).")

st.info(
    "**Note:** This is a standalone calculation tool for personal use and estimation only. "
    "Results are not stored in any official system, do not guarantee payment, and are not an official offer or record.",
    icon="ℹ️",
)


# ---------------------------
# Sidebar inputs (clean + minimal)
# ---------------------------
with st.sidebar:
    st.subheader("Inputs")

    selected_currency_label = st.selectbox("Currency", list(CURRENCIES.keys()), index=2)
    currency_symbol = CURRENCIES[selected_currency_label]

    abs_value = st.number_input(
        "Annual Base Salary (ABS)",
        min_value=0,
        value=100000,
        step=1000,
    )

    # Keep close to original behavior, but broaden if you want:
    # Original looked like options ~ 8..16 in your file. [1](https://pmicloud-my.sharepoint.com/personal/rcohen5_pmintl_net/Documents/Microsoft%20Copilot%20Chat%20Files/app.txt)
    salary_grade = st.selectbox("Salary Grade", options=list(range(8, 18)), index=2)

    st.markdown("---")
    st.caption("Multipliers")

    personal_mult = st.slider("Personal Multiplier (%)", 0, 150, 100)
    company_mult = st.slider("Company Multiplier (%)", 0, 150, 100)

    st.markdown("---")
    export_enabled = st.toggle("Enable export (CSV/JSON)", value=False)


# ---------------------------
# Calculations (same logic as your original)
# ---------------------------
ic_pct = IC_MAPPING.get(int(salary_grade), 0.0)
stock_pct = STOCK_MAPPING.get(int(salary_grade), 0.0)

p_mult_decimal = personal_mult / 100.0
c_mult_decimal = company_mult / 100.0

# IC uses both multipliers
predicted_ic = abs_value * ic_pct * p_mult_decimal * c_mult_decimal

# Stock uses company multiplier only
predicted_stock = abs_value * stock_pct * c_mult_decimal

total = predicted_ic + predicted_stock

eligible = (ic_pct > 0) or (stock_pct > 0)


# ---------------------------
# Results (calm, uncluttered)
# ---------------------------
st.subheader("Results")

m1, m2, m3 = st.columns(3)
m1.metric("Estimated IC", fmt_money(predicted_ic, currency_symbol))
m2.metric("Estimated Stock", fmt_money(predicted_stock, currency_symbol))
m3.metric("Total", fmt_money(total, currency_symbol))

st.caption(
    f"Assumptions: Grade {salary_grade} · IC {fmt_pct(ic_pct)} · Stock {fmt_pct(stock_pct)} · "
    f"Personal {personal_mult}% · Company {company_mult}%"
)

st.markdown("")

# Eligibility messaging (as in your original)
if not eligible:
    st.warning(
        "**Eligibility note:** This salary grade is currently ineligible for Incentive Compensation (IC) or Stock "
        "participation based on the configured mapping.",
        icon="⚠️",
    )

# IMPORTANT: Bring back stock availability warning for SG 10–13 (your requirement)
# You specifically called out: not available to all for SG 10-13.
if int(salary_grade) in (10, 11, 12, 13) and stock_pct > 0:
    st.warning(
        "**Stock participation note (SG 10–13):** Stock eligibility is by exception in this salary grade.",
        icon="⚠️",
    )

st.warning(
    "Final amounts are subject to policy, board approval, vesting schedules, and local taxes.",
    icon="🧾",
)


# ---------------------------
# Optional: simple breakdown (not busy)
# ---------------------------
with st.expander("Show calculation breakdown", expanded=False):
    st.write("**IC** = ABS × IC% × Personal × Company")
    st.code(
        f"{abs_value:,.0f} × {ic_pct:.2f} × {p_mult_decimal:.2f} × {c_mult_decimal:.2f} = {predicted_ic:,.0f}",
        language="text",
    )
    st.write("**Stock** = ABS × Stock% × Company")
    st.code(
        f"{abs_value:,.0f} × {stock_pct:.2f} × {c_mult_decimal:.2f} = {predicted_stock:,.0f}",
        language="text",
    )


# ---------------------------
# Optional export (only if toggled)
# ---------------------------
if export_enabled:
    st.markdown("---")
    st.subheader("Export scenario")

    scenario = {
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "currency_label": selected_currency_label,
        "currency_symbol": currency_symbol,
        "annual_base_salary": abs_value,
        "salary_grade": int(salary_grade),
        "ic_pct": ic_pct,
        "stock_pct": stock_pct,
        "personal_multiplier_pct": int(personal_mult),
        "company_multiplier_pct": int(company_mult),
        "predicted_ic": predicted_ic,
        "predicted_stock": predicted_stock,
        "predicted_total": total,
    }

    export_df = pd.DataFrame([scenario])

    b1, b2 = st.columns(2)
    with b1:
        st.download_button(
            "⬇️ Download CSV",
            data=export_df.to_csv(index=False).encode("utf-8"),
            file_name="ic_stock_scenario.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with b2:
        st.download_button(
            "⬇️ Download JSON",
            data=json.dumps(scenario, indent=2).encode("utf-8"),
            file_name="ic_stock_scenario.json",
            mime="application/json",
            use_container_width=True,
        )
