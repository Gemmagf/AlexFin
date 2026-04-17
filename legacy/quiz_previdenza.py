import streamlit as st
import pandas as pd
import altair as alt
import random
from collections import defaultdict

st.set_page_config(
    page_title="Previdenza Svizzera – Ripasso Esame",
    page_icon="🇨🇭",
    layout="wide",
)

st.markdown("""
<style>
h1, h2, h3 { color: #c0392b !important; }
.stButton > button {
    background-color: #c0392b; color: white;
    border-radius: 8px; border: none; font-weight: 600;
}
.stButton > button:hover { background-color: #a93226; }
.feedback-correct {
    background: #d4edda; border-left: 5px solid #28a745;
    padding: 14px 18px; border-radius: 6px; margin: 10px 0;
}
.feedback-wrong {
    background: #f8d7da; border-left: 5px solid #dc3545;
    padding: 14px 18px; border-radius: 6px; margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────── TEORIA ────────────────────────────────────────

THEORY = {
    "1° Pilastro – AVS / AI / IPG": {
        "icon": "🏛️",
        "obiettivo": "Garantire il minimo vitale per vecchiaia, invalidità e superstiti.",
        "sistema": "**Ripartizione** (pay-as-you-go): i contributi degli attivi finanziano le rendite correnti.",
        "obbligatorio": "✅ Sì, per tutte le persone residenti o che lavorano in Svizzera.",
        "componenti": "AVS (vecchiaia + superstiti) · AI (invalidità) · IPG (indennità perdita guadagno)",
        "dati": [
            ("Rendita minima mensile", "CHF 1,260"),
            ("Rendita massima mensile – individuale", "CHF 2,520"),
            ("Rendita massima mensile – coppia", "CHF 3,780"),
            ("Aliquota AVS (lavoratore + datore)", "8.7%  (4.35% + 4.35%)"),
            ("Aliquota totale AVS + AI + IPG", "10.6%  (5.3% + 5.3%)"),
            ("Età di riferimento uomini", "65 anni"),
            ("Età di riferimento donne (2026 – riforma AVS 21)", "64 anni e 9 mesi"),
            ("Anni di contribuzione per rendita intera (uomini)", "44 anni"),
        ],
    },
    "2° Pilastro – LPP (Previdenza Professionale)": {
        "icon": "🏢",
        "obiettivo": "Mantenere il tenore di vita (1° + 2° pilastro ≈ 60% dell'ultimo salario).",
        "sistema": "**Capitalizzazione individuale**: ogni assicurato accumula il proprio avere.",
        "obbligatorio": "✅ Per i dipendenti con salario annuo ≥ CHF 22,680.",
        "componenti": "Rendita vecchiaia · Rendita invalidità · Rendita superstiti · Prestazione in capitale",
        "dati": [
            ("Soglia d'entrata (salario annuo minimo)", "CHF 22,680"),
            ("Deduzione di coordinamento", "CHF 26,460"),
            ("Tasso minimo di conversione", "6.8%"),
            ("Inizio contributi di risparmio", "25 anni"),
            ("Inizio copertura rischi (morte / invalidità)", "17 anni"),
            ("Tasso d'interesse minimo LPP", "Fissato annualmente dal Consiglio federale"),
        ],
    },
    "3° Pilastro – Previdenza Privata": {
        "icon": "🏦",
        "obiettivo": "Colmare lacune previdenziali e ottimizzare il carico fiscale.",
        "sistema": "**Risparmio volontario individuale.**",
        "obbligatorio": "❌ Completamente facoltativo.",
        "componenti": "3a (vincolato, deducibile fiscalmente) · 3b (libero, flessibile)",
        "dati": [
            ("3a – max deducibile, dipendenti con 2° pilastro", "CHF 7,258 / anno"),
            ("3a – max deducibile, indipendenti senza 2° pilastro", "20% reddito AVS, max CHF 36,288"),
            ("3a – chi può versare", "Chi ha reddito soggetto all'AVS"),
            ("3a – ritiro anticipato ammesso", "Abitazione, att. indipendente, partenza CH, invalidità"),
            ("3a – tassazione al ritiro", "Separatamente, aliquota ridotta, cantone di domicilio"),
            ("3b – limiti di versamento", "Nessuno (vantaggi fiscali limitati / cantonali)"),
        ],
    },
}

# ─────────────────────────── DOMANDE ───────────────────────────────────────

QUESTIONS = [
    # ── 1° PILASTRO ─────────────────────────────────────────────────────────
    {
        "id": 1, "pillar": "1° Pilastro",
        "question": "Qual è la rendita AVS massima mensile per una persona sola nel 2026?",
        "options": ["CHF 1,260", "CHF 2,000", "CHF 2,520", "CHF 3,780"],
        "correct": 2,
        "explanation": "La rendita massima AVS individuale è CHF 2,520/mese. La minima è CHF 1,260 (la metà esatta). Per le coppie il massimo è CHF 3,780 (150% della max individuale).",
    },
    {
        "id": 2, "pillar": "1° Pilastro",
        "question": "Qual è il principio di finanziamento del 1° pilastro (AVS)?",
        "options": ["Capitalizzazione individuale", "Sistema misto", "Ripartizione (pay-as-you-go)", "Finanziamento statale diretto"],
        "correct": 2,
        "explanation": "L'AVS funziona a ripartizione: i contributi degli attivi pagano direttamente le rendite dei pensionati correnti. Non si accumula un capitale individuale.",
    },
    {
        "id": 3, "pillar": "1° Pilastro",
        "question": "Come viene finanziata l'AVS?",
        "options": [
            "Solo dai contributi dei lavoratori",
            "Contributi salariali (lavoratori + datori), Confederazione e quota IVA",
            "Solo da contributi di lavoratori e datori di lavoro",
            "Solo dalla Confederazione e dalle imposte federali",
        ],
        "correct": 1,
        "explanation": "L'AVS è finanziata da: contributi salariali paritari (lavoratore + datore), un contributo della Confederazione e una quota IVA dedicata (aumentata con la riforma AVS 21).",
    },
    {
        "id": 4, "pillar": "1° Pilastro",
        "question": "Qual è l'aliquota contributiva totale AVS sul salario (lavoratore + datore)?",
        "options": ["4.35%", "6.0%", "8.7%", "10.6%"],
        "correct": 2,
        "explanation": "L'aliquota AVS totale è 8.7% (4.35% lavoratore + 4.35% datore). Aggiungendo AI (1.4%) e IPG (0.5%) si arriva al 10.6% totale per l'insieme del 1° pilastro.",
    },
    {
        "id": 5, "pillar": "1° Pilastro",
        "question": "Qual è la rendita massima mensile per una coppia sposata (AVS) nel 2026?",
        "options": ["CHF 2,520", "CHF 3,360", "CHF 3,780", "CHF 5,040"],
        "correct": 2,
        "explanation": "CHF 3,780/mese = 150% della rendita massima individuale (CHF 2,520 × 1.5). La rendita della coppia viene plafonata a questo importo.",
    },
    {
        "id": 6, "pillar": "1° Pilastro",
        "question": "Secondo la riforma AVS 21, qual è l'età di riferimento delle donne nel 2026?",
        "options": ["64 anni", "64 anni e 6 mesi", "64 anni e 9 mesi", "65 anni"],
        "correct": 2,
        "explanation": "Con AVS 21 l'età delle donne aumenta di 3 mesi/anno: 64.25 (2024) → 64.5 (2025) → 64.75 (2026) → 65 (2028). Nel 2026 = 64 anni e 9 mesi.",
    },
    {
        "id": 7, "pillar": "1° Pilastro",
        "question": "Quanti anni di contribuzione AVS danno diritto a una rendita intera (uomini)?",
        "options": ["40 anni", "42 anni", "43 anni", "44 anni"],
        "correct": 3,
        "explanation": "Servono 44 anni di contribuzione completi per una rendita AVS intera (uomini). Con la riforma AVS 21, anche le donne raggiungeranno 44 anni a regime.",
    },
    {
        "id": 8, "pillar": "1° Pilastro",
        "question": "Cosa comprende il 1° pilastro svizzero?",
        "options": [
            "Solo la rendita di vecchiaia (AVS)",
            "AVS (vecchiaia + superstiti), AI (invalidità) e infortuni",
            "AVS (vecchiaia + superstiti), AI (invalidità) e IPG (indennità perdita guadagno)",
            "Vecchiaia, malattia, maternità e disoccupazione",
        ],
        "correct": 2,
        "explanation": "1° pilastro = AVS (vecchiaia e superstiti) + AI (invalidità e reinserimento) + IPG (servizio militare/civile e maternità). Malattia e infortuni sono coperture separate.",
    },
    {
        "id": 9, "pillar": "1° Pilastro",
        "question": "A chi si applica l'obbligo di assicurazione AVS?",
        "options": [
            "Solo ai cittadini svizzeri",
            "Solo ai lavoratori dipendenti con salario ≥ CHF 22,680",
            "A tutte le persone residenti o che esercitano attività lucrativa in Svizzera",
            "Solo a chi ha più di 20 anni",
        ],
        "correct": 2,
        "explanation": "L'AVS è universale: riguarda tutti i residenti in Svizzera e chi vi esercita un'attività lucrativa, indipendentemente da nazionalità o importo del salario.",
    },
    {
        "id": 10, "pillar": "1° Pilastro",
        "question": "Qual è la rendita AVS minima mensile nel 2026?",
        "options": ["CHF 840", "CHF 1,050", "CHF 1,260", "CHF 1,500"],
        "correct": 2,
        "explanation": "La rendita minima AVS è CHF 1,260/mese, esattamente la metà della rendita massima individuale (CHF 2,520). Spetta a chi ha lacune contributive significative.",
    },
    # ── 2° PILASTRO ─────────────────────────────────────────────────────────
    {
        "id": 11, "pillar": "2° Pilastro",
        "question": "Qual è il principio di finanziamento del 2° pilastro (LPP)?",
        "options": ["Ripartizione", "Capitalizzazione individuale", "Sistema misto", "Finanziamento statale"],
        "correct": 1,
        "explanation": "Il 2° pilastro funziona a capitalizzazione: ogni lavoratore accumula il proprio avere individuale che viene investito. Al pensionamento si dispone del capitale accumulato (convertito in rendita o ritirato in capitale).",
    },
    {
        "id": 12, "pillar": "2° Pilastro",
        "question": "Qual è la soglia minima d'entrata LPP nel 2026 (salario annuale per l'assicurazione obbligatoria)?",
        "options": ["CHF 15,000", "CHF 18,900", "CHF 22,680", "CHF 26,460"],
        "correct": 2,
        "explanation": "Chi guadagna meno di CHF 22,680/anno non è obbligatoriamente assicurato LPP. La soglia = 3/4 della rendita massima AVS annuale (3/4 × CHF 30,240).",
    },
    {
        "id": 13, "pillar": "2° Pilastro",
        "question": "Qual è la deduzione di coordinamento LPP nel 2026?",
        "options": ["CHF 22,680", "CHF 24,885", "CHF 26,460", "CHF 30,240"],
        "correct": 2,
        "explanation": "La deduzione di coordinamento è CHF 26,460 (= 7/8 della rendita massima AVS annuale). Si sottrae dal salario per calcolare il salario assicurato LPP (salario coordinato).",
    },
    {
        "id": 14, "pillar": "2° Pilastro",
        "question": "Da quale età iniziano i contributi di risparmio LPP?",
        "options": ["17 anni", "18 anni", "20 anni", "25 anni"],
        "correct": 3,
        "explanation": "La copertura rischi (morte e invalidità) inizia a 17 anni. I contributi di risparmio per la vecchiaia partono a 25 anni.",
    },
    {
        "id": 15, "pillar": "2° Pilastro",
        "question": "Qual è il tasso minimo di conversione LPP (obbligatorio) nel 2026?",
        "options": ["5.0%", "6.0%", "6.8%", "7.2%"],
        "correct": 2,
        "explanation": "Il tasso di conversione minimo obbligatorio è 6.8%. Trasforma l'avere accumulato in rendita annua: Rendita annua = Avere di vecchiaia × 6.8%.",
    },
    {
        "id": 16, "pillar": "2° Pilastro",
        "question": "Come si calcola il salario coordinato (assicurato) LPP?",
        "options": [
            "Salario lordo × tasso di conversione",
            "Salario AVS − deduzione di coordinamento",
            "Salario AVS − soglia d'entrata",
            "Salario lordo ÷ 12",
        ],
        "correct": 1,
        "explanation": "Salario coordinato = Salario AVS − Deduzione di coordinamento (CHF 26,460). È la parte di salario su cui si calcolano i contributi LPP.",
    },
    {
        "id": 17, "pillar": "2° Pilastro",
        "question": "Chi fissa il tasso d'interesse minimo sugli averi LPP?",
        "options": ["La FINMA", "Il Parlamento federale", "Il Consiglio federale", "Le singole casse pensioni"],
        "correct": 2,
        "explanation": "Il Consiglio federale determina annualmente il tasso d'interesse minimo che le casse pensioni devono accreditare sugli averi obbligatori LPP.",
    },
    {
        "id": 18, "pillar": "2° Pilastro",
        "question": "Cosa si intende con 'prestazione d'uscita' (libero passaggio) LPP?",
        "options": [
            "La rendita mensile al pensionamento",
            "Il capitale accumulato che si porta alla nuova cassa pensioni in caso di cambio datore di lavoro",
            "L'indennità in caso di licenziamento senza giusta causa",
            "Il rimborso dei contributi in caso di emigrazione",
        ],
        "correct": 1,
        "explanation": "La prestazione d'uscita è l'avere LPP che il lavoratore porta con sé cambiando impiego. Va trasferito alla nuova cassa pensioni o, in assenza, su un conto/polizza di libero passaggio.",
    },
    {
        "id": 19, "pillar": "2° Pilastro",
        "question": "Quali rischi copre il 2° pilastro per un lavoratore attivo?",
        "options": [
            "Solo la vecchiaia",
            "Vecchiaia e malattia",
            "Vecchiaia, morte (superstiti) e invalidità",
            "Vecchiaia, disoccupazione e invalidità",
        ],
        "correct": 2,
        "explanation": "Il 2° pilastro copre tre rischi: vecchiaia (risparmio), decesso prematuro (rendita ai superstiti) e invalidità. Copertura rischi da 17 anni, risparmio da 25 anni.",
    },
    {
        "id": 20, "pillar": "2° Pilastro",
        "question": "Cosa succede all'avere LPP in caso di partenza definitiva dalla Svizzera verso un paese extra-UE/AELS?",
        "options": [
            "Rimane bloccato fino ai 65 anni",
            "Viene perso automaticamente",
            "Può essere ritirato interamente in contanti",
            "Viene trasferito alla cassa pensioni del paese di destinazione",
        ],
        "correct": 2,
        "explanation": "Emigrando definitivamente verso un paese extra-UE/AELS, l'intero avere LPP (obbligatorio e sovraobbligatorio) può essere ritirato in contanti, con trattenuta d'imposta alla fonte.",
    },
    # ── 3° PILASTRO ─────────────────────────────────────────────────────────
    {
        "id": 21, "pillar": "3° Pilastro",
        "question": "Qual è l'importo massimo deducibile per il pilastro 3a (dipendenti con 2° pilastro) nel 2026?",
        "options": ["CHF 6,826", "CHF 7,056", "CHF 7,258", "CHF 8,000"],
        "correct": 2,
        "explanation": "Nel 2026 i lavoratori dipendenti assicurati al 2° pilastro possono dedurre fino a CHF 7,258/anno per i versamenti nel pilastro 3a.",
    },
    {
        "id": 22, "pillar": "3° Pilastro",
        "question": "Qual è la differenza principale tra pilastro 3a e 3b?",
        "options": [
            "Il 3a è obbligatorio, il 3b è facoltativo",
            "Il 3a è vincolato con vantaggi fiscali garantiti; il 3b è libero, senza vantaggi fiscali fissi",
            "Il 3a è riservato ai dipendenti, il 3b agli indipendenti",
            "Il 3b è gestito dallo Stato, il 3a dalle banche",
        ],
        "correct": 1,
        "explanation": "Il 3a (previdenza vincolata) offre vantaggi fiscali certi (deducibilità, esenzione rendimenti) ma con restrizioni di ritiro. Il 3b è flessibile ma i vantaggi fiscali dipendono dal cantone.",
    },
    {
        "id": 23, "pillar": "3° Pilastro",
        "question": "Chi può aprire un conto pilastro 3a?",
        "options": [
            "Tutti i residenti in Svizzera",
            "Solo i cittadini svizzeri con reddito",
            "Chi ha un reddito soggetto all'AVS (dipendenti e indipendenti)",
            "Solo i dipendenti con 2° pilastro",
        ],
        "correct": 2,
        "explanation": "Possono aprire un 3a le persone con reddito soggetto all'AVS: dipendenti (con o senza 2° pilastro) e indipendenti. Non chi non ha reddito da lavoro.",
    },
    {
        "id": 24, "pillar": "3° Pilastro",
        "question": "Fino a quando è possibile versare nel pilastro 3a (riforma AVS 21)?",
        "options": [
            "Fino all'età di pensionamento ordinaria",
            "Fino a 5 anni dopo l'età di riferimento, se si continua a lavorare",
            "Senza limiti d'età",
            "Fino a 60 anni",
        ],
        "correct": 1,
        "explanation": "Con la riforma AVS 21, chi continua a lavorare oltre l'età di riferimento può versare nel 3a fino a 5 anni in più (es. fino a 70 anni se l'età di riferimento è 65).",
    },
    {
        "id": 25, "pillar": "3° Pilastro",
        "question": "Qual è il massimo annuo nel 3a per un indipendente SENZA 2° pilastro nel 2026?",
        "options": ["CHF 7,258", "CHF 14,516", "20% del reddito AVS, max CHF 36,288", "CHF 50,000"],
        "correct": 2,
        "explanation": "Gli indipendenti senza 2° pilastro possono versare fino al 20% del reddito netto da lavoro, con un massimo di CHF 36,288 nel 2026 (≈ 5× il limite per i dipendenti).",
    },
    {
        "id": 26, "pillar": "3° Pilastro",
        "question": "In quali casi è ammesso il ritiro anticipato del pilastro 3a?",
        "options": [
            "In qualsiasi momento con una penale",
            "Solo in caso di invalidità permanente",
            "Acquisto abitazione, inizio att. indipendente, partenza definitiva CH, invalidità, decesso",
            "A partire dai 60 anni senza condizioni",
        ],
        "correct": 2,
        "explanation": "Il ritiro anticipato è consentito solo nei casi previsti dalla legge: acquisto/costruzione abitazione principale, rimborso ipoteca, avvio att. indipendente, partenza definitiva dalla CH, invalidità o decesso.",
    },
    # ── GENERALE ────────────────────────────────────────────────────────────
    {
        "id": 27, "pillar": "Generale",
        "question": "Qual è l'obiettivo del sistema previdenziale svizzero a tre pilastri?",
        "options": [
            "Garantire il 100% dell'ultimo salario",
            "Mantenere adeguatamente il tenore di vita (1° + 2° pilastro ≈ 60% dell'ultimo reddito)",
            "Garantire solo il minimo vitale",
            "Sostituire il reddito al 40%",
        ],
        "correct": 1,
        "explanation": "Il sistema mira a garantire circa il 60% dell'ultimo reddito combinando 1° e 2° pilastro. Il 3° colma le lacune per chi vuole mantenere il tenore di vita precedente.",
    },
    {
        "id": 28, "pillar": "Generale",
        "question": "Quale pilastro è obbligatorio per TUTTI i residenti in Svizzera?",
        "options": [
            "Solo il 1° pilastro",
            "Il 1° e il 2° per tutti",
            "Il 1° per tutti; il 2° obbligatorio per i dipendenti oltre la soglia salariale",
            "Tutti e tre i pilastri",
        ],
        "correct": 2,
        "explanation": "Il 1° pilastro (AVS) è obbligatorio per tutti. Il 2° è obbligatorio per i dipendenti con salario ≥ CHF 22,680. Il 3° è sempre facoltativo.",
    },
    {
        "id": 29, "pillar": "Generale",
        "question": "Cosa si intende per 'lacuna previdenziale'?",
        "options": [
            "Anni di contributi AVS mancanti",
            "La differenza tra le rendite dei pilastri e il reddito desiderato in pensione",
            "Un debito della cassa pensioni verso lo Stato",
            "Il mancato versamento nel 3° pilastro",
        ],
        "correct": 1,
        "explanation": "La lacuna previdenziale è la differenza tra quanto garantito dai pilastri (spesso 40-60% dell'ultimo salario) e il reddito necessario per mantenere il tenore di vita. Si colma con il 3° pilastro o altri risparmi.",
    },
    {
        "id": 30, "pillar": "Generale",
        "question": "Come viene tassato il capitale del pilastro 3a al momento del ritiro?",
        "options": [
            "Non è tassato",
            "È aggiunto al reddito ordinario e tassato all'aliquota marginale",
            "È tassato separatamente con aliquota ridotta nel cantone di domicilio",
            "È tassato solo a livello federale diretto",
        ],
        "correct": 2,
        "explanation": "Al ritiro il 3a è tassato separatamente dal reddito ordinario (aliquota ridotta ≈ 1/5 dell'aliquota piena) nel cantone di domicilio. Durante l'accumulo i versamenti sono completamente deducibili.",
    },
]

# ─────────────────────────── SESSION STATE ─────────────────────────────────

def init_quiz():
    shuffled = QUESTIONS.copy()
    random.shuffle(shuffled)
    st.session_state.quiz_qs = shuffled
    st.session_state.q_idx = 0
    st.session_state.phase = "question"   # "question" | "feedback"
    st.session_state.selected_idx = None
    st.session_state.history = []         # list of {"pillar": str, "correct": bool}

if "quiz_qs" not in st.session_state:
    init_quiz()

# ─────────────────────────── HEADER ────────────────────────────────────────

st.title("🇨🇭 Previdenza Svizzera – Ripasso Esame")
st.caption("1° · 2° · 3° pilastro   ·   Esame venerdì 18 aprile 2026   ·   Dati aggiornati 2026")
st.divider()

tab_theory, tab_quiz, tab_stats = st.tabs(["📚 Teoria", "🎯 Quiz", "📊 Statistiche"])

# ─────────────────────────── TEORIA ────────────────────────────────────────

with tab_theory:
    for name, d in THEORY.items():
        with st.expander(f"{d['icon']}  {name}", expanded=True):
            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown(f"**Obiettivo:** {d['obiettivo']}")
                st.markdown(f"**Sistema:** {d['sistema']}")
                st.markdown(f"**Obbligatorio:** {d['obbligatorio']}")
                st.markdown(f"**Comprende:** {d['componenti']}")
            with col_right:
                st.markdown("**Dati chiave 2026:**")
                for label, value in d["dati"]:
                    st.markdown(f"- **{label}:** {value}")

# ─────────────────────────── QUIZ ──────────────────────────────────────────

with tab_quiz:
    qs = st.session_state.quiz_qs
    idx = st.session_state.q_idx
    total = len(qs)
    history = st.session_state.history
    done = len(history)

    if idx < total:
        n_correct_so_far = sum(h["correct"] for h in history)
        st.progress(
            done / total,
            text=f"Domanda {idx + 1} di {total}  ·  Corrette finora: {n_correct_so_far}/{done}",
        )

        q = qs[idx]
        st.markdown(f"`{q['pillar']}`")
        st.markdown(f"### {q['question']}")

        if st.session_state.phase == "question":
            choice = st.radio(
                "Scegli la risposta:",
                q["options"],
                index=None,
                key=f"radio_{idx}",
            )

            col_btn, _ = st.columns([1, 4])
            with col_btn:
                if st.button("✅ Conferma risposta", disabled=(choice is None)):
                    st.session_state.selected_idx = q["options"].index(choice)
                    st.session_state.phase = "feedback"
                    st.rerun()

        else:  # feedback
            sel = st.session_state.selected_idx
            correct = q["correct"]
            is_correct = sel == correct

            for i, opt in enumerate(q["options"]):
                if i == correct:
                    st.success(f"✅  {opt}")
                elif i == sel:
                    st.error(f"❌  {opt}")
                else:
                    st.write(f"○  {opt}")

            if is_correct:
                st.markdown(
                    '<div class="feedback-correct">🎉 <strong>Corretto!</strong></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="feedback-wrong">❌ <strong>Sbagliato.</strong> '
                    f'Risposta corretta: <em>{q["options"][correct]}</em></div>',
                    unsafe_allow_html=True,
                )

            st.info(f"💡 **Spiegazione:** {q['explanation']}")

            # Record only once per question
            if len(history) == idx:
                history.append({"pillar": q["pillar"], "correct": is_correct})

            col_btn, _ = st.columns([1, 4])
            with col_btn:
                label = "Prossima domanda →" if idx < total - 1 else "📊 Risultati finali"
                if st.button(label):
                    st.session_state.q_idx += 1
                    st.session_state.phase = "question"
                    st.session_state.selected_idx = None
                    st.rerun()

    else:
        # ── Risultati finali ──
        n_correct = sum(h["correct"] for h in history)
        pct = int(n_correct / total * 100)

        st.markdown("## Risultati finali")
        if pct >= 75:
            st.success(f"🎉 Ottimo! **{n_correct}/{total}** corrette ({pct}%)")
        elif pct >= 50:
            st.warning(f"📚 Quasi! **{n_correct}/{total}** corrette ({pct}%) — Ripassate la teoria.")
        else:
            st.error(f"❌ **{n_correct}/{total}** corrette ({pct}%) — Serve più ripasso!")

        c1, c2, c3 = st.columns(3)
        c1.metric("Domande totali", total)
        c2.metric("Corrette", n_correct)
        c3.metric("Percentuale", f"{pct}%")

        if st.button("🔄 Ricomincia quiz"):
            init_quiz()
            st.rerun()

# ─────────────────────────── STATISTICHE ───────────────────────────────────

with tab_stats:
    history = st.session_state.history

    if not history:
        st.info("Nessuna statistica disponibile. Completa almeno una domanda del quiz.")
    else:
        n_done = len(history)
        n_correct = sum(h["correct"] for h in history)
        pct_overall = int(n_correct / n_done * 100)

        c1, c2, c3 = st.columns(3)
        c1.metric("Domande risposte", n_done)
        c2.metric("Corrette", n_correct)
        c3.metric("Percentuale", f"{pct_overall}%")

        st.divider()

        pillar_stats = defaultdict(lambda: {"correct": 0, "total": 0})
        for h in history:
            pillar_stats[h["pillar"]]["total"] += 1
            if h["correct"]:
                pillar_stats[h["pillar"]]["correct"] += 1

        rows = [
            {
                "Pilastro": p,
                "Risposte": v["total"],
                "Corrette": v["correct"],
                "% Corrette": round(v["correct"] / v["total"] * 100),
            }
            for p, v in pillar_stats.items()
        ]
        df = pd.DataFrame(rows)

        st.markdown("### Risultati per pilastro")
        st.dataframe(df, hide_index=True, use_container_width=True)

        bar = (
            alt.Chart(df)
            .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
            .encode(
                x=alt.X("Pilastro:N", axis=alt.Axis(labelAngle=0), title=""),
                y=alt.Y("% Corrette:Q", scale=alt.Scale(domain=[0, 100]), title="% Corrette"),
                color=alt.condition(
                    alt.datum["% Corrette"] >= 70,
                    alt.value("#28a745"),
                    alt.value("#dc3545"),
                ),
                tooltip=["Pilastro", "Corrette", "Risposte", "% Corrette"],
            )
            .properties(title="Risultati per pilastro", height=280)
        )

        threshold = alt.Chart(pd.DataFrame({"y": [70]})).mark_rule(
            color="#f0ad4e", strokeDash=[6, 3], strokeWidth=2
        ).encode(y="y:Q")

        st.altair_chart(bar + threshold, use_container_width=True)
        st.caption("La linea arancione indica la soglia del 70%.")

        if st.button("🗑️ Azzera statistiche"):
            st.session_state.history = []
            st.rerun()
