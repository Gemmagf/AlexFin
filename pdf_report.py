# pdf_report.py — AlexFin PDF meeting report generator
# Uses fpdf2 (pure Python, no system dependencies)

from fpdf import FPDF
from datetime import date

from products import calcola_raccomandazioni

# ── Text sanitiser (Helvetica uses latin-1 internally) ────────────────────────
_UNICODE_MAP = str.maketrans({
    "\u2013": "-",    # en dash
    "\u2014": "-",    # em dash
    "\u2018": "'",    # left single quotation mark
    "\u2019": "'",    # right single quotation mark
    "\u201c": '"',    # left double quotation mark
    "\u201d": '"',    # right double quotation mark
    "\u2026": "...",  # horizontal ellipsis
    "\u2022": "-",    # bullet
    "\u2019": "'",    # right single quote
    # emojis → strip (replaced in caller with text equivalents)
})


def _s(text) -> str:
    """Sanitise text to latin-1 safe characters, dropping anything outside the range."""
    if not text:
        return ""
    text = str(text).translate(_UNICODE_MAP)
    return text.encode("latin-1", errors="replace").decode("latin-1")


# ── Colour palette ────────────────────────────────────────────────────────────
RED    = (192,  57,  43)
DARK   = ( 30,  34,  53)
GRAY   = (130, 130, 130)
LGRAY  = (220, 220, 220)
LIGHT  = (248, 249, 252)
BLUE   = ( 41, 128, 185)
GREEN  = ( 39, 174,  96)
ORANGE = (243, 156,  18)
WHITE  = (255, 255, 255)


# ── PDF class ─────────────────────────────────────────────────────────────────

class AlexFinPDF(FPDF):
    def header(self):
        pass  # drawn manually

    def footer(self):
        self.set_y(-13)
        self.set_font("Helvetica", "I", 7.5)
        self.set_text_color(*GRAY)
        oggi = date.today().strftime("%d/%m/%Y")
        self.cell(
            0, 8,
            _s(f"AlexFin Advisor Tool  |  SVAG  |  Generato il {oggi}  |  Pagina {self.page_no()}"),
            align="C",
        )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _kpi_box(pdf, x, y, w, h, label, value, color=None):
    color = color or DARK
    pdf.set_fill_color(*LIGHT)
    pdf.set_draw_color(*LGRAY)
    pdf.rect(x, y, w, h, "FD")
    pdf.set_font("Helvetica", "", 6.5)
    pdf.set_text_color(*GRAY)
    pdf.set_xy(x, y + 2.5)
    pdf.cell(w, 4, _s(label), align="C")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*color)
    pdf.set_xy(x, y + 7)
    pdf.cell(w, 6, _s(value), align="C")


def _section_title(pdf, title):
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*DARK)
    pdf.set_x(14)
    pdf.cell(0, 6, _s(title), ln=True)
    pdf.set_draw_color(*LGRAY)
    pdf.set_line_width(0.3)
    pdf.line(14, pdf.get_y(), 196, pdf.get_y())
    pdf.ln(3)


# ── Main generator ────────────────────────────────────────────────────────────

def genera_pdf(
    store,
    note_libere: str = "",
    prossimi_passi: str = "",
    temi_discussi: list = None,
    urgenza_label: str = "Media",
) -> bytes:
    """Generate the meeting-report PDF and return raw bytes."""

    store = store or {}
    nome         = store.get("nome") or "Cliente"
    eta          = int(store.get("eta", 38))
    situazione   = store.get("situazione", "Dipendente")
    canton       = store.get("canton", "Zurigo")
    reddito_mens = int(store.get("reddito_mensile", 5500))
    stato_civile = store.get("stato_civile", "-")
    figli        = store.get("figli", False)
    n_figli      = int(store.get("n_figli", 0))
    ipoteca      = store.get("ipoteca", False)
    rischio      = store.get("tolleranza_rischio", "Media")
    temi_discussi = temi_discussi or []

    reddito_annuo = reddito_mens * 12
    avs     = min(reddito_annuo * 0.18, 2520 * 12)
    lpp     = max((reddito_annuo - 26460) * 0.18, 0) if situazione != "Indipendente" else 0
    pensione = avs + lpp
    lacuna  = max(reddito_annuo * 0.7 - pensione, 0)
    anni_pens = max(65 - eta, 1)
    oggi = date.today().strftime("%d/%m/%Y")

    raccomandazioni = calcola_raccomandazioni(store)

    pdf = AlexFinPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=18)

    # ── HEADER BAND ──────────────────────────────────────────────────────────
    pdf.set_fill_color(*RED)
    pdf.rect(0, 0, 210, 34, "F")

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(14, 5)
    pdf.cell(80, 12, "AlexFin")

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(255, 200, 200)
    pdf.set_xy(14, 18)
    pdf.cell(80, 6, "Rapporto colloquio  |  Analisi patrimoniale svizzera")

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(100, 6)
    pdf.cell(96, 8, _s(nome), align="R")

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(255, 200, 200)
    pdf.set_xy(100, 15)
    pdf.cell(96, 6, _s(f"{oggi}  |  Canton {canton}"), align="R")

    pdf.set_y(40)

    # ── PROFILO ───────────────────────────────────────────────────────────────
    _section_title(pdf, "PROFILO CLIENTE")

    COL = 58
    figli_txt = f"Si ({n_figli})" if figli else "No"
    rows = [
        [("Eta", f"{eta} anni"),         ("Situazione", situazione),    ("Canton", canton)],
        [("Reddito mensile", f"CHF {reddito_mens:,}"), ("Stato civile", stato_civile), ("Figli", figli_txt)],
        [("Ipoteca", "Si" if ipoteca else "No"), ("Rischio", rischio),  ("Anni pensione", str(anni_pens))],
    ]
    for row in rows:
        for i, (lbl, val) in enumerate(row):
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(*GRAY)
            pdf.set_xy(14 + i * COL, pdf.get_y())
            pdf.cell(COL, 4.5, _s(lbl))
        pdf.ln(4.5)
        for i, (lbl, val) in enumerate(row):
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*DARK)
            pdf.set_xy(14 + i * COL, pdf.get_y())
            pdf.cell(COL, 5.5, _s(val))
        pdf.ln(7)

    # ── KPI ROW ───────────────────────────────────────────────────────────────
    pdf.ln(2)
    KW, KH, KG = 36, 18, 2
    kpis = [
        ("Reddito annuo",    f"CHF {reddito_annuo:,}",   DARK),
        ("Pensione stimata", f"CHF {pensione:,.0f}/a",    DARK),
        ("1. Pilastro AVS",  f"CHF {avs:,.0f}/a",         BLUE),
        ("2. Pilastro LPP",  f"CHF {lpp:,.0f}/a",         GREEN),
        ("Lacuna previd.",   f"CHF {lacuna:,.0f}/a",      RED if lacuna > 0 else GREEN),
    ]
    ky = pdf.get_y()
    for i, (lbl, val, col) in enumerate(kpis):
        _kpi_box(pdf, 14 + i * (KW + KG), ky, KW, KH, lbl, val, col)
    pdf.set_y(ky + KH + 8)

    # ── BAR CHART ─────────────────────────────────────────────────────────────
    _section_title(pdf, "SITUAZIONE PREVIDENZIALE STIMATA (CHF/anno)")

    total     = max(avs + lpp + lacuna, 1)
    LBL_W     = 55
    BAR_X     = 14 + LBL_W + 2
    BAR_MAX_W = 105
    BAR_H     = 11
    BAR_GAP   = 4

    for lbl, val, col in [
        ("1. Pilastro AVS",   avs,    BLUE),
        ("2. Pilastro LPP",   lpp,    GREEN),
        ("Lacuna previdenz.", lacuna, RED),
    ]:
        bw = (val / total) * BAR_MAX_W
        by = pdf.get_y()
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*GRAY)
        pdf.set_xy(14, by + 1.5)
        pdf.cell(LBL_W, BAR_H - 3, _s(lbl), align="R")
        if bw > 0:
            pdf.set_fill_color(*col)
            pdf.rect(BAR_X, by + 1.5, max(bw, 1.5), BAR_H - 3, "F")
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*col)
        pdf.set_xy(BAR_X + max(bw, 1.5) + 3, by + 1.5)
        pdf.cell(40, BAR_H - 3, f"CHF {val:,.0f}", align="L")
        pdf.ln(BAR_H + BAR_GAP)

    # 70% target note
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(*ORANGE)
    pdf.set_x(14)
    pdf.cell(0, 5, f">> Obiettivo previdenziale (70%): CHF {reddito_annuo * 0.7:,.0f}/anno", ln=True)

    if lacuna > 0:
        pct = pensione / max(reddito_annuo * 0.7, 1) * 100
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*RED)
        pdf.set_x(14)
        pdf.cell(0, 5, f"[!] Lacuna: CHF {lacuna:,.0f}/anno  --  copertura attuale: {pct:.0f}%", ln=True)
    else:
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*GREEN)
        pdf.set_x(14)
        pdf.cell(0, 5, "[OK] Obiettivo previdenziale raggiunto", ln=True)

    pdf.ln(5)

    # ── RACCOMANDAZIONI ───────────────────────────────────────────────────────
    _section_title(pdf, "RACCOMANDAZIONI PERSONALIZZATE")

    priority_map = {
        "Alta":         (RED,    "[PRIORITA ALTA]"),
        "Raccomandata": (ORANGE, "[RACCOMANDATA]"),
        "Opzionale":    (GRAY,   "[OPZIONALE]"),
    }

    for r in raccomandazioni:
        prio = r.get("priorita", "")
        key  = ("Alta" if "Alta" in prio
                else "Raccomandata" if "Raccomandata" in prio
                else "Opzionale")
        col, badge = priority_map[key]

        pdf.set_x(14)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*DARK)
        pdf.cell(5, 6, ">")
        product_text = _s(r.get("prodotto", ""))
        pdf.cell(110, 6, product_text)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*col)
        pdf.cell(0, 6, badge, ln=True)
        # reason (strip emojis from motivo)
        pdf.set_x(19)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*GRAY)
        pdf.multi_cell(177, 4.5, _s(r.get("motivo", "")))
        pdf.ln(1.5)

    # ── NOTE DEL COLLOQUIO ────────────────────────────────────────────────────
    if temi_discussi or prossimi_passi or note_libere:
        pdf.ln(3)
        _section_title(pdf, "NOTE DEL COLLOQUIO")

        if temi_discussi:
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.set_text_color(*DARK)
            pdf.set_x(14)
            pdf.cell(0, 5, "Temi discussi:", ln=True)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*GRAY)
            for tema in temi_discussi:
                pdf.set_x(19)
                pdf.cell(0, 4.5, _s(f"- {tema}"), ln=True)
            pdf.ln(2)

        if prossimi_passi:
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.set_text_color(*DARK)
            pdf.set_x(14)
            pdf.cell(0, 5, "Prossimi passi:", ln=True)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*GRAY)
            pdf.set_x(19)
            pdf.multi_cell(177, 4.5, _s(prossimi_passi))
            pdf.ln(2)

        if note_libere:
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.set_text_color(*DARK)
            pdf.set_x(14)
            pdf.cell(0, 5, "Note libere:", ln=True)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*GRAY)
            pdf.set_x(19)
            pdf.multi_cell(177, 4.5, _s(note_libere))
            pdf.ln(2)

        # urgency
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*DARK)
        pdf.set_x(14)
        pdf.cell(35, 5, "Urgenza riunione:")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*GRAY)
        pdf.cell(0, 5, _s(urgenza_label), ln=True)

    # ── DISCLAIMER ────────────────────────────────────────────────────────────
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 6.5)
    pdf.set_text_color(*GRAY)
    pdf.set_x(14)
    pdf.multi_cell(
        182, 4,
        "Il presente rapporto e' generato automaticamente da AlexFin Advisor Tool a scopo informativo. "
        "Non costituisce consulenza finanziaria, legale o fiscale. Le stime previdenziali sono indicative "
        "e basate sui dati inseriti. SVAG non si assume responsabilita' per decisioni prese sulla base "
        "di questo documento.",
    )

    return bytes(pdf.output())
