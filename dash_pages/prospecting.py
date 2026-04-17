# dash_pages/prospecting.py — Prospecting & Networking page

import json
import os
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import dash
from dash import callback, dcc, html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc

from i18n import t
from prospect_data import EVENTS, NETWORKING_SPOTS, EMAIL_TEMPLATES, CITIES, EVENT_TYPES, SPOT_CATEGORIES

dash.register_page(__name__, path="/prospecting", name="Prospecting")

SENT_LOG = os.path.join(os.path.dirname(__file__), "..", "email_sent.json")


def load_sent():
    if os.path.exists(SENT_LOG):
        with open(SENT_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_sent(log):
    with open(SENT_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

TYPE_COLORS = {
    "Networking": "#2980b9",
    "Camera di Commercio": "#8e44ad",
    "Startup & Tech": "#e67e22",
    "Rotary": "#2c3e50",
    "Lions": "#f39c12",
    "Expat Network": "#27ae60",
    "Finance": "#c0392b",
    "Elite Networking": "#1abc9c",
    "Forum Economico": "#d35400",
    "PMI": "#7f8c8d",
    "Università": "#16a085",
    "Industria": "#8e44ad",
}

CAT_COLORS = {
    "Rotary & Lions": "#2c3e50",
    "Referral Networking": "#2980b9",
    "Camere di Commercio": "#8e44ad",
    "Alumni University": "#16a085",
    "Professional Clubs": "#c0392b",
    "Expat & International": "#27ae60",
    "PMI & Imprenditori": "#e67e22",
}


def freq_badge(freq):
    colors = {"Settimanale": "#27ae60", "Mensile": "#2980b9", "Bimestrale": "#f39c12",
              "Trimestrale": "#e67e22", "Annuale": "#8e44ad", "Annuale ": "#8e44ad"}
    color = colors.get(freq, "#95a5a6")
    return html.Span(
        freq,
        style={"background": color, "color": "white", "padding": "2px 10px",
               "borderRadius": "12px", "fontSize": "0.7rem", "fontWeight": "700", "whiteSpace": "nowrap"}
    )


def event_card(ev):
    type_color = TYPE_COLORS.get(ev["type"], "#95a5a6")
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(ev["icon"], style={"fontSize": "1.4rem", "marginRight": "10px"}),
                            html.Div(
                                [
                                    html.Div(ev["name"], style={"fontWeight": "700", "fontSize": "0.95rem", "color": "#1e2235"}),
                                    html.Div(
                                        [
                                            html.Span(ev["type"], style={"background": type_color + "22", "color": type_color,
                                                                          "padding": "2px 9px", "borderRadius": "10px",
                                                                          "fontSize": "0.7rem", "fontWeight": "700", "marginRight": "6px"}),
                                            freq_badge(ev["frequency"]),
                                        ],
                                        style={"marginTop": "4px", "display": "flex", "gap": "6px", "flexWrap": "wrap"},
                                    ),
                                ]
                            ),
                        ],
                        style={"display": "flex", "alignItems": "flex-start"},
                    ),
                    html.Div(
                        html.A("→ Sito", href=ev["url"], target="_blank",
                               style={"color": "#c0392b", "fontWeight": "600", "fontSize": "0.82rem", "textDecoration": "none"}),
                    ),
                ],
                style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start", "marginBottom": "10px"},
            ),
            html.Div(ev["desc"], style={"fontSize": "0.85rem", "color": "#555", "marginBottom": "8px"}),
            html.Div(
                [html.Span("🎯 Target: ", style={"fontWeight": "600", "color": "#888", "fontSize": "0.8rem"}),
                 html.Span(ev["audience"], style={"color": "#555", "fontSize": "0.8rem"})],
            ),
        ],
        style={
            "background": "white", "borderRadius": "14px", "padding": "16px 20px",
            "marginBottom": "12px", "boxShadow": "0 2px 14px rgba(0,0,0,0.05)",
            "border": f"1px solid #eaecf2", "borderLeft": f"4px solid {type_color}",
        }
    )


def spot_card(sp):
    cat_color = CAT_COLORS.get(sp["category"], "#95a5a6")
    return html.Div(
        [
            html.Div(
                [
                    html.Span(sp["icon"], style={"fontSize": "1.6rem", "marginRight": "12px"}),
                    html.Div(
                        [
                            html.Div(sp["name"], style={"fontWeight": "700", "fontSize": "1rem", "color": "#1e2235"}),
                            html.Span(sp["category"], style={"background": cat_color + "22", "color": cat_color,
                                                              "padding": "2px 10px", "borderRadius": "10px",
                                                              "fontSize": "0.7rem", "fontWeight": "700"}),
                        ]
                    ),
                ],
                style={"display": "flex", "alignItems": "center", "marginBottom": "12px"},
            ),
            html.Div(sp["desc"], style={"fontSize": "0.88rem", "color": "#555", "marginBottom": "10px"}),
            html.Div(
                [html.Span("🎯 Target: ", style={"fontWeight": "700", "fontSize": "0.82rem"}),
                 html.Span(sp["target"], style={"fontSize": "0.82rem", "color": "#555"})],
                style={"marginBottom": "6px"},
            ),
            html.Div(
                [html.Span("🚪 Come entrare: ", style={"fontWeight": "700", "fontSize": "0.82rem"}),
                 html.Span(sp["come_entrare"], style={"fontSize": "0.82rem", "color": "#555"})],
                style={"marginBottom": "10px"},
            ),
            html.A("→ Visita sito", href=sp["url"], target="_blank",
                   style={"color": "#c0392b", "fontWeight": "600", "fontSize": "0.82rem", "textDecoration": "none"}),
        ],
        style={
            "background": "white", "borderRadius": "16px", "padding": "20px 22px",
            "marginBottom": "14px", "boxShadow": "0 2px 16px rgba(0,0,0,0.06)",
            "border": "1px solid #eaecf2", "borderLeft": f"4px solid {cat_color}",
        }
    )


# ─────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────

def layout():
    return html.Div([
        html.Div(id="prosp-header"),
        dbc.Tabs(
            [
                dbc.Tab(label="📅 Events & Networking", tab_id="tab-events"),
                dbc.Tab(label="🏛️ Luoghi & Associazioni", tab_id="tab-spots"),
                dbc.Tab(label="📧 Email Marketing", tab_id="tab-email"),
                dbc.Tab(label="📊 Storico Invii", tab_id="tab-log"),
            ],
            id="prosp-tabs",
            active_tab="tab-events",
        ),
        html.Div(id="prosp-tab-content", style={"marginTop": "16px"}),
        dcc.Store(id="prosp-email-status", data=""),
    ])


@callback(Output("prosp-header", "children"), Input("app-store", "data"))
def render_header(store):
    store = store or {}
    lc = store.get("lc", "it")
    return html.Div([
        html.H1("🔭 Prospecting & Networking", className="page-title"),
        html.P("Trova nuovi clienti, partecipa agli eventi giusti e invia comunicazioni professionali.", className="page-caption"),
        html.Hr(),
    ])


@callback(
    Output("prosp-tab-content", "children"),
    Input("prosp-tabs", "active_tab"),
    Input("app-store", "data"),
)
def render_tab(active_tab, store):
    store = store or {}
    if active_tab == "tab-events":
        return render_events()
    elif active_tab == "tab-spots":
        return render_spots()
    elif active_tab == "tab-email":
        return render_email(store)
    elif active_tab == "tab-log":
        return render_log()
    return html.Div()


# ─────────────────────────────────────────────
# TAB 1 — EVENTS
# ─────────────────────────────────────────────

def render_events():
    return html.Div([
        # Filters
        html.Div(
            [
                dbc.Row([
                    dbc.Col([
                        html.Label("🏙️ Città", style={"fontSize": "0.8rem", "fontWeight": "700", "color": "#555", "marginBottom": "4px"}),
                        dcc.Dropdown(
                            id="ev-city-filter",
                            options=[{"label": "Tutte le città", "value": "all"}] + [{"label": c, "value": c} for c in CITIES],
                            value="all", clearable=False,
                            style={"fontSize": "0.87rem"},
                        ),
                    ], md=4),
                    dbc.Col([
                        html.Label("📌 Tipo", style={"fontSize": "0.8rem", "fontWeight": "700", "color": "#555", "marginBottom": "4px"}),
                        dcc.Dropdown(
                            id="ev-type-filter",
                            options=[{"label": "Tutti i tipi", "value": "all"}] + [{"label": t, "value": t} for t in EVENT_TYPES],
                            value="all", clearable=False,
                            style={"fontSize": "0.87rem"},
                        ),
                    ], md=4),
                    dbc.Col([
                        html.Label("🔁 Frequenza", style={"fontSize": "0.8rem", "fontWeight": "700", "color": "#555", "marginBottom": "4px"}),
                        dcc.Dropdown(
                            id="ev-freq-filter",
                            options=[{"label": "Tutte", "value": "all"},
                                     {"label": "Settimanale", "value": "Settimanale"},
                                     {"label": "Mensile", "value": "Mensile"},
                                     {"label": "Annuale", "value": "Annuale"}],
                            value="all", clearable=False,
                            style={"fontSize": "0.87rem"},
                        ),
                    ], md=4),
                ], className="g-3"),
            ],
            style={"background": "white", "borderRadius": "14px", "padding": "16px 20px",
                   "marginBottom": "16px", "boxShadow": "0 2px 12px rgba(0,0,0,0.05)", "border": "1px solid #eaecf2"},
        ),
        html.Div(id="ev-list"),
    ])


@callback(
    Output("ev-list", "children"),
    Input("ev-city-filter", "value"),
    Input("ev-type-filter", "value"),
    Input("ev-freq-filter", "value"),
)
def filter_events(city, ev_type, freq):
    filtered = EVENTS
    if city and city != "all":
        filtered = [e for e in filtered if e["city"] == city]
    if ev_type and ev_type != "all":
        filtered = [e for e in filtered if e["type"] == ev_type]
    if freq and freq != "all":
        filtered = [e for e in filtered if e["frequency"] == freq]

    if not filtered:
        return html.Div("Nessun evento trovato con i filtri selezionati.",
                        style={"color": "#888", "textAlign": "center", "padding": "40px"})

    # Group by city
    by_city = {}
    for ev in filtered:
        by_city.setdefault(ev["city"], []).append(ev)

    sections = []
    for city_name in sorted(by_city.keys()):
        evs = by_city[city_name]
        sections.append(
            html.Div([
                html.Div(
                    [
                        html.Span("📍", style={"marginRight": "8px"}),
                        city_name,
                        html.Span(f" ({len(evs)})", style={"color": "#888", "fontWeight": "400", "fontSize": "0.9rem"}),
                    ],
                    style={"fontSize": "1rem", "fontWeight": "800", "color": "#1e2235",
                           "marginBottom": "14px", "paddingBottom": "8px", "borderBottom": "2px solid #eaecf2"},
                ),
                *[event_card(ev) for ev in evs],
            ], style={"marginBottom": "28px"})
        )
    return html.Div([
        html.Div(f"{len(filtered)} eventi trovati",
                 style={"color": "#888", "fontSize": "0.82rem", "marginBottom": "16px"}),
        *sections,
    ])


# ─────────────────────────────────────────────
# TAB 2 — SPOTS
# ─────────────────────────────────────────────

def render_spots():
    return html.Div([
        html.Div(
            [
                html.Label("📂 Categoria", style={"fontSize": "0.8rem", "fontWeight": "700", "color": "#555", "marginBottom": "4px"}),
                dcc.Dropdown(
                    id="sp-cat-filter",
                    options=[{"label": "Tutte le categorie", "value": "all"}] + [{"label": c, "value": c} for c in SPOT_CATEGORIES],
                    value="all", clearable=False, style={"fontSize": "0.87rem", "maxWidth": "380px"},
                ),
            ],
            style={"background": "white", "borderRadius": "14px", "padding": "16px 20px",
                   "marginBottom": "16px", "boxShadow": "0 2px 12px rgba(0,0,0,0.05)", "border": "1px solid #eaecf2"},
        ),
        html.Div(id="sp-list"),
    ])


@callback(Output("sp-list", "children"), Input("sp-cat-filter", "value"))
def filter_spots(cat):
    filtered = NETWORKING_SPOTS if not cat or cat == "all" else [s for s in NETWORKING_SPOTS if s["category"] == cat]
    if not filtered:
        return html.Div("Nessun risultato.", style={"color": "#888", "padding": "40px", "textAlign": "center"})
    by_cat = {}
    for sp in filtered:
        by_cat.setdefault(sp["category"], []).append(sp)
    sections = []
    for cat_name, spots in by_cat.items():
        color = CAT_COLORS.get(cat_name, "#95a5a6")
        sections.append(html.Div([
            html.Div(cat_name, style={"fontSize": "1rem", "fontWeight": "800", "color": color,
                                      "marginBottom": "14px", "paddingBottom": "8px", "borderBottom": f"2px solid {color}33"}),
            *[spot_card(s) for s in spots],
        ], style={"marginBottom": "28px"}))
    return html.Div(sections)


# ─────────────────────────────────────────────
# TAB 3 — EMAIL MARKETING
# ─────────────────────────────────────────────

def render_email(store):
    nome_adv = store.get("nome", "Alex Bevilacqua") or "Alex Bevilacqua"
    canton = store.get("canton", "Ticino")

    template_opts = [{"label": v["nome"], "value": k} for k, v in EMAIL_TEMPLATES.items()]

    return html.Div([
        dbc.Row([
            # Left — compose
            dbc.Col([
                html.Div([
                    html.Div("📧 Componi Email", className="section-title"),

                    # Template selector
                    html.Label("Template", style={"fontSize": "0.8rem", "fontWeight": "700", "color": "#555", "marginBottom": "4px"}),
                    dcc.Dropdown(id="em-template", options=template_opts,
                                 value="fredda_presentazione", clearable=False,
                                 style={"fontSize": "0.87rem", "marginBottom": "14px"}),

                    # Personalization
                    dbc.Row([
                        dbc.Col([
                            html.Label("Nome destinatario", style={"fontSize": "0.78rem", "fontWeight": "600", "color": "#666"}),
                            dbc.Input(id="em-dest-nome", placeholder="Marco Rossi", size="sm"),
                        ], md=6),
                        dbc.Col([
                            html.Label("Email destinatario", style={"fontSize": "0.78rem", "fontWeight": "600", "color": "#666"}),
                            dbc.Input(id="em-dest-email", placeholder="marco@example.ch", type="email", size="sm"),
                        ], md=6),
                    ], className="g-2 mb-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Dove l'ha conosciuto/a", style={"fontSize": "0.78rem", "fontWeight": "600", "color": "#666"}),
                            dbc.Input(id="em-dove", placeholder="BNI Zurigo / LinkedIn / ...", size="sm"),
                        ], md=6),
                        dbc.Col([
                            html.Label("Telefono mittente", style={"fontSize": "0.78rem", "fontWeight": "600", "color": "#666"}),
                            dbc.Input(id="em-tel", placeholder="+41 91 000 0000", size="sm"),
                        ], md=6),
                    ], className="g-2 mb-3"),

                    # SMTP config
                    dbc.Accordion([
                        dbc.AccordionItem([
                            dbc.Row([
                                dbc.Col([html.Label("SMTP Server", style={"fontSize": "0.78rem", "fontWeight": "600", "color": "#666"}),
                                         dbc.Input(id="em-smtp-srv", value="smtp.gmail.com", size="sm")], md=6),
                                dbc.Col([html.Label("Porta", style={"fontSize": "0.78rem", "fontWeight": "600", "color": "#666"}),
                                         dbc.Input(id="em-smtp-port", value="587", size="sm")], md=6),
                            ], className="g-2 mb-2"),
                            dbc.Row([
                                dbc.Col([html.Label("Email mittente", style={"fontSize": "0.78rem", "fontWeight": "600", "color": "#666"}),
                                         dbc.Input(id="em-smtp-user", placeholder="tuoindirizzo@gmail.com", size="sm")], md=6),
                                dbc.Col([html.Label("Password / App Password", style={"fontSize": "0.78rem", "fontWeight": "600", "color": "#666"}),
                                         dbc.Input(id="em-smtp-pass", type="password", size="sm")], md=6),
                            ], className="g-2"),
                        ], title="⚙️ Configurazione SMTP"),
                    ], start_collapsed=True, style={"marginBottom": "14px"}),

                    dbc.Button("📤 Invia Email", id="em-send-btn", color="danger", size="sm", className="me-2"),
                    dbc.Button("👁️ Anteprima", id="em-preview-btn", color="secondary", size="sm", outline=True),
                    html.Div(id="em-status", style={"marginTop": "10px"}),
                ], className="content-card"),
            ], md=5),

            # Right — preview
            dbc.Col([
                html.Div([
                    html.Div("👁️ Anteprima", className="section-title"),
                    html.Div(id="em-preview-area"),
                ], className="content-card", style={"minHeight": "400px"}),
            ], md=7),
        ], className="g-4"),
    ])


@callback(
    Output("em-preview-area", "children"),
    Input("em-preview-btn", "n_clicks"),
    Input("em-template", "value"),
    State("em-dest-nome", "value"),
    State("em-dove", "value"),
    State("em-tel", "value"),
    State("em-smtp-user", "value"),
    State("app-store", "data"),
    prevent_initial_call=False,
)
def preview_email(n, template_key, dest_nome, dove, tel, smtp_user, store):
    store = store or {}
    canton = store.get("canton", "Ticino")
    nome_adv = store.get("nome", "Alex Bevilacqua") or "Alex Bevilacqua"
    mittente = nome_adv
    email_mittente = smtp_user or "alex@svag.ch"
    telefono = tel or "+41 91 000 0000"

    tpl = EMAIL_TEMPLATES.get(template_key or "fredda_presentazione", {})
    body = tpl.get("body", "")
    subject = tpl.get("subject", "")
    report_html = tpl.get("report_html", "")
    tags = tpl.get("tags", [])

    replacements = {
        "{nome}": dest_nome or "[Nome]",
        "{mittente}": mittente,
        "{cantone}": canton,
        "{dove_conosciuto}": dove or "[evento/luogo]",
        "{telefono}": telefono,
        "{email_mittente}": email_mittente,
        "{evento}": dove or "[Nome Evento]",
        "{data_disponibilita}": "[data]",
        "{numero_posti}": "5",
    }
    for k, v in replacements.items():
        body = body.replace(k, str(v))
        subject = subject.replace(k, str(v))

    tag_pills = [
        html.Span(tag, style={"background": "#fde8e8", "color": "#c0392b", "padding": "2px 10px",
                               "borderRadius": "12px", "fontSize": "0.7rem", "fontWeight": "700", "marginRight": "6px"})
        for tag in tags
    ]

    return html.Div([
        html.Div(
            [*tag_pills],
            style={"marginBottom": "10px", "display": "flex", "flexWrap": "wrap", "gap": "4px"},
        ),
        html.Div(
            [html.Span("Oggetto: ", style={"fontWeight": "700", "color": "#888", "fontSize": "0.82rem"}),
             html.Span(subject, style={"fontWeight": "600", "fontSize": "0.88rem"})],
            style={"background": "#f8f9fc", "padding": "10px 14px", "borderRadius": "8px",
                   "marginBottom": "12px", "border": "1px solid #eaecf2"},
        ),
        html.Pre(
            body,
            style={"whiteSpace": "pre-wrap", "fontSize": "0.85rem", "color": "#333",
                   "fontFamily": "inherit", "marginBottom": "16px"},
        ),
        html.Hr(),
        html.Div("📊 Mini-Report allegato:", style={"fontWeight": "700", "fontSize": "0.85rem", "color": "#555", "marginBottom": "8px"}),
        html.Div(
            [dcc.Markdown(
                report_html,
                dangerously_allow_html=True,
                style={"fontSize": "0.85rem"},
            )],
            style={"background": "#f8f9fc", "borderRadius": "10px", "padding": "14px",
                   "border": "1px solid #eaecf2"},
        ),
    ])


@callback(
    Output("em-status", "children"),
    Input("em-send-btn", "n_clicks"),
    State("em-template", "value"),
    State("em-dest-nome", "value"),
    State("em-dest-email", "value"),
    State("em-dove", "value"),
    State("em-tel", "value"),
    State("em-smtp-srv", "value"),
    State("em-smtp-port", "value"),
    State("em-smtp-user", "value"),
    State("em-smtp-pass", "value"),
    State("app-store", "data"),
    prevent_initial_call=True,
)
def send_email(n_clicks, template_key, dest_nome, dest_email, dove, tel, smtp_srv, smtp_port, smtp_user, smtp_pass, store):
    if not n_clicks:
        return ""
    if not dest_email:
        return html.Div("⚠️ Inserisci l'email del destinatario.", className="budget-warn")
    if not smtp_user or not smtp_pass:
        return html.Div("⚠️ Configura le credenziali SMTP per inviare.", className="budget-warn")

    store = store or {}
    canton = store.get("canton", "Ticino")
    nome_adv = store.get("nome", "Alex Bevilacqua") or "Alex Bevilacqua"
    mittente = nome_adv
    email_mittente = smtp_user
    telefono = tel or "+41 91 000 0000"

    tpl = EMAIL_TEMPLATES.get(template_key or "fredda_presentazione", {})
    body_txt = tpl.get("body", "")
    subject = tpl.get("subject", "")
    report_html = tpl.get("report_html", "")

    replacements = {
        "{nome}": dest_nome or "Cliente",
        "{mittente}": mittente,
        "{cantone}": canton,
        "{dove_conosciuto}": dove or "evento di networking",
        "{telefono}": telefono,
        "{email_mittente}": email_mittente,
        "{evento}": dove or "evento",
        "{data_disponibilita}": "questa settimana",
        "{numero_posti}": "5",
    }
    for k, v in replacements.items():
        body_txt = body_txt.replace(k, str(v))
        subject = subject.replace(k, str(v))

    body_html = f"""
<html><body style="font-family:Inter,Arial,sans-serif;color:#333;max-width:640px;margin:auto;padding:20px">
<div style="background:#1e2235;padding:20px 24px;border-radius:10px 10px 0 0">
  <h2 style="color:white;margin:0;font-size:1.15rem">🇨🇭 AlexFin — {nome_adv}</h2>
  <p style="color:#a0aec0;margin:4px 0 0;font-size:0.85rem">Consulente SVAG · Canton {canton}</p>
</div>
<div style="background:white;border:1px solid #eaecf2;border-top:none;border-radius:0 0 10px 10px;padding:28px 24px">
<pre style="white-space:pre-wrap;font-family:inherit;font-size:0.88rem;color:#333;margin:0 0 24px">{body_txt}</pre>
<hr style="border:none;border-top:1px solid #eaecf2;margin:20px 0">
<div style="background:#f8f9fc;border-radius:10px;padding:20px">
{report_html}
</div>
<hr style="border:none;border-top:1px solid #eaecf2;margin:20px 0">
<p style="font-size:0.75rem;color:#aaa;text-align:center">
Generato da AlexFin Advisor Tool · {mittente} · SVAG · {date.today().strftime('%d/%m/%Y')}<br>
I dati riportati sono indicativi e non costituiscono consulenza legale o fiscale.
</p>
</div>
</body></html>"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = dest_email
        msg.attach(MIMEText(body_txt, "plain", "utf-8"))
        msg.attach(MIMEText(body_html, "html", "utf-8"))

        port = int(smtp_port or 587)
        with smtplib.SMTP(smtp_srv or "smtp.gmail.com", port) as s:
            s.starttls()
            s.login(smtp_user, smtp_pass)
            s.sendmail(smtp_user, dest_email, msg.as_string())

        # Log it
        log = load_sent()
        log.append({
            "data": date.today().isoformat(),
            "destinatario": dest_nome or dest_email,
            "email": dest_email,
            "template": tpl.get("nome", template_key),
            "oggetto": subject,
            "canton": canton,
            "mittente": nome_adv,
        })
        save_sent(log)

        return html.Div(f"✅ Email inviata con successo a {dest_nome or dest_email} ({dest_email})", className="budget-ok")
    except Exception as e:
        return html.Div(f"❌ Errore invio: {str(e)}", className="budget-err")


# ─────────────────────────────────────────────
# TAB 4 — LOG INVII
# ─────────────────────────────────────────────

def render_log():
    log = load_sent()
    if not log:
        return html.Div(
            [
                html.Div("📭", style={"fontSize": "3rem", "textAlign": "center", "marginBottom": "12px"}),
                html.Div("Nessuna email inviata ancora.",
                         style={"textAlign": "center", "color": "#888", "fontSize": "0.95rem"}),
            ],
            style={"padding": "60px 20px"}
        )

    rows = []
    for entry in reversed(log[-50:]):
        rows.append(
            html.Tr([
                html.Td(entry.get("data", "—"), style={"fontSize": "0.82rem", "color": "#888", "whiteSpace": "nowrap"}),
                html.Td(entry.get("destinatario", "—"), style={"fontWeight": "600", "fontSize": "0.88rem"}),
                html.Td(entry.get("email", "—"), style={"fontSize": "0.82rem", "color": "#555"}),
                html.Td(
                    html.Span(entry.get("template", "—"),
                              style={"background": "#fde8e8", "color": "#c0392b", "padding": "2px 10px",
                                     "borderRadius": "12px", "fontSize": "0.7rem", "fontWeight": "700"}),
                ),
                html.Td(entry.get("canton", "—"), style={"fontSize": "0.82rem", "color": "#555"}),
            ])
        )

    return html.Div([
        html.Div(
            [
                html.Div(str(len(log)), style={"fontSize": "2.5rem", "fontWeight": "800", "color": "#c0392b"}),
                html.Div("Email inviate totali", style={"fontSize": "0.82rem", "color": "#888", "fontWeight": "600"}),
            ],
            style={"background": "white", "borderRadius": "14px", "padding": "20px", "textAlign": "center",
                   "boxShadow": "0 2px 14px rgba(0,0,0,0.06)", "border": "1px solid #eaecf2",
                   "display": "inline-block", "marginBottom": "20px", "minWidth": "160px"},
        ),
        html.Div(
            dbc.Table(
                [
                    html.Thead(html.Tr([
                        html.Th("Data", style={"fontSize": "0.78rem"}),
                        html.Th("Destinatario", style={"fontSize": "0.78rem"}),
                        html.Th("Email", style={"fontSize": "0.78rem"}),
                        html.Th("Template", style={"fontSize": "0.78rem"}),
                        html.Th("Cantone", style={"fontSize": "0.78rem"}),
                    ])),
                    html.Tbody(rows),
                ],
                striped=True, hover=True, responsive=True, size="sm",
            ),
            className="content-card", style={"padding": "0", "overflow": "hidden"},
        ),
    ])
