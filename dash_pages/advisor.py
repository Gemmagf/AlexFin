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
from dash import callback, dcc, html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc

from i18n import t
from products import calcola_raccomandazioni
from sources import sources_footer
from pdf_report import genera_pdf

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


def rec_card(r, lc="it"):
    prio = r["priorita"]  # internal code: "Alta" / "Raccomandata" / "Opzionale"
    if prio == "Alta":
        card_cls, badge_cls = "alexfin-card card-alta", "badge-alta"
        badge_lbl = t("rac_prio_alta", lc)
    elif prio == "Raccomandata":
        card_cls, badge_cls = "alexfin-card card-racc", "badge-racc"
        badge_lbl = t("rac_prio_racc", lc)
    else:
        card_cls, badge_cls = "alexfin-card card-opz", "badge-opz"
        badge_lbl = t("rac_prio_opz", lc)
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        f"{r['icona']} {r['prodotto']}",
                        style={"fontWeight": "700", "fontSize": "0.95rem",
                               "color": "#1e2235", "flex": "1", "minWidth": "0",
                               "overflow": "hidden", "textOverflow": "ellipsis",
                               "whiteSpace": "nowrap"},
                    ),
                    html.Span(badge_lbl, className=badge_cls,
                              style={"flexShrink": "0", "marginLeft": "8px",
                                     "fontSize": "0.7rem", "whiteSpace": "nowrap"}),
                ],
                style={"display": "flex", "justifyContent": "space-between",
                       "alignItems": "center", "marginBottom": "8px"},
            ),
            html.P(r["motivo"],
                   style={"color": "#555", "fontSize": "0.85rem",
                          "lineHeight": "1.5", "margin": "0",
                          "wordBreak": "break-word"}),
        ],
        className=card_cls,
        style={"minHeight": "80px"},
    )


# ─────────────────────────────────────────────
# PAGE LAYOUT
# ─────────────────────────────────────────────

def layout():
    return html.Div([
        html.Div(id="adv-header"),
        html.Div(id="adv-tabs-container"),
        html.Div(id="adv-tab-content"),

        # Note state stores (to avoid circular deps)
        dcc.Store(id="note-libere-store", data=""),
        dcc.Store(id="temi-store", data=[]),
        dcc.Store(id="crm-trigger", data=0),
        dcc.Store(id="email-status", data=""),

        # PDF download component (lives outside tabs so it always exists in DOM)
        dcc.Download(id="pdf-download"),
    ])


# ─────────────────────────────────────────────
# HEADER CALLBACK
# ─────────────────────────────────────────────

@callback(
    Output("adv-header", "children"),
    Output("adv-tabs-container", "children"),
    Input("app-store", "data")
)
def render_header(store):
    if not store:
        store = {}
    lc = store.get("lc", "it")
    nome = store.get("nome", "") or "Cliente"
    eta = store.get("eta", 38)
    sit = store.get("situazione", "Dipendente")
    canton = store.get("canton", "Ticino")
    reddito = store.get("reddito_mensile", 5500)
    header = html.Div([
        html.H1(f"🧑‍💼 {t('adv_title', lc)}", className="page-title"),
        html.P(f"{nome} · {eta} {t('adv_anni', lc)} · {sit} · {canton} · CHF {reddito:,}/m", className="page-subtitle"),
        html.Hr(),
    ])
    tabs = dbc.Tabs(
        [
            dbc.Tab(label=t("tab_rac", lc), tab_id="tab-rac"),
            dbc.Tab(label=t("tab_sim", lc), tab_id="tab-sim"),
            dbc.Tab(label=t("tab_note", lc), tab_id="tab-note"),
            dbc.Tab(label="📋 CRM", tab_id="tab-crm"),
        ],
        id="adv-tabs",
        active_tab="tab-rac",
        style={"marginBottom": "20px"},
    )
    return header, tabs


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

    footer = sources_footer("advisor")
    if active_tab == "tab-rac":
        return html.Div([render_raccomandazioni(store, lc, eta, reddito_mensile, reddito_annuo, situazione, anni_pensionamento), footer])
    elif active_tab == "tab-sim":
        return html.Div([render_simulatore(lc, eta, reddito_mensile), footer])
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

    raccomandazioni = calcola_raccomandazioni(store, lc)

    # Bar chart AVS/LPP/Lacuna
    _lac_lbl = t("rac_lacuna_warning", lc)
    df_lac = pd.DataFrame({
        "Fonte": ["1° AVS", "2° LPP", _lac_lbl],
        "CHF": [int(avs_stimata), int(lpp_stimata), int(lacuna)],
    })
    fig_lac = px.bar(
        df_lac, x="Fonte", y="CHF",
        color="Fonte",
        color_discrete_map={"1° AVS": "#2980b9", "2° LPP": "#27ae60", _lac_lbl: "#e74c3c"},
        labels={"Fonte": t("rac_fonte", lc), "CHF": "CHF"},
        template="plotly_white",
        height=280,
    )
    # Objective line at 70% of income
    fig_lac.add_hline(y=reddito_annuo * 0.7, line_dash="dash", line_color="#f39c12",
                      annotation_text=t("lacuna_obj", lc), annotation_position="top right")
    fig_lac.update_layout(showlegend=False, margin=dict(t=20, b=0), xaxis_title="", yaxis_title=t("adv_chf_anno", lc))

    lacuna_alert = (
        html.Div(f"⚠️ {t('rac_lacuna_warning', lc)}: CHF {lacuna:,.0f}/anno",
                 className="budget-err", style={"fontWeight": "600"})
        if lacuna > 0
        else html.Div(t("rac_lacuna_ok", lc), className="budget-ok")
    )

    rec_cards = [rec_card(r, lc) for r in raccomandazioni]

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
# TAB 2 — SIMULATORE SCENARI DI RISCHIO
# ─────────────────────────────────────────────

def render_simulatore(lc, eta, reddito_mensile):
    return html.Div([
        html.H4(t("sim_header", lc), style={"marginBottom": "6px"}),
        html.P(t("sim_risk_subtitle", lc),
               style={"color": "#666", "fontSize": "13px", "marginBottom": "20px"}),
        dbc.Row([
            dbc.Col([
                html.Label(t("sim_scenario_lbl", lc),
                           style={"fontSize": "12px", "fontWeight": "600", "marginBottom": "8px"}),
                dcc.RadioItems(
                    id="sim-scenario-type",
                    options=[
                        {"label": f" 🤒  {t('sim_scen_malattia', lc)}", "value": "malattia"},
                        {"label": f" 🦽  {t('sim_scen_invalidita', lc)}", "value": "invalidita"},
                        {"label": f" 💼  {t('sim_scen_atur', lc)}", "value": "atur"},
                    ],
                    value="malattia",
                    inputStyle={"marginRight": "6px"},
                    labelStyle={"display": "block", "marginBottom": "10px", "fontSize": "13px"},
                ),
            ], md=4),
            dbc.Col([
                html.Label(t("sim_dipendenti_label", lc), style={"fontSize": "12px"}),
                dcc.RadioItems(
                    id="sim-con-dipendenti",
                    options=[{"label": " No", "value": "no"},
                             {"label": f" {t('sidebar_figli_opt', lc)[1]}", "value": "si"}],
                    value="no",
                    inline=True,
                    style={"fontSize": "13px", "marginBottom": "16px"},
                ),
                html.Label(t("sim_grado_inval_label", lc), style={"fontSize": "12px"}),
                dcc.Slider(
                    id="sim-grado-inv",
                    min=25, max=100, step=25, value=50,
                    marks={25: "25%", 50: "50%", 75: "75%", 100: "100%"},
                    tooltip={"always_visible": False},
                ),
            ], md=4),
            dbc.Col([
                html.Div(id="sim-scenario-info",
                         style={"background": "#f8f9fc", "borderRadius": "10px",
                                "padding": "14px", "fontSize": "12px", "color": "#555",
                                "lineHeight": "1.6"}),
            ], md=4),
        ], className="mb-3 g-3"),
        html.Div(id="sim-chart-container"),
        html.Div(id="sim-metrics"),
        dcc.Store(id="sim-eta-store", data=eta),
        dcc.Store(id="sim-reddito-store", data=reddito_mensile),
        dcc.Store(id="sim-lc-store", data=lc),
    ])


@callback(
    Output("sim-chart-container", "children"),
    Output("sim-metrics", "children"),
    Output("sim-scenario-info", "children"),
    Input("sim-scenario-type", "value"),
    Input("sim-con-dipendenti", "value"),
    Input("sim-grado-inv", "value"),
    Input("sim-eta-store", "data"),
    Input("sim-reddito-store", "data"),
    Input("sim-lc-store", "data"),
    prevent_initial_call=False,
)
def update_simulatore(scenario, con_dip, grado_inv, eta, reddito_mensile, lc):
    scenario = scenario or "malattia"
    con_dip = con_dip or "no"
    grado_inv = grado_inv or 50
    eta = eta or 38
    reddito_mensile = reddito_mensile or 5500
    lc = lc or "it"

    months = list(range(0, 25))   # default 24-month window

    # ── Swiss social insurance parameters (2026) ──────────────────────────
    AVS_AI_MAX = 2520          # CHF/month max AI full pension
    ALV_MAX_SALARY = 12350     # CHF/month (CHF 148,200/year insured ceiling)

    if scenario == "malattia":
        # Employer/Taggeld insurance: 80% for up to 730 days (~24 months)
        pct_cop = 0.80
        copertura = [reddito_mensile * pct_cop] * len(months)
        gap_vals  = [reddito_mensile * (1 - pct_cop)] * len(months)
        durata_mesi = 24
        prodotto = f"🤒 Taggeldversicherung — {t('rac_prod_perdita', lc)}"
        info_lines = [
            f"📋 Datore di lavoro copre 80% per 730 gg (~24 mesi).",
            f"⚠️ Gap mensile: CHF {reddito_mensile * 0.20:,.0f}/mese.",
            f"💡 Soluzione: indennità giornaliera complementare.",
        ]

    elif scenario == "invalidita":
        months = list(range(0, 37))   # 36-month view — AI kicks in ~month 12
        ai_full = min(AVS_AI_MAX, reddito_mensile * 0.60)
        lpp_dis  = min(reddito_mensile * 0.35, 1800)          # simplified 2nd pillar
        benefit  = (ai_full + lpp_dis) * (grado_inv / 100)
        # First 12 months: waiting period (only employer salary obligation ~3 months)
        copertura = []
        for m in months:
            if m < 3:
                copertura.append(reddito_mensile * 0.80)   # employer obligation
            elif m < 12:
                copertura.append(0.0)                       # gap period
            else:
                copertura.append(benefit)                   # AI + LPP
        gap_vals    = [max(reddito_mensile - c, 0) for c in copertura]
        durata_mesi = None   # permanent once established
        prodotto = f"🦽 AI + LPP + {t('rac_prod_invalidita', lc)}"
        info_lines = [
            f"📋 AI max CHF {AVS_AI_MAX:,}/mese al 100%.",
            f"⚠️ Attesa AI: ~12 mesi. Gap totale periodo attesa: CHF {sum(gap_vals[:12]):,.0f}.",
            f"💡 Grado {grado_inv}% → benefit stimato CHF {benefit:,.0f}/mese.",
        ]

    else:   # atur / unemployment
        pct_alv   = 0.80 if con_dip == "si" else 0.70
        alv_base  = min(reddito_mensile, ALV_MAX_SALARY) * pct_alv
        alv_days  = 520 if con_dip == "si" else 400   # days
        alv_months = round(alv_days / 30)
        copertura = [alv_base if m < alv_months else 0.0 for m in months]
        gap_vals  = [reddito_mensile - c for c in copertura]
        durata_mesi = alv_months
        pct_lbl   = "80%" if con_dip == "si" else "70%"
        prodotto  = f"💼 ALV {pct_lbl} + {t('rac_prod_3a', lc)}"
        info_lines = [
            f"📋 ALV: {pct_lbl} del salario assicurato per {alv_days} giorni (~{alv_months} mesi).",
            f"⚠️ Tetto ALV: CHF {ALV_MAX_SALARY:,}/mese. Benefit: CHF {alv_base:,.0f}/mese.",
            f"💡 Dopo {alv_months} mesi: reddito zero. Riserva liquida essenziale.",
        ]

    # ── Chart ─────────────────────────────────────────────────────────────
    _x_lbl   = t("sim_dopo_evento", lc)
    _red_lbl = t("sim_reddito_attuale", lc)
    _cop_lbl = t("sim_copertura_lbl", lc)
    _gap_lbl = t("sim_gap_lbl", lc)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=[reddito_mensile] * len(months),
        name=_red_lbl, mode="lines",
        line=dict(color="#2c3e50", width=2, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=months, y=copertura,
        name=_cop_lbl, mode="lines",
        fill="tozeroy", fillcolor="rgba(39,174,96,0.15)",
        line=dict(color="#27ae60", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=months, y=gap_vals,
        name=_gap_lbl, mode="lines",
        fill="tozeroy", fillcolor="rgba(231,76,60,0.12)",
        line=dict(color="#e74c3c", width=2),
    ))
    if durata_mesi and durata_mesi <= max(months):
        fig.add_vline(x=durata_mesi, line_dash="dash", line_color="#f39c12",
                      annotation_text="Fine copertura", annotation_position="top right")
    fig.update_layout(
        template="plotly_white", height=300,
        margin=dict(t=10, b=0),
        xaxis_title=_x_lbl,
        yaxis=dict(tickformat=",.0f", title="CHF/mese"),
        legend=dict(orientation="h", y=-0.30),
    )

    # ── KPIs ──────────────────────────────────────────────────────────────
    gap_peak   = max(gap_vals)
    gap_medio  = sum(gap_vals) / len(gap_vals)
    tot_cop    = sum(copertura)
    tot_red    = reddito_mensile * len(months)
    pct_cop_kpi = (tot_cop / tot_red * 100) if tot_red > 0 else 0

    dur_label = f"{durata_mesi} m" if durata_mesi else "∞ (AI)"

    metrics = dbc.Row([
        dbc.Col(kpi_box(
            t("sim_gap_mensile", lc), f"CHF {gap_peak:,.0f}/m",
            delta="⚠️ Gap presente" if gap_peak > 0 else "✓ Coperto",
            delta_good=(gap_peak == 0),
        ), width=3),
        dbc.Col(kpi_box(
            t("sim_copertura", lc), f"{pct_cop_kpi:.0f}%",
            delta="≥ 80% ✓" if pct_cop_kpi >= 80 else "< 80% ⚠️",
            delta_good=(pct_cop_kpi >= 80),
        ), width=3),
        dbc.Col(kpi_box(t("sim_durata_copertura", lc), dur_label), width=3),
        dbc.Col(kpi_box(t("sim_prodotto_racc", lc), prodotto), width=3),
    ], className="g-3 mt-3")

    # ── Info box ──────────────────────────────────────────────────────────
    info_box = html.Div([html.Div(line) for line in info_lines])

    return dcc.Graph(figure=fig, config={"displayModeBar": False}), metrics, info_box


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

TEMI_LISTA_KEYS = [
    ("❤️", "temi_vita"), ("🦽", "temi_invalidita"), ("🤒", "temi_perdita"),
    ("🩹", "temi_infortuni"), ("🛡️", "temi_rc"), ("💊", "temi_kk"),
    ("🏥", "temi_spital"), ("🏦", "temi_3a"), ("🏢", "temi_lpp"),
    ("🏡", "temi_budget"), ("🎯", "temi_obiettivi"), ("📈", "temi_sim"),
]


def render_note(lc, nome, eta, situazione, store):
    temi_checks = [
        dcc.Checklist(
            id=f"tema-{i}",
            options=[{"label": f" {ico} {t(key, lc)}", "value": t(key, lc)}],
            value=[],
            style={"fontSize": "13px", "marginBottom": "4px"},
        )
        for i, (ico, key) in enumerate(TEMI_LISTA_KEYS)
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
                dbc.Button(
                    t("pdf_btn", lc),
                    id="pdf-btn",
                    color="danger",
                    outline=True,
                    size="sm",
                    className="w-100 mb-2 mt-2",
                ),
                html.Div(id="pdf-feedback", style={"fontSize": "12px", "marginBottom": "8px"}),
                html.Hr(),
                html.H6(t("email_header", lc)),
                dbc.Accordion([
                    dbc.AccordionItem([
                        dbc.Row([
                            dbc.Col([html.Label("SMTP Server", style={"fontSize": "12px"}),
                                     dcc.Input(id="smtp-server", type="text", value="smtp.gmail.com", className="form-control")], width=6),
                            dbc.Col([html.Label(t("smtp_porta", lc), style={"fontSize": "12px"}),
                                     dcc.Input(id="smtp-port", type="number", value=587, className="form-control")], width=3),
                        ], className="mb-2"),
                        dbc.Row([
                            dbc.Col([html.Label(t("smtp_mittente", lc), style={"fontSize": "12px"}),
                                     dcc.Input(id="smtp-user", type="email", placeholder="tuoindirizzo@gmail.com", className="form-control")], width=6),
                            dbc.Col([html.Label("Password", style={"fontSize": "12px"}),
                                     dcc.Input(id="smtp-pass", type="password", className="form-control")], width=6),
                        ]),
                    ], title=f"⚙️ {t('email_header', lc)}"),
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
    *[Input(f"tema-{i}", "value") for i in range(len(TEMI_LISTA_KEYS))],
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

    rac_alta = [r for r in calcola_raccomandazioni(profilo, lc or "it") if r["priorita"] == "Alta"]

    oggi = date.today().strftime("%d/%m/%Y")
    figli_info = f"Sì ({store.get('n_figli', 0)})" if store.get("figli") else "No"
    ipot_info = "Sì" if store.get("ipoteca") else "No"

    txt = f"""{'='*50}
{t('rie_titolo', lc)} — {nome}
{oggi}
{'='*50}

{t('rie_profilo', lc)}
{t('crm_eta', lc)}: {eta} | {situazione} | Canton {canton}
{t('crm_reddito', lc)}: CHF {reddito_mensile:,}

{t('rie_prio', lc)}
{chr(10).join(['• '+r['prodotto']+' — '+r['motivo'] for r in rac_alta]) if rac_alta else '• —'}

{t('rie_temi', lc)}
{chr(10).join(['• '+tn for tn in temi_disc]) if temi_disc else '• —'}

{t('rie_passi', lc)}
{prossimi or '—'}

{t('rie_note', lc)}
{note_libere or '—'}

{t('rie_urgenza', lc)}: {urgenza}
{'='*50}
AlexFin · SVAG · {oggi}
"""
    return html.Pre(txt, style={"background": "#f8f9fc", "borderRadius": "8px", "padding": "14px",
                                "fontSize": "11px", "maxHeight": "340px", "overflowY": "auto",
                                "border": "1px solid #eee", "whiteSpace": "pre-wrap"})


@callback(
    Output("pdf-download", "data"),
    Output("pdf-feedback", "children"),
    Input("pdf-btn", "n_clicks"),
    State("note-store-data", "data"),
    prevent_initial_call=True,
)
def download_pdf(n_clicks, store):
    store = store or {}
    nome  = store.get("nome") or "Cliente"
    try:
        pdf_bytes = genera_pdf(store=store)
        oggi = date.today().strftime("%Y%m%d")
        filename = f"AlexFin_{nome.replace(' ', '_')}_{oggi}.pdf"
        feedback = html.Div(f"✅ PDF generato: {filename}", style={"color": "#27ae60", "fontSize": "12px"})
        return dcc.send_bytes(pdf_bytes, filename), feedback
    except Exception as e:
        feedback = html.Div(f"❌ Errore PDF: {e}", style={"color": "#e74c3c", "fontSize": "12px"})
        return dash.no_update, feedback


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
    store = store or {}
    lc = store.get("lc", "it")
    if not dest:
        return html.Div(t("email_err_dest", lc), className="budget-warn")
    if not smtp_user or not smtp_pass:
        return html.Div(t("email_err_smtp_cfg", lc), className="budget-warn")
    nome = store.get("nome", "Cliente") or "Cliente"
    eta = store.get("eta", 38)
    situazione = store.get("situazione", "Dipendente")
    canton = store.get("canton", "Ticino")
    reddito_mensile = store.get("reddito_mensile", 5500)
    rac_alta = [r for r in calcola_raccomandazioni(store, lc) if r["priorita"] == "Alta"]
    oggi = date.today().strftime("%d/%m/%Y")
    body_html = f"""
<html><body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:auto">
<div style="background:#c0392b;padding:20px;border-radius:8px 8px 0 0">
  <h2 style="color:white;margin:0">AlexFin — {t('rie_titolo', lc)}</h2>
  <p style="color:#fcc;margin:4px 0">{nome}</p>
</div>
<div style="background:#f9f9f9;padding:24px;border:1px solid #eee;border-radius:0 0 8px 8px">
  <h3>{t('rie_profilo', lc)}</h3>
  <ul>
    <li>{t('crm_eta', lc)}: <b>{eta}</b> {t('adv_anni', lc)} | {situazione} | Canton {canton}</li>
    <li>{t('crm_reddito', lc)}: <b>CHF {reddito_mensile:,}</b></li>
  </ul>
  <h3>{t('rie_prio', lc)}</h3>
  <ul>{"".join(["<li><b>"+r["prodotto"]+"</b> — "+r["motivo"]+"</li>" for r in rac_alta]) if rac_alta else "<li>—</li>"}</ul>
  <h3>{t('rie_passi', lc)}</h3>
  <p>{(prossimi or "—").replace(chr(10),"<br>")}</p>
  <hr>
  <p style="color:#888;font-size:12px">AlexFin Advisor Tool · SVAG · {oggi}</p>
</div></body></html>"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = oggetto or f"AlexFin — {t('rie_titolo', lc)}"
        msg["From"] = smtp_user
        msg["To"] = dest
        msg.attach(MIMEText(body_html, "html"))
        with smtplib.SMTP(smtp_server or "smtp.gmail.com", smtp_port or 587) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.sendmail(smtp_user, dest, msg.as_string())
        return html.Div(f"{t('email_ok', lc)} {dest}", className="budget-ok")
    except Exception as e:
        return html.Div(f"{t('email_err', lc)}: {e}", className="budget-err")


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
                dcc.Textarea(placeholder=t("crm_appunti", lc), style={"width": "100%", "height": "120px",
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
        nome_c = c.get("nome", "")
        items.append(
            dbc.Card([
                dbc.CardHeader(
                    dbc.Row([
                        dbc.Col(f"👤 {nome_c} — {c.get('data','—')} · {c.get('canton','—')}",
                                style={"fontWeight": "600", "alignSelf": "center"}),
                        dbc.Col(
                            dbc.Button(
                                f"📂 {t('adv_carica', lc)}",
                                id={"type": "crm-load-btn", "index": nome_c},
                                color="danger",
                                outline=True,
                                size="sm",
                                n_clicks=0,
                            ),
                            width="auto",
                        ),
                    ], align="center", justify="between"),
                ),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.Div([html.Div(t("crm_eta", lc), className="kpi-label"), html.Div(str(c.get("eta", "—")), className="kpi-value")], className="kpi-box"), width=4),
                        dbc.Col(html.Div([html.Div(t("crm_reddito", lc), className="kpi-label"), html.Div(f"CHF {c.get('reddito_mensile', 0):,}", className="kpi-value")], className="kpi-box"), width=4),
                        dbc.Col(html.Div([html.Div(t("crm_situazione", lc), className="kpi-label"), html.Div(c.get("situazione", "—"), className="kpi-value", style={"fontSize": "1rem"})], className="kpi-box"), width=4),
                    ], className="g-2"),
                ], style={"padding": "12px"}),
            ], style={"marginBottom": "10px", "border": "1px solid #eef0f4"})
        )
    return html.Div([html.P(f"{len(clienti)} {t('adv_n_clienti', lc)}", style={"color": "#666", "fontSize": "13px"}), *items])


@callback(
    Output("crm-load-store", "data"),
    Input({"type": "crm-load-btn", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def crm_load_client(n_clicks_list):
    """Load a CRM client into the sidebar by writing their data to crm-load-store."""
    if not n_clicks_list or not any(n for n in n_clicks_list if n):
        return dash.no_update
    triggered = ctx.triggered_id
    if not triggered:
        return dash.no_update
    nome = triggered.get("index", "")
    clienti = carica_clienti()
    match = next((c for c in clienti if c.get("nome") == nome), None)
    return match if match else dash.no_update


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
