# dash_pages/home.py — AlexFin Home

import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

from i18n import t

dash.register_page(__name__, path="/", name="Home")


def layout():
    return html.Div(id="home-layout", style={"minHeight": "60vh"})


@callback(
    Output("home-layout", "children"),
    Input("app-store", "data"),
)
def render_home(store):
    store = store or {}
    lc = store.get("lc", "it")
    nome = store.get("nome", "")
    eta = store.get("eta", 38)
    canton = store.get("canton", "Ticino")

    client_pill = []
    if nome:
        client_pill = [
            html.Div(
                f"👤 {nome} · {eta} anni · {canton}",
                style={
                    "display": "inline-flex", "alignItems": "center",
                    "background": "#fde8e8", "color": "#c0392b",
                    "borderRadius": "20px", "padding": "5px 16px",
                    "fontSize": "0.85rem", "fontWeight": "600",
                    "marginBottom": "24px",
                }
            )
        ]

    cards = dbc.Row(
        [
            dbc.Col(
                html.A(
                    html.Div([
                        html.Span("🧑‍💼", className="mod-icon"),
                        html.Div("Advisor Dashboard", className="mod-title"),
                        html.Div(
                            "Analisi profilo, raccomandazioni prioritarie, simulatore patrimoniale, note e CRM clienti.",
                            className="mod-desc",
                        ),
                        html.Div(
                            "→ Apri",
                            style={"marginTop": "18px", "color": "#c0392b", "fontWeight": "700", "fontSize": "0.9rem"},
                        ),
                    ], className="mod-card"),
                    href="/advisor", className="mod-card-wrap",
                ), md=4,
            ),
            dbc.Col(
                html.A(
                    html.Div([
                        html.Span("🛡️", className="mod-icon"),
                        html.Div("Assicurazioni & Pilastri", className="mod-title"),
                        html.Div(
                            "Prodotti SVAG, comparatore Krankenkasse con franchigie/modelli, 1°/2°/3° pilastro.",
                            className="mod-desc",
                        ),
                        html.Div(
                            "→ Apri",
                            style={"marginTop": "18px", "color": "#c0392b", "fontWeight": "700", "fontSize": "0.9rem"},
                        ),
                    ], className="mod-card"),
                    href="/assegurances", className="mod-card-wrap",
                ), md=4,
            ),
            dbc.Col(
                html.A(
                    html.Div([
                        html.Span("🏡", className="mod-icon"),
                        html.Div("Vita & Budget", className="mod-title"),
                        html.Div(
                            "Budget mensile, pianificazione per fase di vita, obiettivi finanziari con timeline.",
                            className="mod-desc",
                        ),
                        html.Div(
                            "→ Apri",
                            style={"marginTop": "18px", "color": "#c0392b", "fontWeight": "700", "fontSize": "0.9rem"},
                        ),
                    ], className="mod-card"),
                    href="/vida-budget", className="mod-card-wrap",
                ), md=4,
            ),
        ],
        className="g-4",
    )

    # Stats row
    stats = dbc.Row([
        dbc.Col(html.Div([
            html.Div("11", style={"fontSize": "2rem", "fontWeight": "800", "color": "#c0392b"}),
            html.Div("Lingue supportate", style={"fontSize": "0.78rem", "color": "#888", "fontWeight": "600"}),
        ], className="metric-card", style={"textAlign": "center", "padding": "20px"}), md=3),
        dbc.Col(html.Div([
            html.Div("6", style={"fontSize": "2rem", "fontWeight": "800", "color": "#c0392b"}),
            html.Div("Prodotti assicurativi", style={"fontSize": "0.78rem", "color": "#888", "fontWeight": "600"}),
        ], className="metric-card", style={"textAlign": "center", "padding": "20px"}), md=3),
        dbc.Col(html.Div([
            html.Div("3", style={"fontSize": "2rem", "fontWeight": "800", "color": "#c0392b"}),
            html.Div("Pilastri previdenziali", style={"fontSize": "0.78rem", "color": "#888", "fontWeight": "600"}),
        ], className="metric-card", style={"textAlign": "center", "padding": "20px"}), md=3),
        dbc.Col(html.Div([
            html.Div("∞", style={"fontSize": "2rem", "fontWeight": "800", "color": "#c0392b"}),
            html.Div("Clienti nel CRM", style={"fontSize": "0.78rem", "color": "#888", "fontWeight": "600"}),
        ], className="metric-card", style={"textAlign": "center", "padding": "20px"}), md=3),
    ], className="g-3 mb-4")

    return html.Div([
        # Hero
        html.Div([
            html.H1(
                [html.Span("AlexFin", style={"color": "#c0392b"}), " Advisor Tool"],
                style={"fontSize": "2rem", "fontWeight": "800", "color": "#1e2235", "marginBottom": "4px"},
            ),
            html.P(
                t("app_subtitle", lc),
                style={"color": "#888", "fontSize": "0.95rem", "marginBottom": "20px"},
            ),
            *client_pill,
        ]),
        html.Hr(style={"borderColor": "#eaecf2", "marginBottom": "28px"}),
        stats,
        html.Div(
            html.H2("Moduli", style={"fontSize": "1rem", "fontWeight": "700", "color": "#1e2235", "marginBottom": "20px"}),
        ),
        cards,
        html.Hr(style={"marginTop": "40px", "borderColor": "#eaecf2"}),
        html.P(t("footer", lc), className="footer"),
    ])
