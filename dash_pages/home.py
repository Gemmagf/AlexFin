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
    lc    = store.get("lc", "it")
    nome  = store.get("nome", "")
    eta   = store.get("eta", 38)
    canton = store.get("canton", "Zürich")

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

    open_lbl = t("home_open", lc)

    def mod_card(icon, title, desc, href):
        return dbc.Col(
            html.A(
                html.Div([
                    html.Span(icon, className="mod-icon"),
                    html.Div(title, className="mod-title"),
                    html.Div(desc, className="mod-desc"),
                    html.Div(
                        open_lbl,
                        style={"marginTop": "18px", "color": "#c0392b",
                               "fontWeight": "700", "fontSize": "0.9rem"},
                    ),
                ], className="mod-card"),
                href=href, className="mod-card-wrap",
            ), md=3,
        )

    n_ev = len(EVENTS)
    n_sp = len(NETWORKING_SPOTS)
    n_em = len(EMAIL_TEMPLATES)

    cards = dbc.Row(
        [
            mod_card("🧑‍💼",
                     t("home_mod_advisor_title", lc),
                     t("home_mod_advisor_desc", lc),
                     "/advisor"),
            mod_card("🛡️",
                     t("home_mod_ass_title", lc),
                     t("home_mod_ass_desc", lc),
                     "/assegurances"),
            mod_card("🏡",
                     t("home_mod_budget_title", lc),
                     t("home_mod_budget_desc", lc),
                     "/vida-budget"),
            mod_card("🔭",
                     t("home_mod_prosp_title", lc),
                     t("home_mod_prosp_desc", lc).format(n_ev=n_ev, n_sp=n_sp, n_em=n_em),
                     "/prospecting"),
        ],
        className="g-4",
    )

    def stat_box(value, label):
        return dbc.Col(html.Div([
            html.Div(value, style={"fontSize": "2rem", "fontWeight": "800", "color": "#c0392b"}),
            html.Div(label,  style={"fontSize": "0.78rem", "color": "#888", "fontWeight": "600"}),
        ], className="metric-card", style={"textAlign": "center", "padding": "20px"}), md=3)

    stats = dbc.Row([
        stat_box("11",      t("home_stat_lingue",   lc)),
        stat_box(str(n_ev), t("home_stat_eventi",   lc)),
        stat_box("3",       t("home_stat_pilastri", lc)),
        stat_box("∞",       t("home_stat_crm",      lc)),
    ], className="g-3 mb-4")

    return html.Div([
        html.Div([
            html.H1(
                [html.Span("AlexFin", style={"color": "#c0392b"}), " Advisor Tool"],
                style={"fontSize": "2rem", "fontWeight": "800",
                       "color": "#1e2235", "marginBottom": "4px"},
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
            html.H2(t("home_moduli", lc),
                    style={"fontSize": "1rem", "fontWeight": "700",
                           "color": "#1e2235", "marginBottom": "20px",
                           "letterSpacing": "-0.2px"}),
        ),
        cards,
        html.Hr(style={"marginTop": "40px", "borderColor": "#eaecf2"}),
        html.P(t("footer", lc), className="footer"),
    ])
