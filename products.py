# products.py — AlexFin Advisor Tool
# Catalogo prodotti: Assicurazioni, Krankenkasse, Previdenza

from i18n import t as _t

# ─────────────────────────────────────────────
# ASSICURAZIONI PRIVATE
# ─────────────────────────────────────────────

ASSICURAZIONI = [
    {
        "id": "vita",
        "nome": "Assicurazione Vita",
        "icona": "❤️",
        "categoria": "Protezione",
        "descrizione": "Protezione finanziaria per i propri cari in caso di decesso prematuro. Garantisce un capitale o una rendita ai superstiti.",
        "coperture": [
            "Capitale in caso di decesso",
            "Rendita per il coniuge e i figli",
            "Copertura ipoteche e debiti",
            "Pagamento anticipato in caso di malattia terminale",
        ],
        "esclusioni": [
            "Suicidio entro i primi 2 anni dalla stipula",
            "Attività ad alto rischio non dichiarate",
            "Malattie preesistenti non dichiarate",
        ],
        "costo_indicativo": "CHF 30 – 150 / mese",
        "costo_note": "Dipende da capitale assicurato, età e stato di salute",
        "premi_per_eta": {25: 35, 30: 45, 35: 60, 40: 85, 45: 120, 50: 175, 55: 250},
        "capitale_esempio": 400000,
        "scenario": {
            "caso": "Marco, 44 anni, muore improvvisamente. Moglie e 2 figli a carico.",
            "senza": "La famiglia perde CHF 90,000 di reddito annuo. L'ipoteca è a rischio.",
            "con": "Capitale CHF 400,000 versato entro 30 giorni. Famiglia protetta.",
        },
        "profili_raccomandati": ["married", "has_kids", "has_mortgage"],
    },
    {
        "id": "invalidita",
        "nome": "Assicurazione Invalidità",
        "icona": "🦽",
        "categoria": "Protezione",
        "descrizione": "Integra la rendita AI dell'AVS in caso di invalidità. L'AI statale copre solo il minimo vitale — questa assicurazione colma la lacuna.",
        "coperture": [
            "Rendita mensile complementare all'AI",
            "Copertura invalidità parziale (dal 25%) o totale",
            "Protezione per malattia e infortuni",
            "Rendita per i figli in caso di invalidità del genitore",
        ],
        "esclusioni": [
            "Invalidità preesistente dichiarata prima della stipula",
            "Dipendenze (alcol, droghe) come causa principale",
            "Malattie psichiatriche (spesso con franchigia o esclusione parziale)",
        ],
        "costo_indicativo": "CHF 50 – 250 / mese",
        "costo_note": "Dipende dal grado di copertura, dall'età e dall'attività professionale",
        "premi_per_eta": {25: 55, 30: 75, 35: 100, 40: 140, 45: 190, 50: 250, 55: 320},
        "capitale_esempio": None,
        "rendita_mensile_esempio": 2500,
        "scenario": {
            "caso": "Elena, infermiera 38 anni, problemi alla schiena. Invalidità parziale (50%).",
            "senza": "AI statale: CHF 900/mese. Reddito perso: CHF 2,800/mese.",
            "con": "Rendita privata integra il gap: +CHF 1,800/mese garantiti.",
        },
        "profili_raccomandati": ["indipendente", "dipendente"],
    },
    {
        "id": "perdita_guadagno",
        "nome": "Perdita di Guadagno",
        "icona": "🤒",
        "categoria": "Protezione",
        "descrizione": "Copre il reddito durante una malattia prolungata. Indispensabile per gli indipendenti, utile complemento per i dipendenti.",
        "coperture": [
            "Indennità giornaliera dal 1° o 30° giorno di malattia",
            "Fino all'80–90% del salario assicurato",
            "Prestazioni fino a 720 giorni (2 anni)",
            "Coordinamento con AI e LAA",
        ],
        "esclusioni": [
            "Malattie preesistenti nei primi anni di contratto",
            "Gravidanza (coperta separatamente dall'IPG)",
            "Periodi di attesa per malattie psicosomatiche",
        ],
        "costo_indicativo": "CHF 80 – 350 / mese",
        "costo_note": "In base al salario assicurato, al periodo di attesa e all'attività svolta",
        "premi_per_eta": {25: 80, 30: 100, 35: 130, 40: 175, 45: 230, 50: 300, 55: 380},
        "capitale_esempio": None,
        "rendita_mensile_esempio": 3500,
        "scenario": {
            "caso": "Luca, artigiano indipendente, burnout per 8 mesi.",
            "senza": "Zero reddito. Deve attingere ai risparmi: CHF 24,000 persi.",
            "con": "CHF 3,200/mese garantiti per tutta la durata della malattia.",
        },
        "profili_raccomandati": ["indipendente"],
    },
    {
        "id": "infortuni",
        "nome": "Assicurazione Infortuni",
        "icona": "🩹",
        "categoria": "Protezione",
        "descrizione": "Copre infortuni professionali e non. Obbligatoria per i dipendenti via datore di lavoro (LAA) — gli indipendenti devono stipularla privatamente.",
        "coperture": [
            "Spese mediche da infortuni (senza franchigia)",
            "Indennità giornaliera durante il recupero (80% salario)",
            "Rendita invalidità da infortuni",
            "Capitale decesso da infortuni ai superstiti",
        ],
        "esclusioni": [
            "Malattie (coperte da Krankenkasse/LAMal)",
            "Infortuni intenzionali o auto-inflitti",
            "Sport estremi non dichiarati (paracadutismo, alpinismo, ecc.)",
        ],
        "costo_indicativo": "CHF 20 – 100 / mese",
        "costo_note": "Dipende dalla professione (rischio) e dal capitale assicurato",
        "premi_per_eta": {25: 22, 30: 28, 35: 35, 40: 45, 45: 58, 50: 72, 55: 90},
        "capitale_esempio": 150000,
        "scenario": {
            "caso": "Paolo, freelance IT, cade in bici. Frattura, 3 mesi di stop.",
            "senza": "Spese mediche CHF 8,000 + reddito perso CHF 15,000.",
            "con": "Tutto coperto. Indennità giornaliera CHF 250/giorno.",
        },
        "profili_raccomandati": ["indipendente"],
    },
    {
        "id": "rc_privata",
        "nome": "RC Privata",
        "icona": "🛡️",
        "categoria": "Responsabilità",
        "descrizione": "Copre i danni causati involontariamente a terzi nella vita privata. Una delle assicurazioni più economiche e indispensabili.",
        "coperture": [
            "Danni materiali causati a terzi",
            "Danni fisici causati a terzi",
            "Danni causati dai figli minorenni",
            "Danni causati da animali domestici",
        ],
        "esclusioni": [
            "Danni causati intenzionalmente",
            "Danni coperti da altre polizze (auto, professionale)",
            "Attività professionali (richiedono RC professionale separata)",
        ],
        "costo_indicativo": "CHF 100 – 200 / anno",
        "costo_note": "Tra le più economiche — alto valore di protezione a costo minimo",
        "premi_per_eta": {25: 130, 30: 140, 35: 150, 40: 155, 45: 160, 50: 165, 55: 170},
        "capitale_esempio": 5000000,
        "scenario": {
            "caso": "Tuo figlio rompe accidentalmente un vetro antico da CHF 15,000.",
            "senza": "Devi pagare CHF 15,000 di tasca tua.",
            "con": "RC Privata copre interamente il danno.",
        },
        "profili_raccomandati": ["tutti"],
    },
    {
        "id": "complementare_spital",
        "nome": "Complementare Ospedaliera",
        "icona": "🏥",
        "categoria": "Salute",
        "descrizione": "Integra la LAMal di base per le cure ospedaliere. Permette di scegliere il medico e il tipo di camera in tutta la Svizzera.",
        "coperture": [
            "Camera semi-privata o privata",
            "Libera scelta del medico in tutta la Svizzera",
            "Cure in cliniche private convenzionate",
            "Rimborso differenza costi cantonali",
        ],
        "esclusioni": [
            "Cure non urgenti non preventivamente autorizzate",
            "Malattie preesistenti (escluse nei primi anni)",
            "Cure puramente estetiche",
        ],
        "costo_indicativo": "CHF 40 – 200 / mese",
        "costo_note": "Semi-privata più economica; privata con libera scelta più cara",
        "premi_per_eta": {25: 45, 30: 55, 35: 70, 40: 90, 45: 115, 50: 150, 55: 195},
        "capitale_esempio": None,
        "scenario": {
            "caso": "Operazione urgente al ginocchio. Il cliente vuole il suo ortopedico di fiducia.",
            "senza": "Solo medico assegnato dalla struttura, camera condivisa.",
            "con": "Scelta del chirurgo, camera privata, convalescenza ottimale.",
        },
        "profili_raccomandati": ["tutti"],
    },
]

# ─────────────────────────────────────────────
# KRANKENKASSE (LAMal / KVG)
# ─────────────────────────────────────────────

# Premi base mensili 2026 per canton (adulto, franchigia 300, modello standard)
KK_PREMI_CANTON = {
    "Ticino":       {"adulto": 468, "giovane": 398, "bambino": 115},
    "Zurigo":       {"adulto": 512, "giovane": 435, "bambino": 125},
    "Ginevra":      {"adulto": 598, "giovane": 508, "bambino": 140},
    "Berna":        {"adulto": 480, "giovane": 408, "bambino": 118},
    "Basilea":      {"adulto": 620, "giovane": 527, "bambino": 148},
    "Vaud":         {"adulto": 575, "giovane": 489, "bambino": 135},
    "Lucerna":      {"adulto": 390, "giovane": 332, "bambino": 96},
    "Argovia":      {"adulto": 425, "giovane": 361, "bambino": 104},
}

KK_MODELLI = [
    {
        "nome": "Standard",
        "descrizione": "Libera scelta del medico senza restrizioni.",
        "risparmio_pct": 0,
        "vincoli": "Nessuno — massima libertà",
        "ideale_per": "Chi vuole massima flessibilità",
        "rating_liberta": 5,
        "rating_risparmio": 1,
    },
    {
        "nome": "Medico di famiglia",
        "descrizione": "Prima consulta sempre dal medico di famiglia, che poi indirizza agli specialisti.",
        "risparmio_pct": 12,
        "vincoli": "Prima visita obbligatoria dal medico di famiglia",
        "ideale_per": "Famiglie con un medico di fiducia",
        "rating_liberta": 3,
        "rating_risparmio": 3,
    },
    {
        "nome": "Telmed",
        "descrizione": "Consulta telefonica obbligatoria prima di andare dal medico.",
        "risparmio_pct": 13,
        "vincoli": "Chiamata obbligatoria alla hotline medica",
        "ideale_per": "Persone sane con pochi contatti medici",
        "rating_liberta": 3,
        "rating_risparmio": 3,
    },
    {
        "nome": "HMO",
        "descrizione": "Tutte le cure gestite da un centro medico HMO (gruppo di medici integrato).",
        "risparmio_pct": 22,
        "vincoli": "Solo medici del centro HMO convenzionato",
        "ideale_per": "Zone urbane con HMO disponibili — massimo risparmio",
        "rating_liberta": 1,
        "rating_risparmio": 5,
    },
]

KK_FRANCHIGIE = [
    {"importo": 300,  "risparmio_pct": 0,   "nota": "Minimo legale — premio più alto"},
    {"importo": 500,  "risparmio_pct": 7,   "nota": "Piccolo risparmio, bassa esposizione"},
    {"importo": 1000, "risparmio_pct": 17,  "nota": "Buon equilibrio rischio/risparmio"},
    {"importo": 1500, "risparmio_pct": 24,  "nota": "Raccomandata se hai poche spese mediche"},
    {"importo": 2500, "risparmio_pct": 35,  "nota": "Massima franchigia — solo per persone sane"},
]

KK_COMPLEMENTARI = [
    {
        "nome": "🦷 Dentista",
        "copertura": "Trattamenti dentistici: otturazioni, estrazioni, protesi, ortodonzia",
        "costo_indicativo": "CHF 15 – 60 / mese",
        "nota": "LAMal base non copre quasi nulla per i denti adulti",
        "rimborso_max": "CHF 3,000 – 10,000 / anno",
    },
    {
        "nome": "🌿 Medicina alternativa",
        "copertura": "Agopuntura, omeopatia, naturopatia, osteopatia, chiropratica",
        "costo_indicativo": "CHF 10 – 30 / mese",
        "nota": "Per chi usa regolarmente medicine complementari",
        "rimborso_max": "CHF 500 – 2,000 / anno",
    },
    {
        "nome": "✈️ Estero & Mondo",
        "copertura": "Cure d'emergenza all'estero, rimpatrio sanitario, elisoccorso",
        "costo_indicativo": "CHF 5 – 20 / mese",
        "nota": "Indispensabile per chi viaggia frequentemente",
        "rimborso_max": "Illimitato per emergenze",
    },
    {
        "nome": "💪 Fitness & Prevenzione",
        "copertura": "Abbonamento palestra, yoga, corsi fitness, check-up preventivi",
        "costo_indicativo": "CHF 10 – 25 / mese",
        "nota": "Fino a CHF 500/anno rimborsati in molti piani",
        "rimborso_max": "CHF 300 – 600 / anno",
    },
    {
        "nome": "👶 Maternità Plus",
        "copertura": "Corsi preparto, osteopata neonatale, visite extra non coperte da LAMal",
        "costo_indicativo": "CHF 20 – 50 / mese",
        "nota": "Utile per famiglie in fase di pianificazione o con neonati",
        "rimborso_max": "CHF 1,000 – 3,000 / gravidanza",
    },
]

# ─────────────────────────────────────────────
# PREVIDENZA (3 PILASTRI)
# ─────────────────────────────────────────────

PILASTRI = {
    "1": {
        "nome": "1° Pilastro – AVS / AI / IPG",
        "icona": "🏛️",
        "colore": "#2980b9",
        "obiettivo": "Garantire il minimo vitale per vecchiaia, invalidità e superstiti.",
        "sistema": "Ripartizione (pay-as-you-go): i contributi degli attivi finanziano le rendite correnti.",
        "obbligatorio": True,
        "dati_chiave": [
            ("Rendita minima mensile", "CHF 1,260"),
            ("Rendita massima mensile (individuale)", "CHF 2,520"),
            ("Rendita massima mensile (coppia)", "CHF 3,780"),
            ("Aliquota totale AVS+AI+IPG", "10.6% (5.3% + 5.3%)"),
            ("Età riferimento uomini", "65 anni"),
            ("Età riferimento donne (2026)", "64 anni e 9 mesi"),
            ("Anni contribuzione per rendita intera", "44 anni"),
        ],
        "lacuna_tipica": "L'AVS copre solo il minimo vitale — spesso insufficiente per mantenere il tenore di vita.",
    },
    "2": {
        "nome": "2° Pilastro – LPP (Cassa Pensioni)",
        "icona": "🏢",
        "colore": "#27ae60",
        "obiettivo": "Mantenere il tenore di vita (1° + 2° ≈ 60% dell'ultimo salario).",
        "sistema": "Capitalizzazione individuale: ogni assicurato accumula il proprio avere.",
        "obbligatorio": True,
        "soglia_entrata": 22680,
        "deduzione_coordinamento": 26460,
        "tasso_conversione": 6.8,
        "dati_chiave": [
            ("Soglia d'entrata (salario annuo)", "CHF 22,680"),
            ("Deduzione di coordinamento", "CHF 26,460"),
            ("Tasso minimo di conversione", "6.8%"),
            ("Inizio contributi di risparmio", "25 anni"),
            ("Inizio copertura rischi", "17 anni"),
        ],
        "lacuna_tipica": "Il tasso di conversione è in calo. Molte casse pensioni rendono meno del previsto.",
    },
    "3": {
        "nome": "3° Pilastro – Previdenza Privata",
        "icona": "🏦",
        "colore": "#8e44ad",
        "obiettivo": "Colmare lacune previdenziali e ottimizzare il carico fiscale.",
        "sistema": "Risparmio volontario individuale.",
        "obbligatorio": False,
        "max_3a_dipendente_2026": 7258,
        "max_3a_indipendente_2026": 36288,
        "dati_chiave": [
            ("Max deducibile — dipendenti", "CHF 7,258 / anno"),
            ("Max deducibile — indipendenti senza 2°", "20% reddito, max CHF 36,288"),
            ("Tassazione al ritiro", "Aliquota ridotta ~7%, separatamente"),
            ("Ritiro anticipato", "Abitazione, indipendente, partenza CH, invalidità"),
            ("3b — limiti versamento", "Nessuno (vantaggi fiscali limitati)"),
        ],
        "lacuna_tipica": "Chi non versa il massimo nel 3a rinuncia a migliaia di CHF di risparmio fiscale ogni anno.",
        "confronto_banca_assicurazione": {
            "banca": {
                "pro": [
                    "Flessibile — si può ritirare prima",
                    "Nessun obbligo di versamento annuo",
                    "Cambio prodotto o banca facile",
                    "Nessun costo di gestione fisso",
                ],
                "contro": [
                    "Nessuna copertura vita/invalidità inclusa",
                    "Rendimento legato ai mercati (rischio)",
                ],
            },
            "assicurazione": {
                "pro": [
                    "Include copertura vita e/o invalidità",
                    "Versamenti garantiti in caso di invalidità",
                    "Disciplina di risparmio forzato",
                    "Rendimento minimo garantito",
                ],
                "contro": [
                    "Meno flessibile — penali per uscita anticipata",
                    "Costi di gestione più elevati",
                ],
            },
        },
    },
}

# ─────────────────────────────────────────────
# MOTORE DI RACCOMANDAZIONE
# ─────────────────────────────────────────────

def calcola_raccomandazioni(profilo: dict, lc: str = "it") -> list:
    """
    Restituisce lista di raccomandazioni ordinate per priorità.
    profilo: dict con eta, situazione, stato_civile, figli, ipoteca,
             reddito_mensile, tolleranza_rischio
    lc: language code for i18n (default 'it')
    """
    rac = []
    eta = profilo.get("eta", 35)
    situazione = profilo.get("situazione", "Dipendente")
    ha_figli = profilo.get("figli", False)
    ha_ipoteca = profilo.get("ipoteca", False)
    reddito = profilo.get("reddito_mensile", 5000)
    reddito_annuo = reddito * 12

    def p(key): return _t(key, lc)  # shortcut

    # Assicurazione Vita
    if ha_figli or ha_ipoteca:
        motivi = []
        if ha_figli:   motivi.append(p("rac_mot_figli"))
        if ha_ipoteca: motivi.append(p("rac_mot_ipoteca"))
        rac.append({
            "prodotto": p("rac_prod_vita"),
            "icona": "❤️",
            "priorita": "Alta",
            "motivo": p("rac_mot_vita").format(motivi=" + ".join(motivi)),
        })

    # Perdita di Guadagno
    if situazione == "Indipendente":
        rac.append({
            "prodotto": p("rac_prod_perdita"),
            "icona": "🤒",
            "priorita": "Alta",
            "motivo": p("rac_mot_perdita"),
        })

    # Invalidità
    avs_ai_massima = 2520 * 12
    lacuna_invalidita = max(reddito_annuo - avs_ai_massima, 0)
    if lacuna_invalidita > 0:
        rac.append({
            "prodotto": p("rac_prod_invalidita"),
            "icona": "🦽",
            "priorita": "Alta" if situazione == "Indipendente" else "Raccomandata",
            "motivo": p("rac_mot_invalidita").format(
                reddito=f"{reddito:,}", lacuna=f"{lacuna_invalidita:,.0f}"
            ),
        })

    # Infortuni (indipendenti)
    if situazione == "Indipendente":
        rac.append({
            "prodotto": p("rac_prod_infortuni"),
            "icona": "🩹",
            "priorita": "Alta",
            "motivo": p("rac_mot_infortuni"),
        })

    # RC Privata (sempre)
    rac.append({
        "prodotto": p("rac_prod_rc"),
        "icona": "🛡️",
        "priorita": "Raccomandata",
        "motivo": p("rac_mot_rc"),
    })

    # Complementare ospedaliera
    if reddito > 4500:
        rac.append({
            "prodotto": p("rac_prod_complementare"),
            "icona": "🏥",
            "priorita": "Raccomandata",
            "motivo": p("rac_mot_complementare"),
        })

    # 3° Pilastro
    max_3a = (PILASTRI["3"]["max_3a_dipendente_2026"]
              if situazione == "Dipendente"
              else PILASTRI["3"]["max_3a_indipendente_2026"])
    risparmio_fiscale = int(max_3a * 0.25)
    rac.append({
        "prodotto": p("rac_prod_3a"),
        "icona": "🏦",
        "priorita": "Raccomandata",
        "motivo": p("rac_mot_3a").format(
            max_3a=f"{max_3a:,}", risparmio=f"{risparmio_fiscale:,}"
        ),
    })

    # Revisione 2° pilastro
    if eta >= 40:
        rac.append({
            "prodotto": p("rac_prod_lpp"),
            "icona": "🏢",
            "priorita": "Raccomandata",
            "motivo": p("rac_mot_lpp").format(eta=eta),
        })

    # Ottimizzazione KK
    rac.append({
        "prodotto": p("rac_prod_kk"),
        "icona": "💊",
        "priorita": "Opzionale",
        "motivo": p("rac_mot_kk"),
    })

    return rac


def stima_premio_vita(eta: int, capitale: int = 400000) -> int:
    """Stima indicativa del premio mensile assicurazione vita per età e capitale."""
    premi_base = ASSICURAZIONI[0]["premi_per_eta"]
    eta_keys = sorted(premi_base.keys())
    eta_vicina = min(eta_keys, key=lambda x: abs(x - eta))
    premio_base = premi_base[eta_vicina]
    return int(premio_base * capitale / 300000)
