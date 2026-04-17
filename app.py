# app.py — AlexFin Landing Page

import streamlit as st
from utils import CSS, render_sidebar
from i18n import t

st.set_page_config(
    page_title="AlexFin – Advisor Tool",
    layout="wide",
    page_icon="🇨🇭",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)

profilo, lc = render_sidebar()
nome_display = profilo["nome"] if profilo["nome"] else "Advisor"

# ── Header ──
st.title(f"🇨🇭 AlexFin")
st.markdown(f"#### {t('app_subtitle', lc)}")
if profilo["nome"]:
    st.markdown(f"**{t('sidebar_profilo', lc)}:** {profilo['nome']} · {profilo['eta']} anni · {profilo['canton']}")
st.divider()

# ── 3 module cards ──
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="mod-card">
        <span class="mod-icon">🧑‍💼</span>
        <div class="mod-title">Advisor Dashboard</div>
        <div class="mod-desc">Analisi del profilo cliente, raccomandazioni prioritarie, simulatore patrimoniale e note del colloquio con invio email.</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Advisor.py", label="→ Apri Advisor", use_container_width=True)

with c2:
    st.markdown("""
    <div class="mod-card">
        <span class="mod-icon">🛡️</span>
        <div class="mod-title">Assicurazioni & Pilastri</div>
        <div class="mod-desc">Prodotti assicurativi SVAG, comparatore Krankenkasse con franchigie e modelli, sistema previdenziale svizzero (1°/2°/3° pilastro).</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Assegurances.py", label="→ Apri Prodotti", use_container_width=True)

with c3:
    st.markdown("""
    <div class="mod-card">
        <span class="mod-icon">🏡</span>
        <div class="mod-title">Vita & Budget</div>
        <div class="mod-desc">Budget mensile familiare, pianificazione per fase di vita, obiettivi finanziari con timeline e simulazione del risparmio necessario.</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_Vida_Budget.py", label="→ Apri Vita & Budget", use_container_width=True)

st.divider()
st.caption(t("footer", lc))
