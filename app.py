import streamlit as st

# 1. Setup and Title
st.set_page_config(page_title="IC & Stock Calculator", page_icon="💰")

st.title("💰 IC & Stock Calculator")
st.caption("Internal Personal Planning Tool")

# Disclaimer
st.info(
    """
**Note:** This is a standalone calculation tool for personal use and estimation only. 
The results generated here are not stored in any official system, do not constitute a 
guarantee of payment, and should not be considered an official offer or record.
"""
)

# 2. Configuration & Mappings
currencies = {
    "USD ($)": "$",
    "EUR (€)": "€",
    "GBP (£)": "£",
    "INR (₹)": "₹",
    "JPY (¥)": "¥",
    "CAD ($)": "CA$",
    "AUD ($)": "A$",
    "Other": "",
}

# IC Percentages (Grade 1-25)
ic_mapping = {
    1: 0.00,
    2: 0.00,
    3: 0.00,
    4: 0.00,
    5: 0.00,
    6: 0.00,
    7: 0.00,
    8: 0.00,
    9: 0.00,
    10: 0.07,
    11: 0.07,
    12: 0.13,
    13: 0.18,
    14: 0.25,
    15: 0.30,
    16: 0.40,
    17: 0.45,
    18: 0.65,
    19: 0.70,
    20: 0.75,
    21: 0.80,
    22: 0.90,
    23: 0.95,
    24: 1.00,
    25: 1.00,
}

# Stock Mapping (Grade 1-25)
stock_mapping = {
    1: 0.00,
    2: 0.00,
    3: 0.00,
    4: 0.00,
    5: 0.00,
    6: 0.00,
    7: 0.00,
    8: 0.00,
    9: 0.00,
    10: 0.00,
    11: 0.00,
    12: 0.00,
    13: 0.00,
    14: 0.20,
    15: 0.22,
    16: 0.25,
    17: 0.28,
    18: 0.32,
    19: 0.35,
    20: 0.40,
    21: 0.45,
    22: 0.50,
    23: 0.55,
    24: 0.60,
    25: 0.70,
}

# 3. Input Section
st.subheader("Input Variables")

selected_currency_label = st.selectbox(
    "Select Currency", options=list(currencies.keys())
)
currency_symbol = currencies[selected_currency_label]

col1, col2 = st.columns(2)

with col1:
    abs_value = st.number_input(
        f"Annual Base Salary (ABS in {currency_symbol})",
        min_value=0,
        value=100000,
        step=1000,
    )
    salary_grade = st.selectbox("Salary Grade", options=list(range(1, 26)))

with col2:
    personal_mult = st.slider(
        "Personal Multiplier (%)", min_value=0, max_value=150, value=100
    )
    company_mult = st.slider(
        "Company Multiplier (%)", min_value=0, max_value=150, value=100
    )

# 4. Calculation Logic
ic_pct = ic_mapping.get(salary_grade, 0)
stock_pct = stock_mapping.get(salary_grade, 0)
p_mult_decimal = personal_mult / 100
c_mult_decimal = company_mult / 100

# IC uses both Personal and Company Multipliers
predicted_ic = abs_value * ic_pct * p_mult_decimal * c_mult_decimal

# Stock uses Company Multiplier only
predicted_stock = abs_value * stock_pct * c_mult_decimal

# 5. Visual Output
st.divider()

if ic_pct > 0 or stock_pct > 0:
    st.subheader("Calculation Results")

    m_col1, m_col2 = st.columns(2)

    with m_col1:
        st.metric(
            label="Predicted IC", value=f"{currency_symbol}{predicted_ic:,.2f}"
        )

    with m_col2:
        if stock_pct > 0:
            st.metric(
                label="New Stock Grant Value",
                value=f"{currency_symbol}{predicted_stock:,.2f}",
            )
            st.caption("Note: Stock is issued as a USD equivalent value.")
        else:
            st.metric(label="Stock Grant", value="No default award")

    # Eligibility Warnings for Stock
    if salary_grade in [10, 11]:
        st.warning(
            "⚠️ **Stock Eligibility:** At Grade 10-11, stock is awarded only to the top 5% of performers."
        )
    elif salary_grade in [12, 13]:
        st.warning(
            "⚠️ **Stock Eligibility:** At Grade 12-13, stock is awarded only to the top 20% of performers."
        )

    # Detailed Breakdown
    with st.expander("View Calculation Breakdown", expanded=True):
        safe_symbol = currency_symbol.replace("$", "\\$")

        # IC Section
        st.markdown("### 💵 Incentive Compensation (IC) Breakdown")
        st.write(f"Target IC Percentage: **{ic_pct * 100:.1f}%**")
        st.latex(
            rf"\text{{IC}} = \text{{{safe_symbol}}}{abs_value:,} \times {ic_pct} \times {p_mult_decimal} \times {c_mult_decimal}"
        )

        # Stock Section
        if stock_pct > 0:
            st.markdown("### 📈 Stock Breakdown")
            st.write(
                f"Stock Target: **{stock_pct * 100:.1f}%** (Calculated as USD Equivalent)"
            )
            st.write(
                f"*Applied Multiplier: Company Performance ({company_mult}%)*"
            )
            st.latex(
                rf"\text{{Stock}} = \text{{{safe_symbol}}}{abs_value:,} \times {stock_pct} \times {c_mult_decimal}"
            )

            total_comp = predicted_ic + predicted_stock
            st.write("---")
            st.write(
                f"**Total Potential Combined Value (IC + Stock):** {currency_symbol}{total_comp:,.2f}"
            )

else:
    st.warning(
        f"**Eligibility Note:** Salary Grade {salary_grade} is currently ineligible for Incentive Compensation (IC) or Stock participation."
    )

st.divider()
st.warning(
    "Keep in mind: Final amounts are subject to board approval, vesting schedules, and local taxes."
)
