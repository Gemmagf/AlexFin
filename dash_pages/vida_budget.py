# dash_pages/vida_budget.py — Vita & Budget Familiare
# Tabs: Budget, Fasi di vita, Obiettivi

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import callback, dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc

from i18n import t
from sources import sources_footer

dash.register_page(__name__, path="/vida-budget", name="Vita & Budget")


def layout():
    return html.Div([
        html.Div(id="vb-header"),
        html.Div(id="vb-tabs-container"),
        html.Div(id="vb-tab-content"),
    ])


@callback(
    Output("vb-header", "children"),
    Output("vb-tabs-container", "children"),
    Input("app-store", "data")
)
def render_header(store):
    if not store:
        store = {}
    lc = store.get("lc", "it")
    header = html.Div([
        html.H1(f"🏡 {t('vita_header', lc)}", className="page-title"),
        html.Hr(),
    ])
    tabs = dbc.Tabs(
        [
            dbc.Tab(label=t("vita_tab1", lc), tab_id="tab-budget"),
            dbc.Tab(label=t("vita_tab2", lc), tab_id="tab-fasi"),
            dbc.Tab(label=t("vita_tab3", lc), tab_id="tab-obiettivi"),
        ],
        id="vb-tabs",
        active_tab="tab-budget",
        style={"marginBottom": "20px"},
    )
    return header, tabs


@callback(
    Output("vb-tab-content", "children"),
    Input("vb-tabs", "active_tab"),
    Input("app-store", "data"),
    State("budget-store", "data"),
)
def render_tab(active_tab, store, budget_data):
    if not store:
        store = {}
    lc = store.get("lc", "it")
    reddito_mensile = store.get("reddito_mensile", 5500)
    figli = store.get("figli", False)
    eta = store.get("eta", 38)
    saved = budget_data or {}

    if active_tab == "tab-budget":
        content = render_budget(lc, reddito_mensile, figli, saved)
    elif active_tab == "tab-fasi":
        content = render_fasi(lc, eta, figli, reddito_mensile)
    elif active_tab == "tab-obiettivi":
        content = render_obiettivi(lc, reddito_mensile)
    else:
        return html.Div()
    return html.Div([content, sources_footer("budget")])


# ─────────────────────────────────────────────
# TAB 1 — BUDGET MENSILE
# ─────────────────────────────────────────────

def _budget_row(label, input_id, value, mn, mx, step):
    """Compact label + number input row for the budget form."""
    return [
        html.Label(label, style={
            "fontSize": "0.72rem", "fontWeight": "600", "color": "#555",
            "marginBottom": "2px", "marginTop": "6px", "display": "block",
            "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap",
        }),
        dcc.Input(id=input_id, type="number", value=value, min=mn, max=mx, step=step,
                  className="form-control form-control-sm",
                  style={"marginBottom": "2px", "fontSize": "0.82rem", "padding": "4px 8px"}),
    ]


def render_budget(lc, reddito_mensile, figli, saved=None):
    s = saved or {}
    return html.Div([
        html.H4(t("vita_tab1", lc), style={"marginBottom": "16px"}),
        dbc.Row([
            dbc.Col([
                html.H6(f"💰 {t('vita_entrate', lc)}", style={"fontSize": "0.85rem", "fontWeight": "700"}),
                *_budget_row(t("vita_salario1", lc), "vb-sal1", s.get("sal1", reddito_mensile), 0, 50000, 100),
                *_budget_row(t("vita_salario2", lc), "vb-sal2", s.get("sal2", 0), 0, 30000, 100),
                *_budget_row(t("vita_altri_entrate", lc), "vb-altri", s.get("altri", 0), 0, 10000, 50),
            ], md=4),
            dbc.Col([
                html.H6(f"📤 {t('vita_uscite', lc)}", style={"fontSize": "0.85rem", "fontWeight": "700"}),
                *_budget_row(t("vita_affitto", lc), "vb-aff", s.get("aff", 1600), 0, 10000, 50),
                *_budget_row(t("vita_cibo", lc), "vb-cibo", s.get("cibo", 700), 0, 5000, 50),
                *_budget_row(t("vita_trasporto", lc), "vb-tras", s.get("tras", 300), 0, 3000, 50),
                *_budget_row(t("vita_salute", lc), "vb-sal", s.get("salute", 500), 0, 5000, 50),
                *_budget_row(t("vita_intrattenimento", lc), "vb-int", s.get("intrat", 300), 0, 3000, 50),
                *_budget_row(t("vita_asilo", lc), "vb-asilo", s.get("asilo", 800 if figli else 0), 0, 5000, 50),
                *_budget_row(t("vita_altro", lc), "vb-alt", s.get("altro", 200), 0, 3000, 50),
            ], md=4),
            dbc.Col([
                html.H6(f"🎯 {t('vita_risparmio_target', lc)}", style={"fontSize": "0.85rem", "fontWeight": "700"}),
                dcc.Input(id="vb-risp-target", type="number", value=s.get("risp_target", int(reddito_mensile * 0.15)),
                          min=0, max=10000, step=100, className="form-control form-control-sm",
                          style={"marginBottom": "12px"}),
                html.Hr(),
                html.Div(id="vb-kpis"),
                html.Div(id="vb-semaforo", style={"marginTop": "12px"}),
            ], md=4),
        ], className="mb-4 g-3"),
        dbc.Row([
            dbc.Col([dcc.Graph(id="vb-pie", config={"displayModeBar": False})], width=6),
            dbc.Col([
                html.H6(f"📐 {t('vita_regola', lc)}"),
                html.Div(id="vb-5030-table"),
                dcc.Graph(id="vb-5030-chart", config={"displayModeBar": False}),
            ], width=6),
        ]),
        dcc.Store(id="vb-lc-store", data=lc),
    ])


@callback(
    Output("vb-kpis", "children"),
    Output("vb-semaforo", "children"),
    Output("vb-pie", "figure"),
    Output("vb-5030-table", "children"),
    Output("vb-5030-chart", "figure"),
    Input("vb-sal1", "value"),
    Input("vb-sal2", "value"),
    Input("vb-altri", "value"),
    Input("vb-aff", "value"),
    Input("vb-cibo", "value"),
    Input("vb-tras", "value"),
    Input("vb-sal", "value"),
    Input("vb-int", "value"),
    Input("vb-asilo", "value"),
    Input("vb-alt", "value"),
    Input("vb-risp-target", "value"),
    Input("vb-lc-store", "data"),
    prevent_initial_call=False,
)
def update_budget(sal1, sal2, altri, aff, cibo, tras, salute, intrat, asilo, altro, risp_target, lc):
    lc = lc or "it"
    sal1 = sal1 or 0
    sal2 = sal2 or 0
    altri = altri or 0
    aff = aff or 0
    cibo = cibo or 0
    tras = tras or 0
    salute = salute or 0
    intrat = intrat or 0
    asilo = asilo or 0
    altro = altro or 0
    risp_target = risp_target or 0

    totale_entrate = sal1 + sal2 + altri
    totale_uscite = aff + cibo + tras + salute + intrat + asilo + altro
    saldo = totale_entrate - totale_uscite

    kpis = dbc.Row([
        dbc.Col(html.Div([html.Div(t("vita_entrate", lc), className="kpi-label"), html.Div(f"CHF {totale_entrate:,}", className="kpi-value")], className="kpi-box"), width=6),
        dbc.Col(html.Div([html.Div(t("vita_uscite", lc), className="kpi-label"), html.Div(f"CHF {totale_uscite:,}", className="kpi-value")], className="kpi-box"), width=6),
        dbc.Col(html.Div([html.Div(t("vita_saldo", lc), className="kpi-label"), html.Div(f"CHF {saldo:,}", className="kpi-value", style={"color": "#27ae60" if saldo > 0 else "#e74c3c"})], className="kpi-box mt-2"), width=6),
        dbc.Col(html.Div([html.Div(t("vita_risparmio_target", lc), className="kpi-label"), html.Div(f"CHF {risp_target:,}", className="kpi-value")], className="kpi-box mt-2"), width=6),
    ], className="g-2")

    if saldo >= risp_target:
        pct = risp_target / totale_entrate * 100 if totale_entrate > 0 else 0
        semaforo = html.Div(t("vita_sem_ok", lc, saldo=f"{saldo:,}", pct=pct), className="budget-ok")
    elif saldo > 0:
        semaforo = html.Div(t("vita_sem_warn", lc, saldo=f"{saldo:,}"), className="budget-warn")
    else:
        semaforo = html.Div(t("vita_sem_err", lc, saldo=f"{saldo:,}"), className="budget-err")

    # Pie chart
    voci = [t("vita_affitto", lc), t("vita_cibo", lc), t("vita_trasporto", lc),
            t("vita_salute", lc), t("vita_intrattenimento", lc), t("vita_asilo", lc), t("vita_altro", lc)]
    vals = [aff, cibo, tras, salute, intrat, asilo, altro]
    df_pie = pd.DataFrame({"Voce": voci, "CHF": vals}).query("CHF > 0")
    if not df_pie.empty:
        fig_pie = go.Figure(go.Pie(labels=df_pie["Voce"], values=df_pie["CHF"], hole=0.45,
                                   marker_colors=px.colors.qualitative.Set3))
        fig_pie.update_layout(template="plotly_white", height=260, margin=dict(t=20, b=0),
                              title=t("vita_uscite", lc), showlegend=True,
                              legend=dict(orientation="v", font=dict(size=11)))
    else:
        fig_pie = go.Figure()
        fig_pie.update_layout(template="plotly_white", height=200)

    # 50/30/20
    necessario = aff + cibo + tras + salute + asilo
    discrezionale = intrat + altro
    _cat = t("vita_categoria", lc)
    _att = t("vita_attuale", lc)
    _tar = t("vita_target", lc)
    df_5030 = pd.DataFrame({
        _cat: [t("vita_necessita", lc), t("vita_discrezionale", lc), t("vita_risparmio_voce", lc)],
        _att: [necessario, discrezionale, risp_target],
        _tar: [int(totale_entrate * 0.5), int(totale_entrate * 0.3), int(totale_entrate * 0.2)],
    })
    table_5030 = dbc.Table.from_dataframe(df_5030, striped=True, hover=True, responsive=True, size="sm")
    df_melted = df_5030.melt(_cat, [_att, _tar], var_name="Tipo", value_name="CHF")
    fig_5030 = px.bar(df_melted, x=_cat, y="CHF", color="Tipo", barmode="group",
                      color_discrete_map={_att: "#c0392b", _tar: "#bdc3c7"},
                      template="plotly_white", height=200)
    fig_5030.update_layout(margin=dict(t=10, b=0), xaxis_title="", legend=dict(orientation="h", y=-0.4))

    return kpis, semaforo, fig_pie, table_5030, fig_5030


@callback(
    Output("budget-store", "data"),
    Input("vb-sal1", "value"),
    Input("vb-sal2", "value"),
    Input("vb-altri", "value"),
    Input("vb-aff", "value"),
    Input("vb-cibo", "value"),
    Input("vb-tras", "value"),
    Input("vb-sal", "value"),
    Input("vb-int", "value"),
    Input("vb-asilo", "value"),
    Input("vb-alt", "value"),
    Input("vb-risp-target", "value"),
    prevent_initial_call=True,
)
def save_budget(sal1, sal2, altri, aff, cibo, tras, salute, intrat, asilo, altro, risp_target):
    """Persist budget inputs to session storage whenever any field changes."""
    return {
        "sal1": sal1, "sal2": sal2, "altri": altri,
        "aff": aff, "cibo": cibo, "tras": tras, "salute": salute,
        "intrat": intrat, "asilo": asilo, "altro": altro,
        "risp_target": risp_target,
    }


# ─────────────────────────────────────────────
# TAB 2 — FASI DI VITA  (redesigned: realistic 2026 costs, auto-detect, priorities)
# ─────────────────────────────────────────────

# Costi tipici mensili CH 2026 per fase — franchi svizzeri, media nazionale
# Fonte: UST, comparis.ch, Compendio svizzero delle assicurazioni sociali 2026
# N.B.: valori "netti" (senza risparmio/saldo — quello si calcola dal delta reddito)
_COSTI_FASE_BASE = [
    # 0 — Giovane senza figli (single 22-32 anni)
    {"affitto": 1700, "cibo": 650, "trasporto": 380, "kk": 499,
     "telefonia": 80, "svago": 400, "abbigliamento": 200, "3a": 500},
    # 1 — Coppia senza figli (30-40 anni, 2 redditi)
    {"affitto": 2400, "cibo": 1100, "trasporto": 700, "kk": 998,
     "telefonia": 120, "svago": 600, "abbigliamento": 350, "3a": 1200},
    # 2 — Famiglia bambini piccoli (35-45 anni, 2 figli <10)
    {"affitto": 2800, "cibo": 1400, "trasporto": 750, "kk": 1240,
     "asilo_nido": 2200, "telefonia": 130, "svago": 500,
     "abbigliamento": 400, "3a": 800},
    # 3 — Famiglia figli adolescenti (45-55 anni, 2 figli 12-18)
    {"affitto": 2800, "cibo": 1600, "trasporto": 900, "kk": 1500,
     "telefonia": 200, "svago": 800, "abbigliamento": 500, "3a": 1200},
    # 4 — Figli all'università (50-58 anni, 2 figli fuori casa)
    {"affitto": 2600, "cibo": 1400, "trasporto": 800, "kk": 1100,
     "contributo_figli": 2000, "telefonia": 150, "svago": 700, "3a": 1200},
    # 5 — Nido vuoto 50+ (55-63 anni, senza figli a carico)
    {"affitto": 2100, "cibo": 1200, "trasporto": 600, "kk": 1400,
     "telefonia": 100, "svago": 1000, "3a": 1450},
    # 6 — Pre-pensione (62-65 anni)
    {"affitto": 1900, "cibo": 1100, "trasporto": 500, "kk": 1600,
     "telefonia": 100, "svago": 1200, "risparmio_extra": 1500},
]

# Etichette i18n per le voci comuni
_VOCE_KEY = {
    "affitto": "vita_affitto", "cibo": "vita_cibo", "trasporto": "vita_trasporto",
    "svago": "vita_intrattenimento", "abbigliamento": "vita_altro",
    "asilo_nido": "vita_asilo",
}


def _auto_fase(eta, figli):
    """Suggerisce la fase di vita dal profilo del cliente."""
    if eta >= 62:
        return 6
    if eta >= 55:
        return 5 if not figli else 4
    if eta >= 45:
        return 3 if figli else 5
    if eta >= 35:
        return 2 if figli else 1
    return 0


def render_fasi(lc, eta, figli, reddito_mensile):
    fase_opts = t("vita_fase_opts", lc)
    auto_idx  = _auto_fase(eta, figli)
    return html.Div([
        html.H4(t("vita_tab2", lc), style={"marginBottom": "8px"}),
        html.Div([
            html.Span(t("vita_fase_badge", lc) + f": ", style={"fontSize": "12px", "color": "#555"}),
            html.Span(fase_opts[auto_idx],
                      style={"fontSize": "12px", "fontWeight": "700", "color": "#c0392b"}),
            html.Span(f"  ·  {t('vita_fase_pers', lc)} →",
                      style={"fontSize": "11px", "color": "#999", "marginLeft": "8px"}),
        ], style={"marginBottom": "12px"}),
        html.Label(t("vita_fase_label", lc), style={"fontSize": "12px"}),
        dcc.Slider(
            id="vb-fase",
            min=0, max=len(fase_opts) - 1, step=1,
            value=auto_idx,
            marks={i: {"label": fase_opts[i],
                       "style": {"fontSize": "10px", "whiteSpace": "nowrap",
                                 "fontWeight": "700" if i == auto_idx else "400",
                                 "color": "#c0392b" if i == auto_idx else "#555"}}
                   for i in range(len(fase_opts))},
            tooltip={"always_visible": False},
        ),
        html.Div(id="vb-fasi-content"),
        dcc.Store(id="vb-fasi-lc-store", data=lc),
        dcc.Store(id="vb-fasi-opts-store", data=fase_opts),
        dcc.Store(id="vb-fasi-red-store", data=reddito_mensile),
    ])


@callback(
    Output("vb-fasi-content", "children"),
    Input("vb-fase", "value"),
    Input("vb-fasi-lc-store", "data"),
    Input("vb-fasi-opts-store", "data"),
    Input("vb-fasi-red-store", "data"),
    prevent_initial_call=False,
)
def update_fasi(fase_idx, lc, fase_opts, reddito_mensile):
    lc = lc or "it"
    reddito_mensile = reddito_mensile or 5500
    fase_opts = fase_opts or t("vita_fase_opts", lc)
    fase_idx = fase_idx if fase_idx is not None else 0
    fase_nome = fase_opts[fase_idx]

    # Build translated label → CHF dict for this phase
    raw = _COSTI_FASE_BASE[fase_idx]
    _voce_lbl = t("vita_costi_tipici", lc)
    _chfm_lbl = t("vita_chf_mese_stimato", lc)
    dati = {}
    for k, v in raw.items():
        if k in _VOCE_KEY:
            lbl = t(_VOCE_KEY[k], lc)
        elif k == "kk":
            lbl = "💊 KK / LAMal"
        elif k == "3a":
            lbl = "🏦 3° Pilastro"
        elif k == "contributo_figli":
            lbl = "🎓 Supporto figli (univ.)"
        elif k == "risparmio_extra":
            lbl = "💰 Risparmio pre-pensione"
        else:
            lbl = k.replace("_", " ").capitalize()
        dati[lbl] = v

    totale = sum(dati.values())
    delta  = reddito_mensile - totale
    n_pers = 2 if fase_idx > 0 else 1   # single vs famiglia
    costo_pp = totale // n_pers

    df_fase = pd.DataFrame([{_voce_lbl: k, _chfm_lbl: v} for k, v in dati.items()])
    fig = px.bar(
        df_fase, x=_chfm_lbl, y=_voce_lbl, orientation="h",
        color_discrete_sequence=["#c0392b"],
        template="plotly_white", height=320, title=fase_nome,
    )
    fig.update_layout(
        margin=dict(t=32, b=0), yaxis_title="",
        yaxis=dict(categoryorder="total ascending"),
    )

    alert_cls = "budget-ok" if delta >= 0 else "budget-err"
    alert_txt = (t("vita_reddito_suff", lc, delta=f"{delta:,}")
                 if delta >= 0
                 else t("vita_reddito_deficit", lc, abs_delta=f"{abs(delta):,}"))

    # Phase priorities
    priorita_lista = t("vita_fase_priorita", lc)
    prios = priorita_lista[fase_idx] if isinstance(priorita_lista, list) and fase_idx < len(priorita_lista) else []

    return html.Div([
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Table.from_dataframe(df_fase, striped=True, hover=True,
                                         responsive=True, size="sm"),
                dbc.Row([
                    dbc.Col(html.Div([
                        html.Div(t("vita_totale_mensile", lc), className="kpi-label"),
                        html.Div(f"CHF {totale:,}", className="kpi-value"),
                    ], className="kpi-box"), width=6),
                    dbc.Col(html.Div([
                        html.Div(t("vita_costo_pp", lc), className="kpi-label"),
                        html.Div(f"CHF {costo_pp:,}", className="kpi-value"),
                    ], className="kpi-box"), width=6),
                ], className="g-2 mt-2"),
                html.Div(alert_txt, className=alert_cls, style={"marginTop": "10px"}),
            ], width=5),
            dbc.Col([
                dcc.Graph(figure=fig, config={"displayModeBar": False}),
            ], width=7),
        ]),
        html.Hr(),
        html.H6(f"📋 Priorità finanziarie — {fase_nome}",
                style={"fontWeight": "700", "marginBottom": "10px"}),
        html.Div([
            html.Div(p, style={"fontSize": "13px", "padding": "6px 0",
                               "borderBottom": "1px solid #f0f0f0"})
            for p in prios
        ], style={"background": "#f8f9fc", "borderRadius": "10px",
                  "padding": "14px 18px"}),
    ])


# ─────────────────────────────────────────────
# TAB 3 — OBIETTIVI
# ─────────────────────────────────────────────

def render_obiettivi(lc, reddito_mensile):
    default_nomi = t("vita_default_nomi", lc)
    default_importi = [100000, 30000, 500000, 80000, 15000, 50000]
    default_anni = [10, 3, 20, 15, 2, 5]

    return html.Div([
        html.H4(t("vita_obiettivi_titolo", lc), style={"marginBottom": "16px"}),
        html.Label(t("vita_n_obiettivi", lc), style={"fontSize": "12px"}),
        dcc.Slider(id="vb-n-obj", min=1, max=6, step=1, value=2, marks={i: str(i) for i in range(1, 7)}),
        html.Div(id="vb-obj-inputs"),
        html.Hr(),
        html.Div(id="vb-obj-results"),
        dcc.Store(id="vb-obj-lc-store", data=lc),
        dcc.Store(id="vb-obj-red-store", data=reddito_mensile),
        dcc.Store(id="vb-obj-defaults", data={
            "nomi": default_nomi, "importi": default_importi, "anni": default_anni
        }),
    ])


@callback(
    Output("vb-obj-inputs", "children"),
    Input("vb-n-obj", "value"),
    Input("vb-obj-lc-store", "data"),
    Input("vb-obj-defaults", "data"),
    prevent_initial_call=False,
)
def render_obj_inputs(n_obj, lc, defaults):
    lc = lc or "it"
    n_obj = n_obj or 2
    defaults = defaults or {}
    nomi = defaults.get("nomi", [""] * 6)
    importi = defaults.get("importi", [0] * 6)
    anni = defaults.get("anni", [5] * 6)

    rows = []
    for i in range(n_obj):
        rows.append(
            dbc.Row([
                dbc.Col([html.Label(f"{t('vita_obj_nome', lc)} {i+1}", style={"fontSize": "11px"}),
                         dcc.Input(id={"type": "obj-nome", "index": i}, type="text",
                                   placeholder=nomi[i], className="form-control")], width=4),
                dbc.Col([html.Label(t("vita_obj_importo", lc), style={"fontSize": "11px"}),
                         dcc.Input(id={"type": "obj-importo", "index": i}, type="number",
                                   value=importi[i], min=0, max=2000000, step=1000, className="form-control")], width=4),
                dbc.Col([html.Label(t("vita_obj_anni", lc), style={"fontSize": "11px"}),
                         dcc.Input(id={"type": "obj-anni", "index": i}, type="number",
                                   value=anni[i], min=1, max=40, step=1, className="form-control")], width=4),
            ], className="mb-2 g-2")
        )
    return html.Div([html.Br(), *rows])


@callback(
    Output("vb-obj-results", "children"),
    Input("vb-n-obj", "value"),
    Input({"type": "obj-nome", "index": dash.ALL}, "value"),
    Input({"type": "obj-importo", "index": dash.ALL}, "value"),
    Input({"type": "obj-anni", "index": dash.ALL}, "value"),
    Input("vb-obj-lc-store", "data"),
    Input("vb-obj-red-store", "data"),
    Input("vb-obj-defaults", "data"),
    prevent_initial_call=False,
)
def update_obj_results(n_obj, nomi_vals, importi_vals, anni_vals, lc, reddito_mensile, defaults):
    lc = lc or "it"
    n_obj = n_obj or 2
    reddito_mensile = reddito_mensile or 5500
    defaults = defaults or {}
    default_nomi = defaults.get("nomi", ["Obiettivo"] * 6)
    default_importi = defaults.get("importi", [50000] * 6)
    default_anni = defaults.get("anni", [5] * 6)

    _nome_col = t("vita_obj_nome", lc)
    _imp_col = t("vita_obj_importo", lc)
    _anni_col = t("vita_obj_anni", lc)
    _chfm_col = t("vita_chf_mese_nec", lc)

    obiettivi = []
    for i in range(n_obj):
        nome_v = (nomi_vals[i] if i < len(nomi_vals) and nomi_vals[i] else default_nomi[i])
        importo_v = (importi_vals[i] if i < len(importi_vals) and importi_vals[i] else default_importi[i])
        anni_v = (anni_vals[i] if i < len(anni_vals) and anni_vals[i] else default_anni[i])
        importo_v = max(int(importo_v), 0)
        anni_v = max(int(anni_v), 1)
        risp_mens = int(importo_v / (anni_v * 12))
        obiettivi.append({
            _nome_col: nome_v,
            _imp_col: importo_v,
            _anni_col: anni_v,
            _chfm_col: risp_mens,
        })

    if not obiettivi:
        return html.Div()

    df_obj = pd.DataFrame(obiettivi)
    totale_risp = sum(o[_chfm_col] for o in obiettivi)
    capacita = reddito_mensile - totale_risp

    # Summary table
    table = dbc.Table.from_dataframe(df_obj, striped=True, hover=True, responsive=True, size="sm")

    metrics = dbc.Row([
        dbc.Col(html.Div([html.Div(t("vita_totale_risp", lc), className="kpi-label"),
                          html.Div(f"CHF {totale_risp:,}/m", className="kpi-value")], className="kpi-box"), width=6),
        dbc.Col(html.Div([html.Div(t("vita_capacita_residua", lc), className="kpi-label"),
                          html.Div(f"CHF {capacita:,}/m", className="kpi-value",
                                   style={"color": "#27ae60" if capacita >= 0 else "#e74c3c"})], className="kpi-box"), width=6),
    ], className="g-3 mb-3")

    if capacita >= 0:
        alert = html.Div(t("vita_obj_raggiungibili", lc, capacita=f"{capacita:,}"), className="budget-ok")
    else:
        alert = html.Div(t("vita_obj_insufficiente", lc, totale=f"{totale_risp:,}", deficit=f"{abs(capacita):,}"), className="budget-err")

    # Gantt timeline
    df_gantt = pd.DataFrame([{
        "Obiettivo": o[_nome_col],
        "Inizio": 0,
        "Fine": o[_anni_col],
        "Importo": o[_imp_col],
        "CHF/mese": o[_chfm_col],
    } for o in obiettivi])

    # Use horizontal bar as Gantt
    fig_gantt = go.Figure()
    colors = px.colors.sequential.Reds
    max_importo = max(o[_imp_col] for o in obiettivi) or 1
    for i, row in df_gantt.iterrows():
        color_idx = min(int(row["Importo"] / max_importo * (len(colors) - 1)), len(colors) - 1)
        fig_gantt.add_trace(go.Bar(
            x=[row["Fine"] - row["Inizio"]],
            y=[row["Obiettivo"]],
            orientation="h",
            base=row["Inizio"],
            marker_color=colors[color_idx],
            hovertemplate=f"{row['Obiettivo']}: CHF {row['Importo']:,} — {row['Fine']} {t('adv_anni', lc)}<extra></extra>",
            showlegend=False,
        ))
    fig_gantt.update_layout(
        template="plotly_white",
        height=max(180, len(obiettivi) * 50),
        xaxis_title=t("vita_anni_da_oggi", lc),
        yaxis_title="",
        title=t("vita_timeline", lc),
        margin=dict(t=40, b=0),
        barmode="stack",
    )

    # Accumulation line chart
    rows_acc = []
    for o in obiettivi:
        acc = 0
        for mese in range(o[_anni_col] * 12 + 1):
            acc += o[_chfm_col]
            if mese % 12 == 0:
                rows_acc.append({"Obiettivo": o[_nome_col], "Anno": mese // 12, "CHF": acc})
    if rows_acc:
        df_acc = pd.DataFrame(rows_acc)
        fig_acc = px.line(df_acc, x="Anno", y="CHF", color="Obiettivo",
                          color_discrete_sequence=px.colors.qualitative.Set1,
                          template="plotly_white", height=280,
                          title=f"📈 {t('vita_proiez_acc', lc)}")
        fig_acc.update_layout(margin=dict(t=40, b=0), yaxis=dict(tickformat=",.0f"))
        acc_chart = dcc.Graph(figure=fig_acc, config={"displayModeBar": False})
    else:
        acc_chart = html.Div()

    return html.Div([
        table,
        html.Div(style={"marginTop": "12px"}),
        metrics,
        alert,
        html.Hr(),
        dcc.Graph(figure=fig_gantt, config={"displayModeBar": False}),
        acc_chart,
    ])
