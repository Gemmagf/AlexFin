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
        "resources": "📂 Free Tools & Guides"
    },
    "Deutsch": {
        "title": "🇨🇭 Schweizer Finanzen einfach erklärt",
        "subtitle": "Hallo, ich bin Alex. Ich helfe dir, Investitionen, Krankenkasse und Steuern in der Schweiz zu verstehen.",
        "about_me": "👋 Über mich",
        "what_i_help": "Womit ich helfen kann",
        "topics": "📘 Finanzthemen",
        "resources": "📂 Kostenlose Tools & Leitfäden"
    },
    "Français": {
        "title": "🇨🇭 La finance suisse simplifiée",
        "subtitle": "Salut, je suis Alex. Je t'aide à comprendre les investissements, l'assurance maladie et les impôts en Suisse.",
        "about_me": "👋 À propos de moi",
        "what_i_help": "Ce que je peux vous aider à comprendre",
        "topics": "📘 Sujets financiers",
        "resources": "📂 Outils et guides gratuits"
    },
    "Italiano": {
        "title": "🇨🇭 Finanza Svizzera Semplificata",
        "subtitle": "Ciao, sono Alex. Ti aiuto a capire investimenti, cassa malati e tasse in Svizzera.",
        "about_me": "👋 Chi sono",
        "what_i_help": "Come posso aiutarti",
        "topics": "📘 Argomenti finanziari",
        "resources": "📂 Strumenti e guide gratuite"
    },
    "Español": {
        "title": "🇨🇭 Finanzas suizas simplificadas",
        "subtitle": "Hola, soy Alex. Te ayudo a entender inversiones, Krankenkasse y impuestos en Suiza.",
        "about_me": "👋 Sobre mí",
        "what_i_help": "En qué puedo ayudarte",
        "topics": "📘 Temas financieros",
        "resources": "📂 Herramientas y guías gratuitas"
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
tabs = st.tabs([lang["about_me"], lang["topics"], lang["resources"]])

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
# (The existing Topics content remains as-is and will be shown under lang["topics"])
# --- Resources Tab ---
# (Remains as-is under lang["resources"])
