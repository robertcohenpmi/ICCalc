import streamlit as st

# 1. Setup and Title
st.set_page_config(page_title="IC & Stock Calculator", page_icon="💰")

st.title("💰 IC & Stock Calculator")
st.caption("Internal Personal Planning Tool")

# Disclaimer
st.info("""
**Note:** This is a standalone calculation tool for personal use and estimation only. 
The results generated here are not stored in any official system, do not constitute a 
guarantee of payment, and should not be considered an official offer or record.
""")

# 2. Configuration & Mappings
# Currency Mapping
currencies = {
    "USD ($)": "$",
    "EUR (€)": "€",
    "GBP (£)": "£",
    "INR (₹)": "₹",
    "JPY (¥)": "¥",
    "CAD ($)": "CA$",
    "AUD ($)": "A$",
    "Other": ""
}

# Salary Grade Mapping (Grades 1-25)
grade_mapping = {
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
    25: 1.00
}

# 3. Input Section
st.subheader("Input Variables")

# Currency Dropdown
selected_currency_label = st.selectbox("Select Currency", options=list(currencies.keys()))
currency_symbol = currencies[selected_currency_label]

col1, col2 = st.columns(2)

with col1:
    abs_value = st.number_input(f"Annual Base Salary (ABS in {currency_symbol})", min_value=0, value=100000, step=1000)
    salary_grade = st.selectbox("Salary Grade", options=list(range(1, 26)))

with col2:
    personal_mult = st.slider("Personal Multiplier (%)", min_value=0, max_value=150, value=100)
    company_mult = st.slider("Company Multiplier (%)", min_value=0, max_value=150, value=100)

# 4. Calculation Logic
target_pct = grade_mapping.get(salary_grade, 0)
p_mult_decimal = personal_mult / 100
c_mult_decimal = company_mult / 100

predicted_bonus = abs_value * target_pct * p_mult_decimal * c_mult_decimal

# 5. Visual Output
st.divider()
st.subheader("Calculation Result")

# Display the main result with the dynamic currency symbol
st.metric(
    label="Predicted Bonus", 
    value=f"{currency_symbol}{predicted_bonus:,.2f}"
)

# Breakdown for transparency
with st.expander("View Calculation Breakdown"):
    st.write(f"**Base Salary:** {currency_symbol}{abs_value:,}")
    st.write(f"**Target Percentage (Grade {salary_grade}):** {target_pct * 100:.1f}%")
    st.write(f"**Personal Performance:** {personal_mult}%")
    st.write(f"**Company Performance:** {company_mult}%")
    
    # Using a raw string for LaTeX to handle the currency symbol safely
    st.latex(f"\\text{{Bonus}} = \\text{{{currency_symbol}}}{abs_value} \\times {target_pct} \\times {p_mult_decimal} \\times {c_mult_decimal}")

st.divider()
st.warning("Keep in mind: Final bonus amounts are usually subject to tax and local withholdings.")
