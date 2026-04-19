# dash_app.py — AlexFin Dash Entry Point
# Dash 4.x multi-page app with sidebar + top navbar

import os
import dash
from dash import Dash, html, dcc, callback, Input, Output, State, page_container
from flask import session, redirect, request, render_template_string
import dash_bootstrap_components as dbc

from i18n import LANGUAGES, t, get_lang_code
from products import KK_PREMI_CANTON

# ─────────────────────────────────────────────
# APP INIT
# ─────────────────────────────────────────────

app = Dash(
    __name__,
    use_pages=True,
    pages_folder="dash_pages",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
    suppress_callback_exceptions=True,
)

server = app.server

# ─────────────────────────────────────────────
# AUTH — Flask session-based login
# ─────────────────────────────────────────────

server.secret_key = os.environ.get("SECRET_KEY", "alexfin-dev-secret-change-in-prod")
AUTH_USER = os.environ.get("AUTH_USER", "alex")
AUTH_PASS = os.environ.get("AUTH_PASS", "svag2026")

_LOGIN_HTML = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AlexFin — Accesso</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  *, body { font-family: 'Inter', sans-serif; box-sizing: border-box; margin: 0; padding: 0; }
  body {
    min-height: 100vh;
    background: linear-gradient(135deg, #1e2235 0%, #151929 60%, #0f121e 100%);
    display: flex; align-items: center; justify-content: center;
  }
  .card {
    background: white; border-radius: 20px;
    padding: 48px 44px; width: 100%; max-width: 420px;
    box-shadow: 0 24px 64px rgba(0,0,0,0.35);
  }
  .logo {
    display: flex; align-items: center; gap: 12px; margin-bottom: 32px;
  }
  .logo-flag { font-size: 2rem; }
  .logo-text { font-size: 1.5rem; font-weight: 800; color: #1e2235; }
  .logo-text span { color: #c0392b; }
  .subtitle { font-size: 0.85rem; color: #888; margin-top: 2px; }
  label {
    display: block; font-size: 0.78rem; font-weight: 700;
    color: #555; margin-bottom: 6px; letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  input[type=text], input[type=password] {
    width: 100%; padding: 11px 14px; border-radius: 10px;
    border: 1.5px solid #dde0e8; font-size: 0.95rem;
    font-family: inherit; margin-bottom: 18px;
    transition: border-color 0.2s, box-shadow 0.2s;
    outline: none;
  }
  input:focus { border-color: #c0392b; box-shadow: 0 0 0 3px rgba(192,57,43,0.12); }
  button {
    width: 100%; padding: 13px; background: #c0392b;
    color: white; border: none; border-radius: 10px;
    font-size: 1rem; font-weight: 700; font-family: inherit;
    cursor: pointer; transition: background 0.2s, transform 0.1s;
    margin-top: 4px;
  }
  button:hover { background: #a93226; transform: translateY(-1px); }
  button:active { transform: translateY(0); }
  .error {
    background: #fde8e8; color: #c0392b; border-radius: 10px;
    padding: 11px 14px; font-size: 0.85rem; font-weight: 600;
    margin-bottom: 18px; display: flex; align-items: center; gap: 8px;
  }
  .footer-note {
    text-align: center; color: #bbb; font-size: 0.72rem; margin-top: 28px;
  }
</style>
</head>
<body>
<div class="card">
  <div class="logo">
    <span class="logo-flag">🇨🇭</span>
    <div>
      <div class="logo-text"><span>Alex</span>Fin</div>
      <div class="subtitle">Advisor Tool · SVAG</div>
    </div>
  </div>
  {% if error %}
  <div class="error">⚠️ {{ error }}</div>
  {% endif %}
  <form method="POST" action="/login">
    <label for="username">Utente</label>
    <input type="text" id="username" name="username" placeholder="nome utente" autocomplete="username" required>
    <label for="password">Password</label>
    <input type="password" id="password" name="password" placeholder="••••••••" autocomplete="current-password" required>
    <button type="submit">→ Accedi</button>
  </form>
  <div class="footer-note">Uso professionale riservato · © 2026 SVAG</div>
</div>
</body>
</html>
"""


@server.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "")
        if u == AUTH_USER and p == AUTH_PASS:
            session["auth"] = True
            return redirect(request.args.get("next", "/"))
        error = "Credenziali non valide. Riprova."
    return render_template_string(_LOGIN_HTML, error=error)


@server.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


_PUBLIC_PREFIXES = ("/login", "/assets", "/_favicon")

@server.before_request
def require_login():
    # Allow public paths
    if any(request.path.startswith(p) for p in _PUBLIC_PREFIXES):
        return
    # Dash internal AJAX calls: return 401 (not redirect) so JS doesn't break
    if request.path.startswith("/_dash"):
        if not session.get("auth"):
            return ("Unauthorized", 401)
        return
    # All other routes require session
    if not session.get("auth"):
        return redirect(f"/login?next={request.path}")

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────

CUSTOM_CSS = """
body, * { font-family: 'Inter', sans-serif !important; }

/* Sidebar */
#sidebar {
    background: linear-gradient(180deg, #1e2235 0%, #151929 100%);
    min-height: 100vh;
    padding: 20px 16px;
    color: #d8dce8;
    position: sticky;
    top: 56px;
    height: calc(100vh - 56px);
    overflow-y: auto;
}
#sidebar h5, #sidebar h6, #sidebar label, #sidebar .form-label { color: #d8dce8 !important; }
#sidebar .form-control, #sidebar .form-select {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: #ffffff !important;
    font-size: 13px;
}
#sidebar .form-control::placeholder { color: rgba(255,255,255,0.4) !important; }
#sidebar .form-check-label { color: #d8dce8 !important; }
#sidebar .form-check-input { border-color: rgba(255,255,255,0.3) !important; }
#sidebar hr { border-color: rgba(255,255,255,0.15) !important; }
#sidebar-summary { color: #a0aec0; font-size: 12px; }

/* Navbar */
#top-navbar { background: #1e2235 !important; }
#top-navbar .navbar-brand { color: white !important; font-weight: 700; font-size: 1.1rem; }
#top-navbar .nav-link { color: #a0aec0 !important; font-weight: 500; transition: color 0.2s; }
#top-navbar .nav-link:hover { color: #ffffff !important; }
#client-badge {
    background: rgba(192,57,43,0.8);
    color: white;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

/* Main content */
#page-content { padding: 24px 28px; background: #f5f7fa; min-height: calc(100vh - 56px); }

/* Cards */
.alexfin-card {
    background: white;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    border: 1px solid #eef0f4;
}
.card-alta { border-left: 5px solid #e74c3c; }
.card-racc { border-left: 5px solid #f39c12; }
.card-opz  { border-left: 5px solid #bdc3c7; }

.badge-alta { background:#fde8e8; color:#c0392b; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; display:inline-block; }
.badge-racc { background:#fef3cd; color:#856404; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; display:inline-block; }
.badge-opz  { background:#f0f2f6; color:#666;    padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; display:inline-block; }

/* Metrics */
.kpi-box {
    background: #f8f9fc;
    border-radius: 12px;
    padding: 16px 18px;
    border: 1px solid #eef0f4;
    text-align: center;
}
.kpi-label { font-size: 11px; color: #888; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.kpi-value { font-size: 1.4rem; font-weight: 700; color: #1e2235; }
.kpi-delta { font-size: 12px; margin-top: 2px; }
.kpi-delta.good { color: #27ae60; }
.kpi-delta.bad  { color: #e74c3c; }

/* Budget semaphore */
.budget-ok   { background:#eafaf1; border-radius:10px; padding:14px 18px; border-left:5px solid #27ae60; margin:12px 0; }
.budget-warn { background:#fef9e7; border-radius:10px; padding:14px 18px; border-left:5px solid #f39c12; margin:12px 0; }
.budget-err  { background:#fdedec; border-radius:10px; padding:14px 18px; border-left:5px solid #e74c3c; margin:12px 0; }

/* Module cards (home) */
.mod-card {
    background: white; border-radius: 18px;
    padding: 32px 24px; text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    border: 2px solid transparent; height: 100%;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.mod-card:hover { border-color: #c0392b; box-shadow: 0 8px 32px rgba(192,57,43,0.15); }
.mod-icon  { font-size: 3rem; display: block; margin-bottom: 12px; }
.mod-title { font-size: 1.15rem; font-weight: 700; color: #1e2235; margin-bottom: 8px; }
.mod-desc  { font-size: 0.87rem; color: #666; line-height: 1.55; }

/* Cover lists */
.cover-ok { color: #27ae60; font-weight: 500; }
.cover-no { color: #e74c3c; font-weight: 500; }

/* Page title */
.page-title { color: #c0392b; font-weight: 700; font-size: 1.6rem; margin-bottom: 4px; }
.page-subtitle { color: #666; font-size: 0.88rem; margin-bottom: 16px; }

/* Tabs */
.nav-tabs .nav-link { font-weight: 600; font-size: 14px; color: #555; }
.nav-tabs .nav-link.active { color: #c0392b !important; border-bottom: 2px solid #c0392b !important; }
"""

# ─────────────────────────────────────────────
# SIDEBAR LAYOUT
# ─────────────────────────────────────────────

CANTON_LIST = list(KK_PREMI_CANTON.keys())
LANG_OPTIONS = [{"label": lbl, "value": code} for lbl, code in LANGUAGES.items()]


def make_sidebar():
    return html.Div(
        id="sidebar",
        children=[
            html.H5("🇨🇭 AlexFin", style={"color": "white", "fontWeight": "700", "marginBottom": "16px"}),
            # Language
            html.Label("🌍 Lingua / Sprache / Langue", style={"fontSize": "11px", "color": "#a0aec0", "marginBottom": "4px"}),
            dcc.Dropdown(
                id="sb-lang",
                options=LANG_OPTIONS,
                value="it",
                clearable=False,
                style={"fontSize": "13px"},
            ),
            html.Hr(),
            html.H6(id="sb-profilo-label", children="👤 Profilo Cliente", style={"color": "#ffffff", "fontWeight": "600"}),
            # Name
            html.Label(id="sb-nome-lbl", children="Nome e Cognome", className="form-label", style={"fontSize": "12px"}),
            dcc.Input(id="sb-nome", type="text", placeholder="es. Marco Rossi", className="form-control", style={"marginBottom": "10px"}),
            # Age + Gender
            dbc.Row([
                dbc.Col([
                    html.Label(id="sb-eta-lbl", children="Età", className="form-label", style={"fontSize": "12px"}),
                    dcc.Input(id="sb-eta", type="number", value=38, min=18, max=80, className="form-control"),
                ], width=6),
                dbc.Col([
                    html.Label(id="sb-sesso-lbl", children="Sesso", className="form-label", style={"fontSize": "12px"}),
                    dcc.Dropdown(id="sb-sesso", options=[{"label": "M", "value": "M"}, {"label": "F", "value": "F"}], value="M", clearable=False, style={"fontSize": "13px"}),
                ], width=6),
            ], style={"marginBottom": "10px"}),
            # Employment
            html.Label(id="sb-sit-lbl", children="Situazione lavorativa", className="form-label", style={"fontSize": "12px"}),
            dcc.Dropdown(
                id="sb-sit",
                options=[{"label": x, "value": x} for x in ["Dipendente", "Indipendente", "Pensionato", "Disoccupato"]],
                value="Dipendente",
                clearable=False,
                style={"fontSize": "13px", "marginBottom": "10px"},
            ),
            # Canton
            html.Label(id="sb-canton-lbl", children="Cantone", className="form-label", style={"fontSize": "12px"}),
            dcc.Dropdown(
                id="sb-canton",
                options=[{"label": c, "value": c} for c in CANTON_LIST],
                value="Ticino",
                clearable=False,
                style={"fontSize": "13px", "marginBottom": "10px"},
            ),
            # Monthly income
            html.Label(id="sb-reddito-lbl", children="Reddito mensile netto (CHF)", className="form-label", style={"fontSize": "12px"}),
            dcc.Input(id="sb-reddito", type="number", value=5500, min=0, max=50000, step=500, className="form-control", style={"marginBottom": "10px"}),
            # Civil status
            html.Label(id="sb-sc-lbl", children="Stato civile", className="form-label", style={"fontSize": "12px"}),
            dcc.Dropdown(
                id="sb-sc",
                options=[{"label": x, "value": x} for x in ["Single", "Sposato/a", "Divorziato/a", "Vedovo/a"]],
                value="Single",
                clearable=False,
                style={"fontSize": "13px", "marginBottom": "10px"},
            ),
            # Children
            html.Label(id="sb-figli-lbl", children="Figli a carico?", className="form-label", style={"fontSize": "12px"}),
            dcc.RadioItems(
                id="sb-figli",
                options=[{"label": " No", "value": "No"}, {"label": " Sì", "value": "Si"}],
                value="No",
                inline=True,
                style={"marginBottom": "6px", "fontSize": "13px"},
            ),
            html.Div(id="sb-nfigli-wrap", children=[
                html.Label(id="sb-nfigli-lbl", children="Quanti figli?", className="form-label", style={"fontSize": "12px"}),
                dcc.Input(id="sb-nfigli", type="number", value=1, min=1, max=10, className="form-control", style={"marginBottom": "10px"}),
            ], style={"display": "none"}),
            # Mortgage
            html.Label(id="sb-ipot-lbl", children="Ipoteca / mutuo?", className="form-label", style={"fontSize": "12px"}),
            dcc.RadioItems(
                id="sb-ipot",
                options=[{"label": " No", "value": "No"}, {"label": " Sì", "value": "Si"}],
                value="No",
                inline=True,
                style={"marginBottom": "10px", "fontSize": "13px"},
            ),
            # Risk tolerance
            html.Label(id="sb-rischio-lbl", children="Tolleranza al rischio", className="form-label", style={"fontSize": "12px"}),
            dcc.Slider(id="sb-rischio", min=0, max=2, step=1, value=1, marks={0: "Bassa", 1: "Media", 2: "Alta"}, tooltip={"always_visible": False}),
            html.Hr(),
            # Summary
            html.Div(id="sb-summary", style={"fontSize": "12px", "color": "#a0aec0"}),
        ],
    )


# ─────────────────────────────────────────────
# TOP NAVBAR
# ─────────────────────────────────────────────

def make_navbar():
    return dbc.Navbar(
        id="top-navbar",
        children=dbc.Container(
            fluid=True,
            style={"padding": "0 24px"},
            children=[
                dbc.NavbarBrand("🇨🇭 AlexFin", href="/", style={"fontWeight": "800", "fontSize": "1.05rem", "color": "white", "marginRight": "24px"}),
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("🏠 Home", href="/", active="exact")),
                        dbc.NavItem(dbc.NavLink("🧑‍💼 Advisor", href="/advisor", active="exact")),
                        dbc.NavItem(dbc.NavLink("🛡️ Assicurazioni", href="/assegurances", active="exact")),
                        dbc.NavItem(dbc.NavLink("🏡 Vita & Budget", href="/vida-budget", active="exact")),
                        dbc.NavItem(dbc.NavLink("🔭 Prospecting", href="/prospecting", active="exact")),
                    ],
                    navbar=True,
                    className="me-auto",
                ),
                html.Div(id="client-badge", children="👤 Advisor"),
                html.A(
                    "⎋ Esci",
                    href="/logout",
                    style={
                        "color": "rgba(255,255,255,0.55)", "fontSize": "0.8rem",
                        "fontWeight": "600", "textDecoration": "none",
                        "marginLeft": "16px", "padding": "4px 12px",
                        "border": "1px solid rgba(255,255,255,0.2)",
                        "borderRadius": "6px", "transition": "all 0.18s",
                    }
                ),
            ],
        ),
        dark=True,
        fixed="top",
        style={"background": "#1e2235", "height": "56px"},
    )


# ─────────────────────────────────────────────
# GLOBAL LAYOUT
# ─────────────────────────────────────────────

app.layout = html.Div([
    dcc.Store(id="app-store", storage_type="session", data={
        "lc": "it",
        "nome": "",
        "eta": 38,
        "sesso": "M",
        "situazione": "Dipendente",
        "canton": "Ticino",
        "reddito_mensile": 5500,
        "stato_civile": "Single",
        "figli": False,
        "n_figli": 0,
        "ipoteca": False,
        "tolleranza_rischio": "Media",
    }),
    make_navbar(),
    html.Div(
        [
            make_sidebar(),
            html.Div(page_container, id="page-content"),
        ],
        className="app-shell",
    ),
])


# ─────────────────────────────────────────────
# MASTER STORE CALLBACK
# ─────────────────────────────────────────────

@callback(
    Output("app-store", "data"),
    Input("sb-lang", "value"),
    Input("sb-nome", "value"),
    Input("sb-eta", "value"),
    Input("sb-sesso", "value"),
    Input("sb-sit", "value"),
    Input("sb-canton", "value"),
    Input("sb-reddito", "value"),
    Input("sb-sc", "value"),
    Input("sb-figli", "value"),
    Input("sb-nfigli", "value"),
    Input("sb-ipot", "value"),
    Input("sb-rischio", "value"),
    prevent_initial_call=False,
)
def update_store(lc, nome, eta, sesso, sit, canton, reddito, sc, figli_val, n_figli, ipot_val, rischio_idx):
    eta = eta or 38
    reddito = reddito or 5500
    n_figli = n_figli or 0
    figli = figli_val == "Si"
    ipoteca = ipot_val == "Si"
    risc_map = {0: "Bassa", 1: "Media", 2: "Alta"}
    tolleranza = risc_map.get(rischio_idx or 1, "Media")
    sit_norm_map = {
        "Dipendente": "Dipendente", "Indipendente": "Indipendente",
        "Pensionato": "Pensionato", "Disoccupato": "Disoccupato",
        "Angestellt": "Dipendente", "Selbständig": "Indipendente",
    }
    situazione = sit_norm_map.get(sit or "Dipendente", "Dipendente")
    return {
        "lc": lc or "it",
        "nome": nome or "",
        "eta": int(eta),
        "sesso": sesso or "M",
        "situazione": situazione,
        "canton": canton or "Ticino",
        "reddito_mensile": int(reddito),
        "stato_civile": sc or "Single",
        "figli": figli,
        "n_figli": int(n_figli) if figli else 0,
        "ipoteca": ipoteca,
        "tolleranza_rischio": tolleranza,
    }


@callback(
    Output("sb-nfigli-wrap", "style"),
    Input("sb-figli", "value"),
)
def toggle_nfigli(val):
    return {"display": "block"} if val == "Si" else {"display": "none"}


@callback(
    Output("client-badge", "children"),
    Input("app-store", "data"),
)
def update_badge(store):
    if not store:
        return "Advisor"
    nome = store.get("nome", "")
    return nome if nome else "Advisor"


@callback(
    Output("sb-summary", "children"),
    Input("app-store", "data"),
)
def update_summary(store):
    if not store:
        return ""
    lc = store.get("lc", "it")
    eta = store.get("eta", 38)
    reddito = store.get("reddito_mensile", 5500)
    anni_p = max(65 - int(eta), 0)
    return [
        html.Div(f"📅 {t('sidebar_anni_pens', lc)}: {anni_p}"),
        html.Div(f"💰 {t('sidebar_reddito_annuo', lc)}: CHF {int(reddito)*12:,}"),
    ]


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DASH_DEBUG", "true").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=port)
