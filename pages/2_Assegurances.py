# pages/2_Assegurances.py — Assicurazioni, KK & Previdenza

import altair as alt
import pandas as pd
import streamlit as st

from i18n import t
from products import (
    ASSICURAZIONI, KK_COMPLEMENTARI, KK_FRANCHIGIE, KK_MODELLI,
    KK_PREMI_CANTON, PILASTRI,
)
from utils import CSS, render_sidebar

st.set_page_config(
    page_title="AlexFin – Prodotti",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)

profilo, lc = render_sidebar()

eta = profilo["eta"]
situazione_norm = profilo["situazione"]
canton = profilo["canton"]
reddito_mensile = profilo["reddito_mensile"]
reddito_annuo = reddito_mensile * 12
nome_display = profilo["nome"] if profilo["nome"] else "Cliente"
anni_pensionamento = max(65 - eta, 1)

st.title(f"🛡️ {t('ass_header', lc)} & {t('kk_header', lc)}")
st.divider()

tab_ass, tab_kk, tab_prev = st.tabs([
    t("tab_ass", lc),
    t("tab_kk", lc),
    t("tab_prev", lc),
])


# ══════════════════════════════════════════════
# TAB 1 — ASSICURAZIONI
# ══════════════════════════════════════════════

with tab_ass:
    st.header(t("ass_header", lc))
    col_sel, col_det = st.columns([1, 2])

    with col_sel:
        nomi = [f"{p['icona']} {p['nome']}" for p in ASSICURAZIONI]
        prodotto_sel = st.radio(t("ass_sel", lc), nomi, label_visibility="collapsed")
        prodotto = next(p for p in ASSICURAZIONI if f"{p['icona']} {p['nome']}" == prodotto_sel)
        st.divider()
        st.markdown(f"**{t('ass_categoria', lc)}:** `{prodotto['categoria']}`")
        st.markdown(f"**{t('ass_costo', lc)}:** `{prodotto['costo_indicativo']}`")
        st.caption(prodotto["costo_note"])
        if prodotto.get("premi_per_eta"):
            eta_vicina = min(prodotto["premi_per_eta"].keys(), key=lambda x: abs(x - eta))
            premio_eta = prodotto["premi_per_eta"][eta_vicina]
            st.markdown(f"**{t('ass_stima_eta', lc, eta=eta)}:** `CHF {premio_eta}/mese`")

    with col_det:
        st.subheader(f"{prodotto['icona']} {prodotto['nome']}")
        st.write(prodotto["descrizione"])
        ca, cb = st.columns(2)
        with ca:
            st.markdown(f"**✅ {t('ass_copre', lc)}**")
            for cov in prodotto["coperture"]:
                st.markdown(f"<span class='cover-ok'>✔ {cov}</span>", unsafe_allow_html=True)
        with cb:
            st.markdown(f"**❌ {t('ass_non_copre', lc)}**")
            for exc in prodotto["esclusioni"]:
                st.markdown(f"<span class='cover-no'>✘ {exc}</span>", unsafe_allow_html=True)
        st.divider()
        sc = prodotto["scenario"]
        st.markdown(f"**📖 {t('ass_caso', lc)}:** _{sc['caso']}_")
        cx, cy = st.columns(2)
        with cx:
            st.error(f"**{t('ass_senza', lc)}:** {sc['senza']}")
        with cy:
            st.success(f"**{t('ass_con', lc)}:** {sc['con']}")

    st.divider()
    st.subheader(t("ass_grafico_premi", lc))
    righe = []
    for p in ASSICURAZIONI:
        if p.get("premi_per_eta"):
            for e_k, pr in p["premi_per_eta"].items():
                righe.append({"Età": e_k, "CHF/mese": pr, "Prodotto": p["nome"]})
    df_premi = pd.DataFrame(righe)
    linea_eta = alt.Chart(pd.DataFrame({"x": [eta]})).mark_rule(
        color="#c0392b", strokeDash=[6, 3], strokeWidth=2
    ).encode(x="x:Q")
    lines = alt.Chart(df_premi).mark_line(point=True, strokeWidth=2.5).encode(
        x=alt.X("Età:Q"),
        y=alt.Y("CHF/mese:Q"),
        color=alt.Color("Prodotto:N", legend=alt.Legend(orient="bottom", columns=3)),
        opacity=alt.condition(alt.datum["Prodotto"] == prodotto["nome"], alt.value(1.0), alt.value(0.25)),
        strokeWidth=alt.condition(alt.datum["Prodotto"] == prodotto["nome"], alt.value(3.5), alt.value(1.5)),
        tooltip=["Prodotto", "Età", "CHF/mese"],
    ).properties(height=280)
    st.altair_chart(lines + linea_eta, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 2 — KRANKENKASSE
# ══════════════════════════════════════════════

with tab_kk:
    st.header(t("kk_header", lc))
    kk1, kk2, kk3 = st.tabs([t("kk_tab1", lc), t("kk_tab2", lc), t("kk_tab3", lc)])
    premio_base = KK_PREMI_CANTON[canton]["adulto"]

    with kk1:
        col_info, col_chart = st.columns(2)
        with col_info:
            st.subheader(f"🗺️ {canton} — {t('kk_premi_canton', lc)}")
            dati = KK_PREMI_CANTON[canton]
            ca, cb, cc = st.columns(3)
            ca.metric(t("kk_adulto", lc), f"CHF {dati['adulto']}/m")
            cb.metric(t("kk_giovane", lc), f"CHF {dati['giovane']}/m")
            cc.metric(t("kk_bambino", lc), f"CHF {dati['bambino']}/m")
            st.divider()
            st.subheader(t("kk_franchigie", lc))
            df_fran = pd.DataFrame([{
                "Franchigia": f"CHF {f['importo']}",
                "Premio/mese": f"CHF {int(premio_base*(1-f['risparmio_pct']/100))}",
                "Risparmio/anno": f"CHF {int(premio_base*f['risparmio_pct']/100*12)}",
                "Note": f["nota"],
            } for f in KK_FRANCHIGIE])
            st.dataframe(df_fran, hide_index=True, use_container_width=True)

        with col_chart:
            st.subheader(t("kk_confronto_canton", lc))
            df_cant = pd.DataFrame([
                {"Cantone": c, "Premio (CHF/m)": v["adulto"]}
                for c, v in KK_PREMI_CANTON.items()
            ]).sort_values("Premio (CHF/m)")
            bar_c = alt.Chart(df_cant).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                x=alt.X("Premio (CHF/m):Q"),
                y=alt.Y("Cantone:N", sort="-x", title=""),
                color=alt.condition(alt.datum["Cantone"] == canton, alt.value("#c0392b"), alt.value("#bdc3c7")),
                tooltip=["Cantone", "Premio (CHF/m)"],
            ).properties(height=260)
            st.altair_chart(bar_c, use_container_width=True)

        st.divider()
        st.subheader(t("kk_modelli", lc))
        df_mod = pd.DataFrame([{
            "Modello": m["nome"],
            "Risparmio %": m["risparmio_pct"],
            "CHF/anno": int(premio_base * m["risparmio_pct"] / 100 * 12),
            "Premio/mese": int(premio_base * (1 - m["risparmio_pct"] / 100)),
            "Libertà": m["rating_liberta"],
            "Risparmio": m["rating_risparmio"],
        } for m in KK_MODELLI])
        cm1, cm2 = st.columns(2)
        with cm1:
            bar_m = alt.Chart(df_mod).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                x=alt.X("Modello:N", axis=alt.Axis(labelAngle=0), title=""),
                y=alt.Y("CHF/anno:Q"),
                color=alt.Color("Modello:N", scale=alt.Scale(
                    domain=["Standard", "Medico di famiglia", "Telmed", "HMO"],
                    range=["#bdc3c7", "#3498db", "#9b59b6", "#27ae60"]), legend=None),
                tooltip=["Modello", "CHF/anno", "Premio/mese"],
            ).properties(height=220)
            st.altair_chart(bar_m, use_container_width=True)
        with cm2:
            sc2 = alt.Chart(df_mod).mark_circle(size=200).encode(
                x=alt.X("Libertà:Q", scale=alt.Scale(domain=[0, 6])),
                y=alt.Y("Risparmio:Q", scale=alt.Scale(domain=[0, 6])),
                color=alt.Color("Modello:N", scale=alt.Scale(
                    domain=["Standard", "Medico di famiglia", "Telmed", "HMO"],
                    range=["#bdc3c7", "#3498db", "#9b59b6", "#27ae60"])),
                tooltip=["Modello", "Libertà", "Risparmio", "CHF/anno"],
            )
            lbl = alt.Chart(df_mod).mark_text(dy=-16, fontSize=11, fontWeight=600).encode(
                x="Libertà:Q", y="Risparmio:Q", text="Modello:N",
                color=alt.Color("Modello:N", scale=alt.Scale(
                    domain=["Standard", "Medico di famiglia", "Telmed", "HMO"],
                    range=["#bdc3c7", "#3498db", "#9b59b6", "#27ae60"]), legend=None),
            )
            st.altair_chart((sc2 + lbl).properties(height=220), use_container_width=True)

    with kk2:
        st.subheader(t("kk_tab2", lc))
        for comp in KK_COMPLEMENTARI:
            with st.expander(f"{comp['nome']} — {comp['costo_indicativo']}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write(comp["copertura"])
                    st.caption(f"ℹ️ {comp['nota']}")
                with c2:
                    st.markdown(f"**Rimborso max:** {comp['rimborso_max']}")

    with kk3:
        st.subheader(t("kk_tab3", lc))
        cx1, cx2 = st.columns(2)
        with cx1:
            st.markdown(f"##### {t('kk_situazione_att', lc)}")
            fran_att = st.selectbox(t("kk_franchigia_att", lc), [f["importo"] for f in KK_FRANCHIGIE], format_func=lambda x: f"CHF {x}", key="fa")
            mod_att = st.selectbox(t("kk_modello_att", lc), [m["nome"] for m in KK_MODELLI], key="ma")
        with cx2:
            st.markdown(f"##### {t('kk_proposta', lc)}")
            fran_nuo = st.selectbox(t("kk_franchigia_nuo", lc), [f["importo"] for f in KK_FRANCHIGIE], format_func=lambda x: f"CHF {x}", index=3, key="fn")
            mod_nuo = st.selectbox(t("kk_modello_nuo", lc), [m["nome"] for m in KK_MODELLI], index=3, key="mn")

        rfa = next(f["risparmio_pct"] for f in KK_FRANCHIGIE if f["importo"] == fran_att)
        rfn = next(f["risparmio_pct"] for f in KK_FRANCHIGIE if f["importo"] == fran_nuo)
        rma = next(m["risparmio_pct"] for m in KK_MODELLI if m["nome"] == mod_att)
        rmn = next(m["risparmio_pct"] for m in KK_MODELLI if m["nome"] == mod_nuo)
        pa = int(premio_base * (1 - min(rfa + rma, 55) / 100))
        pn = int(premio_base * (1 - min(rfn + rmn, 55) / 100))
        risp = (pa - pn) * 12

        ck1, ck2, ck3, ck4 = st.columns(4)
        ck1.metric(t("kk_prem_att", lc), f"CHF {pa}/m")
        ck2.metric(t("kk_prem_nuo", lc), f"CHF {pn}/m")
        ck3.metric(t("kk_risp_anno", lc), f"CHF {risp:,}", delta=f"+CHF {risp:,}" if risp > 0 else f"CHF {risp:,}")
        ck4.metric(t("kk_risp_5anni", lc), f"CHF {risp*5:,}")

        df_ck = pd.DataFrame({"Config": [t("kk_situazione_att", lc), t("kk_proposta", lc)], "CHF/mese": [pa, pn]})
        bar_ck = alt.Chart(df_ck).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
            x=alt.X("Config:N", axis=alt.Axis(labelAngle=0), title=""),
            y=alt.Y("CHF/mese:Q", scale=alt.Scale(domain=[0, pa * 1.3])),
            color=alt.Color("Config:N", scale=alt.Scale(
                domain=[t("kk_situazione_att", lc), t("kk_proposta", lc)],
                range=["#bdc3c7", "#27ae60"]), legend=None),
            tooltip=["Config", "CHF/mese"],
        ).properties(height=200)
        st.altair_chart(bar_ck, use_container_width=True)
        if risp > 0:
            st.success(f"✅ **{nome_display}** {t('kk_risp_anno', lc)}: **CHF {risp:,}**")


# ══════════════════════════════════════════════
# TAB 3 — PREVIDENZA
# ══════════════════════════════════════════════

with tab_prev:
    st.header(t("prev_header", lc))
    pt1, pt2, pt3 = st.tabs([t("prev_tab1", lc), t("prev_tab2", lc), t("prev_tab3", lc)])

    with pt1:
        for num, p in PILASTRI.items():
            badge = f"✅ {t('prev_obbligatorio', lc)}" if p["obbligatorio"] else f"🔵 {t('prev_facoltativo', lc)}"
            with st.expander(f"{p['icona']} {p['nome']} — {badge}", expanded=(num == "3")):
                pc1, pc2 = st.columns([2, 1])
                with pc1:
                    st.markdown(f"**Obiettivo:** {p['obiettivo']}")
                    st.markdown(f"**Sistema:** {p['sistema']}")
                    st.warning(f"⚠️ {p['lacuna_tipica']}")
                with pc2:
                    for lbl_p, val_p in p["dati_chiave"]:
                        st.markdown(f"- **{lbl_p}:** {val_p}")

    with pt2:
        st.subheader(t("prev_tab2", lc))
        max_3a = (PILASTRI["3"]["max_3a_dipendente_2026"] if situazione_norm == "Dipendente"
                  else PILASTRI["3"]["max_3a_indipendente_2026"])
        pp1, pp2, pp3, pp4 = st.columns(4)
        with pp1:
            versamento_annuo = st.number_input(t("prev_versamento", lc), 0, max_3a, min(max_3a, 7258), step=100)
        with pp2:
            anni_inv = st.slider(t("prev_anni_inv", lc), 5, 40, anni_pensionamento)
        with pp3:
            rend_pct = st.slider(t("prev_rendimento", lc), 0.5, 7.0, 3.5, step=0.5)
        with pp4:
            aliquota = st.slider(t("prev_aliquota", lc), 10, 45, 25)

        def sim3a(v, n, r):
            c = [0]
            for _ in range(n):
                c.append(c[-1] * (1 + r / 100) + v)
            return c

        cap_ora = sim3a(versamento_annuo, anni_inv, rend_pct)
        cap_tardi = [0] * 6 + sim3a(versamento_annuo, max(anni_inv - 5, 1), rend_pct)
        if len(cap_tardi) < len(cap_ora):
            cap_tardi += [cap_tardi[-1]] * (len(cap_ora) - len(cap_tardi))

        risp_fis = [versamento_annuo * aliquota / 100 * i for i in range(len(cap_ora))]
        df3 = pd.DataFrame({
            "Anno": list(range(len(cap_ora))),
            "Inizia ora": [int(c) for c in cap_ora],
            "Inizia tra 5 anni": [int(c) for c in cap_tardi[:len(cap_ora)]],
            "Risparmio fiscale": [int(r) for r in risp_fis],
        })
        df3m = df3.melt("Anno", ["Inizia ora", "Inizia tra 5 anni", "Risparmio fiscale"], var_name="Scenario", value_name="CHF")
        colori3 = {"Inizia ora": "#c0392b", "Inizia tra 5 anni": "#e8a0a0", "Risparmio fiscale": "#27ae60"}
        line3 = alt.Chart(df3m).mark_line(strokeWidth=2.5).encode(
            x=alt.X("Anno:Q"),
            y=alt.Y("CHF:Q", axis=alt.Axis(format=",.0f")),
            color=alt.Color("Scenario:N", scale=alt.Scale(domain=list(colori3.keys()), range=list(colori3.values()))),
            strokeDash=alt.condition(alt.datum["Scenario"] == "Inizia tra 5 anni", alt.value([6, 3]), alt.value([0])),
            tooltip=["Anno", "Scenario", alt.Tooltip("CHF:Q", format=",.0f")],
        ).properties(height=300)
        st.altair_chart(line3, use_container_width=True)

        capitale_finale = int(cap_ora[-1])
        costo_ritardo = capitale_finale - int(cap_tardi[len(cap_ora) - 1])
        risp_fis_tot = int(versamento_annuo * aliquota / 100 * anni_inv)
        pp1, pp2, pp3, pp4 = st.columns(4)
        pp1.metric(t("prev_capitale", lc), f"CHF {capitale_finale:,}")
        pp2.metric(t("prev_risp_fis", lc), f"CHF {risp_fis_tot:,}")
        pp3.metric(t("prev_costo_ritardo", lc), f"CHF {costo_ritardo:,}", delta=f"-CHF {costo_ritardo:,}", delta_color="inverse")
        pp4.metric(t("prev_tassazione", lc), f"CHF {int(capitale_finale*0.07):,}", delta="~7%", delta_color="off")

        st.divider()
        cf = PILASTRI["3"]["confronto_banca_assicurazione"]
        pb1, pb2 = st.columns(2)
        with pb1:
            st.markdown(f"#### 🏦 {t('prev_banca', lc)}")
            for item in cf["banca"]["pro"]:
                st.markdown(f"<span class='cover-ok'>✔ {item}</span>", unsafe_allow_html=True)
            for item in cf["banca"]["contro"]:
                st.markdown(f"<span class='cover-no'>✘ {item}</span>", unsafe_allow_html=True)
        with pb2:
            st.markdown(f"#### 🏢 {t('prev_assic', lc)}")
            for item in cf["assicurazione"]["pro"]:
                st.markdown(f"<span class='cover-ok'>✔ {item}</span>", unsafe_allow_html=True)
            for item in cf["assicurazione"]["contro"]:
                st.markdown(f"<span class='cover-no'>✘ {item}</span>", unsafe_allow_html=True)

    with pt3:
        st.subheader(t("prev_tab3", lc))
        obj_pct = st.slider(t("prev_obiettivo", lc), 50, 100, 70)
        obj_anno = reddito_annuo * obj_pct / 100
        avs_d = min(reddito_annuo * 0.18, 2520 * 12)
        lpp_d = max((reddito_annuo - 26460) * 0.18, 0) if situazione_norm != "Indipendente" else 0
        terzo_d = int(capitale_finale * 0.04) if anni_inv > 0 else 0
        totale_d = avs_d + lpp_d + terzo_d
        lacuna_d = max(obj_anno - totale_d, 0)

        df_ld = pd.DataFrame({
            "Fonte": ["1° AVS", "2° LPP", f"3° {t('prev_banca', lc)}", t("prev_lacuna", lc)],
            "CHF": [int(avs_d), int(lpp_d), int(terzo_d), int(lacuna_d)],
            "Col": [PILASTRI["1"]["colore"], PILASTRI["2"]["colore"], PILASTRI["3"]["colore"], "#e74c3c"],
        })
        pcc1, pcc2 = st.columns([2, 1])
        with pcc1:
            bar_ld = alt.Chart(df_ld).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("Fonte:N", axis=alt.Axis(labelAngle=0), title=""),
                y=alt.Y("CHF:Q", axis=alt.Axis(format=",.0f")),
                color=alt.Color("Col:N", scale=None, legend=None),
                tooltip=["Fonte", alt.Tooltip("CHF:Q", format=",.0f")],
            ).properties(height=280)
            linea_ob = alt.Chart(pd.DataFrame({"y": [int(obj_anno)]})).mark_rule(
                color="#f39c12", strokeDash=[8, 4], strokeWidth=2.5
            ).encode(y="y:Q")
            st.altair_chart(bar_ld + linea_ob, use_container_width=True)
        with pcc2:
            st.metric(t("prev_obiettivo_annuo", lc), f"CHF {int(obj_anno):,}")
            st.metric("1° AVS", f"CHF {int(avs_d):,}")
            st.metric("2° LPP", f"CHF {int(lpp_d):,}")
            st.metric("3° Pilastro", f"CHF {int(terzo_d):,}")
            st.metric(t("prev_lacuna", lc), f"CHF {int(lacuna_d):,}",
                      delta=f"-CHF {int(lacuna_d):,}" if lacuna_d > 0 else "✓",
                      delta_color="inverse" if lacuna_d > 0 else "normal")

st.divider()
st.caption(t("footer", lc))
