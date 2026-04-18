# dash_pages/home.py — AlexFin Home

import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

from i18n import t
from prospect_data import EVENTS, NETWORKING_SPOTS, EMAIL_TEMPLATES

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

    def mod_card(icon, title, desc, href):
        return dbc.Col(
            html.A(
                html.Div([
                    html.Span(icon, className="mod-icon"),
                    html.Div(title, className="mod-title"),
                    html.Div(desc, className="mod-desc"),
                    html.Div(
                        "→ Apri",
                        style={"marginTop": "18px", "color": "#c0392b", "fontWeight": "700", "fontSize": "0.9rem"},
                    ),
                ], className="mod-card"),
                href=href, className="mod-card-wrap",
            ), md=3,
        )

    cards = dbc.Row(
        [
            mod_card("🧑‍💼", "Advisor Dashboard",
                     "Analisi profilo, raccomandazioni prioritarie, simulatore patrimoniale, note e CRM clienti.",
                     "/advisor"),
            mod_card("🛡️", "Assicurazioni & Pilastri",
                     "Prodotti SVAG, comparatore Krankenkasse con franchigie/modelli, 1°/2°/3° pilastro.",
                     "/assegurances"),
            mod_card("🏡", "Vita & Budget",
                     "Budget mensile, pianificazione per fase di vita, obiettivi finanziari con timeline.",
                     "/vida-budget"),
            mod_card("🔭", "Prospecting",
                     f"{len(EVENTS)} eventi networking · {len(NETWORKING_SPOTS)} associazioni · {len(EMAIL_TEMPLATES)} template email.",
                     "/prospecting"),
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
            html.Div(str(len(EVENTS)), style={"fontSize": "2rem", "fontWeight": "800", "color": "#c0392b"}),
            html.Div("Eventi networking", style={"fontSize": "0.78rem", "color": "#888", "fontWeight": "600"}),
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
            html.H2("Moduli", style={"fontSize": "1rem", "fontWeight": "700", "color": "#1e2235", "marginBottom": "20px", "letterSpacing": "-0.2px"}),
        ),
        cards,
        html.Hr(style={"marginTop": "40px", "borderColor": "#eaecf2"}),
        html.P(t("footer", lc), className="footer"),
    ])
