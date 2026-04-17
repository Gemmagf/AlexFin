# dash_pages/advisor.py — AlexFin Advisor Dashboard
# Tabs: Raccomandazioni, Simulatore, Note, CRM

import json
import os
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import callback, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

from i18n import t
from products import calcola_raccomandazioni

dash.register_page(__name__, path="/advisor", name="Advisor")

CRM_FILE = os.path.join(os.path.dirname(__file__), "..", "clienti.json")


def carica_clienti():
    if os.path.exists(CRM_FILE):
        with open(CRM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def salva_clienti(lista):
    with open(CRM_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def kpi_box(label, value, delta=None, delta_good=True):
    delta_el = []
    if delta:
        cls = "kpi-delta good" if delta_good else "kpi-delta bad"
        delta_el = [html.Div(delta, className=cls)]
    return html.Div(
        [
            html.Div(label, className="kpi-label"),
            html.Div(value, className="kpi-value"),
            *delta_el,
        ],
        className="kpi-box",
    )


def rec_card(r):
    prio = r["priorita"]
    if "Alta" in prio:
        card_cls, badge_cls = "alexfin-card card-alta", "badge-alta"
    elif "Raccomandata" in prio:
        card_cls, badge_cls = "alexfin-card card-racc", "badge-racc"
    else:
        card_cls, badge_cls = "alexfin-card card-opz", "badge-opz"
    return html.Div(
        [
            html.Div(
                [
                    html.Span(f"{r['icona']} {r['prodotto']}", style={"fontWeight": "600", "fontSize": "1rem"}),
                    html.Span(prio, className=badge_cls),
                ],
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "6px"},
            ),
            html.Span(r["motivo"], style={"color": "#555", "fontSize": "0.9rem"}),
        ],
        className=card_cls,
    )


# ─────────────────────────────────────────────
# PAGE LAYOUT
# ─────────────────────────────────────────────

def layout():
    return html.Div([
        html.Div(id="adv-header"),
        dbc.Tabs(
            [
                dbc.Tab(label="🎯 Raccomandazioni", tab_id="tab-rac"),
                dbc.Tab(label="📈 Simulatore", tab_id="tab-sim"),
                dbc.Tab(label="📝 Note", tab_id="tab-note"),
                dbc.Tab(label="📋 CRM", tab_id="tab-crm"),
            ],
            id="adv-tabs",
            active_tab="tab-rac",
            style={"marginBottom": "20px"},
        ),
        html.Div(id="adv-tab-content"),

        # Note state stores (to avoid circular deps)
        dcc.Store(id="note-libere-store", data=""),
        dcc.Store(id="temi-store", data=[]),
        dcc.Store(id="crm-trigger", data=0),
        dcc.Store(id="email-status", data=""),
    ])


# ─────────────────────────────────────────────
# HEADER CALLBACK
# ─────────────────────────────────────────────

@callback(Output("adv-header", "children"), Input("app-store", "data"))
def render_header(store):
    if not store:
        store = {}
    lc = store.get("lc", "it")
    nome = store.get("nome", "") or "Cliente"
    eta = store.get("eta", 38)
    sit = store.get("situazione", "Dipendente")
    canton = store.get("canton", "Ticino")
    reddito = store.get("reddito_mensile", 5500)
    return html.Div([
        html.H1(f"🧑‍💼 {t('adv_title', lc)}", className="page-title"),
        html.P(f"{nome} · {eta} anni · {sit} · {canton} · CHF {reddito:,}/m", className="page-subtitle"),
        html.Hr(),
    ])


# ─────────────────────────────────────────────
# MAIN TAB CONTENT CALLBACK
# ─────────────────────────────────────────────

@callback(Output("adv-tab-content", "children"), Input("adv-tabs", "active_tab"), Input("app-store", "data"))
def render_tab(active_tab, store):
    if not store:
        store = {}
    lc = store.get("lc", "it")
    eta = store.get("eta", 38)
    reddito_mensile = store.get("reddito_mensile", 5500)
    reddito_annuo = reddito_mensile * 12
    situazione = store.get("situazione", "Dipendente")
    nome = store.get("nome", "") or "Cliente"
    anni_pensionamento = max(65 - eta, 1)

    if active_tab == "tab-rac":
        return render_raccomandazioni(store, lc, eta, reddito_mensile, reddito_annuo, situazione, anni_pensionamento)
    elif active_tab == "tab-sim":
        return render_simulatore(lc, eta, reddito_mensile)
    elif active_tab == "tab-note":
        return render_note(lc, nome, eta, situazione, store)
    elif active_tab == "tab-crm":
        return render_crm(lc, store)
    return html.Div()


# ─────────────────────────────────────────────
# TAB 1 — RACCOMANDAZIONI
# ─────────────────────────────────────────────

def render_raccomandazioni(store, lc, eta, reddito_mensile, reddito_annuo, situazione, anni_pensionamento):
    avs_stimata = min(reddito_annuo * 0.18, 2520 * 12)
    lpp_stimata = max((reddito_annuo - 26460) * 0.18, 0) if situazione != "Indipendente" else 0
    reddito_pensione = avs_stimata + lpp_stimata
    lacuna = max(reddito_annuo * 0.7 - reddito_pensione, 0)

    kpis = dbc.Row([
        dbc.Col(kpi_box(t("kpi_eta", lc), f"{eta} anni"), width=True),
        dbc.Col(kpi_box(t("kpi_reddito", lc), f"CHF {reddito_annuo:,}"), width=True),
        dbc.Col(kpi_box(t("kpi_anni_pens", lc), str(anni_pensionamento)), width=True),
        dbc.Col(kpi_box(t("kpi_pensione", lc), f"CHF {reddito_pensione:,.0f}/a"), width=True),
        dbc.Col(kpi_box(
            t("kpi_lacuna", lc),
            f"CHF {lacuna:,.0f}/a",
            delta=f"-{lacuna/reddito_annuo*100:.0f}%" if lacuna > 0 and reddito_annuo > 0 else "✓",
            delta_good=(lacuna == 0),
        ), width=True),
    ], className="g-3 mb-4")

    raccomandazioni = calcola_raccomandazioni(store)

    # Bar chart AVS/LPP/Lacuna
    df_lac = pd.DataFrame({
        "Fonte": ["1° AVS", "2° LPP", t("rac_lacuna_warning", lc)],
        "CHF": [int(avs_stimata), int(lpp_stimata), int(lacuna)],
    })
    fig_lac = px.bar(
        df_lac, x="Fonte", y="CHF",
        color="Fonte",
        color_discrete_map={"1° AVS": "#2980b9", "2° LPP": "#27ae60", t("rac_lacuna_warning", lc): "#e74c3c"},
        template="plotly_white",
        height=280,
    )
    # Objective line at 70% of income
    fig_lac.add_hline(y=reddito_annuo * 0.7, line_dash="dash", line_color="#f39c12",
                      annotation_text="Obiettivo 70%", annotation_position="top right")
    fig_lac.update_layout(showlegend=False, margin=dict(t=20, b=0), xaxis_title="", yaxis_title="CHF/anno")

    lacuna_alert = (
        html.Div(f"⚠️ {t('rac_lacuna_warning', lc)}: CHF {lacuna:,.0f}/anno",
                 className="budget-err", style={"fontWeight": "600"})
        if lacuna > 0
        else html.Div(t("rac_lacuna_ok", lc), className="budget-ok")
    )

    rec_cards = [rec_card(r) for r in raccomandazioni]

    return html.Div([
        html.H4(t("rac_header", lc), style={"marginBottom": "16px"}),
        kpis,
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H5(t("rac_header", lc), style={"fontSize": "1rem", "marginBottom": "12px"}),
                *rec_cards,
            ], width=7),
            dbc.Col([
                html.H5(t("rac_subheader_lacuna", lc), style={"fontSize": "1rem", "marginBottom": "8px"}),
                dcc.Graph(figure=fig_lac, config={"displayModeBar": False}),
                lacuna_alert,
            ], width=5),
        ]),
    ])


# ─────────────────────────────────────────────
# TAB 2 — SIMULATORE
# ─────────────────────────────────────────────

def render_simulatore(lc, eta, reddito_mensile):
    return html.Div([
        html.H4(t("sim_header", lc), style={"marginBottom": "16px"}),
        dbc.Row([
            dbc.Col([html.Label(t("sim_risparmi", lc), style={"fontSize": "12px"}),
                     dcc.Input(id="sim-risparmi", type="number", value=25000, min=0, max=2000000, step=5000, className="form-control")], width=3),
            dbc.Col([html.Label(t("sim_contrib", lc), style={"fontSize": "12px"}),
                     dcc.Input(id="sim-contrib", type="number", value=int(reddito_mensile * 0.15), min=0, max=20000, step=100, className="form-control")], width=3),
            dbc.Col([html.Label(t("sim_rendimento", lc), style={"fontSize": "12px"}),
                     dcc.Slider(id="sim-rend", min=0, max=8, step=0.5, value=4.0, marks={0: "0%", 4: "4%", 8: "8%"})], width=3),
            dbc.Col([html.Label(t("sim_eta_pens", lc), style={"fontSize": "12px"}),
                     dcc.Slider(id="sim-eta-pens", min=55, max=70, step=1, value=65, marks={55: "55", 65: "65", 70: "70"})], width=3),
        ], className="mb-3 g-3"),
        html.Div([
            html.Strong(f"⚡ {t('sim_whatif', lc)}", style={"fontSize": "14px"}),
            dbc.Row([
                dbc.Col(dcc.Checklist(id="sim-shock", options=[{"label": f" {t('sim_shock', lc)}", "value": "shock"}], value=[], inline=True), width=4),
                dbc.Col(dcc.Checklist(id="sim-part", options=[{"label": f" {t('sim_part', lc)}", "value": "part"}], value=[], inline=True), width=4),
                dbc.Col(dcc.Checklist(id="sim-spesa", options=[{"label": f" {t('sim_spesa', lc)}", "value": "spesa"}], value=[], inline=True), width=4),
            ]),
        ], style={"background": "#f8f9fc", "borderRadius": "10px", "padding": "14px", "marginBottom": "16px"}),
        html.Div(id="sim-chart-container"),
        html.Div(id="sim-metrics"),
        dcc.Store(id="sim-eta-store", data=eta),
        dcc.Store(id="sim-reddito-store", data=reddito_mensile),
        dcc.Store(id="sim-lc-store", data=lc),
    ])


@callback(
    Output("sim-chart-container", "children"),
    Output("sim-metrics", "children"),
    Input("sim-risparmi", "value"),
    Input("sim-contrib", "value"),
    Input("sim-rend", "value"),
    Input("sim-eta-pens", "value"),
    Input("sim-shock", "value"),
    Input("sim-part", "value"),
    Input("sim-spesa", "value"),
    Input("sim-eta-store", "data"),
    Input("sim-reddito-store", "data"),
    Input("sim-lc-store", "data"),
    prevent_initial_call=False,
)
def update_simulatore(risparmi_att, contrib_mens, rend_sim, eta_pens,
                      shock_vals, part_vals, spesa_vals, eta, reddito_mensile, lc):
    risparmi_att = risparmi_att or 25000
    contrib_mens = contrib_mens or 800
    rend_sim = rend_sim or 4.0
    eta_pens = eta_pens or 65
    eta = eta or 38
    reddito_mensile = reddito_mensile or 5500
    lc = lc or "it"
    anni_s = max(eta_pens - eta, 1)
    contrib_base = contrib_mens * 12

    def sim_pat(risparmi, contrib, rend, anni, shock_anno=None):
        p = [risparmi]
        for i in range(1, anni + 1):
            c = contrib
            if shock_anno and i == shock_anno:
                c -= 50000
            p.append(max(p[-1] * (1 + rend / 100) + c, 0))
        return p

    pat_base = sim_pat(risparmi_att, contrib_base, rend_sim, anni_s)
    rows_sim = [{"Età": eta + i, "CHF": p, "Scenario": "Base"} for i, p in enumerate(pat_base)]

    if shock_vals:
        rows_sim += [{"Età": eta + i, "CHF": p, "Scenario": t("sim_shock", lc)}
                     for i, p in enumerate(sim_pat(risparmi_att, contrib_base, rend_sim - 2, anni_s))]
    if part_vals:
        rows_sim += [{"Età": eta + i, "CHF": p, "Scenario": t("sim_part", lc)}
                     for i, p in enumerate(sim_pat(risparmi_att, contrib_base * 0.5, rend_sim, anni_s))]
    if spesa_vals:
        rows_sim += [{"Età": eta + i, "CHF": p, "Scenario": t("sim_spesa", lc)}
                     for i, p in enumerate(sim_pat(risparmi_att, contrib_base, rend_sim, anni_s, shock_anno=5))]

    df_sim = pd.DataFrame(rows_sim)
    fig = px.line(df_sim, x="Età", y="CHF", color="Scenario",
                  color_discrete_sequence=["#c0392b", "#3498db", "#27ae60", "#f39c12"],
                  template="plotly_white", height=320)
    fig.add_vline(x=eta_pens, line_dash="dash", line_color="#555")
    fig.update_layout(margin=dict(t=10, b=0), yaxis=dict(tickformat=",.0f"))

    pat_fin = int(pat_base[-1])
    rendita = int(pat_fin * 0.04 / 12)
    copertura = rendita / max(reddito_mensile, 1) * 100

    metrics = dbc.Row([
        dbc.Col(kpi_box(t("sim_patrimonio", lc), f"CHF {pat_fin:,}"), width=3),
        dbc.Col(kpi_box(t("sim_versato", lc), f"CHF {int(contrib_base * anni_s):,}"), width=3),
        dbc.Col(kpi_box(t("sim_rendita", lc), f"CHF {rendita:,}/m"), width=3),
        dbc.Col(kpi_box(t("sim_copertura", lc), f"{copertura:.0f}%",
                        delta="≥ 70% ✓" if copertura >= 70 else "< 70% ⚠️",
                        delta_good=copertura >= 70), width=3),
    ], className="g-3 mt-3")

    return dcc.Graph(figure=fig, config={"displayModeBar": False}), metrics


def kpi_box(label, value, delta=None, delta_good=True):
    delta_el = []
    if delta:
        cls = "kpi-delta good" if delta_good else "kpi-delta bad"
        delta_el = [html.Div(delta, className=cls)]
    return html.Div(
        [html.Div(label, className="kpi-label"), html.Div(value, className="kpi-value"), *delta_el],
        className="kpi-box",
    )


# ─────────────────────────────────────────────
# TAB 3 — NOTE
# ─────────────────────────────────────────────

TEMI_LISTA = [
    ("❤️", "Assicurazione Vita"), ("🦽", "Invalidità"), ("🤒", "Perdita di Guadagno"),
    ("🩹", "Infortuni"), ("🛡️", "RC Privata"), ("💊", "Krankenkasse"),
    ("🏥", "Complementare Ospedaliera"), ("🏦", "3° Pilastro"), ("🏢", "Revisione LPP"),
    ("🏡", "Budget familiare"), ("🎯", "Obiettivi di vita"), ("📈", "Simulatore"),
]


def render_note(lc, nome, eta, situazione, store):
    temi_checks = [
        dcc.Checklist(
            id=f"tema-{i}",
            options=[{"label": f" {ico} {nome_t}", "value": nome_t}],
            value=[],
            style={"fontSize": "13px", "marginBottom": "4px"},
        )
        for i, (ico, nome_t) in enumerate(TEMI_LISTA)
    ]
    urgenza_opts = t("note_urgenza_opt", lc)

    return html.Div([
        html.H4(t("note_header", lc), style={"marginBottom": "16px"}),
        dbc.Row([
            dbc.Col([
                html.H6(f"✏️ {t('note_appunti', lc)}"),
                dcc.Textarea(id="note-libere", placeholder="...", style={"width": "100%", "height": "140px", "borderRadius": "8px", "border": "1px solid #ddd", "padding": "10px", "fontSize": "13px"}),
                html.H6(f"☑️ {t('note_temi', lc)}", style={"marginTop": "16px"}),
                *temi_checks,
                html.H6(f"📌 {t('note_passi', lc)}", style={"marginTop": "12px"}),
                dcc.Textarea(id="note-passi", placeholder="...", style={"width": "100%", "height": "90px", "borderRadius": "8px", "border": "1px solid #ddd", "padding": "10px", "fontSize": "13px"}),
                html.Label(t("note_urgenza", lc), style={"fontSize": "12px", "marginTop": "10px"}),
                dcc.Slider(id="note-urgenza", min=0, max=2, step=1, value=1,
                           marks={0: urgenza_opts[0], 1: urgenza_opts[1], 2: urgenza_opts[2]}),
            ], width=6),
            dbc.Col([
                html.H6(f"📄 {t('note_riepilogo', lc)}"),
                html.Div(id="note-riepilogo-box"),
                html.Hr(),
                html.H6(t("email_header", lc)),
                dbc.Accordion([
                    dbc.AccordionItem([
                        dbc.Row([
                            dbc.Col([html.Label("SMTP Server", style={"fontSize": "12px"}),
                                     dcc.Input(id="smtp-server", type="text", value="smtp.gmail.com", className="form-control")], width=6),
                            dbc.Col([html.Label("Porta", style={"fontSize": "12px"}),
                                     dcc.Input(id="smtp-port", type="number", value=587, className="form-control")], width=3),
                        ], className="mb-2"),
                        dbc.Row([
                            dbc.Col([html.Label("Email mittente", style={"fontSize": "12px"}),
                                     dcc.Input(id="smtp-user", type="email", placeholder="tuoindirizzo@gmail.com", className="form-control")], width=6),
                            dbc.Col([html.Label("Password", style={"fontSize": "12px"}),
                                     dcc.Input(id="smtp-pass", type="password", className="form-control")], width=6),
                        ]),
                    ], title="⚙️ Configurazione SMTP"),
                ], start_collapsed=True, style={"marginBottom": "12px"}),
                dcc.Input(id="email-dest", type="email", placeholder=t("email_ph", lc), className="form-control", style={"marginBottom": "8px"}),
                dcc.Input(id="email-oggetto", type="text", value=t("email_oggetto_default", lc), className="form-control", style={"marginBottom": "8px"}),
                dbc.Button(t("email_btn", lc), id="email-btn", color="danger", className="w-100"),
                html.Div(id="email-feedback", style={"marginTop": "8px"}),
                # hidden stores to pass profile data
                dcc.Store(id="note-lc-store", data=lc),
                dcc.Store(id="note-nome-store", data=nome),
                dcc.Store(id="note-eta-store", data=eta),
                dcc.Store(id="note-sit-store", data=situazione),
                dcc.Store(id="note-store-data", data=store),
            ], width=6),
        ]),
    ])


@callback(
    Output("note-riepilogo-box", "children"),
    Input("note-libere", "value"),
    Input("note-passi", "value"),
    Input("note-urgenza", "value"),
    Input("note-lc-store", "data"),
    Input("note-nome-store", "data"),
    Input("note-eta-store", "data"),
    Input("note-sit-store", "data"),
    Input("note-store-data", "data"),
    *[Input(f"tema-{i}", "value") for i in range(len(TEMI_LISTA))],
    prevent_initial_call=False,
)
def update_riepilogo(note_libere, prossimi, urgenza_idx, lc, nome, eta, situazione, store, *temi_vals):
    lc = lc or "it"
    nome = nome or "Cliente"
    eta = eta or 38
    situazione = situazione or "Dipendente"
    store = store or {}
    canton = store.get("canton", "Ticino")
    reddito_mensile = store.get("reddito_mensile", 5500)
    profilo = store

    urgenza_opts = t("note_urgenza_opt", lc)
    urgenza = urgenza_opts[urgenza_idx or 1]

    temi_disc = []
    for vals in temi_vals:
        if vals:
            temi_disc.extend(vals)

    rac_alta = [r for r in calcola_raccomandazioni(profilo) if "Alta" in r["priorita"]]

    oggi = date.today().strftime("%d/%m/%Y")
    figli_info = f"Sì ({store.get('n_figli', 0)})" if store.get("figli") else "No"
    ipot_info = "Sì" if store.get("ipoteca") else "No"

    txt = f"""{'='*50}
RIEPILOGO COLLOQUIO — {nome}
Data: {oggi}
{'='*50}

PROFILO
Età: {eta} | {situazione} | Canton {canton}
Reddito mensile: CHF {reddito_mensile:,}
Figli: {figli_info} | Ipoteca: {ipot_info}

PRIORITÀ ALTA
{chr(10).join(['• '+r['prodotto']+' — '+r['motivo'] for r in rac_alta]) if rac_alta else '• Nessuna urgenza immediata'}

TEMI DISCUSSI
{chr(10).join(['• '+tn for tn in temi_disc]) if temi_disc else '• —'}

PROSSIMI PASSI
{prossimi or '—'}

NOTE
{note_libere or '—'}

URGENZA: {urgenza}
{'='*50}
AlexFin · SVAG · {oggi}
"""
    return html.Pre(txt, style={"background": "#f8f9fc", "borderRadius": "8px", "padding": "14px",
                                "fontSize": "11px", "maxHeight": "340px", "overflowY": "auto",
                                "border": "1px solid #eee", "whiteSpace": "pre-wrap"})


@callback(
    Output("email-feedback", "children"),
    Input("email-btn", "n_clicks"),
    State("email-dest", "value"),
    State("email-oggetto", "value"),
    State("smtp-server", "value"),
    State("smtp-port", "value"),
    State("smtp-user", "value"),
    State("smtp-pass", "value"),
    State("note-libere", "value"),
    State("note-passi", "value"),
    State("note-store-data", "data"),
    prevent_initial_call=True,
)
def send_email(n, dest, oggetto, smtp_server, smtp_port, smtp_user, smtp_pass,
               note_libere, prossimi, store):
    if not dest:
        return html.Div("Inserisci l'email del destinatario.", className="budget-warn")
    if not smtp_user or not smtp_pass:
        return html.Div("⚠️ Configura le credenziali SMTP.", className="budget-warn")
    store = store or {}
    nome = store.get("nome", "Cliente") or "Cliente"
    eta = store.get("eta", 38)
    situazione = store.get("situazione", "Dipendente")
    canton = store.get("canton", "Ticino")
    reddito_mensile = store.get("reddito_mensile", 5500)
    rac_alta = [r for r in calcola_raccomandazioni(store) if "Alta" in r["priorita"]]
    oggi = date.today().strftime("%d/%m/%Y")
    body_html = f"""
<html><body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:auto">
<div style="background:#c0392b;padding:20px;border-radius:8px 8px 0 0">
  <h2 style="color:white;margin:0">🇨🇭 AlexFin — Analisi Patrimoniale</h2>
  <p style="color:#fcc;margin:4px 0">Riepilogo colloquio per {nome}</p>
</div>
<div style="background:#f9f9f9;padding:24px;border:1px solid #eee;border-radius:0 0 8px 8px">
  <h3>👤 Profilo</h3>
  <ul>
    <li>Età: <b>{eta}</b> anni | {situazione} | Canton {canton}</li>
    <li>Reddito mensile: <b>CHF {reddito_mensile:,}</b></li>
  </ul>
  <h3>🔴 Priorità Alta</h3>
  <ul>{"".join(["<li><b>"+r["prodotto"]+"</b> — "+r["motivo"]+"</li>" for r in rac_alta]) if rac_alta else "<li>Nessuna urgenza immediata</li>"}</ul>
  <h3>📌 Prossimi passi</h3>
  <p>{(prossimi or "—").replace(chr(10),"<br>")}</p>
  <hr>
  <p style="color:#888;font-size:12px">Generato da AlexFin Advisor Tool · SVAG · {oggi}</p>
</div></body></html>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = oggetto or "Analisi patrimoniale – AlexFin"
        msg["From"] = smtp_user
        msg["To"] = dest
        msg.attach(MIMEText(body_html, "html"))
        with smtplib.SMTP(smtp_server or "smtp.gmail.com", smtp_port or 587) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.sendmail(smtp_user, dest, msg.as_string())
        return html.Div(f"✅ Email inviata a {dest}", className="budget-ok")
    except Exception as e:
        return html.Div(f"❌ Errore: {e}", className="budget-err")


# ─────────────────────────────────────────────
# TAB 4 — CRM
# ─────────────────────────────────────────────

def render_crm(lc, store):
    nome_profilo = store.get("nome", "")
    return html.Div([
        html.H4(f"📋 {t('adv_clienti_recenti', lc)}", style={"marginBottom": "16px"}),
        dbc.Row([
            dbc.Col([
                html.Div(id="crm-list"),
                dcc.Store(id="crm-lc-store", data=lc),
                dcc.Store(id="crm-profilo-store", data=store),
            ], width=8),
            dbc.Col([
                html.H6(t("adv_salva_cliente", lc)),
                dbc.Button(
                    f"💾 {t('adv_salva_cliente', lc)}",
                    id="crm-save-btn",
                    color="danger",
                    disabled=not bool(nome_profilo),
                    className="w-100 mb-3",
                ),
                html.Div(id="crm-save-feedback"),
                html.Hr(),
                html.H6(t("adv_note_sessione", lc)),
                dcc.Textarea(placeholder="Appunti interni...", style={"width": "100%", "height": "120px",
                             "borderRadius": "8px", "border": "1px solid #ddd", "padding": "10px", "fontSize": "13px"}),
            ], width=4),
        ]),
    ])


@callback(
    Output("crm-list", "children"),
    Input("crm-save-btn", "n_clicks"),
    State("crm-profilo-store", "data"),
    State("crm-lc-store", "data"),
    prevent_initial_call=False,
)
def update_crm_list(n_clicks, store, lc):
    lc = lc or "it"
    store = store or {}
    if n_clicks and store.get("nome"):
        clienti = carica_clienti()
        entry = {**store, "data": date.today().strftime("%d/%m/%Y")}
        existing = next((i for i, c in enumerate(clienti) if c.get("nome") == store["nome"]), None)
        if existing is not None:
            clienti[existing] = entry
        else:
            clienti.append(entry)
        salva_clienti(clienti)

    clienti = carica_clienti()
    if not clienti:
        return html.Div(t("adv_nessun_cliente", lc), className="budget-warn")

    items = []
    for c in reversed(clienti[-20:]):
        items.append(
            dbc.Card([
                dbc.CardHeader(f"👤 {c.get('nome','—')} — {c.get('data','—')} · {c.get('canton','—')}",
                               style={"cursor": "pointer", "fontWeight": "600"}),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.Div([html.Div("Età", className="kpi-label"), html.Div(str(c.get("eta", "—")), className="kpi-value")], className="kpi-box"), width=4),
                        dbc.Col(html.Div([html.Div("Reddito/m", className="kpi-label"), html.Div(f"CHF {c.get('reddito_mensile', 0):,}", className="kpi-value")], className="kpi-box"), width=4),
                        dbc.Col(html.Div([html.Div("Situazione", className="kpi-label"), html.Div(c.get("situazione", "—"), className="kpi-value", style={"fontSize": "1rem"})], className="kpi-box"), width=4),
                    ], className="g-2"),
                ], style={"padding": "12px"}),
            ], style={"marginBottom": "10px", "border": "1px solid #eef0f4"})
        )
    return html.Div([html.P(f"{len(clienti)} {t('adv_n_clienti', lc)}", style={"color": "#666", "fontSize": "13px"}), *items])


@callback(
    Output("crm-save-feedback", "children"),
    Input("crm-save-btn", "n_clicks"),
    State("crm-profilo-store", "data"),
    State("crm-lc-store", "data"),
    prevent_initial_call=True,
)
def crm_save_feedback(n_clicks, store, lc):
    lc = lc or "it"
    store = store or {}
    nome = store.get("nome", "")
    if nome:
        return html.Div(f"✅ {t('adv_salvato', lc)}: {nome}", className="budget-ok")
    return html.Div("Inserisci il nome nella sidebar.", className="budget-warn")
