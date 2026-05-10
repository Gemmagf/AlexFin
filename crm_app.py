"""
AlexFin CRM — App standalone per a Alex Bevilacqua (SVAG)
Gestió completa de clients: pipeline, agenda, fitxa, notes.

Execució:  python3 crm_app.py
URL:       http://localhost:8051
Login:     AUTH_USER / AUTH_PASS  (env vars, default: alex / svag2026)
"""

import os
import json
import math
from datetime import date, datetime, timedelta

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback, ctx, ALL, MATCH
from flask import Flask, session, redirect, request, render_template_string

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
CRM_FILE   = os.path.join(os.path.dirname(__file__), "clienti.json")
PORT       = int(os.environ.get("CRM_PORT", 8051))
AUTH_USER  = os.environ.get("AUTH_USER", "alex")
AUTH_PASS  = os.environ.get("AUTH_PASS", "svag2026")

PIPELINE_STAGES = [
    ("lead",      "🔵 Lead",      "#3b82f6"),
    ("contattato","📞 Contattato","#f59e0b"),
    ("riunione",  "🤝 Riunione",  "#8b5cf6"),
    ("proposta",  "📄 Proposta",  "#f97316"),
    ("chiuso",    "✅ Chiuso",    "#22c55e"),
    ("perso",     "❌ Perso",     "#ef4444"),
]
STAGE_KEYS    = [s[0] for s in PIPELINE_STAGES]
STAGE_LABELS  = {s[0]: s[1] for s in PIPELINE_STAGES}
STAGE_COLORS  = {s[0]: s[2] for s in PIPELINE_STAGES}

CANTONS = [
    "Zürich","Bern","Luzern","Uri","Schwyz","Obwalden","Nidwalden","Glarus","Zug",
    "Fribourg","Solothurn","Basel-Stadt","Basel-Landschaft","Schaffhausen",
    "Appenzell AR","Appenzell AI","St. Gallen","Graubünden","Aargau","Thurgau",
    "Ticino","Vaud","Valais","Neuchâtel","Genève","Jura",
]

# ─────────────────────────────────────────────
# DATA LAYER
# ─────────────────────────────────────────────
def _default(c: dict) -> dict:
    """Assegura que tots els camps nous existeixin (compat. backward)."""
    defaults = {
        "telefono": "", "email": "",
        "pipeline_stage": "chiuso" if c.get("stato") == "chiuso" else "lead",
        "data_primo_contatto": c.get("data_salvataggio", ""),
        "data_prossimo_followup": "",
        "valore_stimato": 0,
        "prodotto_contrattato": "",
        "note": "",
        "data_salvataggio": date.today().isoformat(),
        "stato": "lead",
    }
    for k, v in defaults.items():
        c.setdefault(k, v)
    # Sync stato amb pipeline_stage per compat. amb dashboard principal
    if c["pipeline_stage"] == "chiuso":
        c["stato"] = "chiuso"
    elif c["pipeline_stage"] == "perso":
        c["stato"] = "perso"
    else:
        c["stato"] = "da_chiudere"
    return c

def load_clients() -> list:
    if os.path.exists(CRM_FILE):
        try:
            with open(CRM_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [_default(c) for c in data]
        except Exception:
            pass
    return []

def save_clients(lst: list):
    with open(CRM_FILE, "w", encoding="utf-8") as f:
        json.dump(lst, f, ensure_ascii=False, indent=2)

def get_client(nome: str):
    return next((c for c in load_clients() if c.get("nome") == nome), None)

def upsert_client(entry: dict):
    clients = load_clients()
    idx = next((i for i, c in enumerate(clients) if c.get("nome") == entry["nome"]), None)
    if idx is not None:
        clients[idx] = entry
    else:
        clients.append(entry)
    save_clients(clients)

def delete_client(nome: str):
    clients = [c for c in load_clients() if c.get("nome") != nome]
    save_clients(clients)

# ─────────────────────────────────────────────
# FLASK + AUTH
# ─────────────────────────────────────────────
server = Flask(__name__)
server.secret_key = os.environ.get("SECRET_KEY", "alexfin-crm-secret")

_LOGIN_HTML = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AlexFin CRM · Login</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  *, body { font-family:'Inter',sans-serif; box-sizing:border-box; margin:0; padding:0; }
  body { background:linear-gradient(135deg,#1e2235 0%,#151929 100%); min-height:100vh;
         display:flex; align-items:center; justify-content:center; }
  .card { background:#fff; border-radius:20px; padding:48px 44px; width:380px;
          box-shadow:0 20px 60px rgba(0,0,0,0.35); }
  .logo { display:flex; align-items:center; gap:14px; margin-bottom:32px; }
  .logo-text { font-size:1.7rem; font-weight:800; color:#1e2235; }
  .logo-text span { color:#c0392b; }
  .logo-badge { background:#fde8e8; color:#c0392b; font-size:0.65rem; font-weight:700;
                padding:3px 9px; border-radius:20px; letter-spacing:0.08em; }
  label { display:block; font-size:0.78rem; font-weight:600; color:#555;
          text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px; }
  input { width:100%; padding:11px 14px; border:1px solid #e0e3ec; border-radius:10px;
          font-size:0.95rem; margin-bottom:18px; outline:none; color:#1e2235; transition:border .2s; }
  input:focus { border-color:#c0392b; }
  button { width:100%; padding:13px; background:#c0392b; color:#fff; border:none;
           border-radius:10px; font-size:1rem; font-weight:700; cursor:pointer;
           transition:background .2s; margin-top:4px; }
  button:hover { background:#a93226; }
  .error { background:#fde8e8; color:#c0392b; border-radius:8px; padding:10px 14px;
           font-size:0.84rem; margin-bottom:18px; }
  .footer { text-align:center; font-size:0.75rem; color:#aaa; margin-top:24px; }
</style>
</head>
<body>
<div class="card">
  <div class="logo">
    <div>
      <div class="logo-text"><span>Alex</span>Fin</div>
      <span class="logo-badge">CRM</span>
    </div>
  </div>
  {% if error %}<div class="error">⚠️ {{ error }}</div>{% endif %}
  <form method="POST" action="/login">
    <label for="u">Utente</label>
    <input type="text" id="u" name="username" placeholder="nome utente" autocomplete="username" required>
    <label for="p">Password</label>
    <input type="password" id="p" name="password" placeholder="••••••••" autocomplete="current-password" required>
    <button type="submit">→ Accedi al CRM</button>
  </form>
  <div class="footer">Uso professionale riservato · © 2026 SVAG</div>
</div>
</body>
</html>"""

@server.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("username","").strip() == AUTH_USER and request.form.get("password","") == AUTH_PASS:
            session["auth"] = True
            return redirect(request.args.get("next", "/"))
        error = "Credenziali non valide."
    return render_template_string(_LOGIN_HTML, error=error)

@server.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@server.before_request
def require_login():
    if any(request.path.startswith(p) for p in ("/login", "/assets", "/_favicon")):
        return
    if request.path.startswith("/_dash"):
        if not session.get("auth"): return ("Unauthorized", 401)
        return
    if not session.get("auth"):
        return redirect(f"/login?next={request.path}")

# ─────────────────────────────────────────────
# DASH APP
# ─────────────────────────────────────────────
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="AlexFin CRM",
    assets_folder="crm_assets",
)

_CSS = None  # CSS injectat via crm_assets/crm.css

# ─────────────────────────────────────────────
# LAYOUT HELPERS
# ─────────────────────────────────────────────
def _stage_pill(stage: str) -> html.Span:
    label = STAGE_LABELS.get(stage, stage)
    color = STAGE_COLORS.get(stage, "#aaa")
    return html.Span(label, className="stage-pill",
                     style={"background": color + "22", "color": color, "border": f"1px solid {color}55"})

def _kpi(label, value, cls="", delta=None):
    return dbc.Col(html.Div([
        html.Div(label, className="kpi-label"),
        html.Div(value, className=f"kpi-value {cls}"),
        html.Div(delta, className="kpi-delta") if delta else html.Div(),
    ], className="kpi-card"))

def _section(title, children):
    return html.Div([
        html.Div(title, className="c-card-title"),
        *children,
    ], className="c-card")

# ─────────────────────────────────────────────
# FORM HELPER
# ─────────────────────────────────────────────
def _form_row(label, child, width=6):
    return dbc.Col([
        html.Div(label, className="crm-form-label"),
        child,
    ], width=width, className="mb-3")


def _client_form(c=None):
    c = c or {}
    def v(k, d=""): return c.get(k, d)

    stage_opts = [{"label": lbl, "value": k} for k, lbl, _ in PIPELINE_STAGES]
    situ_opts  = [{"label": x, "value": x} for x in
                  ["Dipendente","Indipendente","Pensionato","Studente","Disoccupato"]]
    sc_opts    = [{"label": x, "value": x} for x in
                  ["Single","Sposato/a","Divorziato/a","Vedovo/a","Unione civile"]]
    risc_opts  = [{"label": x, "value": x} for x in ["Bassa","Media","Alta"]]
    canton_opts= [{"label": x, "value": x} for x in CANTONS]

    return dbc.Form([
        html.H6("Dati anagrafici", className="text-muted mb-2 mt-1",
                style={"fontSize":"0.7rem","textTransform":"uppercase","letterSpacing":"0.07em"}),
        dbc.Row([
            _form_row("Nome e Cognome",
                dbc.Input(id="cf-nome", value=v("nome"), placeholder="Mario Rossi"), width=4),
            _form_row("Età",
                dbc.Input(id="cf-eta", type="number", value=v("eta", 35), min=18, max=99), width=2),
            _form_row("Sesso",
                dbc.Select(id="cf-sesso", value=v("sesso","M"),
                           options=[{"label":"Uomo","value":"M"},{"label":"Donna","value":"F"}]), width=2),
            _form_row("Telefono",
                dbc.Input(id="cf-tel", value=v("telefono"), placeholder="+41 79 000 00 00"), width=4),
        ]),
        dbc.Row([
            _form_row("Email",
                dbc.Input(id="cf-email", type="email", value=v("email"), placeholder="mario@esempio.ch"), width=5),
            _form_row("Cantone",
                dbc.Select(id="cf-canton", value=v("canton","Zürich"), options=canton_opts), width=3),
            _form_row("Lingua",
                dbc.Select(id="cf-lc", value=v("lc","it"),
                           options=[{"label":"Italiano","value":"it"},{"label":"Deutsch","value":"de"},
                                    {"label":"Français","value":"fr"},{"label":"English","value":"en"}]), width=2),
            _form_row("Reddito /mese CHF",
                dbc.Input(id="cf-reddito", type="number", value=v("reddito_mensile",5000),
                          min=0, step=100), width=2),
        ]),
        dbc.Row([
            _form_row("Situazione lav.",
                dbc.Select(id="cf-situazione", value=v("situazione","Dipendente"), options=situ_opts), width=3),
            _form_row("Stato civile",
                dbc.Select(id="cf-sc", value=v("stato_civile","Single"), options=sc_opts), width=3),
            _form_row("Figli",
                dbc.Select(id="cf-figli", value="Si" if v("figli") else "No",
                           options=[{"label":"No","value":"No"},{"label":"Sì","value":"Si"}]), width=2),
            _form_row("N° figli",
                dbc.Input(id="cf-nfigli", type="number", value=v("n_figli",0), min=0, max=10), width=2),
            _form_row("Ipoteca",
                dbc.Select(id="cf-ipoteca", value="Si" if v("ipoteca") else "No",
                           options=[{"label":"No","value":"No"},{"label":"Sì","value":"Si"}]), width=2),
        ]),
        html.H6("Pipeline CRM", className="text-muted mb-2 mt-2",
                style={"fontSize":"0.7rem","textTransform":"uppercase","letterSpacing":"0.07em"}),
        dbc.Row([
            _form_row("Fase pipeline",
                dbc.Select(id="cf-stage", value=v("pipeline_stage","lead"), options=stage_opts), width=3),
            _form_row("Tolleranza rischio",
                dbc.Select(id="cf-rischio", value=v("tolleranza_rischio","Media"), options=risc_opts), width=3),
            _form_row("Valore stimato (CHF/anno)",
                dbc.Input(id="cf-valore", type="number", value=v("valore_stimato",0), min=0, step=100), width=3),
            _form_row("Data primo contatto",
                dbc.Input(id="cf-data1", type="date", value=v("data_primo_contatto",date.today().isoformat())), width=3),
        ]),
        dbc.Row([
            _form_row("Prossimo follow-up",
                dbc.Input(id="cf-followup", type="date", value=v("data_prossimo_followup","")), width=3),
            _form_row("Prodotto contrattato",
                dbc.Input(id="cf-prodotto", value=v("prodotto_contrattato",""),
                          placeholder="Es: 3° Pilastro + KK ottimizzata"), width=9),
        ]),
        html.H6("Note", className="text-muted mb-2 mt-2",
                style={"fontSize":"0.7rem","textTransform":"uppercase","letterSpacing":"0.07em"}),
        dbc.Textarea(id="cf-note", value=v("note",""),
                     placeholder="Osservazioni, preferenze, prossimi passi…",
                     className="form-control", style={"minHeight":"100px"}),
    ])

# ─────────────────────────────────────────────
# APP LAYOUT
# ─────────────────────────────────────────────
app.layout = html.Div([
    # STORES
    dcc.Store(id="crm-reload",    data=0),
    dcc.Store(id="crm-edit-name", data=None),  # nome del client en edició
    dcc.Interval(id="crm-interval", interval=30_000, n_intervals=0),  # refresh auto

    # NAVBAR
    html.Nav([
        html.Div([
            html.Span("Alex", style={"color":"#c0392b"}),
            html.Span("Fin"),
        ], className="crm-logo"),
        html.Span("CRM", className="crm-badge"),
        html.Span("·", style={"color":"rgba(255,255,255,0.2)","margin":"0 4px"}),
        html.A("📊 Dashboard", id="nav-dashboard", className="crm-nav-link active",
               href="#", **{"data-tab":"tab-dash"}),
        html.A("👥 Clienti",   id="nav-clienti",   className="crm-nav-link",
               href="#", **{"data-tab":"tab-list"}),
        html.A("📋 Pipeline",  id="nav-pipeline",  className="crm-nav-link",
               href="#", **{"data-tab":"tab-kanban"}),
        html.A("📅 Agenda",    id="nav-agenda",    className="crm-nav-link",
               href="#", **{"data-tab":"tab-agenda"}),
        html.A("+ Nuovo cliente", id="btn-new-client", className="crm-nav-link",
               href="#", style={"background":"rgba(192,57,43,0.25)","color":"#fca5a5 !important"}),
        html.A("⎋ Esci", href="/logout", className="crm-logout"),
    ], className="crm-navbar"),

    # CONTENT AREA
    html.Div(id="crm-content", className="crm-page"),

    # HIDDEN TAB STATE
    dcc.Store(id="active-tab", data="tab-dash"),

    # ADD/EDIT MODAL
    dbc.Modal([
        dbc.ModalHeader(html.Span(id="modal-title", children="Nuovo cliente"),
                        close_button=True, className="modal-header"),
        dbc.ModalBody(html.Div(id="modal-form-body")),
        dbc.ModalFooter([
            dbc.Button("Annulla", id="modal-cancel", color="secondary", outline=True, className="me-2"),
            dbc.Button("💾 Salva", id="modal-save", className="btn-crm-primary"),
            html.Div(id="modal-feedback", style={"fontSize":"0.82rem","color":"#27ae60","marginLeft":"12px"}),
        ]),
    ], id="client-modal", size="xl", scrollable=True, is_open=False),

    # DELETE CONFIRM MODAL
    dbc.Modal([
        dbc.ModalHeader("Conferma eliminazione", close_button=True),
        dbc.ModalBody(html.P(id="delete-confirm-text")),
        dbc.ModalFooter([
            dbc.Button("Annulla",  id="delete-cancel", color="secondary", outline=True, className="me-2"),
            dbc.Button("🗑️ Elimina", id="delete-confirm", color="danger"),
        ]),
    ], id="delete-modal", is_open=False),
    dcc.Store(id="delete-nome", data=None),
], style={"minHeight":"100vh"})


# ─────────────────────────────────────────────
# TAB SWITCHING
# ─────────────────────────────────────────────
app.clientside_callback(
    """
    function(n1, n2, n3, n4, n5, cur) {
        const trig = window.dash_clientside.callback_context.triggered;
        if (!trig || !trig.length) return cur;
        const id = trig[0].prop_id.split('.')[0];
        const map = {
            'nav-dashboard':'tab-dash',
            'nav-clienti':'tab-list',
            'nav-pipeline':'tab-kanban',
            'nav-agenda':'tab-agenda',
            'btn-new-client':'tab-new',
        };
        return map[id] || cur;
    }
    """,
    Output("active-tab", "data"),
    Input("nav-dashboard",  "n_clicks"),
    Input("nav-clienti",    "n_clicks"),
    Input("nav-pipeline",   "n_clicks"),
    Input("nav-agenda",     "n_clicks"),
    Input("btn-new-client", "n_clicks"),
    State("active-tab", "data"),
    prevent_initial_call=True,
)


# ─────────────────────────────────────────────
# MAIN CONTENT RENDER
# ─────────────────────────────────────────────
@callback(
    Output("crm-content", "children"),
    Input("active-tab", "data"),
    Input("crm-reload",  "data"),
    Input("crm-interval","n_intervals"),
)
def render_content(tab, _reload, _tick):
    clients = load_clients()
    if tab == "tab-dash":     return render_dashboard(clients)
    if tab == "tab-list":     return render_client_list(clients)
    if tab == "tab-kanban":   return render_pipeline(clients)
    if tab == "tab-agenda":   return render_agenda(clients)
    return render_dashboard(clients)


# ─────────────────────────────────────────────
# TAB 1 — DASHBOARD
# ─────────────────────────────────────────────
def render_dashboard(clients: list):
    today = date.today()
    total   = len(clients)
    chiusi  = sum(1 for c in clients if c.get("pipeline_stage") == "chiuso")
    attivi  = sum(1 for c in clients if c.get("pipeline_stage") not in ("chiuso","perso"))
    persi   = sum(1 for c in clients if c.get("pipeline_stage") == "perso")
    followup_oggi = [c for c in clients
                     if c.get("data_prossimo_followup") == today.isoformat()]
    followup_sett = [c for c in clients
                     if c.get("data_prossimo_followup") and
                     today <= date.fromisoformat(c["data_prossimo_followup"]) <= today + timedelta(days=7)]
    val_pipeline = sum(c.get("valore_stimato", 0) for c in clients
                       if c.get("pipeline_stage") not in ("chiuso","perso"))
    val_chiusi   = sum(c.get("valore_stimato", 0) for c in clients
                       if c.get("pipeline_stage") == "chiuso")

    # Stage breakdown
    stage_counts = {s: 0 for s in STAGE_KEYS}
    for c in clients:
        stage_counts[c.get("pipeline_stage","lead")] += 1

    # Funnel bars
    funnel_stages = [s for s in PIPELINE_STAGES if s[0] not in ("perso",)]
    max_count = max((stage_counts[s[0]] for s in funnel_stages), default=1) or 1

    funnel = []
    for key, label, color in funnel_stages:
        cnt = stage_counts[key]
        pct = int(cnt / max_count * 100) if max_count else 0
        funnel.append(html.Div([
            html.Div([
                html.Span(label, style={"fontSize":"0.82rem","fontWeight":"600","color":"#1e2235","minWidth":"100px"}),
                html.Div(style={"flex":"1","height":"10px","background":"#f0f2f7","borderRadius":"6px","overflow":"hidden","margin":"0 12px"}, children=[
                    html.Div(style={"width":f"{pct}%","height":"100%","background":color,"borderRadius":"6px","transition":"width .4s"})
                ]),
                html.Span(str(cnt), style={"fontSize":"0.82rem","fontWeight":"700","color":color,"minWidth":"24px","textAlign":"right"}),
            ], style={"display":"flex","alignItems":"center","marginBottom":"10px"}),
        ]))

    # Ultimi clienti
    recents = sorted(clients, key=lambda c: c.get("data_salvataggio",""), reverse=True)[:5]
    recent_rows = []
    for c in recents:
        recent_rows.append(html.Tr([
            html.Td(f"👤 {c.get('nome','—')}", style={"fontWeight":"600"}),
            html.Td(_stage_pill(c.get("pipeline_stage","lead"))),
            html.Td(c.get("canton","—"), style={"color":"#888","fontSize":"0.82rem"}),
            html.Td(f"CHF {c.get('reddito_mensile',0):,}", style={"color":"#888","fontSize":"0.82rem"}),
            html.Td(c.get("data_salvataggio","—"), style={"color":"#aaa","fontSize":"0.78rem"}),
        ]))

    # Follow-up urgenti
    urgenti = []
    for c in sorted(followup_sett, key=lambda x: x.get("data_prossimo_followup","")):
        fu = c.get("data_prossimo_followup","")
        try:
            fu_date = date.fromisoformat(fu)
            is_today   = fu_date == today
            is_past    = fu_date < today
            color = "#e74c3c" if is_past else ("#f39c12" if is_today else "#3b82f6")
            label = "SCADUTO" if is_past else ("OGGI" if is_today else fu_date.strftime("%d/%m"))
        except Exception:
            color = "#aaa"; label = fu
        urgenti.append(html.Div([
            html.Div(label, className="agenda-date", style={"color":color}),
            html.Div([
                html.Div(c.get("nome","—"), className="agenda-name"),
                html.Div(f"{c.get('situazione','—')} · Canton {c.get('canton','—')}", className="agenda-sub"),
            ]),
            html.Div(_stage_pill(c.get("pipeline_stage","lead")), style={"marginLeft":"auto"}),
        ], className="agenda-item", style={"borderLeftColor":color}))

    return html.Div([
        html.Div([
            html.Div("Panoramica CRM", className="page-title", style={"fontSize":"1.4rem","fontWeight":"800","color":"#1e2235"}),
            html.Div(f"Aggiornato: {today.strftime('%d/%m/%Y')}", style={"color":"#aaa","fontSize":"0.8rem"}),
        ], style={"marginBottom":"24px"}),

        # KPI ROW
        dbc.Row([
            _kpi("Clienti totali",   total,              "blue"),
            _kpi("Attivi (pipeline)",attivi,             "orange"),
            _kpi("Chiusi ✅",         chiusi,             "green"),
            _kpi("Persi",            persi,              "red"),
            _kpi("Follow-up oggi",   len(followup_oggi), "red" if followup_oggi else ""),
            _kpi("Valore pipeline",  f"CHF {val_pipeline:,}", "orange",
                 delta=f"Chiusi: CHF {val_chiusi:,}"),
        ], className="g-3 mb-4"),

        dbc.Row([
            # Funnel
            dbc.Col(_section("📊 Pipeline funnel", funnel), width=5),

            # Follow-up
            dbc.Col(_section(f"📅 Follow-up questa settimana ({len(followup_sett)})",
                             urgenti or [html.Div("Nessun follow-up in agenda.", style={"color":"#aaa","fontSize":"0.85rem"})]),
                    width=7),
        ], className="g-3"),

        # Recenti
        _section("🕐 Clienti recenti", [
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Nome"), html.Th("Fase"), html.Th("Cantone"),
                    html.Th("Reddito/M"), html.Th("Data"),
                ]), style={"background":"#fafbfc"}),
                html.Tbody(recent_rows),
            ], className="crm-table w-100"),
        ]) if recents else html.Div(),
    ])


# ─────────────────────────────────────────────
# TAB 2 — LISTA CLIENTI
# ─────────────────────────────────────────────
def render_client_list(clients: list):
    stage_opts = [{"label":"Tutte le fasi","value":""}] + \
                 [{"label": STAGE_LABELS[k], "value": k} for k in STAGE_KEYS]
    canton_list = sorted(set(c.get("canton","") for c in clients if c.get("canton")))
    canton_opts = [{"label":"Tutti i cantoni","value":""}] + \
                  [{"label": x, "value": x} for x in canton_list]

    return html.Div([
        html.Div([
            html.Div("👥 Clienti", className="page-title",
                     style={"fontSize":"1.4rem","fontWeight":"800","color":"#1e2235"}),
            html.Div(f"{len(clients)} clienti nel CRM", style={"color":"#aaa","fontSize":"0.8rem"}),
        ], style={"marginBottom":"20px"}),

        # Filtres
        dbc.Row([
            dbc.Col(dbc.Input(id="filter-search", placeholder="🔍  Cerca per nome, email, prodotto…",
                              debounce=True, style={"borderRadius":"10px","border":"1px solid #e0e3ec","fontSize":"0.88rem"}), width=5),
            dbc.Col(dbc.Select(id="filter-stage", value="", options=stage_opts), width=3),
            dbc.Col(dbc.Select(id="filter-canton", value="", options=canton_opts), width=3),
            dbc.Col(dbc.Button("+ Nuovo", id="list-new-btn", className="btn-crm-primary w-100"), width=1),
        ], className="g-2 mb-4"),

        html.Div(id="client-table-body"),
    ])


@callback(
    Output("client-table-body","children"),
    Input("filter-search","value"),
    Input("filter-stage","value"),
    Input("filter-canton","value"),
    Input("crm-reload","data"),
    Input("crm-interval","n_intervals"),
    prevent_initial_call=False,
)
def update_table(search, stage, canton, _r, _t):
    clients = load_clients()
    q = (search or "").lower()
    if q:
        clients = [c for c in clients if q in c.get("nome","").lower()
                   or q in c.get("email","").lower()
                   or q in c.get("prodotto_contrattato","").lower()]
    if stage:
        clients = [c for c in clients if c.get("pipeline_stage") == stage]
    if canton:
        clients = [c for c in clients if c.get("canton") == canton]

    if not clients:
        return html.Div("Nessun cliente trovato.", style={"color":"#aaa","padding":"32px","textAlign":"center"})

    rows = []
    for c in sorted(clients, key=lambda x: x.get("data_salvataggio",""), reverse=True):
        nome = c.get("nome","—")
        fu   = c.get("data_prossimo_followup","")
        try:
            fu_str = date.fromisoformat(fu).strftime("%d/%m/%Y") if fu else "—"
            is_past = fu and date.fromisoformat(fu) < date.today()
        except Exception:
            fu_str = fu or "—"; is_past = False

        rows.append(html.Tr([
            html.Td(f"👤 {nome}", style={"fontWeight":"700"}),
            html.Td(_stage_pill(c.get("pipeline_stage","lead"))),
            html.Td(c.get("canton","—")),
            html.Td(c.get("situazione","—"), style={"color":"#888","fontSize":"0.82rem"}),
            html.Td(f"CHF {c.get('reddito_mensile',0):,}", style={"color":"#888"}),
            html.Td(
                html.Span(fu_str, style={"color":"#e74c3c","fontWeight":"700"} if is_past else {}),
            ),
            html.Td(c.get("prodotto_contrattato","") or "—",
                    style={"fontSize":"0.78rem","color":"#888","maxWidth":"160px","overflow":"hidden","textOverflow":"ellipsis","whiteSpace":"nowrap"}),
            html.Td([
                dbc.Button("✏️", id={"type":"btn-edit","index":nome},   size="sm", color="light",   className="me-1 p-1"),
                dbc.Button("🗑️", id={"type":"btn-delete","index":nome}, size="sm", color="light",   className="p-1"),
            ], style={"whiteSpace":"nowrap"}),
        ]))

    return html.Div([
        html.Table([
            html.Thead(html.Tr([
                html.Th("Nome"), html.Th("Fase"), html.Th("Cantone"), html.Th("Situazione"),
                html.Th("Reddito/M"), html.Th("Follow-up"), html.Th("Prodotto"), html.Th(""),
            ])),
            html.Tbody(rows),
        ], className="crm-table w-100"),
        html.Div(f"{len(clients)} clienti mostrati", style={"color":"#aaa","fontSize":"0.75rem","marginTop":"10px","textAlign":"right"}),
    ], className="c-card", style={"padding":"0","overflow":"hidden"})


# ─────────────────────────────────────────────
# TAB 3 — PIPELINE KANBAN
# ─────────────────────────────────────────────
def render_pipeline(clients: list):
    by_stage = {k: [] for k in STAGE_KEYS}
    for c in clients:
        by_stage[c.get("pipeline_stage","lead")].append(c)

    cols = []
    for key, label, color in PIPELINE_STAGES:
        cards = []
        for c in by_stage[key]:
            nome = c.get("nome","—")
            cards.append(html.Div([
                html.Div(nome, className="kanban-card-name"),
                html.Div(f"{c.get('canton','—')} · CHF {c.get('reddito_mensile',0):,}/m",
                         className="kanban-card-sub"),
                html.Div([
                    html.Span(c.get("situazione",""), style={"fontSize":"0.72rem","color":"#aaa"}),
                    dbc.Button("✏️", id={"type":"btn-edit","index":nome},
                               size="sm", color="light", className="p-0 ms-auto",
                               style={"fontSize":"0.75rem","lineHeight":"1"}),
                ], style={"display":"flex","alignItems":"center","marginTop":"6px"}),
            ], className="kanban-card",
               id={"type":"kanban-card","index":nome}))

        n = len(by_stage[key])
        total_val = sum(c.get("valore_stimato",0) for c in by_stage[key])
        cols.append(dbc.Col(html.Div([
            html.Div([
                html.Span(label, className="kanban-col-title",
                          style={"borderBottomColor": color, "color": color}),
                html.Span(f" {n}", style={"color":color,"fontWeight":"800","fontSize":"0.9rem"}),
                html.Span(f"  CHF {total_val:,}" if total_val else "",
                          style={"fontSize":"0.72rem","color":"#aaa","marginLeft":"8px"}),
            ]),
            *cards,
            html.Div("—", style={"color":"#ddd","textAlign":"center","marginTop":"20px","fontSize":"0.8rem"}) if not cards else html.Div(),
        ], className="kanban-col"), width=2))

    return html.Div([
        html.Div([
            html.Div("📋 Pipeline", className="page-title",
                     style={"fontSize":"1.4rem","fontWeight":"800","color":"#1e2235"}),
            html.Div(f"{len(clients)} clienti totali", style={"color":"#aaa","fontSize":"0.8rem"}),
        ], style={"marginBottom":"20px"}),
        dbc.Row(cols, className="g-2"),
    ])


# ─────────────────────────────────────────────
# TAB 4 — AGENDA FOLLOW-UPS
# ─────────────────────────────────────────────
def render_agenda(clients: list):
    today = date.today()

    with_fu = [(c, date.fromisoformat(c["data_prossimo_followup"]))
               for c in clients if c.get("data_prossimo_followup")]
    with_fu.sort(key=lambda x: x[1])

    past    = [(c, d) for c, d in with_fu if d < today]
    todayL  = [(c, d) for c, d in with_fu if d == today]
    sett    = [(c, d) for c, d in with_fu if today < d <= today + timedelta(days=7)]
    future  = [(c, d) for c, d in with_fu if d > today + timedelta(days=7)]
    no_fu   = [c for c in clients if not c.get("data_prossimo_followup")
               and c.get("pipeline_stage") not in ("chiuso","perso")]

    def fu_block(title, items, color):
        if not items: return html.Div()
        rows = []
        for c, d in items:
            nome = c.get("nome","—")
            rows.append(html.Div([
                html.Div(d.strftime("%d/%m"), className="agenda-date", style={"color":color}),
                html.Div([
                    html.Div(nome, className="agenda-name"),
                    html.Div(f"{c.get('situazione','—')} · {c.get('canton','—')} · "
                             f"CHF {c.get('reddito_mensile',0):,}/m", className="agenda-sub"),
                    html.Div(c.get("note","")[:80] + ("…" if len(c.get("note","")) > 80 else ""),
                             style={"fontSize":"0.72rem","color":"#bbb","marginTop":"2px"}) if c.get("note") else html.Div(),
                ]),
                html.Div([
                    _stage_pill(c.get("pipeline_stage","lead")),
                    dbc.Button("✏️", id={"type":"btn-edit","index":nome},
                               size="sm", color="light", className="ms-2 p-1"),
                ], style={"marginLeft":"auto","display":"flex","alignItems":"center"}),
            ], className="agenda-item", style={"borderLeftColor":color}))
        return _section(title, rows)

    no_fu_items = []
    for c in no_fu:
        nome = c.get("nome","—")
        no_fu_items.append(html.Div([
            html.Div("N/D", className="agenda-date", style={"color":"#ccc"}),
            html.Div([
                html.Div(nome, className="agenda-name"),
                html.Div(f"{c.get('situazione','—')} · {c.get('canton','—')}", className="agenda-sub"),
            ]),
            html.Div([
                _stage_pill(c.get("pipeline_stage","lead")),
                dbc.Button("✏️", id={"type":"btn-edit","index":nome},
                           size="sm", color="light", className="ms-2 p-1"),
            ], style={"marginLeft":"auto","display":"flex","alignItems":"center"}),
        ], className="agenda-item", style={"borderLeftColor":"#ddd"}))

    return html.Div([
        html.Div([
            html.Div("📅 Agenda Follow-up", className="page-title",
                     style={"fontSize":"1.4rem","fontWeight":"800","color":"#1e2235"}),
            html.Div(f"Oggi: {today.strftime('%A %d %B %Y')}", style={"color":"#aaa","fontSize":"0.8rem"}),
        ], style={"marginBottom":"20px"}),

        fu_block(f"🔴 Scaduti ({len(past)})",   past,   "#e74c3c"),
        fu_block(f"🟡 Oggi ({len(todayL)})",     todayL, "#f39c12"),
        fu_block(f"🔵 Questa settimana ({len(sett)})", sett, "#3b82f6"),
        fu_block(f"⬜ Prossimamente ({len(future)})",  future,"#888"),

        _section(f"⚠️ Senza follow-up programmato ({len(no_fu)})", no_fu_items)
        if no_fu else html.Div(),
    ])


# ─────────────────────────────────────────────
# MODAL OPEN — nuovo / edit
# ─────────────────────────────────────────────
@callback(
    Output("client-modal",    "is_open"),
    Output("modal-form-body", "children"),
    Output("modal-title",     "children"),
    Output("crm-edit-name",   "data"),
    Input("btn-new-client",   "n_clicks"),
    Input("list-new-btn",     "n_clicks"),
    Input({"type":"btn-edit","index":ALL}, "n_clicks"),
    Input("modal-cancel",     "n_clicks"),
    Input("modal-save",       "n_clicks"),
    State("crm-edit-name",    "data"),
    prevent_initial_call=True,
)
def open_modal(n_new, n_list_new, n_edit_list, n_cancel, n_save, edit_name):
    tid = ctx.triggered_id
    if tid in ("modal-cancel","modal-save") or tid is None:
        return False, dash.no_update, dash.no_update, None

    # Nuevo client
    if tid in ("btn-new-client","list-new-btn"):
        return True, _client_form(None), "➕ Nuovo cliente", None

    # Edit
    if isinstance(tid, dict) and tid.get("type") == "btn-edit":
        nome = tid["index"]
        c    = get_client(nome)
        return True, _client_form(c), f"✏️ Modifica — {nome}", nome

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


# ─────────────────────────────────────────────
# MODAL SAVE
# ─────────────────────────────────────────────
@callback(
    Output("modal-feedback", "children"),
    Output("crm-reload",     "data"),
    Input("modal-save",      "n_clicks"),
    State("crm-edit-name",   "data"),
    State("cf-nome",         "value"),
    State("cf-eta",          "value"),
    State("cf-sesso",        "value"),
    State("cf-tel",          "value"),
    State("cf-email",        "value"),
    State("cf-canton",       "value"),
    State("cf-lc",           "value"),
    State("cf-reddito",      "value"),
    State("cf-situazione",   "value"),
    State("cf-sc",           "value"),
    State("cf-figli",        "value"),
    State("cf-nfigli",       "value"),
    State("cf-ipoteca",      "value"),
    State("cf-stage",        "value"),
    State("cf-rischio",      "value"),
    State("cf-valore",       "value"),
    State("cf-data1",        "value"),
    State("cf-followup",     "value"),
    State("cf-prodotto",     "value"),
    State("cf-note",         "value"),
    State("crm-reload",      "data"),
    prevent_initial_call=True,
)
def save_client(n, edit_nome, nome, eta, sesso, tel, email, canton, lc,
                reddito, situ, sc, figli, nfigli, ipoteca,
                stage, rischio, valore, data1, followup,
                prodotto, note, reload_n):
    if not n or not nome:
        return "⚠️ Inserisci almeno il nome.", dash.no_update

    entry = _default({
        "nome":                  nome.strip(),
        "eta":                   int(eta or 30),
        "sesso":                 sesso or "M",
        "telefono":              tel or "",
        "email":                 email or "",
        "canton":                canton or "Zürich",
        "lc":                    lc or "it",
        "reddito_mensile":       int(reddito or 0),
        "situazione":            situ or "Dipendente",
        "stato_civile":          sc or "Single",
        "figli":                 figli == "Si",
        "n_figli":               int(nfigli or 0),
        "ipoteca":               ipoteca == "Si",
        "tolleranza_rischio":    rischio or "Media",
        "pipeline_stage":        stage or "lead",
        "valore_stimato":        int(valore or 0),
        "data_primo_contatto":   data1 or date.today().isoformat(),
        "data_prossimo_followup":followup or "",
        "prodotto_contrattato":  prodotto or "",
        "note":                  note or "",
        "data_salvataggio":      date.today().isoformat(),
    })
    upsert_client(entry)
    return f"✅ Salvato!", (reload_n or 0) + 1


# ─────────────────────────────────────────────
# DELETE FLOW
# ─────────────────────────────────────────────
@callback(
    Output("delete-modal",      "is_open"),
    Output("delete-confirm-text","children"),
    Output("delete-nome",       "data"),
    Input({"type":"btn-delete","index":ALL}, "n_clicks"),
    Input("delete-cancel",  "n_clicks"),
    Input("delete-confirm", "n_clicks"),
    State("delete-nome",    "data"),
    prevent_initial_call=True,
)
def delete_flow(n_del_list, n_cancel, n_confirm, nome_state):
    tid = ctx.triggered_id
    if tid == "delete-cancel":
        return False, dash.no_update, None
    if tid == "delete-confirm" and nome_state:
        delete_client(nome_state)
        return False, dash.no_update, None
    if isinstance(tid, dict) and tid.get("type") == "btn-delete":
        nome = tid["index"]
        return True, f"Sei sicuro di voler eliminare il cliente «{nome}»? L'operazione è irreversibile.", nome
    return dash.no_update, dash.no_update, dash.no_update


@callback(
    Output("crm-reload","data", allow_duplicate=True),
    Input("delete-confirm","n_clicks"),
    State("crm-reload","data"),
    prevent_initial_call=True,
)
def reload_after_delete(n, cur):
    if n: return (cur or 0) + 1
    return dash.no_update


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    debug = os.environ.get("DASH_DEBUG","true").lower() == "true"
    print(f"\n✅  AlexFin CRM  →  http://localhost:{PORT}")
    print(f"   Login: {AUTH_USER} / {AUTH_PASS}\n")
    app.run(debug=debug, port=PORT, host="0.0.0.0")
