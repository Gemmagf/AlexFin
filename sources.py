# sources.py — Fonts oficials suïsses per a cada secció
# Totes les URL apunten a pàgines oficials de la Confederació Helvètica o organismes reconeguts

from dash import html

# ─────────────────────────────────────────────────────────────────────────────
# FONTS PER SECCIÓ
# ─────────────────────────────────────────────────────────────────────────────

SOURCES = {
    "assicurazioni": [
        {"label": "FINMA – Autorità federale di vigilanza sui mercati finanziari",
         "url": "https://www.finma.ch/it/"},
        {"label": "SVV – Associazione svizzera d'assicurazioni",
         "url": "https://www.svv.ch/it"},
        {"label": "Ombudsman delle assicurazioni private",
         "url": "https://www.ombudsman-assurance.ch/it/"},
    ],
    "krankenkasse": [
        {"label": "UFSP – Ufficio federale della sanità pubblica (LAMal/KVG)",
         "url": "https://www.bag.admin.ch/bag/it/home/versicherungen/krankenversicherung.html"},
        {"label": "Priminfo.admin.ch – Confronto ufficiale premi cassa malati",
         "url": "https://www.priminfo.admin.ch/it/praemien"},
        {"label": "Ombudsman Casse Malati",
         "url": "https://www.ombudsman-krankenkasse.ch/it/"},
    ],
    "previdenza": [
        {"label": "UFAS – 1° Pilastro (AVS/AI): Ufficio federale delle assicurazioni sociali",
         "url": "https://www.bsv.admin.ch/bsv/it/home/assicurazioni-sociali/alv.html"},
        {"label": "AHV/IV – Portale ufficiale AVS/AI",
         "url": "https://www.ahv-iv.ch/it/"},
        {"label": "UFAS – 2° Pilastro (LPP/BVG): Previdenza professionale",
         "url": "https://www.bsv.admin.ch/bsv/it/home/assicurazioni-sociali/bvg.html"},
        {"label": "UFAS – 3° Pilastro (3a): Previdenza individuale vincolata",
         "url": "https://www.bsv.admin.ch/bsv/it/home/assicurazioni-sociali/bvg/grundlagen-und-gesetze/saeule-3a.html"},
        {"label": "Compenswiss – Fondo AVS/AI/IPG",
         "url": "https://www.compenswiss.ch/it/"},
    ],
    "budget": [
        {"label": "ch.ch – Budget familiare in Svizzera",
         "url": "https://www.ch.ch/it/denaro/finanze-e-imposte/budget-familiare/"},
        {"label": "Budgetberatung Schweiz – Consulenza budget",
         "url": "https://www.budgetberatung.ch/it/"},
        {"label": "SECO – Segreteria di Stato dell'economia (occupazione e salari)",
         "url": "https://www.seco.admin.ch/seco/it/home.html"},
    ],
    "advisor": [
        {"label": "ch.ch – Portale ufficiale della Confederazione Svizzera",
         "url": "https://www.ch.ch/it/"},
        {"label": "FINMA – Vigilanza mercati finanziari",
         "url": "https://www.finma.ch/it/"},
        {"label": "AFC – Amministrazione federale delle contribuzioni (fiscalità)",
         "url": "https://www.estv.admin.ch/estv/it/home.html"},
    ],
    "prospecting": [
        {"label": "SCICC – Camere di commercio italo-svizzere",
         "url": "https://www.scicc.ch/"},
        {"label": "economiesuisse – Federazione delle imprese svizzere",
         "url": "https://www.economiesuisse.ch/it"},
        {"label": "SECO – Segreteria di Stato dell'economia",
         "url": "https://www.seco.admin.ch/seco/it/home.html"},
        {"label": "Swiss Global Enterprise – Promozione economica",
         "url": "https://www.s-ge.com/it"},
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# COMPONENT
# ─────────────────────────────────────────────────────────────────────────────

def sources_footer(section: str) -> html.Div:
    """
    Restituisce un componente Dash con i link alle fonti ufficiali svizzere.
    section: 'assicurazioni' | 'krankenkasse' | 'previdenza' | 'budget' | 'advisor' | 'prospecting'
    """
    links = SOURCES.get(section, [])
    if not links:
        return html.Div()

    return html.Div(
        [
            html.Hr(style={"borderColor": "#e8eaef", "marginTop": "36px", "marginBottom": "14px"}),
            html.Div(
                [
                    html.Span("📋 ", style={"fontSize": "0.78rem"}),
                    html.Span("Fonti ufficiali svizzere",
                              style={"fontSize": "0.72rem", "fontWeight": "700",
                                     "color": "#888", "textTransform": "uppercase",
                                     "letterSpacing": "0.06em"}),
                ],
                style={"marginBottom": "8px"},
            ),
            html.Div(
                [
                    html.A(
                        [html.Span("↗ ", style={"color": "#c0392b"}), s["label"]],
                        href=s["url"],
                        target="_blank",
                        rel="noopener noreferrer",
                        style={
                            "fontSize": "0.75rem", "color": "#555",
                            "textDecoration": "none", "display": "inline-block",
                            "marginRight": "18px", "marginBottom": "4px",
                            "transition": "color 0.15s",
                        },
                    )
                    for s in links
                ],
                style={"display": "flex", "flexWrap": "wrap", "gap": "2px"},
            ),
        ],
        style={
            "background": "#f8f9fc", "borderRadius": "10px", "padding": "14px 18px",
            "border": "1px solid #eaecf2", "marginTop": "28px",
        },
    )
