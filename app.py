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
tabs = st.tabs([lang["about_me"], lang["topics"], lang["resources"], lang["user"])

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
    st.title("📈 Personal Finance Forecast – Swiss Style")

    st.write("Use this calculator to estimate your retirement capital based on your current savings, contributions, and investment strategy in Switzerland.")

    st.subheader("1. Personal Details")
    age = st.slider("Current Age", 18, 65, 30)
    retirement_age = st.slider("Target Retirement Age", age+1, 70, 65)
    years_to_invest = retirement_age - age

    st.subheader("2. Financial Inputs")
    current_savings = st.number_input("Current Savings (CHF)", min_value=0, value=20000, step=1000)
    monthly_contribution = st.number_input("Monthly Contribution (CHF)", min_value=0, value=500, step=50)

    st.subheader("3. Pillar Type & Investment Strategy")
    pillar_type = st.selectbox("Choose Pillar", ["Pillar 3a - Bank", "Pillar 3a - Insurance", "ETF Portfolio", "Mixed"])

    investment_profile = st.radio("Investment Profile", ["Conservative (3%)", "Balanced (5%)", "Aggressive (7%)"])

    return_rate = {
        "Conservative (3%)": 0.03,
        "Balanced (5%)": 0.05,
        "Aggressive (7%)": 0.07
    }[investment_profile]

    st.markdown("---")
    st.subheader("📊 Projection Results")

    months = years_to_invest * 12
    balances = []
    total = current_savings
    for i in range(months):
        total = total * (1 + return_rate / 12) + monthly_contribution
        balances.append(total)

    df = pd.DataFrame({
        "Year": [age + i//12 for i in range(months)],
        "Projected Balance": balances
    })

    chart = alt.Chart(df).mark_line(point=True).encode(
        x="Year:O",
        y=alt.Y("Projected Balance", title="CHF"),
        tooltip=["Year", "Projected Balance"]
    ).properties(
        title="Projected Pension Capital Over Time"
    )

    st.altair_chart(chart, use_container_width=True)

    st.success(f"Estimated capital by age {retirement_age}: CHF {int(balances[-1]):,}")
    st.markdown("_Disclaimer: This is a simplified projection. Returns may vary._")
