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
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------
# Styling (CSS)
# ---------------------------
CUSTOM_CSS = """
<style>
/* Reduce top padding a bit */
.block-container { padding-top: 1.25rem; }

/* App header styling */
.app-title {
    font-size: 2.0rem;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 0.25rem;
}
.app-subtitle {
    color: rgba(255,255,255,0.70);
    margin-top: 0.15rem;
}

/* Card container */
.card {
    border-radius: 18px;
    padding: 18px 18px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 10px 25px rgba(0,0,0,0.18);
}
.card h4 {
    margin: 0 0 6px 0;
    font-size: 0.95rem;
    color: rgba(255,255,255,0.75);
    font-weight: 650;
}
.card .value {
    font-size: 1.65rem;
    font-weight: 850;
    line-height: 1.1;
}
.card .hint {
    margin-top: 6px;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.65);
}

/* Small pill badges */
.pill {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 650;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.12);
    margin-right: 8px;
    margin-top: 4px;
}

/* Divider line */
.hr {
    height: 1px;
    background: rgba(255,255,255,0.10);
    margin: 10px 0 4px 0;
}

/* Footer */
.footer {
    margin-top: 20px;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.55);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------
# Core configuration/mappings
# (keeps your original logic)
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
    10: 0.80, 11: 0.80,
    12: 0.10, 13: 0.18, 14: 0.18, 15: 0.25,
    16: 0.30, 17: 0.40, 18: 0.60, 19: 0.70,
    20: 0.85, 21: 0.95, 22: 1.20, 23: 1.40,
    24: 1.60, 25: 1.75,
}


# ---------------------------
# Helpers
# ---------------------------

def fmt_money(amount: float, symbol: str) -> str:
    """Format monetary values with thousands separators."""
    try:
        return f"{symbol}{amount:,.0f}"
    except Exception:
        return f"{symbol}{amount}"


def fmt_pct(p: float) -> str:
    """Format percent (e.g., 0.25 -> 25%)."""
    return f"{p * 100:.0f}%"


def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


# ---------------------------
# Header
# ---------------------------
left, right = st.columns([0.72, 0.28], vertical_alignment="top")

with left:
    st.markdown('<div class="app-title">💰 IC & Stock Calculator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Internal personal planning tool · clean estimates with transparent assumptions</div>',
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        '<div class="card">'
        '<h4>Quick tips</h4>'
        '<div class="hint">Use the sidebar to change assumptions. Export a scenario for sharing.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

st.info(
    "**Note:** This is a standalone calculation tool for personal use and estimation only. "
    "Results are not stored in any official system, do not guarantee payment, and are not an official offer or record.",
    icon="ℹ️",
)

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)


# ---------------------------
# Sidebar inputs (professional UX)
# ---------------------------
with st.sidebar:
    st.markdown("## ⚙️ Inputs")
    st.caption("Adjust assumptions to calculate estimated IC and Stock values.")

    selected_currency_label = st.selectbox("Currency", options=list(CURRENCIES.keys()), index=2)
    currency_symbol = CURRENCIES[selected_currency_label]

    abs_value = st.number_input(
        f"Annual Base Salary (ABS)",
        min_value=0,
        value=100000,
        step=1000,
        help="Annual Base Salary used as the base for IC/Stock calculation.",
    )

    # Your original app restricted grades to 8..16-ish; here we allow 1..25.
    # If you want to force only 8..17, change list(range(1, 26)) to list(range(8, 18)).
    salary_grade = st.selectbox(
        "Salary Grade",
        options=list(range(1, 26)),
        index=9,  # default = grade 10
        help="Grade determines the IC % and Stock % mappings.",
    )

    st.markdown("### Multipliers")
    personal_mult = st.slider(
        "Personal Multiplier (%)",
        min_value=0,
        max_value=150,
        value=100,
        help="Applied to IC only (e.g., 100 = 1.0x).",
    )
    company_mult = st.slider(
        "Company Multiplier (%)",
        min_value=0,
        max_value=150,
        value=100,
        help="Applied to IC and Stock (e.g., 100 = 1.0x).",
    )

    st.markdown("### Optional controls")
    show_breakdown = st.toggle("Show calculation breakdown", value=True)
    show_chart = st.toggle("Show visual comparison chart", value=True)

    st.markdown("---")
    st.caption("Made for clarity: transparent assumptions, readable outputs, easy export.")


# ---------------------------
# Calculation logic (same as your original intent)
# IC uses both personal & company multipliers; Stock uses company only.
# ---------------------------
ic_pct = IC_MAPPING.get(int(salary_grade), 0.0)
stock_pct = STOCK_MAPPING.get(int(salary_grade), 0.0)

p_mult_decimal = personal_mult / 100.0
c_mult_decimal = company_mult / 100.0

predicted_ic = abs_value * ic_pct * p_mult_decimal * c_mult_decimal
predicted_stock = abs_value * stock_pct * c_mult_decimal

eligible = (ic_pct > 0) or (stock_pct > 0)


# ---------------------------
# Main results area
# ---------------------------
topA, topB, topC, topD = st.columns([0.26, 0.26, 0.26, 0.22])

with topA:
    st.markdown(
        f"""
        <div class="card">
            <h4>Annual Base Salary</h4>
            <div class="value">{fmt_money(abs_value, currency_symbol)}</div>
            <div class="hint">Input ABS</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with topB:
    st.markdown(
        f"""
        <div class="card">
            <h4>Estimated IC</h4>
            <div class="value">{fmt_money(predicted_ic, currency_symbol)}</div>
            <div class="hint">Grade {salary_grade} · IC {fmt_pct(ic_pct)} · P {personal_mult}% · C {company_mult}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with topC:
    st.markdown(
        f"""
        <div class="card">
            <h4>Estimated Stock</h4>
            <div class="value">{fmt_money(predicted_stock, currency_symbol)}</div>
            <div class="hint">Grade {salary_grade} · Stock {fmt_pct(stock_pct)} · C {company_mult}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with topD:
    total = predicted_ic + predicted_stock
    st.markdown(
        f"""
        <div class="card">
            <h4>Total (IC + Stock)</h4>
            <div class="value">{fmt_money(total, currency_symbol)}</div>
            <div class="hint">Combined estimate</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")

# Eligibility messaging
if not eligible:
    st.warning(
        "⚠️ **Eligibility note:** This salary grade is currently ineligible for Incentive Compensation (IC) or Stock participation based on the configured mapping.",
        icon="⚠️",
    )
else:
    st.success("✅ **Calculated successfully.** Review the breakdown and assumptions below.", icon="✅")

st.warning(
    "Keep in mind: final amounts can be subject to board approval, vesting schedules, local policies, and taxes.",
    icon="🧾",
)

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)


# ---------------------------
# Breakdown + chart
# ---------------------------
mid_left, mid_right = st.columns([0.58, 0.42], vertical_alignment="top")

with mid_left:
    st.subheader("🔎 Assumptions & Breakdown")

    badges = [
        f'<span class="pill">Grade: {salary_grade}</span>',
        f'<span class="pill">IC%: {fmt_pct(ic_pct)}</span>',
        f'<span class="pill">Stock%: {fmt_pct(stock_pct)}</span>',
        f'<span class="pill">Personal mult: {personal_mult}%</span>',
        f'<span class="pill">Company mult: {company_mult}%</span>',
    ]
    st.markdown("".join(badges), unsafe_allow_html=True)

    if show_breakdown:
        with st.expander("Show calculation steps", expanded=True):
            st.markdown(
                f"""
**IC calculation (uses Personal + Company multipliers)**  
- IC % (by grade): **{fmt_pct(ic_pct)}**  
- Personal multiplier: **{personal_mult}%** → {p_mult_decimal:.2f}  
- Company multiplier: **{company_mult}%** → {c_mult_decimal:.2f}  
- Formula: `ABS × IC% × Personal × Company`  
- Result: **{fmt_money(abs_value, currency_symbol)} × {ic_pct:.2f} × {p_mult_decimal:.2f} × {c_mult_decimal:.2f} = {fmt_money(predicted_ic, currency_symbol)}**

**Stock calculation (uses Company multiplier only)**  
- Stock % (by grade): **{fmt_pct(stock_pct)}**  
- Company multiplier: **{company_mult}%** → {c_mult_decimal:.2f}  
- Formula: `ABS × Stock% × Company`  
- Result: **{fmt_money(abs_value, currency_symbol)} × {stock_pct:.2f} × {c_mult_decimal:.2f} = {fmt_money(predicted_stock, currency_symbol)}**
                """
            )

    st.markdown("### 📦 Export scenario")
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
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "⬇️ Download CSV",
            data=export_df.to_csv(index=False).encode("utf-8"),
            file_name="ic_stock_scenario.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "⬇️ Download JSON",
            data=json.dumps(scenario, indent=2).encode("utf-8"),
            file_name="ic_stock_scenario.json",
            mime="application/json",
            use_container_width=True,
        )

with mid_right:
    st.subheader("📊 Visual summary")

    chart_df = pd.DataFrame(
        {
            "Component": ["IC", "Stock"],
            "Amount": [predicted_ic, predicted_stock],
        }
    )

    if show_chart:
        # Try Altair for a nicer default vibe; fallback to st.bar_chart if unavailable
        try:
            import altair as alt

            bar = (
                alt.Chart(chart_df)
                .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
                .encode(
                    x=alt.X("Component:N", title=""),
                    y=alt.Y("Amount:Q", title=f"Amount ({selected_currency_label})"),
                    tooltip=["Component", alt.Tooltip("Amount:Q", format=",.0f")],
                    color=alt.Color("Component:N", legend=None),
                )
                .properties(height=260)
            )

            text = (
                alt.Chart(chart_df)
                .mark_text(dy=-10, fontSize=13, fontWeight="bold")
                .encode(
                    x="Component:N",
                    y="Amount:Q",
                    text=alt.Text("Amount:Q", format=",.0f"),
                )
            )

            st.altair_chart(bar + text, use_container_width=True)
        except Exception:
            st.bar_chart(chart_df.set_index("Component"))

    st.markdown(
        f"""
<div class="card">
  <h4>At a glance</h4>
  <div class="hint">
    This chart compares your calculated <b>IC</b> vs <b>Stock</b> estimates using the current mapping and multiplier assumptions.
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------
# Footer
# ---------------------------
st.markdown(
    """
<div class="footer">
  <b>Disclaimer:</b> Estimates are indicative only and may differ from actual outcomes due to policy, eligibility, performance calibration,
  vesting rules, tax treatment, rounding, and any applicable governance/approvals.
</div>
""",
    unsafe_allow_html=True,
)
``
