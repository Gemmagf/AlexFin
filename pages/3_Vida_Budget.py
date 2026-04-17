# pages/3_Vida_Budget.py — Vita & Budget Familiare

import altair as alt
import pandas as pd
import streamlit as st

from i18n import t
from utils import CSS, render_sidebar

st.set_page_config(
    page_title="AlexFin – Vita & Budget",
    layout="wide",
    page_icon="🏡",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)

profilo, lc = render_sidebar()

eta = profilo["eta"]
reddito_mensile = profilo["reddito_mensile"]
figli = profilo["figli"]
nome_display = profilo["nome"] if profilo["nome"] else "Cliente"

st.title(f"🏡 {t('vita_header', lc)}")
st.divider()

vt1, vt2, vt3 = st.tabs([t("vita_tab1", lc), t("vita_tab2", lc), t("vita_tab3", lc)])


# ══════════════════════════════════════════════
# TAB 1 — BUDGET MENSILE
# ══════════════════════════════════════════════

with vt1:
    st.subheader(t("vita_tab1", lc))

    cv1, cv2 = st.columns(2)
    with cv1:
        st.markdown(f"**💰 {t('vita_entrate', lc)}**")
        salario_netto = st.number_input(t("vita_salario1", lc), 0, 50000, reddito_mensile, step=100, key="v_sal1")
        salario2 = st.number_input(t("vita_salario2", lc), 0, 30000, 0, step=100, key="v_sal2")
        altri_entrate = st.number_input("Altri entrate (CHF)", 0, 10000, 0, step=50, key="v_altri")
        totale_entrate = salario_netto + salario2 + altri_entrate

    with cv2:
        st.markdown(f"**📤 {t('vita_uscite', lc)}**")
        affitto = st.number_input(t("vita_affitto", lc), 0, 10000, 1600, step=50, key="v_aff")
        cibo = st.number_input(t("vita_cibo", lc), 0, 5000, 700, step=50, key="v_cibo")
        trasporto = st.number_input(t("vita_trasporto", lc), 0, 3000, 300, step=50, key="v_tras")
        salute = st.number_input(t("vita_salute", lc), 0, 5000, 500, step=50, key="v_sal")
        intrattenimento = st.number_input(t("vita_intrattenimento", lc), 0, 3000, 300, step=50, key="v_int")
        asilo = st.number_input(t("vita_asilo", lc), 0, 5000, 800 if figli else 0, step=50, key="v_asilo")
        altro = st.number_input(t("vita_altro", lc), 0, 3000, 200, step=50, key="v_alt")
        totale_uscite = affitto + cibo + trasporto + salute + intrattenimento + asilo + altro

    risparmio_target = st.number_input(t("vita_risparmio_target", lc), 0, 10000, int(reddito_mensile * 0.15), step=100)
    saldo = totale_entrate - totale_uscite

    st.divider()
    sm1, sm2, sm3, sm4 = st.columns(4)
    sm1.metric(t("vita_entrate", lc), f"CHF {totale_entrate:,}")
    sm2.metric(t("vita_uscite", lc), f"CHF {totale_uscite:,}")
    sm3.metric(t("vita_saldo", lc), f"CHF {saldo:,}",
               delta=f"CHF {saldo:,}", delta_color="normal" if saldo > 0 else "inverse")
    sm4.metric(t("vita_risparmio_target", lc), f"CHF {risparmio_target:,}")

    pct_risparmio = risparmio_target / totale_entrate * 100 if totale_entrate > 0 else 0
    if saldo >= risparmio_target:
        css_b = "budget-ok"
        msg = f"✅ Saldo positivo: CHF {saldo:,}/mese. Risparmio {pct_risparmio:.1f}% — ottimo!"
    elif saldo > 0:
        css_b = "budget-warn"
        msg = f"⚠️ Saldo positivo (CHF {saldo:,}) ma sotto il target di risparmio. Rivedere le uscite."
    else:
        css_b = "budget-err"
        msg = f"❌ Saldo negativo: CHF {saldo:,}/mese. Necessaria una revisione urgente del budget."
    st.markdown(f'<div class="{css_b}">{msg}</div>', unsafe_allow_html=True)

    st.divider()
    col_pie, col_5030 = st.columns(2)

    with col_pie:
        df_uscite = pd.DataFrame({
            "Voce": [t("vita_affitto", lc), t("vita_cibo", lc), t("vita_trasporto", lc),
                     t("vita_salute", lc), t("vita_intrattenimento", lc), t("vita_asilo", lc), t("vita_altro", lc)],
            "CHF": [affitto, cibo, trasporto, salute, intrattenimento, asilo, altro],
        }).query("CHF > 0")
        if not df_uscite.empty:
            pie = alt.Chart(df_uscite).mark_arc(innerRadius=60).encode(
                theta=alt.Theta("CHF:Q"),
                color=alt.Color("Voce:N", scale=alt.Scale(scheme="tableau10")),
                tooltip=["Voce", alt.Tooltip("CHF:Q", format=",.0f")],
            ).properties(height=260, title=t("vita_uscite", lc))
            st.altair_chart(pie, use_container_width=True)

    with col_5030:
        st.subheader(f"📐 {t('vita_regola', lc)}")
        necesario = affitto + cibo + trasporto + salute + asilo
        discrezionale = intrattenimento + altro
        df_5030 = pd.DataFrame({
            "Categoria": ["Necessità (50%)", "Discrezionale (30%)", "Risparmio (20%)"],
            "Attuale (CHF)": [necesario, discrezionale, risparmio_target],
            "Target (CHF)": [int(totale_entrate * 0.5), int(totale_entrate * 0.3), int(totale_entrate * 0.2)],
        })
        st.dataframe(df_5030, hide_index=True, use_container_width=True)

        bar_5030 = alt.Chart(
            df_5030.melt("Categoria", ["Attuale (CHF)", "Target (CHF)"], var_name="Tipo", value_name="CHF")
        ).mark_bar().encode(
            x=alt.X("Categoria:N", axis=alt.Axis(labelAngle=-15), title=""),
            y=alt.Y("CHF:Q", axis=alt.Axis(format=",.0f")),
            color=alt.Color("Tipo:N", scale=alt.Scale(range=["#c0392b", "#bdc3c7"])),
            xOffset="Tipo:N",
            tooltip=["Categoria", "Tipo", alt.Tooltip("CHF:Q", format=",.0f")],
        ).properties(height=200)
        st.altair_chart(bar_5030, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 2 — PIANIFICAZIONE FAMILIARE
# ══════════════════════════════════════════════

with vt2:
    st.subheader(t("vita_tab2", lc))

    fase_opts = t("vita_fase_opts", lc)
    default_fase = fase_opts[2] if figli else fase_opts[0]
    fase = st.select_slider(t("vita_fase_label", lc), options=fase_opts, value=default_fase)

    costi_fase = {
        fase_opts[0]: {"Abitazione": 1400, "Trasporto": 300, "Alimentazione": 600, "Svago": 500, "KK": 470, "3a": 600, "Risparmio": 500},
        fase_opts[1]: {"Abitazione": 1900, "Trasporto": 500, "Alimentazione": 1000, "Svago": 700, "KK": 940, "3a": 1200, "Risparmio": 800},
        fase_opts[2]: {"Abitazione": 2400, "Trasporto": 600, "Alimentazione": 1300, "Asilo/Scuola": 1200, "KK": 1500, "3a": 600, "Risparmio": 400},
        fase_opts[3]: {"Abitazione": 2500, "Trasporto": 700, "Alimentazione": 1500, "Scuola/Sport": 800, "KK": 1600, "3a": 600, "Risparmio": 600},
        fase_opts[4]: {"Abitazione": 2200, "Trasporto": 500, "Alimentazione": 1200, "Università": 2000, "KK": 1400, "3a": 600, "Risparmio": 300},
        fase_opts[5]: {"Abitazione": 2000, "Trasporto": 500, "Alimentazione": 1100, "Svago": 800, "KK": 1800, "3a": 604, "Risparmio": 1200},
        fase_opts[6]: {"Abitazione": 1800, "Trasporto": 400, "Alimentazione": 1000, "Svago": 700, "KK": 2000, "3a": 604, "Risparmio": 1500},
    }

    dati_fase = costi_fase.get(fase, costi_fase[fase_opts[0]])
    df_fase = pd.DataFrame([{"Voce": k, "CHF/mese stimato": v} for k, v in dati_fase.items()])
    totale_fase = sum(dati_fase.values())

    cf1, cf2 = st.columns([1, 1])
    with cf1:
        st.dataframe(df_fase, hide_index=True, use_container_width=True)
        st.metric("Totale stimato mensile", f"CHF {totale_fase:,}")
        delta_v = totale_entrate - totale_fase
        if totale_entrate > 0:
            if delta_v >= 0:
                st.success(f"✅ Reddito sufficiente per questa fase. Margine: CHF {delta_v:,}/mese")
            else:
                st.error(f"❌ Reddito insufficiente per questa fase. Deficit: CHF {abs(delta_v):,}/mese")
    with cf2:
        bar_fase = alt.Chart(df_fase).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, color="#c0392b").encode(
            x=alt.X("CHF/mese stimato:Q"),
            y=alt.Y("Voce:N", sort="-x", title=""),
            tooltip=["Voce", "CHF/mese stimato"],
        ).properties(height=300, title=fase)
        st.altair_chart(bar_fase, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 3 — OBIETTIVI DI VITA
# ══════════════════════════════════════════════

with vt3:
    st.subheader(t("vita_obiettivi_titolo", lc))

    n_obiettivi = st.number_input("Numero di obiettivi", 1, 6, 2)
    default_nomi = ["Casa", "Auto", "Pensione anticipata", "Università figli", "Viaggio", "Emergenza"]
    default_importi = [100000, 30000, 500000, 80000, 15000, 50000]
    default_anni = [10, 3, 20, 15, 2, 5]

    obiettivi = []
    for i in range(int(n_obiettivi)):
        st.markdown(f"**Obiettivo {i+1}**")
        oc1, oc2, oc3 = st.columns(3)
        with oc1:
            nome_obj = st.text_input(t("vita_obj_nome", lc), key=f"on_{i}",
                                     placeholder=default_nomi[i % len(default_nomi)])
        with oc2:
            importo_obj = st.number_input(t("vita_obj_importo", lc), 0, 2_000_000,
                                          default_importi[i % len(default_importi)], step=1000, key=f"oi_{i}")
        with oc3:
            anni_obj = st.number_input(t("vita_obj_anni", lc), 1, 40,
                                       default_anni[i % len(default_anni)], key=f"oa_{i}")
        risp_mens_obj = int(importo_obj / (anni_obj * 12)) if anni_obj > 0 else importo_obj
        obiettivi.append({
            "Nome": nome_obj or f"Obiettivo {i+1}",
            "Importo (CHF)": importo_obj,
            "Anni": anni_obj,
            "CHF/mese necessario": risp_mens_obj,
        })

    st.divider()
    df_obj = pd.DataFrame(obiettivi)
    st.dataframe(df_obj, hide_index=True, use_container_width=True)

    totale_risp_obj = sum(o["CHF/mese necessario"] for o in obiettivi)
    st.metric("Risparmio mensile totale necessario", f"CHF {totale_risp_obj:,}")

    # Use saldo from vt1 if available (re-calculated here since tabs don't share local vars)
    saldo_ref = totale_entrate - totale_uscite
    capacita = saldo_ref - totale_risp_obj
    if capacita >= 0:
        st.success(f"✅ Con il saldo attuale (CHF {saldo_ref:,}/mese) gli obiettivi sono raggiungibili. Margine: CHF {capacita:,}/mese.")
    else:
        st.error(f"❌ Servono CHF {totale_risp_obj:,}/mese ma il saldo è CHF {saldo_ref:,}. Scarto: CHF {abs(capacita):,}/mese.")

    st.divider()
    # Timeline Gantt
    df_gantt = pd.DataFrame([{
        "Obiettivo": o["Nome"],
        "Inizio": 0,
        "Fine": o["Anni"],
        "Importo": o["Importo (CHF)"],
        "CHF/mese": o["CHF/mese necessario"],
    } for o in obiettivi])
    bar_obj = alt.Chart(df_gantt).mark_bar(height=22, cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X("Inizio:Q", title="Anni da oggi"),
        x2="Fine:Q",
        y=alt.Y("Obiettivo:N", title=""),
        color=alt.Color("Importo:Q", scale=alt.Scale(scheme="reds")),
        tooltip=["Obiettivo", "Fine",
                 alt.Tooltip("Importo:Q", format=",.0f", title="Importo CHF"),
                 alt.Tooltip("CHF/mese:Q", format=",.0f", title="CHF/mese")],
    ).properties(height=max(180, int(n_obiettivi) * 50), title="Timeline obiettivi finanziari")
    st.altair_chart(bar_obj, use_container_width=True)

    # Accumulo progressivo per obiettivo
    st.subheader("📈 Proiezione accumulo per obiettivo")
    rows_acc = []
    for o in obiettivi:
        acc = 0
        for mese in range(int(o["Anni"]) * 12 + 1):
            acc += o["CHF/mese necessario"]
            if mese % 12 == 0:
                rows_acc.append({"Obiettivo": o["Nome"], "Anno": mese // 12, "CHF accumulati": acc,
                                  "Target": o["Importo (CHF)"]})
    if rows_acc:
        df_acc = pd.DataFrame(rows_acc)
        line_acc = alt.Chart(df_acc).mark_line(strokeWidth=2).encode(
            x=alt.X("Anno:Q", title="Anni"),
            y=alt.Y("CHF accumulati:Q", axis=alt.Axis(format=",.0f")),
            color="Obiettivo:N",
            tooltip=["Obiettivo", "Anno", alt.Tooltip("CHF accumulati:Q", format=",.0f")],
        ).properties(height=260)
        st.altair_chart(line_acc, use_container_width=True)

st.divider()
st.caption(t("footer", lc))
