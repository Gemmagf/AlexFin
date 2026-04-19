# dash_pages/vida_budget.py — Vita & Budget Familiare
# Tabs: Budget, Fasi di vita, Obiettivi

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import callback, dcc, html, Input, Output, State
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


@callback(Output("vb-tab-content", "children"), Input("vb-tabs", "active_tab"), Input("app-store", "data"))
def render_tab(active_tab, store):
    if not store:
        store = {}
    lc = store.get("lc", "it")
    reddito_mensile = store.get("reddito_mensile", 5500)
    figli = store.get("figli", False)
    eta = store.get("eta", 38)

    if active_tab == "tab-budget":
        content = render_budget(lc, reddito_mensile, figli)
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


def render_budget(lc, reddito_mensile, figli):
    return html.Div([
        html.H4(t("vita_tab1", lc), style={"marginBottom": "16px"}),
        dbc.Row([
            dbc.Col([
                html.H6(f"💰 {t('vita_entrate', lc)}", style={"fontSize": "0.85rem", "fontWeight": "700"}),
                *_budget_row(t("vita_salario1", lc), "vb-sal1", reddito_mensile, 0, 50000, 100),
                *_budget_row(t("vita_salario2", lc), "vb-sal2", 0, 0, 30000, 100),
                *_budget_row(t("vita_altri_entrate", lc), "vb-altri", 0, 0, 10000, 50),
            ], md=4),
            dbc.Col([
                html.H6(f"📤 {t('vita_uscite', lc)}", style={"fontSize": "0.85rem", "fontWeight": "700"}),
                *_budget_row(t("vita_affitto", lc), "vb-aff", 1600, 0, 10000, 50),
                *_budget_row(t("vita_cibo", lc), "vb-cibo", 700, 0, 5000, 50),
                *_budget_row(t("vita_trasporto", lc), "vb-tras", 300, 0, 3000, 50),
                *_budget_row(t("vita_salute", lc), "vb-sal", 500, 0, 5000, 50),
                *_budget_row(t("vita_intrattenimento", lc), "vb-int", 300, 0, 3000, 50),
                *_budget_row(t("vita_asilo", lc), "vb-asilo", 800 if figli else 0, 0, 5000, 50),
                *_budget_row(t("vita_altro", lc), "vb-alt", 200, 0, 3000, 50),
            ], md=4),
            dbc.Col([
                html.H6(f"🎯 {t('vita_risparmio_target', lc)}", style={"fontSize": "0.85rem", "fontWeight": "700"}),
                dcc.Input(id="vb-risp-target", type="number", value=int(reddito_mensile * 0.15),
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
        semaforo = html.Div(f"✅ Saldo CHF {saldo:,}/mese. Risparmio {pct:.1f}% — ottimo!", className="budget-ok")
    elif saldo > 0:
        semaforo = html.Div(f"⚠️ Saldo positivo (CHF {saldo:,}) ma sotto il target.", className="budget-warn")
    else:
        semaforo = html.Div(f"❌ Saldo negativo: CHF {saldo:,}/mese. Revisione urgente.", className="budget-err")

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
    df_5030 = pd.DataFrame({
        "Categoria": ["Necessità (50%)", "Discrezionale (30%)", "Risparmio (20%)"],
        "Attuale (CHF)": [necessario, discrezionale, risp_target],
        "Target (CHF)": [int(totale_entrate * 0.5), int(totale_entrate * 0.3), int(totale_entrate * 0.2)],
    })
    table_5030 = dbc.Table.from_dataframe(df_5030, striped=True, hover=True, responsive=True, size="sm")
    df_melted = df_5030.melt("Categoria", ["Attuale (CHF)", "Target (CHF)"], var_name="Tipo", value_name="CHF")
    fig_5030 = px.bar(df_melted, x="Categoria", y="CHF", color="Tipo", barmode="group",
                      color_discrete_map={"Attuale (CHF)": "#c0392b", "Target (CHF)": "#bdc3c7"},
                      template="plotly_white", height=200)
    fig_5030.update_layout(margin=dict(t=10, b=0), xaxis_title="", legend=dict(orientation="h", y=-0.4))

    return kpis, semaforo, fig_pie, table_5030, fig_5030


# ─────────────────────────────────────────────
# TAB 2 — FASI DI VITA
# ─────────────────────────────────────────────

def render_fasi(lc, eta, figli, reddito_mensile):
    fase_opts = t("vita_fase_opts", lc)
    default_idx = 2 if figli else 0
    return html.Div([
        html.H4(t("vita_tab2", lc), style={"marginBottom": "16px"}),
        html.Label(t("vita_fase_label", lc), style={"fontSize": "12px"}),
        dcc.Slider(
            id="vb-fase",
            min=0, max=len(fase_opts) - 1, step=1,
            value=default_idx,
            marks={i: {"label": fase_opts[i], "style": {"fontSize": "11px", "whiteSpace": "nowrap"}} for i in range(len(fase_opts))},
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
    fase_idx = fase_idx or 0
    fase = fase_opts[fase_idx]

    costi_fase = {
        fase_opts[0]: {"Abitazione": 1400, "Trasporto": 300, "Alimentazione": 600, "Svago": 500, "KK": 470, "3a": 600, "Risparmio": 500},
        fase_opts[1]: {"Abitazione": 1900, "Trasporto": 500, "Alimentazione": 1000, "Svago": 700, "KK": 940, "3a": 1200, "Risparmio": 800},
        fase_opts[2]: {"Abitazione": 2400, "Trasporto": 600, "Alimentazione": 1300, "Asilo/Scuola": 1200, "KK": 1500, "3a": 600, "Risparmio": 400},
        fase_opts[3]: {"Abitazione": 2500, "Trasporto": 700, "Alimentazione": 1500, "Scuola/Sport": 800, "KK": 1600, "3a": 600, "Risparmio": 600},
        fase_opts[4]: {"Abitazione": 2200, "Trasporto": 500, "Alimentazione": 1200, "Università": 2000, "KK": 1400, "3a": 600, "Risparmio": 300},
        fase_opts[5]: {"Abitazione": 2000, "Trasporto": 500, "Alimentazione": 1100, "Svago": 800, "KK": 1800, "3a": 604, "Risparmio": 1200},
        fase_opts[6]: {"Abitazione": 1800, "Trasporto": 400, "Alimentazione": 1000, "Svago": 700, "KK": 2000, "3a": 604, "Risparmio": 1500},
    }
    dati_fase = costi_fase.get(fase, list(costi_fase.values())[0])
    totale_fase = sum(dati_fase.values())
    df_fase = pd.DataFrame([{"Voce": k, "CHF/mese stimato": v} for k, v in dati_fase.items()])

    fig = px.bar(df_fase, x="CHF/mese stimato", y="Voce", orientation="h",
                 color_discrete_sequence=["#c0392b"],
                 template="plotly_white", height=300, title=fase)
    fig.update_layout(margin=dict(t=30, b=0), yaxis_title="", yaxis=dict(categoryorder="total ascending"))

    delta_v = reddito_mensile - totale_fase
    alert = (html.Div(f"✅ Reddito sufficiente. Margine: CHF {delta_v:,}/mese", className="budget-ok")
             if delta_v >= 0
             else html.Div(f"❌ Deficit: CHF {abs(delta_v):,}/mese rispetto al reddito.", className="budget-err"))

    return html.Div([
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Table.from_dataframe(df_fase, striped=True, hover=True, responsive=True, size="sm"),
                html.Div([
                    html.Div([html.Div("Totale stimato mensile", className="kpi-label"),
                              html.Div(f"CHF {totale_fase:,}", className="kpi-value")], className="kpi-box"),
                ], style={"marginTop": "12px"}),
                html.Div(alert, style={"marginTop": "12px"}),
            ], width=5),
            dbc.Col([dcc.Graph(figure=fig, config={"displayModeBar": False})], width=7),
        ]),
    ])


# ─────────────────────────────────────────────
# TAB 3 — OBIETTIVI
# ─────────────────────────────────────────────

def render_obiettivi(lc, reddito_mensile):
    default_nomi = ["Casa", "Auto", "Pensione anticipata", "Università figli", "Viaggio", "Emergenza"]
    default_importi = [100000, 30000, 500000, 80000, 15000, 50000]
    default_anni = [10, 3, 20, 15, 2, 5]

    return html.Div([
        html.H4(t("vita_obiettivi_titolo", lc), style={"marginBottom": "16px"}),
        html.Label("Numero di obiettivi", style={"fontSize": "12px"}),
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

    obiettivi = []
    for i in range(n_obj):
        nome_v = (nomi_vals[i] if i < len(nomi_vals) and nomi_vals[i] else default_nomi[i])
        importo_v = (importi_vals[i] if i < len(importi_vals) and importi_vals[i] else default_importi[i])
        anni_v = (anni_vals[i] if i < len(anni_vals) and anni_vals[i] else default_anni[i])
        importo_v = max(int(importo_v), 0)
        anni_v = max(int(anni_v), 1)
        risp_mens = int(importo_v / (anni_v * 12))
        obiettivi.append({
            "Nome": nome_v,
            "Importo (CHF)": importo_v,
            "Anni": anni_v,
            "CHF/mese necessario": risp_mens,
        })

    if not obiettivi:
        return html.Div()

    df_obj = pd.DataFrame(obiettivi)
    totale_risp = sum(o["CHF/mese necessario"] for o in obiettivi)
    capacita = reddito_mensile - totale_risp

    # Summary table
    table = dbc.Table.from_dataframe(df_obj, striped=True, hover=True, responsive=True, size="sm")

    metrics = dbc.Row([
        dbc.Col(html.Div([html.Div("Risparmio totale necessario", className="kpi-label"),
                          html.Div(f"CHF {totale_risp:,}/m", className="kpi-value")], className="kpi-box"), width=6),
        dbc.Col(html.Div([html.Div("Capacità residua", className="kpi-label"),
                          html.Div(f"CHF {capacita:,}/m", className="kpi-value",
                                   style={"color": "#27ae60" if capacita >= 0 else "#e74c3c"})], className="kpi-box"), width=6),
    ], className="g-3 mb-3")

    if capacita >= 0:
        alert = html.Div(f"✅ Obiettivi raggiungibili. Margine: CHF {capacita:,}/mese.", className="budget-ok")
    else:
        alert = html.Div(f"❌ Servono CHF {totale_risp:,}/mese. Deficit: CHF {abs(capacita):,}/mese.", className="budget-err")

    # Gantt timeline
    df_gantt = pd.DataFrame([{
        "Obiettivo": o["Nome"],
        "Inizio": 0,
        "Fine": o["Anni"],
        "Importo": o["Importo (CHF)"],
        "CHF/mese": o["CHF/mese necessario"],
    } for o in obiettivi])

    # Use horizontal bar as Gantt
    fig_gantt = go.Figure()
    colors = px.colors.sequential.Reds
    max_importo = max(o["Importo (CHF)"] for o in obiettivi) or 1
    for i, row in df_gantt.iterrows():
        color_idx = min(int(row["Importo"] / max_importo * (len(colors) - 1)), len(colors) - 1)
        fig_gantt.add_trace(go.Bar(
            x=[row["Fine"] - row["Inizio"]],
            y=[row["Obiettivo"]],
            orientation="h",
            base=row["Inizio"],
            marker_color=colors[color_idx],
            hovertemplate=f"{row['Obiettivo']}: CHF {row['Importo']:,} — {row['Fine']} anni<extra></extra>",
            showlegend=False,
        ))
    fig_gantt.update_layout(
        template="plotly_white",
        height=max(180, len(obiettivi) * 50),
        xaxis_title="Anni da oggi",
        yaxis_title="",
        title="Timeline obiettivi finanziari",
        margin=dict(t=40, b=0),
        barmode="stack",
    )

    # Accumulation line chart
    rows_acc = []
    for o in obiettivi:
        acc = 0
        for mese in range(o["Anni"] * 12 + 1):
            acc += o["CHF/mese necessario"]
            if mese % 12 == 0:
                rows_acc.append({"Obiettivo": o["Nome"], "Anno": mese // 12, "CHF accumulati": acc})
    if rows_acc:
        df_acc = pd.DataFrame(rows_acc)
        fig_acc = px.line(df_acc, x="Anno", y="CHF accumulati", color="Obiettivo",
                          color_discrete_sequence=px.colors.qualitative.Set1,
                          template="plotly_white", height=280, title="📈 Proiezione accumulo per obiettivo")
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
