# utils.py — AlexFin shared utilities
import streamlit as st
from products import KK_PREMI_CANTON
from i18n import LANGUAGES, t, get_lang_code

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e2235 0%, #151929 100%) !important;
}
section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div { color: #d8dce8 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #ffffff !important; }
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: #ffffff !important;
    border-radius: 6px;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stRadio > div { gap: 8px; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
section[data-testid="stSidebar"] .stSlider > div > div { background: #c0392b !important; }

/* ── Typography ── */
h1 { color: #c0392b !important; font-weight: 700 !important; letter-spacing: -0.5px; }
h2 { color: #1e2235 !important; font-weight: 600 !important; }
h3 { color: #2c3e50 !important; font-weight: 600 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 6px; padding-bottom: 0; }
.stTabs [data-baseweb="tab"] {
    font-size: 14px; font-weight: 600;
    border-radius: 8px 8px 0 0;
    padding: 10px 18px;
    background: #f0f2f6;
}
.stTabs [aria-selected="true"] { background: white !important; color: #c0392b !important; }

/* ── Cards (raccomandazioni) ── */
.card {
    background: white; border-radius: 14px;
    padding: 20px 24px; margin-bottom: 12px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    border: 1px solid #eef0f4;
}
.card-alta    { border-left: 5px solid #e74c3c; }
.card-racc    { border-left: 5px solid #f39c12; }
.card-opz     { border-left: 5px solid #bdc3c7; }

.badge-alta { background:#fde8e8; color:#c0392b; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; }
.badge-racc { background:#fef3cd; color:#856404; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; }
.badge-opz  { background:#f0f2f6; color:#666;    padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; }

/* ── Cover lists ── */
.cover-ok { color:#27ae60; font-weight:500; display:block; margin:3px 0; }
.cover-no { color:#e74c3c; font-weight:500; display:block; margin:3px 0; }

/* ── Budget semaphore ── */
.budget-ok   { background:#eafaf1; border-radius:10px; padding:16px 20px; border-left:5px solid #27ae60; margin:12px 0; }
.budget-warn { background:#fef9e7; border-radius:10px; padding:16px 20px; border-left:5px solid #f39c12; margin:12px 0; }
.budget-err  { background:#fdedec; border-radius:10px; padding:16px 20px; border-left:5px solid #e74c3c; margin:12px 0; }

/* ── Metrics ── */
div[data-testid="metric-container"] {
    background: #f8f9fc; border-radius: 12px;
    padding: 16px 18px; border: 1px solid #eef0f4;
}
div[data-testid="metric-container"] > label { font-size: 12px !important; color: #666 !important; }
div[data-testid="metric-container"] > div { font-size: 1.4rem !important; font-weight: 700 !important; }

/* ── Module cards (home page) ── */
.mod-card {
    background: white; border-radius: 18px;
    padding: 32px 28px; text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    border: 2px solid transparent;
    height: 100%;
}
.mod-card:hover { border-color: #c0392b; box-shadow: 0 8px 32px rgba(192,57,43,0.15); }
.mod-icon  { font-size: 3.5rem; display: block; margin-bottom: 14px; }
.mod-title { font-size: 1.2rem; font-weight: 700; color: #1e2235; margin-bottom: 8px; }
.mod-desc  { font-size: 0.88rem; color: #666; line-height: 1.5; }

/* ── Spacing ── */
.block-container { padding: 2rem 2.5rem 3rem 2.5rem !important; max-width: 1300px; }
hr { margin: 1.5rem 0 !important; }
</style>
"""

# ─────────────────────────────────────────────
# SESSION STATE — defaults (only set if absent)
# ─────────────────────────────────────────────

def init_session():
    """Set default values for all sidebar keys if not already in session_state."""
    defaults = {
        # Language — stores the full label string e.g. "🇮🇹 Italiano"
        "lang_label":  "🇮🇹 Italiano",
        # Profile fields — keys match widget keys so Streamlit manages them
        "sb_nome":     "",
        "sb_eta":      38,
        "sb_sesso":    0,    # index into sesso_opt list
        "sb_sit":      0,    # index into situazione_opt list
        "sb_canton":   "Ticino",
        "sb_reddito":  5500,
        "sb_sc":       0,    # index into stato_civile_opt list
        "sb_figli":    0,    # index 0=No, 1=Sì (radio stored as index)
        "sb_nfigli":   1,
        "sb_ipot":     0,    # index 0=No, 1=Sì
        "sb_risc":     1,    # index 0=Bassa 1=Media 2=Alta
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ─────────────────────────────────────────────
# SHARED SIDEBAR
# ─────────────────────────────────────────────

def render_sidebar():
    """Render the shared profile sidebar on every page.
    Returns (profilo dict, lc str).

    Key design rule for Streamlit MPA:
    - Every widget uses ONLY `key=`. Never combine `key=` + `index=`/`value=`
      because if the key already exists in session_state (from a previous page
      navigation), Streamlit raises a conflict error.
    - `init_session()` plants the defaults before any widget is created.
    """
    init_session()

    with st.sidebar:
        st.markdown("## 🇨🇭 AlexFin")

        # ── Language selector ──────────────────
        # key="lang_label" → st.session_state.lang_label = selected label string
        lang_label = st.selectbox(
            "🌍 Lingua / Sprache / Langue",
            list(LANGUAGES.keys()),
            key="lang_label",
        )
        lc = get_lang_code(lang_label)

        st.divider()
        st.markdown(f"### 👤 {t('sidebar_profilo', lc)}")

        # ── Name ──────────────────────────────
        nome = st.text_input(
            t("sidebar_nome", lc),
            placeholder=t("sidebar_nome_ph", lc),
            key="sb_nome",
        )

        # ── Age + Gender ──────────────────────
        c1, c2 = st.columns(2)
        with c1:
            eta = st.number_input(
                t("sidebar_eta", lc), 18, 80, key="sb_eta"
            )
        with c2:
            sesso_opts = t("sidebar_sesso_opt", lc)
            # range+format_func stores an INTEGER index → language-independent
            sesso_idx = st.selectbox(
                t("sidebar_sesso", lc),
                range(len(sesso_opts)),
                format_func=lambda i: sesso_opts[i],
                key="sb_sesso",
            )

        # ── Employment situation ───────────────
        sit_opts = t("sidebar_situazione_opt", lc)
        sit_idx = st.selectbox(
            t("sidebar_situazione", lc),
            range(len(sit_opts)),
            format_func=lambda i: sit_opts[i],
            key="sb_sit",
        )
        sit_norm = ["Dipendente", "Indipendente", "Pensionato", "Disoccupato"][sit_idx]

        # ── Canton ────────────────────────────
        canton_keys = list(KK_PREMI_CANTON.keys())
        canton = st.selectbox(
            t("sidebar_canton", lc),
            canton_keys,
            key="sb_canton",
        )

        # ── Monthly income ────────────────────
        reddito = st.number_input(
            t("sidebar_reddito", lc), 0, 50000, step=500, key="sb_reddito"
        )

        # ── Civil status ──────────────────────
        sc_opts = t("sidebar_stato_civile_opt", lc)
        sc_idx = st.selectbox(
            t("sidebar_stato_civile", lc),
            range(len(sc_opts)),
            format_func=lambda i: sc_opts[i],
            key="sb_sc",
        )

        # ── Children (radio stored as index) ──
        figli_opts = t("sidebar_figli_opt", lc)
        figli_idx = st.radio(
            t("sidebar_figli", lc),
            range(len(figli_opts)),
            format_func=lambda i: figli_opts[i],
            horizontal=True,
            key="sb_figli",
        )
        figli = figli_idx == 1
        n_figli = 0
        if figli:
            n_figli = st.number_input(
                t("sidebar_n_figli", lc), 1, 10, key="sb_nfigli"
            )

        # ── Mortgage ──────────────────────────
        ipot_opts = t("sidebar_ipoteca_opt", lc)
        ipot_idx = st.radio(
            t("sidebar_ipoteca", lc),
            range(len(ipot_opts)),
            format_func=lambda i: ipot_opts[i],
            horizontal=True,
            key="sb_ipot",
        )
        ipoteca = ipot_idx == 1

        # ── Risk tolerance ────────────────────
        risc_opts = t("sidebar_rischio_opt", lc)
        risc_idx = st.select_slider(
            t("sidebar_rischio", lc),
            options=range(len(risc_opts)),
            format_func=lambda i: risc_opts[i],
            key="sb_risc",
        )

        # ── Summary ───────────────────────────
        st.divider()
        anni_p = max(65 - int(eta), 0)
        st.markdown(f"📅 **{t('sidebar_anni_pens', lc)}:** {anni_p}")
        st.markdown(f"💰 **{t('sidebar_reddito_annuo', lc)}:** CHF {int(reddito) * 12:,}")

    profilo = {
        "nome":             nome,
        "eta":              int(eta),
        "sesso":            sesso_opts[sesso_idx],
        "situazione":       sit_norm,
        "canton":           canton,
        "reddito_mensile":  int(reddito),
        "stato_civile":     sc_opts[sc_idx],
        "figli":            figli,
        "n_figli":          int(n_figli),
        "ipoteca":          ipoteca,
        "tolleranza_rischio": risc_opts[risc_idx],
    }
    return profilo, lc
