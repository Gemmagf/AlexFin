# dash_pages/assegurances.py — Assicurazioni, Krankenkasse & Previdenza

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import callback, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

from i18n import t
from products import (
    ASSICURAZIONI, KK_COMPLEMENTARI, KK_FRANCHIGIE, KK_MODELLI,
    KK_PREMI_CANTON, PILASTRI,
)

dash.register_page(__name__, path="/assegurances", name="Assicurazioni")


def layout():
    return html.Div([
        html.Div(id="ass-header"),
        dbc.Tabs(
            [
                dbc.Tab(label="🛡️ Assicurazioni", tab_id="tab-ass"),
                dbc.Tab(label="💊 Krankenkasse", tab_id="tab-kk"),
                dbc.Tab(label="🏛️ Previdenza", tab_id="tab-prev"),
            ],
            id="ass-tabs",
            active_tab="tab-ass",
            style={"marginBottom": "20px"},
        ),
        html.Div(id="ass-tab-content"),
    ])


@callback(Output("ass-header", "children"), Input("app-store", "data"))
def render_header(store):
    if not store:
        store = {}
    lc = store.get("lc", "it")
    return html.Div([
        html.H1(f"🛡️ {t('ass_header', lc)} & {t('kk_header', lc)}", className="page-title"),
        html.Hr(),
    ])


@callback(Output("ass-tab-content", "children"), Input("ass-tabs", "active_tab"), Input("app-store", "data"))
def render_tab(active_tab, store):
    if not store:
        store = {}
    lc = store.get("lc", "it")
    eta = store.get("eta", 38)
    canton = store.get("canton", "Ticino")
    reddito_mensile = store.get("reddito_mensile", 5500)
    situazione = store.get("situazione", "Dipendente")

    if active_tab == "tab-ass":
        return render_assicurazioni(lc, eta)
    elif active_tab == "tab-kk":
        return render_krankenkasse(lc, canton, eta)
    elif active_tab == "tab-prev":
        return render_previdenza(lc, eta, situazione, reddito_mensile)
    return html.Div()


# ─────────────────────────────────────────────
# TAB 1 — ASSICURAZIONI
# ─────────────────────────────────────────────

def render_assicurazioni(lc, eta):
    nomi_prodotti = [{"label": f"{p['icona']} {p['nome']}", "value": p["id"]} for p in ASSICURAZIONI]
    return html.Div([
        html.H4(t("ass_header", lc), style={"marginBottom": "16px"}),
        dbc.Row([
            dbc.Col([
                html.Label(t("ass_sel", lc), style={"fontSize": "12px", "fontWeight": "600"}),
                dcc.RadioItems(
                    id="ass-prodotto-sel",
                    options=nomi_prodotti,
                    value=ASSICURAZIONI[0]["id"],
                    labelStyle={"display": "block", "marginBottom": "8px", "fontSize": "14px"},
                    style={"marginBottom": "16px"},
                ),
                html.Hr(),
                html.Div(id="ass-prodotto-meta"),
            ], width=3),
            dbc.Col([
                html.Div(id="ass-prodotto-detail"),
            ], width=9),
        ]),
        html.Hr(),
        html.H5(t("ass_grafico_premi", lc)),
        html.Div(id="ass-premi-chart"),
        dcc.Store(id="ass-eta-store", data=eta),
        dcc.Store(id="ass-lc-store", data=lc),
    ])


@callback(
    Output("ass-prodotto-meta", "children"),
    Output("ass-prodotto-detail", "children"),
    Output("ass-premi-chart", "children"),
    Input("ass-prodotto-sel", "value"),
    Input("ass-eta-store", "data"),
    Input("ass-lc-store", "data"),
    prevent_initial_call=False,
)
def update_assicurazioni(prodotto_id, eta, lc):
    eta = eta or 38
    lc = lc or "it"
    prodotto = next((p for p in ASSICURAZIONI if p["id"] == prodotto_id), ASSICURAZIONI[0])

    # Meta block
    eta_vicina = min(prodotto["premi_per_eta"].keys(), key=lambda x: abs(x - eta)) if prodotto.get("premi_per_eta") else None
    premio_eta = prodotto["premi_per_eta"][eta_vicina] if eta_vicina else None
    meta = html.Div([
        html.P([html.Strong(f"{t('ass_categoria', lc)}: "), html.Code(prodotto["categoria"])]),
        html.P([html.Strong(f"{t('ass_costo', lc)}: "), html.Code(prodotto["costo_indicativo"])]),
        html.P(prodotto["costo_note"], style={"fontSize": "11px", "color": "#888"}),
        html.P([html.Strong(f"{t('ass_stima_eta', lc, eta=eta)}: "), html.Code(f"CHF {premio_eta}/mese")]) if premio_eta else html.Div(),
    ])

    # Detail block
    sc = prodotto["scenario"]
    detail = html.Div([
        html.H4(f"{prodotto['icona']} {prodotto['nome']}", style={"color": "#1e2235"}),
        html.P(prodotto["descrizione"]),
        dbc.Row([
            dbc.Col([
                html.Strong(f"✅ {t('ass_copre', lc)}"),
                html.Ul([html.Li(c, className="cover-ok") for c in prodotto["coperture"]]),
            ], width=6),
            dbc.Col([
                html.Strong(f"❌ {t('ass_non_copre', lc)}"),
                html.Ul([html.Li(e, className="cover-no") for e in prodotto["esclusioni"]]),
            ], width=6),
        ]),
        html.Hr(),
        html.P([html.Strong(f"📖 {t('ass_caso', lc)}: "), html.Em(sc["caso"])]),
        dbc.Row([
            dbc.Col(html.Div([html.Strong(f"{t('ass_senza', lc)}: "), sc["senza"]], className="budget-err"), width=6),
            dbc.Col(html.Div([html.Strong(f"{t('ass_con', lc)}: "), sc["con"]], className="budget-ok"), width=6),
        ]),
    ])

    # Premi chart
    righe = []
    for p in ASSICURAZIONI:
        if p.get("premi_per_eta"):
            for e_k, pr in p["premi_per_eta"].items():
                righe.append({"Età": e_k, "CHF/mese": pr, "Prodotto": p["nome"]})
    df_premi = pd.DataFrame(righe)

    fig = go.Figure()
    for prod in ASSICURAZIONI:
        if prod.get("premi_per_eta"):
            df_p = df_premi[df_premi["Prodotto"] == prod["nome"]]
            opacity = 1.0 if prod["id"] == prodotto_id else 0.25
            width = 3.5 if prod["id"] == prodotto_id else 1.5
            fig.add_trace(go.Scatter(
                x=df_p["Età"], y=df_p["CHF/mese"],
                name=prod["nome"],
                mode="lines+markers",
                opacity=opacity,
                line=dict(width=width),
            ))
    fig.add_vline(x=eta, line_dash="dash", line_color="#c0392b", line_width=2)
    fig.update_layout(template="plotly_white", height=280, margin=dict(t=10, b=0),
                      legend=dict(orientation="h", yanchor="bottom", y=-0.5))

    return meta, detail, dcc.Graph(figure=fig, config={"displayModeBar": False})


# ─────────────────────────────────────────────
# TAB 2 — KRANKENKASSE
# ─────────────────────────────────────────────

def render_krankenkasse(lc, canton, eta):
    premio_base = KK_PREMI_CANTON.get(canton, KK_PREMI_CANTON["Ticino"])["adulto"]
    return html.Div([
        html.H4(t("kk_header", lc), style={"marginBottom": "16px"}),
        dbc.Tabs(
            [
                dbc.Tab(label=t("kk_tab1", lc), tab_id="kk-tab1"),
                dbc.Tab(label=t("kk_tab2", lc), tab_id="kk-tab2"),
                dbc.Tab(label=t("kk_tab3", lc), tab_id="kk-tab3"),
            ],
            id="kk-inner-tabs",
            active_tab="kk-tab1",
        ),
        html.Div(id="kk-inner-content"),
        dcc.Store(id="kk-canton-store", data=canton),
        dcc.Store(id="kk-lc-store", data=lc),
        dcc.Store(id="kk-pb-store", data=premio_base),
    ])


@callback(
    Output("kk-inner-content", "children"),
    Input("kk-inner-tabs", "active_tab"),
    Input("kk-canton-store", "data"),
    Input("kk-lc-store", "data"),
    Input("kk-pb-store", "data"),
    prevent_initial_call=False,
)
def render_kk_inner(active_tab, canton, lc, premio_base):
    canton = canton or "Ticino"
    lc = lc or "it"
    premio_base = premio_base or 468

    if active_tab == "kk-tab1":
        return render_kk_franchigie(lc, canton, premio_base)
    elif active_tab == "kk-tab2":
        return render_kk_complementari(lc)
    elif active_tab == "kk-tab3":
        return render_kk_calcola(lc, canton, premio_base)
    return html.Div()


def render_kk_franchigie(lc, canton, premio_base):
    dati = KK_PREMI_CANTON.get(canton, KK_PREMI_CANTON["Ticino"])

    # Canton metrics
    canton_metrics = dbc.Row([
        dbc.Col(html.Div([html.Div(t("kk_adulto", lc), className="kpi-label"), html.Div(f"CHF {dati['adulto']}/m", className="kpi-value")], className="kpi-box"), width=4),
        dbc.Col(html.Div([html.Div(t("kk_giovane", lc), className="kpi-label"), html.Div(f"CHF {dati['giovane']}/m", className="kpi-value")], className="kpi-box"), width=4),
        dbc.Col(html.Div([html.Div(t("kk_bambino", lc), className="kpi-label"), html.Div(f"CHF {dati['bambino']}/m", className="kpi-value")], className="kpi-box"), width=4),
    ], className="g-3 mb-4")

    # Franchigie table
    df_fran = pd.DataFrame([{
        "Franchigia": f"CHF {f['importo']}",
        "Premio/mese": f"CHF {int(premio_base * (1 - f['risparmio_pct'] / 100))}",
        "Risparmio/anno": f"CHF {int(premio_base * f['risparmio_pct'] / 100 * 12)}",
        "Note": f["nota"],
    } for f in KK_FRANCHIGIE])

    # Canton comparison bar chart
    df_cant = pd.DataFrame([
        {"Cantone": c, "Premio (CHF/m)": v["adulto"]}
        for c, v in KK_PREMI_CANTON.items()
    ]).sort_values("Premio (CHF/m)")
    fig_cant = px.bar(df_cant, x="Premio (CHF/m)", y="Cantone",
                      orientation="h",
                      color=df_cant["Cantone"].apply(lambda c_: "selected" if c_ == canton else "other"),
                      color_discrete_map={"selected": "#c0392b", "other": "#bdc3c7"},
                      template="plotly_white", height=280)
    fig_cant.update_layout(showlegend=False, margin=dict(t=10, b=0), yaxis_title="")

    # Models bar
    df_mod = pd.DataFrame([{
        "Modello": m["nome"],
        "CHF/anno risparmio": int(premio_base * m["risparmio_pct"] / 100 * 12),
        "Premio/mese": int(premio_base * (1 - m["risparmio_pct"] / 100)),
        "Libertà": m["rating_liberta"],
        "Risparmio": m["rating_risparmio"],
    } for m in KK_MODELLI])
    fig_mod = px.bar(df_mod, x="Modello", y="CHF/anno risparmio",
                     color="Modello",
                     color_discrete_sequence=["#bdc3c7", "#3498db", "#9b59b6", "#27ae60"],
                     template="plotly_white", height=220)
    fig_mod.update_layout(showlegend=False, margin=dict(t=10, b=0))

    return html.Div([
        html.H5(f"🗺️ {canton} — {t('kk_premi_canton', lc)}"),
        canton_metrics,
        dbc.Row([
            dbc.Col([
                html.H6(t("kk_franchigie", lc)),
                dbc.Table.from_dataframe(df_fran, striped=True, bordered=False, hover=True, responsive=True, size="sm"),
            ], width=6),
            dbc.Col([
                html.H6(t("kk_confronto_canton", lc)),
                dcc.Graph(figure=fig_cant, config={"displayModeBar": False}),
            ], width=6),
        ]),
        html.Hr(),
        html.H5(t("kk_modelli", lc)),
        dbc.Row([
            dbc.Col([dcc.Graph(figure=fig_mod, config={"displayModeBar": False})], width=6),
            dbc.Col([
                dbc.Table.from_dataframe(
                    df_mod[["Modello", "Premio/mese", "CHF/anno risparmio", "Libertà", "Risparmio"]],
                    striped=True, hover=True, responsive=True, size="sm",
                )
            ], width=6),
        ]),
    ])


def render_kk_complementari(lc):
    items = []
    for comp in KK_COMPLEMENTARI:
        items.append(
            dbc.AccordionItem(
                [
                    dbc.Row([
                        dbc.Col([
                            html.P(comp["copertura"]),
                            html.P(f"ℹ️ {comp['nota']}", style={"fontSize": "12px", "color": "#888"}),
                        ], width=8),
                        dbc.Col([
                            html.Div([html.Strong("Rimborso max: "), comp["rimborso_max"]], style={"background": "#f8f9fc", "borderRadius": "8px", "padding": "10px"}),
                        ], width=4),
                    ])
                ],
                title=f"{comp['nome']} — {comp['costo_indicativo']}",
            )
        )
    return html.Div([
        html.H5(t("kk_tab2", lc), style={"marginBottom": "16px"}),
        dbc.Accordion(items, start_collapsed=False),
    ])


def render_kk_calcola(lc, canton, premio_base):
    return html.Div([
        html.H5(t("kk_tab3", lc), style={"marginBottom": "16px"}),
        dbc.Row([
            dbc.Col([
                html.H6(t("kk_situazione_att", lc)),
                html.Label(t("kk_franchigia_att", lc), style={"fontSize": "12px"}),
                dcc.Dropdown(id="kk-fa", options=[{"label": f"CHF {f['importo']}", "value": f["importo"]} for f in KK_FRANCHIGIE], value=300, clearable=False),
                html.Label(t("kk_modello_att", lc), style={"fontSize": "12px", "marginTop": "8px"}),
                dcc.Dropdown(id="kk-ma", options=[{"label": m["nome"], "value": m["nome"]} for m in KK_MODELLI], value="Standard", clearable=False),
            ], width=6),
            dbc.Col([
                html.H6(t("kk_proposta", lc)),
                html.Label(t("kk_franchigia_nuo", lc), style={"fontSize": "12px"}),
                dcc.Dropdown(id="kk-fn", options=[{"label": f"CHF {f['importo']}", "value": f["importo"]} for f in KK_FRANCHIGIE], value=1500, clearable=False),
                html.Label(t("kk_modello_nuo", lc), style={"fontSize": "12px", "marginTop": "8px"}),
                dcc.Dropdown(id="kk-mn", options=[{"label": m["nome"], "value": m["nome"]} for m in KK_MODELLI], value="HMO", clearable=False),
            ], width=6),
        ], className="mb-3"),
        html.Div(id="kk-calcola-result"),
        dcc.Store(id="kk-pb-calc-store", data=premio_base),
        dcc.Store(id="kk-lc-calc-store", data=lc),
    ])


@callback(
    Output("kk-calcola-result", "children"),
    Input("kk-fa", "value"),
    Input("kk-ma", "value"),
    Input("kk-fn", "value"),
    Input("kk-mn", "value"),
    Input("kk-pb-calc-store", "data"),
    Input("kk-lc-calc-store", "data"),
    prevent_initial_call=False,
)
def update_kk_calcola(fran_att, mod_att, fran_nuo, mod_nuo, premio_base, lc):
    lc = lc or "it"
    premio_base = premio_base or 468
    fran_att = fran_att or 300
    fran_nuo = fran_nuo or 1500
    mod_att = mod_att or "Standard"
    mod_nuo = mod_nuo or "HMO"

    rfa = next((f["risparmio_pct"] for f in KK_FRANCHIGIE if f["importo"] == fran_att), 0)
    rfn = next((f["risparmio_pct"] for f in KK_FRANCHIGIE if f["importo"] == fran_nuo), 0)
    rma = next((m["risparmio_pct"] for m in KK_MODELLI if m["nome"] == mod_att), 0)
    rmn = next((m["risparmio_pct"] for m in KK_MODELLI if m["nome"] == mod_nuo), 0)
    pa = int(premio_base * (1 - min(rfa + rma, 55) / 100))
    pn = int(premio_base * (1 - min(rfn + rmn, 55) / 100))
    risp = (pa - pn) * 12

    fig = px.bar(
        pd.DataFrame({"Config": [t("kk_situazione_att", lc), t("kk_proposta", lc)], "CHF/mese": [pa, pn]}),
        x="Config", y="CHF/mese",
        color="Config",
        color_discrete_map={t("kk_situazione_att", lc): "#bdc3c7", t("kk_proposta", lc): "#27ae60"},
        template="plotly_white", height=200,
    )
    fig.update_layout(showlegend=False, margin=dict(t=10, b=0))

    metrics = dbc.Row([
        dbc.Col(html.Div([html.Div(t("kk_prem_att", lc), className="kpi-label"), html.Div(f"CHF {pa}/m", className="kpi-value")], className="kpi-box"), width=3),
        dbc.Col(html.Div([html.Div(t("kk_prem_nuo", lc), className="kpi-label"), html.Div(f"CHF {pn}/m", className="kpi-value")], className="kpi-box"), width=3),
        dbc.Col(html.Div([html.Div(t("kk_risp_anno", lc), className="kpi-label"), html.Div(f"CHF {risp:,}", className="kpi-value", style={"color": "#27ae60" if risp > 0 else "#e74c3c"})], className="kpi-box"), width=3),
        dbc.Col(html.Div([html.Div(t("kk_risp_5anni", lc), className="kpi-label"), html.Div(f"CHF {risp*5:,}", className="kpi-value", style={"color": "#27ae60" if risp > 0 else "#e74c3c"})], className="kpi-box"), width=3),
    ], className="g-3 mb-3")

    alert = (html.Div(f"✅ Risparmio annuo: CHF {risp:,}", className="budget-ok")
             if risp > 0 else html.Div("La configurazione attuale è già ottimale.", className="budget-warn"))

    return html.Div([metrics, dcc.Graph(figure=fig, config={"displayModeBar": False}), alert])


# ─────────────────────────────────────────────
# TAB 3 — PREVIDENZA
# ─────────────────────────────────────────────

def render_previdenza(lc, eta, situazione, reddito_mensile):
    anni_pensionamento = max(65 - eta, 1)
    max_3a = (PILASTRI["3"]["max_3a_dipendente_2026"] if situazione == "Dipendente"
              else PILASTRI["3"]["max_3a_indipendente_2026"])
    return html.Div([
        html.H4(t("prev_header", lc), style={"marginBottom": "16px"}),
        dbc.Tabs(
            [
                dbc.Tab(label=t("prev_tab1", lc), tab_id="prev-tab1"),
                dbc.Tab(label=t("prev_tab2", lc), tab_id="prev-tab2"),
                dbc.Tab(label=t("prev_tab3", lc), tab_id="prev-tab3"),
            ],
            id="prev-inner-tabs",
            active_tab="prev-tab1",
        ),
        html.Div(id="prev-inner-content"),
        dcc.Store(id="prev-lc-store", data=lc),
        dcc.Store(id="prev-eta-store", data=eta),
        dcc.Store(id="prev-sit-store", data=situazione),
        dcc.Store(id="prev-red-store", data=reddito_mensile),
        dcc.Store(id="prev-anni-store", data=anni_pensionamento),
        dcc.Store(id="prev-max3a-store", data=max_3a),
    ])


@callback(
    Output("prev-inner-content", "children"),
    Input("prev-inner-tabs", "active_tab"),
    Input("prev-lc-store", "data"),
    Input("prev-eta-store", "data"),
    Input("prev-sit-store", "data"),
    Input("prev-red-store", "data"),
    Input("prev-anni-store", "data"),
    Input("prev-max3a-store", "data"),
    prevent_initial_call=False,
)
def render_prev_inner(active_tab, lc, eta, situazione, reddito_mensile, anni_pensionamento, max_3a):
    lc = lc or "it"
    eta = eta or 38
    situazione = situazione or "Dipendente"
    reddito_mensile = reddito_mensile or 5500
    anni_pensionamento = anni_pensionamento or 27
    max_3a = max_3a or 7258

    if active_tab == "prev-tab1":
        return render_prev_sistema(lc)
    elif active_tab == "prev-tab2":
        return render_prev_simulatore(lc, anni_pensionamento, max_3a, situazione)
    elif active_tab == "prev-tab3":
        return render_prev_lacuna(lc, eta, reddito_mensile, situazione)
    return html.Div()


def render_prev_sistema(lc):
    items = []
    for num, p in PILASTRI.items():
        badge = (f"✅ {t('prev_obbligatorio', lc)}" if p["obbligatorio"]
                 else f"🔵 {t('prev_facoltativo', lc)}")
        items.append(
            dbc.AccordionItem(
                [
                    dbc.Row([
                        dbc.Col([
                            html.P([html.Strong("Obiettivo: "), p["obiettivo"]]),
                            html.P([html.Strong("Sistema: "), p["sistema"]]),
                            html.Div(f"⚠️ {p['lacuna_tipica']}", className="budget-warn", style={"fontSize": "13px"}),
                        ], width=8),
                        dbc.Col([
                            html.Ul([html.Li([html.Strong(lbl + ": "), val]) for lbl, val in p["dati_chiave"]],
                                    style={"fontSize": "12px", "paddingLeft": "16px"}),
                        ], width=4),
                    ])
                ],
                title=f"{p['icona']} {p['nome']} — {badge}",
            )
        )
    return html.Div([
        dbc.Accordion(items, start_collapsed=False, always_open=True),
    ])


def render_prev_simulatore(lc, anni_pensionamento, max_3a, situazione):
    return html.Div([
        html.H5(t("prev_tab2", lc), style={"marginBottom": "16px"}),
        dbc.Row([
            dbc.Col([html.Label(t("prev_versamento", lc), style={"fontSize": "12px"}),
                     dcc.Input(id="p3a-versamento", type="number", value=min(max_3a, 7258), min=0, max=max_3a, step=100, className="form-control")], width=3),
            dbc.Col([html.Label(t("prev_anni_inv", lc), style={"fontSize": "12px"}),
                     dcc.Slider(id="p3a-anni", min=5, max=40, step=1, value=anni_pensionamento,
                                marks={5: "5", 20: "20", 40: "40"})], width=3),
            dbc.Col([html.Label(t("prev_rendimento", lc), style={"fontSize": "12px"}),
                     dcc.Slider(id="p3a-rend", min=0.5, max=7.0, step=0.5, value=3.5,
                                marks={0.5: "0.5%", 3.5: "3.5%", 7: "7%"})], width=3),
            dbc.Col([html.Label(t("prev_aliquota", lc), style={"fontSize": "12px"}),
                     dcc.Slider(id="p3a-aliquota", min=10, max=45, step=1, value=25,
                                marks={10: "10%", 25: "25%", 45: "45%"})], width=3),
        ], className="mb-3 g-3"),
        html.Div(id="p3a-chart"),
        html.Div(id="p3a-metrics"),
        dcc.Store(id="p3a-lc-store", data=lc),
        dcc.Store(id="p3a-max3a-store", data=max_3a),
    ])


@callback(
    Output("p3a-chart", "children"),
    Output("p3a-metrics", "children"),
    Input("p3a-versamento", "value"),
    Input("p3a-anni", "value"),
    Input("p3a-rend", "value"),
    Input("p3a-aliquota", "value"),
    Input("p3a-lc-store", "data"),
    prevent_initial_call=False,
)
def update_p3a(versamento_annuo, anni_inv, rend_pct, aliquota, lc):
    versamento_annuo = versamento_annuo or 7258
    anni_inv = anni_inv or 27
    rend_pct = rend_pct or 3.5
    aliquota = aliquota or 25
    lc = lc or "it"

    def sim3a(v, n, r):
        c = [0]
        for _ in range(n):
            c.append(c[-1] * (1 + r / 100) + v)
        return c

    cap_ora = sim3a(versamento_annuo, anni_inv, rend_pct)
    n = len(cap_ora)
    cap_tardi_raw = sim3a(versamento_annuo, max(anni_inv - 5, 1), rend_pct)
    cap_tardi = [0] * min(6, n) + cap_tardi_raw
    cap_tardi = cap_tardi[:n]
    if len(cap_tardi) < n:
        cap_tardi += [cap_tardi[-1]] * (n - len(cap_tardi))
    risp_fis = [versamento_annuo * aliquota / 100 * i for i in range(n)]

    rows = []
    for i in range(n):
        rows.append({"Anno": i, "CHF": cap_ora[i], "Scenario": "Inizia ora"})
        rows.append({"Anno": i, "CHF": cap_tardi[i], "Scenario": "Inizia tra 5 anni"})
        rows.append({"Anno": i, "CHF": risp_fis[i], "Scenario": "Risparmio fiscale"})
    df3 = pd.DataFrame(rows)

    fig = px.line(df3, x="Anno", y="CHF", color="Scenario",
                  color_discrete_map={"Inizia ora": "#c0392b", "Inizia tra 5 anni": "#e8a0a0", "Risparmio fiscale": "#27ae60"},
                  template="plotly_white", height=300)
    fig.update_layout(margin=dict(t=10, b=0), yaxis=dict(tickformat=",.0f"))

    cap_finale = int(cap_ora[-1])
    cap_tardi_fin = int(cap_tardi[-1])
    costo_ritardo = cap_finale - cap_tardi_fin
    tass_stim = int(cap_finale * 0.07)
    risp_fis_tot = int(risp_fis[-1])

    metrics = dbc.Row([
        dbc.Col(html.Div([html.Div(t("prev_capitale", lc), className="kpi-label"), html.Div(f"CHF {cap_finale:,}", className="kpi-value")], className="kpi-box"), width=3),
        dbc.Col(html.Div([html.Div(t("prev_risp_fis", lc), className="kpi-label"), html.Div(f"CHF {risp_fis_tot:,}", className="kpi-value", style={"color": "#27ae60"})], className="kpi-box"), width=3),
        dbc.Col(html.Div([html.Div(t("prev_costo_ritardo", lc), className="kpi-label"), html.Div(f"CHF {costo_ritardo:,}", className="kpi-value", style={"color": "#e74c3c"})], className="kpi-box"), width=3),
        dbc.Col(html.Div([html.Div(t("prev_tassazione", lc), className="kpi-label"), html.Div(f"CHF {tass_stim:,}", className="kpi-value")], className="kpi-box"), width=3),
    ], className="g-3 mt-3")

    return dcc.Graph(figure=fig, config={"displayModeBar": False}), metrics


def render_prev_lacuna(lc, eta, reddito_mensile, situazione):
    reddito_annuo = reddito_mensile * 12
    avs = min(reddito_annuo * 0.18, 2520 * 12)
    lpp = max((reddito_annuo - 26460) * 0.18, 0) if situazione != "Indipendente" else 0

    return html.Div([
        html.H5(t("prev_tab3", lc), style={"marginBottom": "16px"}),
        html.Label(t("prev_obiettivo", lc), style={"fontSize": "12px"}),
        dcc.Slider(id="prev-obiettivo-pct", min=50, max=90, step=5, value=70,
                   marks={50: "50%", 70: "70%", 90: "90%"}),
        html.Div(id="prev-lacuna-chart"),
        dcc.Store(id="prev-lac-eta-store", data=eta),
        dcc.Store(id="prev-lac-red-store", data=reddito_mensile),
        dcc.Store(id="prev-lac-sit-store", data=situazione),
        dcc.Store(id="prev-lac-lc-store", data=lc),
    ])


@callback(
    Output("prev-lacuna-chart", "children"),
    Input("prev-obiettivo-pct", "value"),
    Input("prev-lac-eta-store", "data"),
    Input("prev-lac-red-store", "data"),
    Input("prev-lac-sit-store", "data"),
    Input("prev-lac-lc-store", "data"),
    prevent_initial_call=False,
)
def update_lacuna_chart(pct_obiettivo, eta, reddito_mensile, situazione, lc):
    pct_obiettivo = pct_obiettivo or 70
    reddito_mensile = reddito_mensile or 5500
    situazione = situazione or "Dipendente"
    lc = lc or "it"
    reddito_annuo = reddito_mensile * 12
    avs = min(reddito_annuo * 0.18, 2520 * 12)
    lpp = max((reddito_annuo - 26460) * 0.18, 0) if situazione != "Indipendente" else 0
    obiettivo = reddito_annuo * pct_obiettivo / 100
    lacuna = max(obiettivo - avs - lpp, 0)

    df = pd.DataFrame({
        "Fonte": ["1° AVS", "2° LPP", t("rac_lacuna_warning", lc)],
        "CHF/anno": [int(avs), int(lpp), int(lacuna)],
    })
    fig = px.bar(df, x="Fonte", y="CHF/anno",
                 color="Fonte",
                 color_discrete_map={"1° AVS": "#2980b9", "2° LPP": "#27ae60", t("rac_lacuna_warning", lc): "#e74c3c"},
                 template="plotly_white", height=280)
    fig.add_hline(y=obiettivo, line_dash="dash", line_color="#f39c12",
                  annotation_text=f"Obiettivo {pct_obiettivo}%", annotation_position="top right")
    fig.update_layout(showlegend=False, margin=dict(t=20, b=0))

    metrics = dbc.Row([
        dbc.Col(html.Div([html.Div(t("prev_obiettivo_annuo", lc), className="kpi-label"), html.Div(f"CHF {int(obiettivo):,}/a", className="kpi-value")], className="kpi-box"), width=4),
        dbc.Col(html.Div([html.Div("1° + 2° Pilastro", className="kpi-label"), html.Div(f"CHF {int(avs+lpp):,}/a", className="kpi-value")], className="kpi-box"), width=4),
        dbc.Col(html.Div([html.Div(t("prev_lacuna", lc), className="kpi-label"), html.Div(f"CHF {int(lacuna):,}/a", className="kpi-value", style={"color": "#e74c3c" if lacuna > 0 else "#27ae60"})], className="kpi-box"), width=4),
    ], className="g-3 mb-3")

    return html.Div([metrics, dcc.Graph(figure=fig, config={"displayModeBar": False})])
