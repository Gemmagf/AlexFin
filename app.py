import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image

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
language = st.sidebar.selectbox("🌍 Choose Language", ["English", "Deutsch", "Français", "Italiano", "Español"])

translations = {
    "English": {
        "title": "🇨🇭 Swiss Finance Made Simple",
        "subtitle": "Hi, I'm Alex. I help you understand investments, Krankenkasse & taxes in Switzerland.",
        "about_me": "👋 About Me",
        "what_i_help": "What I Can Help With",
        "topics": "📘 Financial Topics",
        "resources": "📂 Free Tools & Guides",
        "user": "📈 Personal Finance Projection"
        
    },
    "Deutsch": {
        "title": "🇨🇭 Schweizer Finanzen einfach erklärt",
        "subtitle": "Hallo, ich bin Alex. Ich helfe dir, Investitionen, Krankenkasse und Steuern in der Schweiz zu verstehen.",
        "about_me": "👋 Über mich",
        "what_i_help": "Womit ich helfen kann",
        "topics": "📘 Finanzthemen",
        "resources": "📂 Kostenlose Tools & Leitfäden",
        "user": "📈 Personal Finance Projection"
    },
    "Français": {
        "title": "🇨🇭 La finance suisse simplifiée",
        "subtitle": "Salut, je suis Alex. Je t'aide à comprendre les investissements, l'assurance maladie et les impôts en Suisse.",
        "about_me": "👋 À propos de moi",
        "what_i_help": "Ce que je peux vous aider à comprendre",
        "topics": "📘 Sujets financiers",
        "resources": "📂 Outils et guides gratuits",
        "user": "📈 Personal Finance Projection"
    },
    "Italiano": {
        "title": "🇨🇭 Finanza Svizzera Semplificata",
        "subtitle": "Ciao, sono Alex. Ti aiuto a capire investimenti, cassa malati e tasse in Svizzera.",
        "about_me": "👋 Chi sono",
        "what_i_help": "Come posso aiutarti",
        "topics": "📘 Argomenti finanziari",
        "resources": "📂 Strumenti e guide gratuite",
        "user": "📈 Personal Finance Projection"
    },
    "Español": {
        "title": "🇨🇭 Finanzas suizas simplificadas",
        "subtitle": "Hola, soy Alex. Te ayudo a entender inversiones, Krankenkasse y impuestos en Suiza.",
        "about_me": "👋 Sobre mí",
        "what_i_help": "En qué puedo ayudarte",
        "topics": "📘 Temas financieros",
        "resources": "📂 Herramientas y guías gratuitas",
        "user": "📈 Personal Finance Projection"
    }
}

lang = translations[language]

# --- Header ---
st.title(lang["title"])
st.subheader(lang["subtitle"])
st.markdown("[📅 Book a free call](mailto:alex@swissfinance.ch)")

# Optional illustration - Alex doll as guide
try:
    alex_img = Image.open("alex_doll.png")
    st.sidebar.image(alex_img, caption="Alex, your Swiss finance buddy", use_column_width=True)
except FileNotFoundError:
    st.sidebar.markdown("👤 Alex – your Swiss finance buddy")

# --- Navigation Tabs ---
tabs = st.tabs([lang["about_me"], lang["topics"], lang["resources"], lang["user"]])

# --- About Tab ---
with tabs[0]:
    st.header(lang["about_me"])
    st.write("""
    My name is Alex, and I’m passionate about helping people confidently navigate the Swiss financial landscape. Whether you’re a local or new to Switzerland, I simplify complex topics like retirement planning, health insurance, tax savings, and everyday budgeting.

    With years of experience working with expats and Swiss citizens alike, I provide tailored advice that works in real life—not just on paper.
    """)
    st.subheader(lang["what_i_help"])
    st.markdown("""
    - Understanding and optimizing your Swiss 3rd pillar (Säule 3a)
    - Comparing Krankenkasse models and saving on health insurance
    - Budgeting effectively in high-cost cities
    - Filing taxes and maximizing deductions
    - Financial planning for families, freelancers, and expats
    - Intro to ETF investing in Switzerland
    """)

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
        "Swiss 3rd Pillar Explained (Säule 3a)",
        "Discover how to reduce your taxes while saving for retirement. Learn the difference between banking vs. insurance options—and why not all 3a accounts are created equal.",
        "Tax-advantaged growth over time",
        "https://www.ch.ch/en/retirement/third-pillar/"
    )

    display_topic(
        "How Krankenkasse Really Works",
        "Confused by Swiss health insurance? Let’s break down basic vs. supplemental coverage, models like Telmed & HMO, and how to save CHF 1,000+ per year.",
        "Annual savings potential with model comparison",
        "https://www.ch.ch/en/health/health-insurance/"
    )

    display_topic(
        "Investing in Switzerland 101",
        "Learn how to start investing with just CHF 100/month. We’ll compare ETFs vs. savings, explain risk levels, and show you how to open your first Swiss brokerage account.",
        "Growth comparison: ETF vs. Savings",
        "https://www.finanztipp.ch/etf/"
    )

    display_topic(
        "Tax Deductions You’re Probably Missing",
        "From 3a contributions to commuting costs—let’s make your tax declaration work for you. These tips could mean hundreds back in your pocket.",
        "Potential tax savings chart",
        "https://www.ch.ch/en/taxes/deductions/"
    )

    display_topic(
        "Monthly Budgeting in Switzerland",
        "Life in Switzerland isn’t cheap—but budgeting doesn’t have to be hard. Here’s a simple way to structure your monthly income using the 50/30/20 rule adapted for Swiss costs.",
        "Example budget allocation",
        "https://www.ch.ch/en/money-budget/"
    )

    display_topic(
        "The True Cost of Living Alone in CH",
        "Want to move out? Let's break down rent, insurance, transport, and food so you can realistically plan a solo life in Zurich, Geneva, or even Lugano.",
        "Estimated cost breakdown for solo living",
        "https://www.ch.ch/en/living/"
    )

    display_topic(
        "Krankenkasse Change Deadline: What You Need to Know",
        "Every November, you have a chance to save. This post walks you through the deadline, how to compare premiums, and send a Kündigung letter.",
        "Savings from timely plan changes",
        "https://www.ch.ch/en/health/health-insurance/change-insurance/"
    )

    display_topic(
        "Pillar 3a: Bank or Insurance?",
        "Weighing your options? Learn why one offers more flexibility, while the other might lock you in for decades. Alex helps you decide what suits your goals.",
        "Comparison of flexibility and returns",
        "https://www.moneyland.ch/en/3a-pillar-bank-or-insurance"
    )

    display_topic(
        "Swiss Franc Stability & Investing",
        "Why is the CHF considered “safe”? What does that mean for your long-term investment strategy? Understand currency strength in simple terms.",
        "CHF vs. global currency performance",
        "https://www.snb.ch/en/"
    )

    display_topic(
        "Expats: How to Navigate Swiss Finance",
        "Just moved to CH? Here’s a quick-start guide on health insurance, mandatory coverage, and how to start saving or investing even as a newcomer.",
        "Newcomer financial onboarding path",
        "https://www.ch.ch/en/moving-to-switzerland/"
    )

# --- Resources Tab ---
with tabs[2]:
    st.header(lang["resources"])
    st.write("Coming soon: downloadable guides, checklists and calculators!")

# --- User Tab ---
with tabs[3]:
    st.header("🌱 Your Future Planner")

    st.subheader("👤 Personal & Lifestyle Info")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("🎂 Age", 18, 70, 30)
        status = st.selectbox("💍 Relationship Status", ["Single", "Married", "Divorced", "Widowed"])
        has_kids = st.radio("👶 Do you have children?", ["No", "Yes", "Planning to have"])
        pets = st.multiselect("🐶 Pets", ["Dog", "Cat", "None", "Other"])
    with col2:
        hobbies = st.multiselect("🎨 Hobbies", ["Travel", "Sports", "Reading", "Gaming", "Art", "Other"])
        wants_to_travel = st.radio("✈️ Do you want to travel frequently in the future?", ["Yes", "No", "Sometimes"])
        career_field = st.selectbox("💼 Job Sector", ["Tech", "Finance", "Healthcare", "Education", "Other"])
        current_salary = st.number_input("💵 Current Net Monthly Income (CHF)", 0, 3000000, 70000)

    st.subheader("🏠 Living Expenses")
    rent = st.number_input("🏡 Monthly Rent or Mortgage", 0, 5000000, 1500)
    food = st.number_input("🍽️ Monthly Food Expenses", 0, 300000000, 600)
    transport = st.number_input("🚗 Monthly Transport (car/train/fuel)", 0, 200000, 300)
    entertainment = st.number_input("🎭 Entertainment & Hobbies", 0, 20000000, 400)
    healthcare = st.number_input("🩺 Healthcare & Insurance", 0, 100000, 350)
    misc = st.number_input("🧾 Other Regular Expenses", 0, 2000, 300)

    total_expenses = rent + food + transport + entertainment + healthcare + misc

    st.markdown(f"**💸 Total Monthly Living Cost:** CHF {total_expenses:,}")

    st.subheader("🎯 Life Goals")
    wants_to_buy_house = st.radio("🏡 Want to own a house in future?", ["Yes", "No", "Maybe"])
    retirement_age = st.slider("🎉 Desired Retirement Age", 55, 70, 65)
    wants_early_retirement = st.radio("⏳ Interested in early retirement?", ["No", "Yes"])

    if st.button("➡️ Continue to Projections"):
        st.session_state["user_profile"] = {
            "age": age, "status": status, "kids": has_kids, "pets": pets,
            "hobbies": hobbies, "career": career_field, "income": current_salary,
            "expenses": total_expenses, "goals": {
                "travel": wants_to_travel,
                "house": wants_to_buy_house,
                "retire_age": retirement_age,
                "early_retire": wants_early_retirement
            }
        }
        st.success("Profile saved. Move on to projections and investment analysis.")


        st.header("📈 Income & Cost Evolution Forecast")

    st.subheader("🔄 Assumptions & Parameters")
    col1, col2 = st.columns(2)
    with col1:
        inflation_rate = st.slider("📈 Annual Inflation Rate (%)", 0.0, 5.0, 1.5, step=0.1)
        salary_growth_rate = st.slider("💼 Expected Annual Salary Growth (%)", 0.0, 10.0, 3.0, step=0.1)
    with col2:
        investment_return = st.slider("📊 Average Investment Return (%)", 0.0, 10.0, 5.0, step=0.1)
        forecast_years = st.slider("📅 Projection Period (Years)", 5, 40, 25)

    st.markdown("Based on your inputs, we’ll simulate cost of living and salary evolution across three scenarios.")

    st.subheader("💼 Income & Cost Projections")

    # Fetch user data
    profile = st.session_state["user_profile"]
    base_income = profile["income"]
    base_cost = profile["expenses"]
    age = profile["age"]
    retire_age = profile["goals"]["retire_age"]

    # Create projections
    import pandas as pd

    years = list(range(0, forecast_years + 1))
    df = pd.DataFrame({"Year": [age + y for y in years]})

    # Income Scenarios
    def project_income(base, rate):
        return [round(base * ((1 + rate / 100) ** y)) for y in years]

    df["Income (Conservative)"] = project_income(base_income, salary_growth_rate * 0.5)
    df["Income (Balanced)"] = project_income(base_income, salary_growth_rate)
    df["Income (Rich)"] = project_income(base_income, salary_growth_rate * 1.5)

    # Expenses with inflation + adjustments for kids, house, etc.
    def project_cost(base, inflation):
        factor = 1 + inflation / 100
        return [round(base * (factor ** y)) for y in years]

    df["Living Costs"] = project_cost(base_cost, inflation_rate)

    # Show chart
    st.line_chart(df.set_index("Year")[["Income (Balanced)", "Living Costs"]])

    st.markdown("This chart shows your expected income vs cost evolution over time. The goal is to keep income comfortably above cost.")

    st.subheader("💰 Investment & Asset Inputs")
    owns_home = st.radio("🏠 Do you currently own a home?", ["No", "Yes"])
    has_3a = st.radio("💼 Do you have a 3rd Pillar account?", ["No", "Yes"])
    has_indexed_investments = st.radio("📈 Do you invest in ETFs/index funds?", ["No", "Yes"])
    wants_to_invest_more = st.radio("➕ Interested in increasing investments?", ["Yes", "No", "Maybe"])

    other_assets = st.multiselect("💡 Other Assets or Plans", [
        "Real estate property", "Crypto", "Business ownership", "High-yield savings", "Rental income", "None"
    ])

    st.markdown("We’ll factor these into your net worth growth over time using average return rates.")

    st.subheader("📊 Net Worth Projection")

    initial_savings = st.number_input("💰 Current Savings & Investments (CHF)", 0, 1_000_000, 20000)

    net_worth = [initial_savings]
    for y in range(1, forecast_years + 1):
        yearly_income = df.loc[y, "Income (Balanced)"]
        yearly_cost = df.loc[y, "Living Costs"]
        yearly_saving = max(0, yearly_income * 12 - yearly_cost * 12)
        growth = net_worth[-1] * (1 + investment_return / 100)
        net_worth.append(round(growth + yearly_saving))

    df["Estimated Net Worth"] = net_worth

    st.line_chart(df.set_index("Year")[["Estimated Net Worth"]])

    st.markdown("Your estimated net worth grows over time, combining salary savings and compounding returns.")

    st.subheader("📄 Summary Report & Suggestions")

    st.markdown("### 🔍 Highlights:")
    st.markdown(f"- **Estimated net worth in {forecast_years} years:** CHF {net_worth[-1]:,}")
    st.markdown(f"- **Yearly costs at age {age + forecast_years}:** CHF {df['Living Costs'].iloc[-1] * 12:,}")
    st.markdown(f"- **Income at that time (balanced):** CHF {df['Income (Balanced)'].iloc[-1] * 12:,}")

    st.markdown("### ✅ 3 Smart Recommendations:")
    st.markdown("""
    1. **Increase investment allocation** by at least 10% of surplus income annually.
    2. **Consider 3a or ETF investing** if not already active — tax-efficient long-term growth.
    3. **Keep expenses under control**, especially lifestyle inflation, even as salary increases.
    """)

    st.markdown("📬 **For deeper insights, we suggest a call with a certified financial planner.**")

    st.download_button("📥 Download Full Financial Report (Mock)", data="Coming soon!", file_name="financial_report.txt")
