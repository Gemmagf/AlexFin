import streamlit as st

# Example form data (could come from your sidebar/input)
form_data = {
    "currentAge": 30,
    "retirementAge": 65,
    "currentChildren": 0,
    "futureChildren": 2,
    "annualGrossSalary1": 110000,
    "annualGrossSalary2": 90000,
    "currentSavings": 150000,
    "monthlyContribution": 2500,
    "investmentReturn": 4.5,
    "monthlyLivingCost": 6000,
    "currentHousingCost": 1800,
    "monthlyDaycareCost": 2500,
    "monthlySchoolActivityCost": 400,
    "yearlyTravelBudget": 6000,
    "universitySupport": 25000
}

# What If toggles
sim_part_time = st.sidebar.checkbox("Pare treballa 50%")
sim_market_shock = st.sidebar.checkbox("Mercat estancat (-2%)")
sim_private_school = st.sidebar.checkbox("Universitat Estrangera")
# financial_projection.py

import pandas as pd

import pandas as pd

def run_projection(form_data, sim_part_time=False, sim_market_shock=False, sim_private_school=False):
    """
    form_data: dict with all user inputs
    sim_part_time: bool, if one parent works 50%
    sim_market_shock: bool, if market growth is negative
    sim_private_school: bool, if private/foreign university costs applied

    Returns:
        df: DataFrame with net worth projection
        retirement_wealth: final net worth
        viable: bool if wealth > 0
        early_retirement_age: optional int
    """
    age = form_data["currentAge"]
    forecast_years = 25
    years = list(range(forecast_years + 1))

    # Adjust income for part-time
    salary1 = form_data["annualGrossSalary1"]
    salary2 = form_data["annualGrossSalary2"]
    if sim_part_time:
        salary2 *= 0.5

    # Apply market shock
    investment_return = form_data["investmentReturn"]
    if sim_market_shock:
        investment_return -= 2

    # Apply costs
    monthly_cost = form_data["monthlyLivingCost"]
    if sim_private_school:
        monthly_cost += form_data["universitySupport"] / 12  # spread over 12 months

    income = [(salary1 + salary2) * ((1 + 0.022)**y) for y in years]
    costs = [monthly_cost * 12 * ((1 + 0.016)**y) for y in years]

    net_worth = [form_data["currentSavings"]]
    for i in range(1, len(years)):
        surplus = income[i] - costs[i]
        net_worth.append(net_worth[-1]*(1+investment_return/100) + surplus)

    df = pd.DataFrame({
        "age": [age + y for y in years],
        "income": income,
        "costs": costs,
        "totalWealth": net_worth
    })

    retirement_wealth = net_worth[-1]
    viable = retirement_wealth > form_data["currentSavings"]
    early_retirement_age = age + forecast_years if viable else None

    return df, retirement_wealth, viable, early_retirement_age

# Call the function from your module
df, retirement_wealth, viable, early_retirement_age = run_projection(
    form_data, sim_part_time, sim_market_shock, sim_private_school
)

st.write("## Projecció Patrimoni")
st.line_chart(df.set_index("age")["totalWealth"])
st.write(f"Patrimoni a la jubilació: CHF {retirement_wealth:,.0f}")
st.write("Pla viable?" , "Sí" if viable else "No")
if early_retirement_age:
    st.write(f"Jubilació anticipada possible als {early_retirement_age} anys")
