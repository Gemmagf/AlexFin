# pages/1_Advisor.py — AlexFin Advisor Dashboard

import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import altair as alt
import pandas as pd
import streamlit as st

from i18n import t
from products import calcola_raccomandazioni
from utils import CSS, render_sidebar

st.set_page_config(
    page_title="AlexFin – Advisor",
    layout="wide",
    page_icon="🧑‍💼",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)

profilo, lc = render_sidebar()

eta = profilo["eta"]
reddito_mensile = profilo["reddito_mensile"]
reddito_annuo = reddito_mensile * 12
situazione_norm = profilo["situazione"]
canton = profilo["canton"]
nome_display = profilo["nome"] if profilo["nome"] else "Cliente"
anni_pensionamento = max(65 - eta, 1)

# ── CRM helpers ──
CRM_FILE = os.path.join(os.path.dirname(__file__), "..", "clienti.json")

def carica_clienti():
    if os.path.exists(CRM_FILE):
        with open(CRM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salva_clienti(lista):
    with open(CRM_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

# ── Header ──
st.title(f"🧑‍💼 {t('adv_title', lc)}")
st.caption(f"{nome_display} · {eta} anni · {situazione_norm} · {canton} · CHF {reddito_mensile:,}/m")
st.divider()

tab_rac, tab_sim, tab_note, tab_crm = st.tabs([
    t("tab_rac", lc),
    t("tab_sim", lc),
    t("tab_note", lc),
    "📋 CRM",
])

# ══════════════════════════════════════════════
# TAB 1 — RACCOMANDAZIONI
# ══════════════════════════════════════════════

with tab_rac:
    st.header(t("rac_header", lc))

    avs_stimata = min(reddito_annuo * 0.18, 2520 * 12)
    lpp_stimata = max((reddito_annuo - 26460) * 0.18, 0) if situazione_norm != "Indipendente" else 0
    reddito_pensione = avs_stimata + lpp_stimata
    lacuna = max(reddito_annuo * 0.7 - reddito_pensione, 0)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(t("kpi_eta", lc), f"{eta} anni")
    c2.metric(t("kpi_reddito", lc), f"CHF {reddito_annuo:,}")
    c3.metric(t("kpi_anni_pens", lc), anni_pensionamento)
    c4.metric(t("kpi_pensione", lc), f"CHF {reddito_pensione:,.0f}/a")
    c5.metric(t("kpi_lacuna", lc), f"CHF {lacuna:,.0f}/a",
              delta=f"-{lacuna/reddito_annuo*100:.0f}%" if lacuna > 0 else "✓",
              delta_color="inverse" if lacuna > 0 else "normal")

    st.divider()
    col_rac, col_chart = st.columns([3, 2])

    with col_rac:
        raccomandazioni = calcola_raccomandazioni(profilo)
        filtro_opts = t("rac_filtro_opt", lc)
        filtro = st.radio(t("rac_filtro_label", lc), filtro_opts, horizontal=True)

        for r in raccomandazioni:
            prio = r["priorita"]
            if filtro == filtro_opts[1] and "Alta" not in prio:
                continue
            if filtro == filtro_opts[2] and "Opzionale" in prio:
                continue
            if "Alta" in prio:
                css_c, badge = "card card-alta", "badge-alta"
            elif "Raccomandata" in prio:
                css_c, badge = "card card-racc", "badge-racc"
            else:
                css_c, badge = "card card-opz", "badge-opz"
            st.markdown(f"""
            <div class="{css_c}">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                    <span style="font-size:1.1rem;font-weight:600">{r['icona']} {r['prodotto']}</span>
                    <span class="{badge}">{prio}</span>
                </div>
                <span style="color:#555;font-size:0.92rem">{r['motivo']}</span>
            </div>
            """, unsafe_allow_html=True)

    with col_chart:
        st.subheader(t("rac_subheader_lacuna", lc))
        df_lac = pd.DataFrame({
            "Fonte": ["1° AVS", "2° LPP", t("rac_lacuna_warning", lc)],
            "CHF": [int(avs_stimata), int(lpp_stimata), int(lacuna)],
            "Colore": ["#2980b9", "#27ae60", "#e74c3c"],
        })
        bar = alt.Chart(df_lac).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("Fonte:N", axis=alt.Axis(labelAngle=0), title=""),
            y=alt.Y("CHF:Q", title="CHF/anno", axis=alt.Axis(format=",.0f")),
            color=alt.Color("Colore:N", scale=None, legend=None),
            tooltip=["Fonte", alt.Tooltip("CHF:Q", format=",.0f")],
        ).properties(height=260)
        linea = alt.Chart(pd.DataFrame({"y": [int(reddito_annuo * 0.7)]})).mark_rule(
            color="#f39c12", strokeDash=[8, 4], strokeWidth=2
        ).encode(y="y:Q")
        st.altair_chart(bar + linea, use_container_width=True)
        if lacuna > 0:
            st.error(f"⚠️ {t('rac_lacuna_warning', lc)}: **CHF {lacuna:,.0f}/anno**")
        else:
            st.success(t("rac_lacuna_ok", lc))


# ══════════════════════════════════════════════
# TAB 2 — SIMULATORE PATRIMONIALE
# ══════════════════════════════════════════════

with tab_sim:
    st.header(t("sim_header", lc))
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        risparmi_att = st.number_input(t("sim_risparmi", lc), 0, 2_000_000, 25000, step=5000)
    with sc2:
        contrib_mens = st.number_input(t("sim_contrib", lc), 0, 20000, int(reddito_mensile * 0.15), step=100)
    with sc3:
        rend_sim = st.slider(t("sim_rendimento", lc), 0.0, 8.0, 4.0, step=0.5)
    with sc4:
        eta_pens = st.slider(t("sim_eta_pens", lc), 55, 70, 65)

    st.markdown(f"**⚡ {t('sim_whatif', lc)}**")
    wa, wb, wc = st.columns(3)
    shock = wa.checkbox(t("sim_shock", lc))
    part = wb.checkbox(t("sim_part", lc))
    spesa = wc.checkbox(t("sim_spesa", lc))

    anni_s = max(eta_pens - eta, 1)
    contrib_base = contrib_mens * 12

    def sim_pat(risparmi, contrib, rend, anni, shock_anno=None):
        p = [risparmi]
        for i in range(1, anni + 1):
            c = contrib
            if shock_anno and i == shock_anno:
                c -= 50000
            p.append(max(p[-1] * (1 + rend / 100) + c, 0))
        return p

    pat_base = sim_pat(risparmi_att, contrib_base, rend_sim, anni_s)
    rows_sim = [{"Età": eta + i, "CHF": p, "Scenario": "Base"} for i, p in enumerate(pat_base)]
    if shock:
        rows_sim += [{"Età": eta + i, "CHF": p, "Scenario": t("sim_shock", lc)} for i, p in enumerate(sim_pat(risparmi_att, contrib_base, rend_sim - 2, anni_s))]
    if part:
        rows_sim += [{"Età": eta + i, "CHF": p, "Scenario": t("sim_part", lc)} for i, p in enumerate(sim_pat(risparmi_att, contrib_base * 0.5, rend_sim, anni_s))]
    if spesa:
        rows_sim += [{"Età": eta + i, "CHF": p, "Scenario": t("sim_spesa", lc)} for i, p in enumerate(sim_pat(risparmi_att, contrib_base, rend_sim, anni_s, shock_anno=5))]

    df_sim = pd.DataFrame(rows_sim)
    line_sim = alt.Chart(df_sim).mark_line(strokeWidth=2.5).encode(
        x=alt.X("Età:Q"),
        y=alt.Y("CHF:Q", axis=alt.Axis(format=",.0f")),
        color="Scenario:N",
        strokeDash=alt.condition(alt.datum["Scenario"] == "Base", alt.value([0]), alt.value([6, 3])),
        tooltip=["Scenario", "Età", alt.Tooltip("CHF:Q", format=",.0f")],
    ).properties(height=320)
    linea_p = alt.Chart(pd.DataFrame({"x": [eta_pens]})).mark_rule(color="#555", strokeDash=[4, 3]).encode(x="x:Q")
    st.altair_chart(line_sim + linea_p, use_container_width=True)

    pat_fin = int(pat_base[-1])
    rendita = int(pat_fin * 0.04 / 12)
    sm1, sm2, sm3, sm4 = st.columns(4)
    sm1.metric(t("sim_patrimonio", lc), f"CHF {pat_fin:,}")
    sm2.metric(t("sim_versato", lc), f"CHF {int(contrib_base * anni_s):,}")
    sm3.metric(t("sim_rendita", lc), f"CHF {rendita:,}/m")
    sm4.metric(t("sim_copertura", lc), f"{rendita/reddito_mensile*100:.0f}%",
               delta="≥70%", delta_color="normal" if rendita / max(reddito_mensile, 1) >= 0.7 else "inverse")
    if pat_fin > 0:
        st.success(f"✅ {nome_display} → **CHF {pat_fin:,}** — {t('sim_rendita', lc)}: **CHF {rendita:,}/mese**")
    else:
        st.error("⚠️ Il patrimonio si esaurisce prima del pensionamento.")


# ══════════════════════════════════════════════
# TAB 3 — NOTE + EMAIL
# ══════════════════════════════════════════════

with tab_note:
    st.header(t("note_header", lc))
    cn1, cn2 = st.columns(2)

    with cn1:
        st.subheader(f"✏️ {t('note_appunti', lc)}")
        note_libere = st.text_area("Note", placeholder="...", height=160, label_visibility="collapsed")

        st.subheader(f"☑️ {t('note_temi', lc)}")
        temi_lista = [
            ("❤️", "Assicurazione Vita"), ("🦽", "Invalidità"), ("🤒", "Perdita di Guadagno"),
            ("🩹", "Infortuni"), ("🛡️", "RC Privata"), ("💊", "Krankenkasse"),
            ("🏥", "Complementare Ospedaliera"), ("🏦", "3° Pilastro"), ("🏢", "Revisione LPP"),
            ("🏡", "Budget familiare"), ("🎯", "Obiettivi di vita"), ("📈", "Simulatore"),
        ]
        temi = {nome: st.checkbox(f"{ico} {nome}") for ico, nome in temi_lista}

        st.subheader(f"📌 {t('note_passi', lc)}")
        prossimi = st.text_area("Passi", placeholder="...", height=100, label_visibility="collapsed")
        urgenza = st.select_slider(t("note_urgenza", lc), t("note_urgenza_opt", lc), value=t("note_urgenza_opt", lc)[1])

    with cn2:
        st.subheader(f"📄 {t('note_riepilogo', lc)}")
        rac_alta = [r for r in calcola_raccomandazioni(profilo) if "Alta" in r["priorita"]]
        temi_disc = [n for n, v in temi.items() if v]

        riepilogo_txt = f"""{'='*50}
RIEPILOGO COLLOQUIO — {nome_display}
Data: {pd.Timestamp.today().strftime('%d/%m/%Y')}
{'='*50}

PROFILO
Età: {eta} | {situazione_norm} | Canton {canton}
Reddito mensile: CHF {reddito_mensile:,}
Figli: {"Sì ("+str(profilo['n_figli'])+")" if profilo['figli'] else "No"} | Ipoteca: {"Sì" if profilo['ipoteca'] else "No"}
Rischio: {profilo['tolleranza_rischio']}

PRIORITÀ ALTA
{chr(10).join(["• "+r["prodotto"]+" — "+r["motivo"] for r in rac_alta]) if rac_alta else "• Nessuna urgenza immediata"}

TEMI DISCUSSI
{chr(10).join(["• "+t_n for t_n in temi_disc]) if temi_disc else "• —"}

PROSSIMI PASSI
{prossimi if prossimi else "—"}

NOTE
{note_libere if note_libere else "—"}

URGENZA: {urgenza}
{'='*50}
AlexFin · SVAG · {pd.Timestamp.today().strftime('%d/%m/%Y')}
"""
        st.code(riepilogo_txt, language=None)
        st.download_button(
            label=t("note_scarica", lc),
            data=riepilogo_txt,
            file_name=f"colloquio_{nome_display.replace(' ','_')}_{pd.Timestamp.today().strftime('%Y%m%d')}.txt",
            mime="text/plain",
        )

        st.divider()
        st.subheader(t("email_header", lc))
        with st.expander("⚙️ Configurazione SMTP", expanded=False):
            smtp_server = st.text_input("SMTP Server", value="smtp.gmail.com", key="smtp_srv")
            smtp_port = st.number_input("Porta", 1, 65535, 587, key="smtp_port")
            smtp_user = st.text_input("Email mittente", placeholder="tuoindirizzo@gmail.com", key="smtp_user")
            smtp_pass = st.text_input("Password / App Password", type="password", key="smtp_pass")

        email_cliente = st.text_input(t("email_indirizzo", lc), placeholder=t("email_ph", lc))
        email_oggetto = st.text_input(t("email_oggetto", lc), value=t("email_oggetto_default", lc))

        if st.button(t("email_btn", lc), type="primary", disabled=not email_cliente):
            if not smtp_user or not smtp_pass:
                st.warning("⚠️ Configura le credenziali SMTP.")
            else:
                try:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = email_oggetto
                    msg["From"] = smtp_user
                    msg["To"] = email_cliente
                    body_html = f"""
<html><body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:auto">
<div style="background:#c0392b;padding:20px;border-radius:8px 8px 0 0">
  <h2 style="color:white;margin:0">🇨🇭 AlexFin — Analisi Patrimoniale</h2>
  <p style="color:#fcc;margin:4px 0">Riepilogo colloquio per {nome_display}</p>
</div>
<div style="background:#f9f9f9;padding:24px;border:1px solid #eee;border-radius:0 0 8px 8px">
  <h3>👤 Profilo</h3>
  <ul>
    <li>Età: <b>{eta}</b> anni | {situazione_norm} | Canton {canton}</li>
    <li>Reddito mensile: <b>CHF {reddito_mensile:,}</b></li>
    <li>Figli: {"Sì ("+str(profilo['n_figli'])+")" if profilo['figli'] else "No"} | Ipoteca: {"Sì" if profilo['ipoteca'] else "No"}</li>
  </ul>
  <h3>🔴 Priorità Alta</h3>
  <ul>{"".join(["<li><b>"+r["prodotto"]+"</b> — "+r["motivo"]+"</li>" for r in rac_alta]) if rac_alta else "<li>Nessuna urgenza immediata</li>"}</ul>
  <h3>☑️ Temi discussi</h3>
  <ul>{"".join(["<li>"+t_n+"</li>" for t_n in temi_disc]) if temi_disc else "<li>—</li>"}</ul>
  <h3>📌 Prossimi passi</h3>
  <p>{prossimi.replace(chr(10),"<br>") if prossimi else "—"}</p>
  <hr>
  <p style="color:#888;font-size:12px">Generato da AlexFin Advisor Tool · SVAG · {pd.Timestamp.today().strftime('%d/%m/%Y')}</p>
</div></body></html>"""
                    msg.attach(MIMEText(body_html, "html"))
                    with smtplib.SMTP(smtp_server, smtp_port) as s:
                        s.starttls()
                        s.login(smtp_user, smtp_pass)
                        s.sendmail(smtp_user, email_cliente, msg.as_string())
                    st.success(f"{t('email_ok', lc)} {email_cliente}")
                except Exception as e:
                    st.error(f"{t('email_err', lc)} ({e})")


# ══════════════════════════════════════════════
# TAB 4 — CRM
# ══════════════════════════════════════════════

with tab_crm:
    st.header(f"📋 {t('adv_clienti_recenti', lc)}")
    col_crm1, col_crm2 = st.columns([2, 1])

    with col_crm2:
        st.subheader(t("adv_salva_cliente", lc))
        if profilo["nome"]:
            if st.button(f"💾 {t('adv_salva_cliente', lc)}", type="primary", use_container_width=True):
                clienti = carica_clienti()
                entry = {**profilo, "data": pd.Timestamp.today().strftime("%d/%m/%Y")}
                existing = next((i for i, c in enumerate(clienti) if c["nome"] == profilo["nome"]), None)
                if existing is not None:
                    clienti[existing] = entry
                else:
                    clienti.append(entry)
                salva_clienti(clienti)
                st.success(f"✅ {t('adv_salvato', lc)}: {profilo['nome']}")
        else:
            st.info("Inserisci il nome del cliente nella sidebar per salvarlo.")

        st.divider()
        st.subheader(t("adv_note_sessione", lc))
        st.text_area("Note CRM", placeholder="Appunti interni...", height=120, label_visibility="collapsed")

    with col_crm1:
        clienti = carica_clienti()
        if not clienti:
            st.info(t("adv_nessun_cliente", lc))
        else:
            st.markdown(f"**{len(clienti)}** {t('adv_n_clienti', lc)}")
            for c in reversed(clienti[-20:]):
                with st.expander(f"👤 {c['nome']} — {c.get('data','—')} · {c.get('canton','—')}"):
                    cc1, cc2, cc3 = st.columns(3)
                    cc1.metric("Età", c.get("eta", "—"))
                    cc2.metric("Reddito/m", f"CHF {c.get('reddito_mensile', 0):,}")
                    cc3.metric("Situazione", c.get("situazione", "—"))
                    if st.button(f"🗑️ {t('adv_elimina', lc)}", key=f"del_{c['nome']}"):
                        clienti = [x for x in clienti if x["nome"] != c["nome"]]
                        salva_clienti(clienti)
                        st.rerun()

st.divider()
st.caption(t("footer", lc))
