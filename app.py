import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image
from idiomes import translations  
# --- Page Config ---
st.set_page_config(page_title="Swiss Finance with Alex", layout="wide")
st.markdown("""
    <style>
        body {font-family: 'Lato', sans-serif;}
        .main {background-color: #fffaf9; color: #333333;}
        h1, h2, h3 {color: #d10000;}
        .stButton>button {background-color: #d10000; color: white; border-radius: 8px;}
    </style>
""", unsafe_allow_html=True)

# --- Language Selection ---
language = st.sidebar.selectbox("🌍 Choose Language", list(translations.keys()))  # Language selection dropdown
lang = translations[language]  # Get the translations for the selected language

# --- Header ---
st.title(lang["title"])
st.subheader(lang["subtitle"])
st.markdown("[📅 Book a free call](mailto:christian.bevilacqua@svag.ch)")

# Optional illustration - Alex doll as guide
try:
    alex_img = Image.open("alex_doll.png")
    st.sidebar.image(alex_img, caption="Alex, your Swiss finance buddy", use_column_width=True)
except FileNotFoundError:
    st.sidebar.markdown("👤 Alex – your Swiss finance buddy")

# --- Navigation Tabs ---
tabs = st.tabs([lang["about_me"], lang["topics"],  lang["user"]])

# --- About Tab ---
with tabs[0]:
    st.header(lang["about_me"])
    st.write(lang["about_me_text"])
    st.subheader(lang["what_i_help"])
    st.markdown(lang["what_i_help_text"])

# --- Topics Tab ---
with tabs[1]:
    st.header(lang["topics"])

    def display_topic(title, summary, chart_caption, link):
        st.subheader(title)
        st.write(summary)
        data = pd.DataFrame({
            "Year": [2024, 2025, 2026, 2027, 2028],
            "Value": [100, 120, 150, 180, 210]
        })
        chart = alt.Chart(data).mark_line(point=True).encode(
            x="Year",
            y="Value"
        ).properties(title=chart_caption)
        st.altair_chart(chart, use_container_width=True)
        st.markdown(f"🔗 [Official Link]({link})")

    display_topic(
        lang["topic_1_title"],
        lang["topic_1_summary"],
        lang["topic_1_chart_caption"],
        lang["topic_1_link"]
    )

    display_topic(
        lang["topic_2_title"],
        lang["topic_2_summary"],
        lang["topic_2_chart_caption"],
        lang["topic_2_link"]
    )

    display_topic(
        lang["topic_3_title"],
        lang["topic_3_summary"],
        lang["topic_3_chart_caption"],
        lang["topic_3_link"]
    )

    display_topic(
        lang["topic_4_title"],
        lang["topic_4_summary"],
        lang["topic_4_chart_caption"],
        lang["topic_4_link"]
    )

    display_topic(
        lang["topic_5_title"],
        lang["topic_5_summary"],
        lang["topic_5_chart_caption"],
        lang["topic_5_link"]
    )

    display_topic(
        lang["topic_6_title"],
        lang["topic_6_summary"],
        lang["topic_6_chart_caption"],
        lang["topic_6_link"]
    )

    display_topic(
        lang["topic_7_title"],
        lang["topic_7_summary"],
        lang["topic_7_chart_caption"],
        lang["topic_7_link"]
    )

    display_topic(
        lang["topic_8_title"],
        lang["topic_8_summary"],
        lang["topic_8_chart_caption"],
        lang["topic_8_link"]
    )

    display_topic(
        lang["topic_9_title"],
        lang["topic_9_summary"],
        lang["topic_9_chart_caption"],
        lang["topic_9_link"]
    )

    display_topic(
        lang["topic_10_title"],
        lang["topic_10_summary"],
        lang["topic_10_chart_caption"],
        lang["topic_10_link"]
    )


# --- User Tab ---
with tabs[2]:
    st.header(lang["planner_title"])

    with st.expander(lang["planner_inputs"]["personal_info_expander"]):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input(lang["planner_inputs"]["age"], 18, 70, 30)
            status = st.selectbox(lang["planner_inputs"]["relationship_status"], lang["planner_inputs"]["relationship_status_options"])
            has_kids = st.radio(lang["planner_inputs"]["has_kids"], lang["planner_inputs"]["has_kids_options"])
            pets = st.multiselect(lang["planner_inputs"]["pets"], lang["planner_inputs"]["pets_options"])
        with col2:
            hobbies = st.multiselect(lang["planner_inputs"]["hobbies"], lang["planner_inputs"]["hobbies_options"])
            wants_to_travel = st.radio(lang["planner_inputs"]["wants_to_travel"], lang["planner_inputs"]["wants_to_travel_options"])
            career_field = st.selectbox(lang["planner_inputs"]["career_field"], lang["planner_inputs"]["career_field_options"])
            current_salary = st.number_input(lang["planner_inputs"]["current_salary"], 0, 300000, 7000)

    with st.expander(lang["planner_inputs"]["expenses_expander"]):
        col1, col2 = st.columns(2)
        with col1:
            rent = st.number_input(lang["planner_inputs"]["rent"], 0, 20000, 1500)
            food = st.number_input(lang["planner_inputs"]["food"], 0, 10000, 600)
            transport = st.number_input(lang["planner_inputs"]["transport"], 0, 5000, 300)
        with col2:
            entertainment = st.number_input(lang["planner_inputs"]["entertainment"], 0, 5000, 400)
            healthcare = st.number_input(lang["planner_inputs"]["healthcare"], 0, 2000, 350)
            misc = st.number_input(lang["planner_inputs"]["misc"], 0, 3000, 300)

    total_expenses = rent + food + transport + entertainment + healthcare + misc
    st.markdown(f"**{lang['planner_inputs']['total_expenses_label']}:** `CHF {total_expenses:,}`")
    st.markdown(lang["planner_inputs"]["preferences_note"])

    with st.expander(lang["planner_inputs"]["goals_expander"]):
        col1, col2 = st.columns(2)
        with col1:
            wants_children = st.radio(lang["planner_inputs"]["wants_children"], lang["planner_inputs"]["wants_children_options"])
            dream_trip = st.text_input(lang["planner_inputs"]["dream_trip"])
            travel_budget = st.slider(lang["planner_inputs"]["travel_budget"], 0, 30000, 5000, step=500)
            major_purchase = st.selectbox(lang["planner_inputs"]["major_purchase"], lang["planner_inputs"]["major_purchase_options"])
        with col2:
            career_goal = st.text_area(lang["planner_inputs"]["career_goal"])
            lifestyle_upgrades = st.multiselect(lang["planner_inputs"]["lifestyle_upgrades"], lang["planner_inputs"]["lifestyle_upgrades_options"])
            wellness_goals = st.radio(lang["planner_inputs"]["wellness_goals"], lang["planner_inputs"]["wellness_goals_options"])

    with st.expander(lang["planner_inputs"]["investment_expander"]):
        wants_to_buy_house = st.radio(lang["planner_inputs"]["wants_to_buy_house"], lang["planner_inputs"]["wants_to_buy_house_options"])
        retirement_age = st.slider(lang["planner_inputs"]["retirement_age"], 55, 70, 65)
        owns_home = st.radio(lang["planner_inputs"]["owns_home"], lang["planner_inputs"]["owns_home_options"])
        has_3a = st.radio(lang["planner_inputs"]["has_3a"], lang["planner_inputs"]["has_3a_options"])
        has_etfs = st.radio(lang["planner_inputs"]["has_etfs"], lang["planner_inputs"]["has_etfs_options"])
        other_assets = st.multiselect(lang["planner_inputs"]["other_assets"], lang["planner_inputs"]["other_assets_options"])
        wants_to_invest_more = st.radio(lang["planner_inputs"]["wants_to_invest_more"], lang["planner_inputs"]["wants_to_invest_more_options"])
        initial_savings = st.number_input(lang["planner_inputs"]["initial_savings"], 0, 1_000_000, 20000)

    # --- Projection Calculation ---
    import pandas as pd
    import numpy as np
    import altair as alt

    inflation_rate = 1.6
    salary_growth_rate = 2.2
    investment_return = 4.8
    forecast_years = 25

    years = list(range(0, forecast_years + 1))
    age_projection = [age + y for y in years]
    df = pd.DataFrame({"Year": age_projection})

    def grow(value, rate):
        return [value * ((1 + rate / 100) ** y) for y in years]

    hobby_cost_map = {"Travel": 6000, "Sports": 2000, "Gaming": 1000, "Reading": 500, "Art": 1200, "Other": 1500}
    total_hobby_expense = sum([hobby_cost_map[h] for h in hobbies]) if hobbies else 0

    if "startup" in career_goal.lower():
        career_multiplier = 1.8
    elif "promotion" in career_goal.lower():
        career_multiplier = 1.5
    elif "change" in career_goal.lower():
        career_multiplier = 1.2
    else:
        career_multiplier = 1.0

    adjusted_salary_growth = salary_growth_rate * career_multiplier

    income = grow(current_salary * 12, adjusted_salary_growth)
    costs = grow(total_expenses * 12 + total_hobby_expense + travel_budget, inflation_rate)

    if has_kids == "Yes" or wants_children == "Yes":
        child_costs = [8000 if age + y < 6 else 12000 for y in years]
    else:
        child_costs = [0] * len(years)

    df["Income"] = income
    df["Expenses"] = [cost + child_costs[i] for i, cost in enumerate(costs)]

    if wellness_goals in ["Yes", "Trying to prioritize"]:
        df["Expenses"] *= 1.15

    net_worth = [initial_savings]
    for i in range(1, len(years)):
        surplus = income[i] - df["Expenses"][i]
        investment_growth = net_worth[-1] * (1 + investment_return / 100)
        net_worth.append(investment_growth + surplus)

    df["Net Worth (Base Case)"] = net_worth

    simulations = 50
    mc_df = pd.DataFrame({"Year": age_projection})
    np.random.seed(42)
    for i in range(simulations):
        net = [initial_savings]
        for j in range(1, len(years)):
            rand_income = income[j] * np.random.normal(1, 0.05)
            rand_cost = df["Expenses"][j] * np.random.normal(1, 0.05)
            rand_return = np.random.normal(investment_return / 100, 0.03)
            surplus = max(0, rand_income - rand_cost)
            new_val = net[-1] * (1 + rand_return) + surplus
            net.append(max(new_val, 0))
        mc_df[f"Sim {i+1}"] = net

    st.subheader(lang["projection_overview"])

    base_chart = alt.Chart(df).mark_line().encode(
        x="Year",
        y=alt.Y("Net Worth (Base Case)", title="CHF"),
        color=alt.value("green"),
        tooltip=["Year", "Net Worth (Base Case)"]
    )

    mc_chart = alt.Chart(mc_df.melt("Year")).mark_line(opacity=0.15).encode(
        x="Year",
        y="value:Q",
        color=alt.value("#888"),
        tooltip=["Year", "value"]
    )

    income_vs_expenses_df = df[["Year", "Income", "Expenses"]].melt(id_vars="Year", var_name="Type", value_name="CHF")

    income_vs_expenses_chart = alt.Chart(income_vs_expenses_df).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Age"),
        y=alt.Y("CHF:Q", title="Annual Amount (CHF)"),
        color=alt.Color("Type:N", title=""),
        tooltip=["Year", "Type", "CHF"]
    ).properties(title=lang["income_vs_expenses_chart"])

    st.altair_chart(income_vs_expenses_chart, use_container_width=True)
    st.altair_chart((mc_chart + base_chart).properties(title="📈 Net Worth Projection (Monte Carlo Simulation)"), use_container_width=True)

    st.subheader(lang["summary_recommendations"])
    st.markdown(f"""
    - Final projected **net worth**: `CHF {int(net_worth[-1]):,}`
    - Estimated **income at age {age + forecast_years}**: `CHF {int(income[-1]):,}`
    - Projected **expenses at that time**: `CHF {int(df['Expenses'].iloc[-1]):,}`
    """)

    savings_rate = (income[0] - total_expenses * 12) / income[0]
    score = 5
    score += 1 if has_3a == "Yes" else 0
    score += 1 if has_etfs == "Yes" else 0
    score += 1 if savings_rate > 0.2 else 0
    score += 1 if owns_home == "Yes" else 0
    score = min(score, 10)

    st.markdown("### " + lang["suggestions"])
    st.markdown(f"""
    1. Keep increasing investment contributions to benefit from compounding.
    2. Consider early retirement savings (3rd Pillar, ETFs) if not started.
    3. Maintain a healthy gap between lifestyle cost and income growth.
    4. 🪙 Your **Future Stability Score**: `{score}/10`
    """)
