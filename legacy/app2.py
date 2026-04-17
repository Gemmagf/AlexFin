# app.py
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from PIL import Image
from idiomes import translations  # Traduccions per idiomes
from financial_projection import run_projection  # your external module


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Swiss Finance with Alex",
    layout="wide",
    page_icon="💼"
)

# --- STYLES ---
st.markdown("""
    <style>
        body {font-family: 'Lato', sans-serif;}
        .main {background-color: #fffaf9; color: #333333;}
        h1, h2, h3 {color: #d10000;}
        .stButton>button {background-color: #d10000; color: white; border-radius: 8px;}
        .stSlider>div>div>div>div {color: black;}
    </style>
""", unsafe_allow_html=True)

# --- LANGUAGE SELECTION ---
language = st.sidebar.selectbox("🌍 Choose Language", list(translations.keys()))
lang = translations[language]

# --- HEADER ---
st.title(lang["title"])
st.subheader(lang["subtitle"])
st.markdown("[📅 Book a free call](mailto:christian.bevilacqua@svag.ch)")

# Optional illustration
try:
    alex_img = Image.open("alex_doll.png")
    st.sidebar.image(alex_img, caption="Alex, your Swiss finance buddy", use_column_width=True)
except FileNotFoundError:
    st.sidebar.markdown("👤 Alex – your Swiss finance buddy")

# --- NAVIGATION TABS ---
tabs = st.tabs([lang["about_me"], lang["topics"], lang["planner_title"], lang["health"], lang["tax"]])

# ---------------- ABOUT ME ----------------
with tabs[0]:
    col1, col2 = st.columns([2,1])
    with col1:
        st.header(lang["about_me"])
        st.write(lang["about_me_text"])
        st.subheader(lang["what_i_help"])
        st.markdown(lang["what_i_help_text"])
    with col2:
        try:
            profile_img = Image.open("photo.png")
            st.image(profile_img, caption="Alex Bevilacqua")
        except FileNotFoundError:
            st.markdown("👤 Alex Bevilacqua")

# ---------------- TOPICS ----------------
import pandas as pd
import altair as alt
import streamlit as st

with tabs[1]:
    st.header(lang["topics"])

    def display_topic(title, summary, chart_caption, link):
        with st.expander(title, expanded=False):
            col1, col2 = st.columns([2,1])
            with col1:
                st.write(summary)
                st.markdown(f"🔗 [Read more]({link})")
            with col2:
                # Example chart
                data = pd.DataFrame({
                    "Year": [2024, 2025, 2026, 2027, 2028],
                    "Value": [100, 120, 150, 180, 210]
                })
                chart = alt.Chart(data).mark_line(point=True).encode(
                    x="Year",
                    y="Value"
                ).properties(title=chart_caption)
                st.altair_chart(chart, use_container_width=True)
            st.markdown("---")  # Separator

    for i in range(1, 11):
        display_topic(
            lang[f"topic_{i}_title"],
            lang[f"topic_{i}_summary"],
            lang[f"topic_{i}_chart_caption"],
            lang[f"topic_{i}_link"]
        )


# ---------------- PLANNER & SIMULATOR ----------------
# ---------------- PLANNER & SIMULATOR ----------------
with tabs[2]:
    st.header(lang["planner_title"])

    # --- USER INPUTS ---
    with st.expander(lang["planner_inputs"]["personal_info_expander"]):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input(
                lang["planner_inputs"]["age"], 18, 70, 30, key="age"
            )
            status = st.selectbox(
                lang["planner_inputs"]["relationship_status"],
                lang["planner_inputs"]["relationship_status_options"],
                key="status"
            )
            has_kids = st.radio(
                lang["planner_inputs"]["has_kids"],
                lang["planner_inputs"]["has_kids_options"],
                key="has_kids"
            )
        with col2:
            career_field = st.selectbox(
                lang["planner_inputs"]["career_field"],
                lang["planner_inputs"]["career_field_options"],
                key="career_field"
            )
            current_salary = st.number_input(
                lang["planner_inputs"]["current_salary"], 0, 300000, 7000, key="current_salary"
            )

    with st.expander(lang["planner_inputs"]["expenses_expander"]):
        col1, col2 = st.columns(2)
        with col1:
            rent = st.number_input(lang["planner_inputs"]["rent"], 0, 20000, 1500, key="rent")
            food = st.number_input(lang["planner_inputs"]["food"], 0, 10000, 600, key="food")
            transport = st.number_input(lang["planner_inputs"]["transport"], 0, 5000, 300, key="transport")
        with col2:
            entertainment = st.number_input(lang["planner_inputs"]["entertainment"], 0, 5000, 400, key="entertainment")
            healthcare = st.number_input(lang["planner_inputs"]["healthcare"], 0, 2000, 350, key="healthcare")
            misc = st.number_input(lang["planner_inputs"]["misc"], 0, 3000, 300, key="misc")

    total_expenses = rent + food + transport + entertainment + healthcare + misc
    st.markdown(f"**{lang['planner_inputs']['total_expenses_label']}:** `CHF {total_expenses:,}`")

    with st.expander(lang["planner_inputs"]["investment_expander"]):
        has_3a = st.radio(lang["planner_inputs"]["has_3a"], lang["planner_inputs"]["has_3a_options"], key="has_3a")
        has_etfs = st.radio(lang["planner_inputs"]["has_etfs"], lang["planner_inputs"]["has_etfs_options"], key="has_etfs")
        initial_savings = st.number_input(lang["planner_inputs"]["initial_savings"], 0, 1_000_000, 20000, key="initial_savings")
        retirement_age = st.slider(lang["planner_inputs"]["retirement_age"], 55, 70, 65, key="retirement_age")
        forecast_years = 25
        investment_return = 4.5

    # --- WHAT-IF SCENARIOS ---
    st.subheader("⚡ Escenaris What-If")
    sim_part_time = st.checkbox("Pare treballa 50%", key="sim_part_time")
    sim_market_shock = st.checkbox("Mercat estancat (-2%)", key="sim_market_shock")
    sim_private_school = st.checkbox("Universitat Estrangera", key="sim_private_school")

    # --- SIMULATION ---
    if st.button(lang["confirm_button"]):
     

        # Prepare input dict for external function
        form_data = {
            "currentAge": age,
            "retirementAge": retirement_age,
            "currentChildren": 0 if has_kids == "No" else 1,
            "futureChildren": 2,  # could make dynamic later
            "annualGrossSalary1": current_salary,
            "annualGrossSalary2": current_salary,  # placeholder
            "currentSavings": initial_savings,
            "monthlyContribution": 3000,  # placeholder
            "investmentReturn": investment_return,
            "monthlyLivingCost": total_expenses,
            "currentHousingCost": rent,
            "monthlyDaycareCost": 2500,
            "monthlySchoolActivityCost": 500,
            "yearlyTravelBudget": 6000,
            "universitySupport": 50000
        }

        # Run projection
        df, retirement_wealth, viable, early_retirement_age = run_projection(
            form_data, sim_part_time, sim_market_shock, sim_private_school
        )

        # Chart
        st.subheader("📈 Net Worth Projection")
        st.line_chart(df.set_index("age")["totalWealth"])

        # Cash Flow Table
        st.subheader("💰 Cash Flow Table")
        st.dataframe(df)

        # Recommendations
        st.markdown("### Recommendations")
        if viable:
            st.success(f"Pla viable! Jubilació anticipada possible als {early_retirement_age} anys")
        else:
            st.warning("Considereu augmentar els estalvis o reduir despeses.")
        st.write(f"Patrimoni a la jubilació: CHF {retirement_wealth:,.0f}")

# ---------------- HEALTH INSURANCE ----------------
with tabs[3]:
    st.header("🏥 Health Insurance Overview")
    st.markdown("Basic coverage, deductible, models and optional add-ons with example costs.")

    # Chart Example
    insurance_df = pd.DataFrame({
        "Layer": ["Basic", "Deductible", "Model", "Add-ons"],
        "Cost Impact": [1, 2, 1.5, 2.5]
    })
    st.altair_chart(
        alt.Chart(insurance_df).mark_bar().encode(
            x="Layer",
            y="Cost Impact",
            tooltip=["Layer", "Cost Impact"]
        ).properties(title="Insurance Plan Layers")
    )

# ---------------- TAX SIMULATOR ----------------
with tabs[4]:
    st.header("🧾 Tax Overview Simulator")
    permit = st.selectbox("Permit Type", ["B", "C", "Swiss"])
    canton = st.selectbox("Canton of Residence", ["Zurich", "Geneva", "Vaud", "Bern"])
    gross_income = st.number_input("💰 Annual Gross Income (CHF)", 10000, 500000, 85000, step=1000)
    pillar_3a = st.slider("💰 Pillar 3a Contribution (CHF)", 0, 7056, 3500)
    deductions = st.number_input("Other Deductions (CHF)", 0, 50000, 5000)

    taxable_income = gross_income - pillar_3a - deductions
    tax_rate = 0.11 if canton=="Zurich" else 0.13
    est_tax = int(taxable_income * tax_rate)

    st.success(f"✅ Net Taxable Income: CHF {int(taxable_income):,}")
    st.info(f"Estimated Tax: CHF {est_tax:,}")

st.markdown("---")
st.markdown("📚 DRAFT")
