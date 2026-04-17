# prospect_data.py — Events, networking spots & email templates for AlexFin

# ─────────────────────────────────────────────
# EVENTS DATABASE — Swiss networking / social events
# ─────────────────────────────────────────────

EVENTS = [
    # ── ZURICH ──
    {"city": "Zürich", "name": "BNI Zürich Metropolis", "type": "Networking", "frequency": "Settimanale",
     "audience": "PMI, liberi professionisti", "desc": "Colazione di networking settimanale con presentazioni incrociate e referral strutturati.",
     "url": "https://bni.ch", "icon": "🤝"},
    {"city": "Zürich", "name": "IHK Zürich — Business Lunch", "type": "Camera di Commercio", "frequency": "Mensile",
     "audience": "Dirigenti, manager, imprenditori", "desc": "Pranzo con speaker ospiti su temi economici, finanza e mercato svizzero.",
     "url": "https://www.zurichihk.ch", "icon": "🏛️"},
    {"city": "Zürich", "name": "Startup Zurich Meetup", "type": "Startup & Tech", "frequency": "Mensile",
     "audience": "Fondatori, investitori, manager tech", "desc": "Incontri informali tra startup e imprese tech nella Greater Zurich Area.",
     "url": "https://www.meetup.com/startupzurich", "icon": "🚀"},
    {"city": "Zürich", "name": "Rotary Club Zürich", "type": "Rotary", "frequency": "Settimanale",
     "audience": "Professionisti senior, imprenditori", "desc": "Club Rotary storico di Zurigo. Pranzi settimanali con speaker di alto profilo.",
     "url": "https://rotaryzurich.ch", "icon": "🔵"},
    {"city": "Zürich", "name": "Expat Professionals Zürich", "type": "Expat Network", "frequency": "Mensile",
     "audience": "Expat, professionisti internazionali", "desc": "Networking per professionisti internazionali e famiglie expat a Zurigo.",
     "url": "https://internations.org/zurich", "icon": "🌍"},
    {"city": "Zürich", "name": "Swiss Finance Breakfast", "type": "Finance", "frequency": "Trimestrale",
     "audience": "Manager finanziari, consulenti, banche", "desc": "Colazione esclusiva per professionisti del settore finanziario svizzero.",
     "url": "https://swissfinance.ch", "icon": "💼"},
    {"city": "Zürich", "name": "WEF Alumni Network Zürich", "type": "Elite Networking", "frequency": "Mensile",
     "audience": "Alumni WEF, C-suite, opinion leaders", "desc": "Network di ex-partecipanti del World Economic Forum basati a Zurigo.",
     "url": "https://weforum.org", "icon": "🌐"},
    {"city": "Zürich", "name": "Lions Club Zürich", "type": "Lions", "frequency": "Mensile",
     "audience": "Professionisti, imprenditori locali", "desc": "Associazione internazionale Lions — attività di networking e beneficenza.",
     "url": "https://lions.ch", "icon": "🦁"},

    # ── LUCERNE ──
    {"city": "Luzern", "name": "BNI Luzern Panorama", "type": "Networking", "frequency": "Settimanale",
     "audience": "PMI, artigiani, liberi professionisti", "desc": "Capitolo BNI attivo a Lucerna con oltre 30 membri professionali.",
     "url": "https://bni.ch", "icon": "🤝"},
    {"city": "Luzern", "name": "IHK Zentralschweiz", "type": "Camera di Commercio", "frequency": "Mensile",
     "audience": "Imprenditori Svizzera Centrale", "desc": "Camera di Commercio della Svizzera Centrale — eventi B2B e formazione.",
     "url": "https://www.ihz.ch", "icon": "🏛️"},
    {"city": "Luzern", "name": "Rotary Club Luzern", "type": "Rotary", "frequency": "Settimanale",
     "audience": "Professionisti senior, medici, avvocati", "desc": "Club Rotary di Lucerna, fondato nel 1924. Luogo ideale per networking d'élite.",
     "url": "https://rotary.ch", "icon": "🔵"},
    {"city": "Luzern", "name": "Luzern Business Network", "type": "Networking", "frequency": "Bimestrale",
     "audience": "PMI e aziende locali", "desc": "Aperitivo networking per imprenditori e manager della regione di Lucerna.",
     "url": "https://luzern.com/business", "icon": "🍷"},
    {"city": "Luzern", "name": "KMU Luzern Events", "type": "PMI", "frequency": "Mensile",
     "audience": "Proprietari PMI, artigiani", "desc": "Associazione PMI del cantone di Lucerna — eventi di aggiornamento e networking.",
     "url": "https://kmu.org", "icon": "⚙️"},

    # ── WINTERTHUR ──
    {"city": "Winterthur", "name": "BNI Winterthur", "type": "Networking", "frequency": "Settimanale",
     "audience": "PMI, consulenti, artigiani", "desc": "Capitolo BNI di Winterthur — colazioni settimanali per generare referral.",
     "url": "https://bni.ch", "icon": "🤝"},
    {"city": "Winterthur", "name": "Wirtschaftsforum Winterthur", "type": "Forum Economico", "frequency": "Annuale",
     "audience": "CEO, manager, imprenditori regionali", "desc": "Forum economico annuale della città di Winterthur con 300+ partecipanti.",
     "url": "https://www.winterthur.ch/wirtschaft", "icon": "📊"},
    {"city": "Winterthur", "name": "Rotary Club Winterthur", "type": "Rotary", "frequency": "Settimanale",
     "audience": "Professionisti stabiliti, imprenditori", "desc": "Club Rotary storico di Winterthur, molto attivo nel territorio.",
     "url": "https://rotary.ch", "icon": "🔵"},
    {"city": "Winterthur", "name": "Technopark Winterthur Events", "type": "Startup & Tech", "frequency": "Mensile",
     "audience": "Startup, ingegneri, innovatori", "desc": "Ecosystem tecnologico e manifatturiero — eventi per innovatori e imprenditori tech.",
     "url": "https://www.technopark-winterthur.ch", "icon": "🏭"},

    # ── ST. GALLEN ──
    {"city": "St. Gallen", "name": "IHK St.Gallen-Appenzell", "type": "Camera di Commercio", "frequency": "Mensile",
     "audience": "Imprenditori, manager, export", "desc": "Camera di Commercio — eventi di internazionalizzazione e networking B2B.",
     "url": "https://ihk.ch", "icon": "🏛️"},
    {"city": "St. Gallen", "name": "Alumni HSG Network", "type": "Università", "frequency": "Mensile",
     "audience": "Alumni Università di San Gallo (HSG)", "desc": "Network degli alumni dell'Università di San Gallo — una delle più prestigiose in Europa.",
     "url": "https://alumni.unisg.ch", "icon": "🎓"},
    {"city": "St. Gallen", "name": "BNI St. Gallen", "type": "Networking", "frequency": "Settimanale",
     "audience": "PMI e professionisti", "desc": "Capitolo BNI attivo nella regione di San Gallo.",
     "url": "https://bni.ch", "icon": "🤝"},

    # ── BERN ──
    {"city": "Bern", "name": "Handelskammer Bern", "type": "Camera di Commercio", "frequency": "Mensile",
     "audience": "Manager, dirigenti pubblici e privati", "desc": "Camera di Commercio di Berna — eventi con focus su politica economica e networking.",
     "url": "https://www.bern-cci.ch", "icon": "🏛️"},
    {"city": "Bern", "name": "Rotary Club Bern", "type": "Rotary", "frequency": "Settimanale",
     "audience": "Professionisti, politici, imprenditori", "desc": "Storico club Rotary di Berna, con forte presenza istituzionale.",
     "url": "https://rotary.ch", "icon": "🔵"},
    {"city": "Bern", "name": "BNI Bern City", "type": "Networking", "frequency": "Settimanale",
     "audience": "PMI, liberi professionisti", "desc": "Capitolo BNI nel centro di Berna.",
     "url": "https://bni.ch", "icon": "🤝"},

    # ── BASEL ──
    {"city": "Basel", "name": "Handelskammer beider Basel", "type": "Camera di Commercio", "frequency": "Mensile",
     "audience": "Industria farmaceutica, chimici, finanza", "desc": "Camera di Commercio di Basilea — fortissima presenza del settore pharma/chimico.",
     "url": "https://www.hkbb.ch", "icon": "🏛️"},
    {"city": "Basel", "name": "BNI Basel", "type": "Networking", "frequency": "Settimanale",
     "audience": "PMI, consulenti", "desc": "Capitolo BNI di Basilea — referral networking settimanale.",
     "url": "https://bni.ch", "icon": "🤝"},
    {"city": "Basel", "name": "Swiss Biotech Day", "type": "Industria", "frequency": "Annuale",
     "audience": "Biotech, pharma, investitori", "desc": "Evento annuale del settore biotech svizzero — ottimo per intercettare manager farmaceutici.",
     "url": "https://www.swissbiotechday.ch", "icon": "🔬"},

    # ── TICINO (home territory) ──
    {"city": "Lugano", "name": "Camera di Commercio Ticino", "type": "Camera di Commercio", "frequency": "Mensile",
     "audience": "Imprenditori ticinesi, manager", "desc": "CCIAA Ticino — evento principale per il networking istituzionale nel cantone.",
     "url": "https://www.cc-ti.ch", "icon": "🏛️"},
    {"city": "Lugano", "name": "Rotary Club Lugano", "type": "Rotary", "frequency": "Settimanale",
     "audience": "Professionisti, medici, avvocati ticinesi", "desc": "Club Rotary di Lugano — uno dei più attivi del Ticino.",
     "url": "https://rotary.ch", "icon": "🔵"},
    {"city": "Lugano", "name": "Ticino Startup Festival", "type": "Startup & Tech", "frequency": "Annuale",
     "audience": "Imprenditori, startup, investitori", "desc": "Festival delle startup ticinesi — networking con giovani imprenditori e scale-up.",
     "url": "https://www.ticino-startup.ch", "icon": "🚀"},
    {"city": "Bellinzona", "name": "BNI Ticino", "type": "Networking", "frequency": "Settimanale",
     "audience": "PMI, artigiani, professionisti ticinesi", "desc": "Capitolo BNI del Ticino — colazione settimanale di referral networking.",
     "url": "https://bni.ch", "icon": "🤝"},
]

# ─────────────────────────────────────────────
# NETWORKING SPOTS — Luoghi & associazioni permanenti
# ─────────────────────────────────────────────

NETWORKING_SPOTS = [
    {"category": "Rotary & Lions", "icon": "🔵",
     "name": "Rotary International Svizzera",
     "desc": "Oltre 300 club in tutta la Svizzera. Riunioni settimanali con professionisti affermati. Ottimo per costruire fiducia nel lungo periodo.",
     "target": "Medici, avvocati, notai, imprenditori consolidati",
     "come_entrare": "Serve una presentazione da un membro. Visita rotary.ch per trovare il club locale.",
     "url": "https://rotary.ch"},
    {"category": "Rotary & Lions", "icon": "🦁",
     "name": "Lions Clubs Svizzera",
     "desc": "Network di service e networking. Meno formale del Rotary, molto diffuso nelle città medie svizzere.",
     "target": "Imprenditori, commercianti, professionisti",
     "come_entrare": "Contatto diretto o attraverso un membro. Molto aperti a nuove adesioni.",
     "url": "https://lions.ch"},
    {"category": "Referral Networking", "icon": "🤝",
     "name": "BNI Switzerland",
     "desc": "Business Network International — struttura di referral settimanale con un solo membro per categoria professionale per capitolo. Altissimo ROI per consulenti.",
     "target": "Consulenti, agenti assicurativi, artigiani, PMI",
     "come_entrare": "Visita come ospite gratuitamente. Sito: bni.ch",
     "url": "https://bni.ch"},
    {"category": "Camere di Commercio", "icon": "🏛️",
     "name": "IHK / Camera di Commercio Cantonale",
     "desc": "Ogni cantone ha la sua Camera di Commercio. Organizzano eventi regolari, seminari e occasioni di networking B2B.",
     "target": "Dirigenti, imprenditori, manager HR e finance",
     "come_entrare": "Iscrizione come membro (quota annua ~500-2000 CHF). Molti eventi aperti anche a non-soci.",
     "url": "https://economiesuisse.ch"},
    {"category": "Alumni University", "icon": "🎓",
     "name": "Alumni HSG (Università di San Gallo)",
     "desc": "Il network alumni HSG è uno dei più potenti in Svizzera. Molti CEO, CFO e decision maker svizzeri sono alumni HSG.",
     "target": "Manager senior, C-suite, professionisti finance",
     "come_entrare": "Partecipa agli eventi aperti. Contatto tramite LinkedIn con alumni locali.",
     "url": "https://alumni.unisg.ch"},
    {"category": "Alumni University", "icon": "🎓",
     "name": "ETH Zürich Alumni",
     "desc": "Network degli ingegneri e scienziati formati all'ETH. Forte presenza nel settore tech, farmaceutico e industriale.",
     "target": "Ingegneri, manager tech, imprenditori innovativi",
     "come_entrare": "Eventi aperti sul sito alumni.ethz.ch",
     "url": "https://alumni.ethz.ch"},
    {"category": "Professional Clubs", "icon": "💼",
     "name": "Swiss Finance Forum",
     "desc": "Community di professionisti della finanza, banche e assicurazioni. Conferenze trimestrali e networking esclusivo.",
     "target": "CFO, wealth manager, banking professionals",
     "come_entrare": "Iscrizione individuale o corporate. Invito tramite banca/assicurazione.",
     "url": "https://swissfinanceforum.ch"},
    {"category": "Professional Clubs", "icon": "🎯",
     "name": "Swiss Young Professionals Network",
     "desc": "Network per professionisti under 40. Molto attivo a Zurigo, Basilea e Ginevra. Ideale per raggiungere clienti giovani in fase di crescita patrimoniale.",
     "target": "Professionisti 28-42 anni, early career managers",
     "come_entrare": "Iscrizione online. Spesso eventi gratuiti o a basso costo.",
     "url": "https://young-professionals.ch"},
    {"category": "Expat & International", "icon": "🌍",
     "name": "InterNations Switzerland",
     "desc": "La piattaforma più grande per expat in Svizzera. Migliaia di professionisti stranieri che hanno bisogno di assicurazioni, KK e pianificazione previdenziale.",
     "target": "Expat, professionisti internazionali, famiglie straniere",
     "come_entrare": "Profilo gratuito su internations.org. Gli eventi premium costano ~20 CHF.",
     "url": "https://internations.org/switzerland"},
    {"category": "Expat & International", "icon": "🇺🇸",
     "name": "American International Club of Zurich",
     "desc": "Club per americani e internazionali residenti a Zurigo. Spesso cercano consulenti fidati per navigare il sistema svizzero.",
     "target": "Americani ed expat anglofoni, famiglie internazionali",
     "come_entrare": "Membership annuale. Sito: aicz.ch",
     "url": "https://aicz.ch"},
    {"category": "PMI & Imprenditori", "icon": "⚙️",
     "name": "SGV / USAM — Unione Svizzera Arti e Mestieri",
     "desc": "La principale associazione delle PMI svizzere. Rappresenta oltre 300.000 imprenditori. Moltissimi hanno bisogno di assicurazioni aziendali e previdenza.",
     "target": "Artigiani, commercianti, piccoli imprenditori",
     "come_entrare": "Attraverso le associazioni di categoria locali affiliate all'USAM.",
     "url": "https://www.sgv-usam.ch"},
    {"category": "PMI & Imprenditori", "icon": "🏆",
     "name": "EO Switzerland (Entrepreneurs' Organization)",
     "desc": "Organizzazione esclusiva per imprenditori con fatturato min. 1M CHF. Altissimo potere d'acquisto.",
     "target": "Imprenditori con aziende mid-size, CEO/owner",
     "come_entrare": "Solo su invito. Connetti su LinkedIn con membri EO locali.",
     "url": "https://eonetwork.org/switzerland"},
]

# ─────────────────────────────────────────────
# EMAIL TEMPLATES
# ─────────────────────────────────────────────

EMAIL_TEMPLATES = {
    "fredda_presentazione": {
        "nome": "🤝 Presentazione a freddo",
        "subject": "Come posso aiutarla a ottimizzare la sua protezione finanziaria in Svizzera",
        "tags": ["Nuovo contatto", "Introduzione"],
        "body": """Gentile {nome},

Mi chiamo {mittente} e sono consulente assicurativo e pianificatore patrimoniale certificato presso SVAG, operante nel Canton {cantone}.

Mi è capitato di incrociarla a {dove_conosciuto} e ho ritenuto potesse valere la pena di approfondire come possiamo supportarla.

Nella mia attività mi occupo di:

  • Ottimizzazione della Krankenkasse (spesso si risparmia tra 800–3'000 CHF/anno)
  • Pianificazione del 3° pilastro con vantaggi fiscali immediati
  • Protezione del reddito in caso di malattia o invalidità
  • Assicurazione vita e protezione familiare

Sarei lieto di offrirle una consulenza gratuita di 30 minuti, senza impegno, per analizzare la sua situazione attuale.

Quando sarebbe disponibile per un breve incontro (in persona o videochiamata)?

Cordiali saluti,
{mittente}
Consulente Assicurativo & Pianificatore Patrimoniale
SVAG — {cantone}
📞 {telefono}
📧 {email_mittente}""",
        "report_html": """<h3>💡 Perché ottimizzare le sue assicurazioni svizzere?</h3>
<table style="width:100%;border-collapse:collapse;font-size:14px">
<tr style="background:#f8f9fc"><td style="padding:10px;font-weight:700">Krankenkasse</td><td style="padding:10px">Cambiando modello + franchigia si risparmia in media <strong>CHF 1'200–2'400/anno</strong></td></tr>
<tr><td style="padding:10px;font-weight:700">3° Pilastro</td><td style="padding:10px">Versando CHF 7'258/anno si risparmiano in media <strong>CHF 1'800 di imposte</strong></td></tr>
<tr style="background:#f8f9fc"><td style="padding:10px;font-weight:700">Assicurazione Vita</td><td style="padding:10px">A 35 anni: da <strong>CHF 45/mese</strong> per un capitale di CHF 400'000</td></tr>
<tr><td style="padding:10px;font-weight:700">Perdita di Guadagno</td><td style="padding:10px">Copre l'80% del salario in caso di malattia lunga. Indispensabile per i <strong>lavoratori indipendenti</strong></td></tr>
</table>"""
    },

    "follow_up_evento": {
        "nome": "📅 Follow-up dopo evento",
        "subject": "Piacere di averla incontrata a {evento} — un pensiero su quanto discusso",
        "tags": ["Post-evento", "Warm lead"],
        "body": """Gentile {nome},

È stato un piacere incontrarla durante {evento}.

Come concordato, le invio alcune informazioni sulla sua situazione specifica. In base a quanto mi ha condiviso, ho preparato una breve analisi dei principali ambiti dove potrebbe ottimizzare la sua posizione finanziaria in Svizzera.

In allegato trova un mini-report con:
  ✅ Stima del risparmio sulla Krankenkasse per il suo profilo
  ✅ Vantaggi fiscali del 3° pilastro nella sua fascia di reddito
  ✅ Un'analisi della lacuna previdenziale tipica per la sua situazione

Sarò a Zurigo/nella sua zona il {data_disponibilita} — sarebbe disponibile per un caffè di 30 minuti?

A presto,
{mittente}
{email_mittente} | {telefono}""",
        "report_html": """<h3>📊 Mini-Analisi Personalizzata — {nome}</h3>
<p style="color:#666;font-size:13px">Analisi indicativa basata sulle informazioni condivise. Non costituisce consulenza legale o fiscale.</p>
<div style="background:#eafaf1;padding:14px;border-radius:8px;border-left:4px solid #27ae60;margin:12px 0">
<strong>✅ Risparmio KK stimato:</strong> CHF 800–2'400/anno con modello Telmed/HMO + franchigia CHF 2'500
</div>
<div style="background:#fef9e7;padding:14px;border-radius:8px;border-left:4px solid #f39c12;margin:12px 0">
<strong>💡 3° Pilastro:</strong> Versando il massimo (CHF 7'258) risparmia ~CHF 1'800 di imposte ogni anno
</div>
<div style="background:#fde8e8;padding:14px;border-radius:8px;border-left:4px solid #c0392b;margin:12px 0">
<strong>⚠️ Lacuna previdenziale:</strong> Senza il 3° pilastro, alla pensione mancheranno circa CHF 300'000 rispetto all'obiettivo del 70% del reddito attuale
</div>"""
    },

    "risparmio_krankenkasse": {
        "nome": "💊 Risparmio Krankenkasse",
        "subject": "Sta pagando troppo per la sua Krankenkasse? Analizziamo insieme",
        "tags": ["KK", "Risparmio immediato"],
        "body": """Gentile {nome},

Le scrivo perché molti miei clienti scoprono di stare pagando centinaia di franchi in più del necessario per la loro cassa malati.

Il sistema svizzero offre strumenti legali per ridurre significativamente il premio mensile:

  💡 Modello Telmed o Medico di Famiglia: -15% a -25%
  💡 Franchigia CHF 2'500 (invece di CHF 300): ulteriore -30%
  💡 Totale risparmio possibile: CHF 800 – 3'000/anno

Per un lavoratore sano di 35 anni a {cantone}, il risparmio medio è di circa CHF 1'500/anno — senza rinunciare a nessuna copertura.

Le offro un'analisi gratuita e personalizzata della sua situazione KK attuale.

Basta rispondere a questa email con il suo premio mensile attuale e la franchigia — le preparo una stima in meno di 24h.

Cordiali saluti,
{mittente}
Consulente SVAG | {cantone}
{telefono}""",
        "report_html": """<h3>💊 Come funziona il risparmio Krankenkasse</h3>
<table style="width:100%;border-collapse:collapse;font-size:14px;margin-top:10px">
<thead><tr style="background:#1e2235;color:white"><th style="padding:10px;text-align:left">Combinazione</th><th style="padding:10px">Premio/mese stimato</th><th style="padding:10px">Risparmio/anno</th></tr></thead>
<tbody>
<tr><td style="padding:10px">Standard + Franchigia CHF 300</td><td style="padding:10px;text-align:center"><strong>CHF 468</strong></td><td style="padding:10px;text-align:center">—</td></tr>
<tr style="background:#f8f9fc"><td style="padding:10px">Medico di famiglia + CHF 1'500</td><td style="padding:10px;text-align:center"><strong>CHF 331</strong></td><td style="padding:10px;text-align:center;color:#27ae60"><strong>CHF 1'644</strong></td></tr>
<tr><td style="padding:10px">Telmed + CHF 2'500</td><td style="padding:10px;text-align:center"><strong>CHF 295</strong></td><td style="padding:10px;text-align:center;color:#27ae60"><strong>CHF 2'076</strong></td></tr>
<tr style="background:#f8f9fc"><td style="padding:10px">HMO + CHF 2'500</td><td style="padding:10px;text-align:center"><strong>CHF 268</strong></td><td style="padding:10px;text-align:center;color:#27ae60"><strong>CHF 2'400</strong></td></tr>
</tbody></table>
<p style="font-size:11px;color:#888;margin-top:8px">*Premi indicativi per adulto 30 anni, Canton Ticino 2026. Ogni situazione va valutata individualmente.</p>"""
    },

    "terzo_pilastro": {
        "nome": "🏛️ Vantaggi 3° Pilastro",
        "subject": "Sta perdendo CHF 1'800 di detrazioni fiscali ogni anno?",
        "tags": ["Fiscalità", "3° Pilastro", "Risparmio"],
        "body": """Gentile {nome},

In Svizzera, il 3° pilastro è uno degli strumenti più potenti per risparmiare sia sulle imposte oggi, sia per costruire un patrimonio per la pensione.

Ecco i numeri per lei:

  ✅ Versamento massimo 2026: CHF 7'258 (lavoratore dipendente)
  ✅ Risparmio fiscale stimato: CHF 1'600 – 2'200/anno (aliquota 22-30%)
  ✅ Capitale accumulato in 20 anni (con rendimento 3.5%): ~CHF 210'000
  ✅ Tassazione al ritiro: solo ~7% sul capitale totale

In pratica: ogni franco versato nel 3° pilastro vale 1.20–1.30 CHF grazie al risparmio fiscale immediato.

Esistono due tipologie: bancario (più flessibile) e assicurativo (include coperture vita e invalidità).

Le organizzo una simulazione personalizzata completamente gratuita?

Con stima,
{mittente}
{email_mittente} | {telefono}""",
        "report_html": """<h3>🏛️ Il Potere del 3° Pilastro — Simulazione</h3>
<div style="display:flex;gap:16px;margin:12px 0;flex-wrap:wrap">
<div style="flex:1;background:#eafaf1;border-radius:10px;padding:16px;text-align:center;min-width:130px">
<div style="font-size:1.8rem;font-weight:800;color:#27ae60">CHF 7'258</div>
<div style="font-size:12px;color:#555;margin-top:4px">Versamento max 2026</div>
</div>
<div style="flex:1;background:#fef9e7;border-radius:10px;padding:16px;text-align:center;min-width:130px">
<div style="font-size:1.8rem;font-weight:800;color:#f39c12">~CHF 1'800</div>
<div style="font-size:12px;color:#555;margin-top:4px">Risparmio fiscale/anno</div>
</div>
<div style="flex:1;background:#fde8e8;border-radius:10px;padding:16px;text-align:center;min-width:130px">
<div style="font-size:1.8rem;font-weight:800;color:#c0392b">CHF 210'000</div>
<div style="font-size:12px;color:#555;margin-top:4px">Capitale in 20 anni (3.5%)</div>
</div>
</div>
<p style="font-size:12px;color:#888">Simulazione indicativa per un dipendente con reddito annuo CHF 75'000 e aliquota fiscale del 25%.</p>"""
    },

    "check_up_gratuito": {
        "nome": "🔍 Check-up finanziario gratuito",
        "subject": "Offerta esclusiva: Check-up finanziario gratuito — 30 minuti che possono valere migliaia di CHF",
        "tags": ["Offerta", "Check-up", "Lead nurturing"],
        "body": """Gentile {nome},

Le propongo qualcosa di concreto: un check-up finanziario gratuito di 30 minuti.

In questa sessione analizziamo insieme:

  🔍 La sua situazione KK attuale (e quanto potrebbe risparmiare)
  🔍 Il suo gap previdenziale per la pensione
  🔍 Le coperture assicurative che ha (e quelle che mancano)
  🔍 Se il suo 3° pilastro è ottimizzato o se perde detrazioni fiscali

Non c'è nessun obbligo. Al termine riceve un report scritto con i punti di attenzione principali — che decida di procedere con noi o meno.

Questo check-up ha un valore reale di CHF 250, ma lo offro gratuitamente a {numero_posti} persone questo mese.

Interessato/a? Mi risponda con due slot di disponibilità e fissiamo la chiamata.

A presto,
{mittente}
Consulente SVAG | Pianificatore Patrimoniale
{telefono} | {email_mittente}""",
        "report_html": """<h3>🔍 Cosa include il Check-up Finanziario Gratuito</h3>
<ul style="list-style:none;padding:0;margin:0">
<li style="padding:10px 0;border-bottom:1px solid #f0f0f0"><span style="color:#27ae60;font-weight:700">✓</span> Analisi Krankenkasse — confronto con le opzioni ottimali per il suo profilo</li>
<li style="padding:10px 0;border-bottom:1px solid #f0f0f0"><span style="color:#27ae60;font-weight:700">✓</span> Calcolo della lacuna previdenziale (gap tra pensione stimata e obiettivo 70%)</li>
<li style="padding:10px 0;border-bottom:1px solid #f0f0f0"><span style="color:#27ae60;font-weight:700">✓</span> Verifica coperture assicurative (vita, invalidità, perdita di guadagno)</li>
<li style="padding:10px 0;border-bottom:1px solid #f0f0f0"><span style="color:#27ae60;font-weight:700">✓</span> Ottimizzazione fiscale 3° pilastro</li>
<li style="padding:10px 0"><span style="color:#27ae60;font-weight:700">✓</span> Report scritto con raccomandazioni personalizzate</li>
</ul>
<div style="background:#fde8e8;padding:12px;border-radius:8px;margin-top:16px;font-size:13px">
<strong>⏱️ Durata:</strong> 30 minuti · <strong>📍 Modalità:</strong> In persona o videochiamata · <strong>💰 Costo:</strong> <span style="color:#c0392b;font-weight:700">Gratuito</span>
</div>"""
    },
}

# ─────────────────────────────────────────────
# CITIES & EVENT TYPES for filters
# ─────────────────────────────────────────────

CITIES = sorted(set(e["city"] for e in EVENTS))
EVENT_TYPES = sorted(set(e["type"] for e in EVENTS))
SPOT_CATEGORIES = sorted(set(s["category"] for s in NETWORKING_SPOTS))
