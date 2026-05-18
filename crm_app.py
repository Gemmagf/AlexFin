"""
AlexFin CRM — App standalone per a Alex Bevilacqua (SVAG)
Execució:  /usr/bin/python3 crm_app.py
URL:       http://localhost:8051  ·  Login: alex / go

Bugs corregits vs v1:
  - Race condition btn-new-client (clientside vs Python callback eliminat)
  - list-new-btn no era sempre al DOM → reemplaçat per list-new-trigger
  - Modal no es tancava al guardar → fix allow_duplicate
  - Afegit i18n complet: IT / DE / FR / EN / CA
"""
import os, json
from datetime import date, timedelta
import dash, dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback, ctx, ALL
from flask import Flask, session, redirect, request, render_template_string

PORT      = int(os.environ.get("CRM_PORT", 8051))
AUTH_USER = os.environ.get("AUTH_USER", "alex")
AUTH_PASS = os.environ.get("AUTH_PASS", "go")
CRM_FILE  = os.path.join(os.path.dirname(__file__), "clienti.json")

PIPELINE_STAGES = [
    ("lead",       "Lead",       "#3b82f6"),
    ("contattato", "Contattato", "#f59e0b"),
    ("riunione",   "Riunione",   "#8b5cf6"),
    ("proposta",   "Proposta",   "#f97316"),
    ("chiuso",     "Chiuso",     "#22c55e"),
    ("perso",      "Perso",      "#ef4444"),
]
STAGE_KEYS   = [s[0] for s in PIPELINE_STAGES]
STAGE_COLORS = {s[0]: s[2] for s in PIPELINE_STAGES}

CANTONS = ["Zürich","Bern","Luzern","Uri","Schwyz","Obwalden","Nidwalden","Glarus","Zug",
           "Fribourg","Solothurn","Basel-Stadt","Basel-Landschaft","Schaffhausen",
           "Appenzell AR","Appenzell AI","St. Gallen","Graubünden","Aargau","Thurgau",
           "Ticino","Vaud","Valais","Neuchâtel","Genève","Jura"]

# ── CATALOGO PRODOTTI ─────────────────────────────────────────────────────────
PRODUCTS = [
  {"id":"3p","icon":"🏦",
   "name":{"it":"3° Pilastro","de":"Säule 3a","fr":"3e Pilier","en":"3rd Pillar","ca":"3r Pilar"},
   "desc":{"it":"Risparmio previdenziale privato con deducibilità fiscale: CHF 7'056/anno (dipendenti) · CHF 35'280 (indipendenti). L'effetto composto premia chi inizia presto — 30 anni vs 35 anni = capitale 50% maggiore a 65.",
           "de":"Private Altersvorsorge mit Steuerabzug: CHF 7'056/Jahr (Angest.) · CHF 35'280 (Selbst.). Frühzeitig anfangen = 50% mehr Kapital dank Zinseszins.",
           "fr":"Épargne-retraite privée déductible: CHF 7'056/an (salariés) · CHF 35'280 (ind.). Commencer à 30 vs 35 ans = 50% de capital en plus à 65.",
           "en":"Private pension savings, tax-deductible: CHF 7,056/year (employees) · CHF 35,280 (self-employed). Starting at 30 vs 35 = 50% more capital at 65.",
           "ca":"Estalvi de previsió deduïble: CHF 7.056/any (assalariats) · CHF 35.280 (autònoms). Iniciar aviat = 50% més capital a 65 anys."},
   "fit": lambda c: c.get("eta",99)<65},
  {"id":"vita","icon":"💚",
   "name":{"it":"Assicurazione Vita","de":"Lebensversicherung","fr":"Assurance Vie","en":"Life Insurance","ca":"Assegurança de Vida"},
   "desc":{"it":"Protezione del reddito familiare in caso di decesso: rischio puro (term life) o risparmio misto. Indispensabile con figli o ipoteca in corso.",
           "de":"Absicherung des Familieneinkommens im Todesfall: Risikovs. oder gemischte Vers. Unerlässlich mit Kindern oder Hypothek.",
           "fr":"Protection du revenu familial au décès: risque pur ou épargne mixte. Indispensable avec enfants ou hypothèque.",
           "en":"Family income protection on death: pure risk (term) or savings component (mixed). Essential with children or mortgage.",
           "ca":"Protecció dels ingressos familiars en defunció: risc pur o mixta. Essencial amb fills o hipoteca."},
   "fit": lambda c: bool(c.get("figli")) or bool(c.get("ipoteca"))},
  {"id":"ai","icon":"🛡️",
   "name":{"it":"Assicurazione Invalidità","de":"Erwerbsunfähigkeitsvers.","fr":"Assurance Invalidité","en":"Disability Insurance","ca":"Assegurança Invalidesa"},
   "desc":{"it":"Integra l'AI statale per mantenere il tenore di vita in caso di incapacità parziale o totale. Critica per indipendenti: nessuna copertura automatica.",
           "de":"Ergänzt staatliche IV bei Erwerbsunfähigkeit. Für Selbstständige kritisch — keine automatische Absicherung.",
           "fr":"Complète l'AI étatique en cas d'incapacité. Critique pour les indépendants (pas de couverture automatique).",
           "en":"Supplements state disability insurance. Critical for self-employed — no automatic coverage.",
           "ca":"Complementa l'AI estatal en cas d'incapacitat. Crític per a autònoms (cap cobertura automàtica)."},
   "fit": lambda c: c.get("situazione") in ["Dipendente","Indipendente"]},
  {"id":"ipoteca","icon":"🏠",
   "name":{"it":"Pianificazione Ipotecaria","de":"Hypothekenplanung","fr":"Planification Hypothécaire","en":"Mortgage Planning","ca":"Planificació Hipotecària"},
   "desc":{"it":"Strutturazione del finanziamento: fisso vs SARON, amortamento indiretto via 3° pilastro (doppio vantaggio fiscale), negoziazione con più banche.",
           "de":"Finanzierungsstruktur: fest vs. SARON, indirekte Amortisation über Säule 3a (doppelter Steuerbonus), Vergleich mehrerer Banken.",
           "fr":"Structure de financement: fixe vs SARON, amortissement indirect via 3e pilier (double avantage fiscal), comparaison de banques.",
           "en":"Financing structure: fixed vs SARON, indirect amortization via pillar 3a (double tax benefit), comparing banks.",
           "ca":"Estructura de finançament: fix vs SARON, amortització indirecta via 3r pilar (doble avantatge fiscal)."},
   "fit": lambda c: bool(c.get("ipoteca")) or c.get("eta",99)<55},
  {"id":"lpp","icon":"🏢",
   "name":{"it":"Ottimizzazione LPP","de":"BVG-Optimierung","fr":"Optimisation LPP","en":"Pension Fund Optim.","ca":"Optimització LPP"},
   "desc":{"it":"Acquisti volontari nella cassa pensione (deducibili): massimizza il capitale e riduce le tasse oggi. Riscatto anticipato per immobile. Rendita vs. capitale.",
           "de":"Freiwillige PK-Einkäufe (steuerabzugsfähig): Kapital maximieren, Steuern senken. Vorbezug für Wohneigentum. Renten- vs. Kapitalplanung.",
           "fr":"Rachats volontaires dans la CP (déductibles): maximiser le capital, réduire les impôts. Retrait anticipé pour logement.",
           "en":"Voluntary pension fund purchases (tax-deductible): maximize capital, reduce taxes. Early withdrawal for property.",
           "ca":"Compres voluntàries a la CP (deduïbles): maximitzar capital i reduir impostos. Retir anticipat per immoble."},
   "fit": lambda c: c.get("situazione")=="Dipendente" and c.get("eta",0)>25},
  {"id":"hausrat","icon":"🏡",
   "name":{"it":"Hausrat + RC Privata","de":"Hausrat + Privathaftpflicht","fr":"Ménage + RC Privée","en":"Household + Liability","ca":"Llar + RC Privada"},
   "desc":{"it":"Assicurazione economica domestica (furto, incendio, danni acqua) + responsabilità civile privata. Pacchetto base essenziale per tutti. Premi CHF 150-350/anno.",
           "de":"Hausrat (Diebstahl, Brand, Wasser) + Privathaftpflicht. Basispaket für alle. Prämien CHF 150-350/Jahr.",
           "fr":"Ménage (vol, incendie, eau) + RC privée. Paquet de base pour tous. Primes CHF 150-350/an.",
           "en":"Household (theft, fire, water) + private liability. Essential for all. Premiums CHF 150-350/year.",
           "ca":"Llar (robatori, incendi, aigua) + RC privada. Bàsic per a tothom. Primes CHF 150-350/any."},
   "fit": lambda c: True},
  {"id":"malattia","icon":"🏥",
   "name":{"it":"Ottimizzazione Cassa Malati","de":"Krankenkassen-Optim.","fr":"Optim. Assur. Maladie","en":"Health Insurance Optim.","ca":"Optim. Assegurança Mèdica"},
   "desc":{"it":"Revisione modello LAMal (HMO/Telmed/standard) + franchigia ottimale. Risparmio medio CHF 300-800/anno mantenendo la copertura adeguata.",
           "de":"KVG-Modell (HMO/Telmed/standard) + optimale Franchise. Durchschnittliche Ersparnis CHF 300-800/Jahr.",
           "fr":"Modèle LAMal (HMO/Telmed/standard) + franchise optimale. Économie moyenne CHF 300-800/an.",
           "en":"LAMal model (HMO/Telmed/standard) + optimal deductible. Average savings CHF 300-800/year.",
           "ca":"Model LAMal (HMO/Telmed/standard) + franquícia òptima. Estalvi mitjà CHF 300-800/any."},
   "fit": lambda c: True},
]

# ── I18N ────────────────────────────────────────────────────────────────────
_T = {
    "nav_dash":       {"it":"📊 Dashboard","de":"📊 Übersicht","fr":"📊 Tableau","en":"📊 Dashboard","ca":"📊 Tauler"},
    "nav_clients":    {"it":"👥 Clienti","de":"👥 Kunden","fr":"👥 Clients","en":"👥 Clients","ca":"👥 Clients"},
    "nav_pipeline":   {"it":"📋 Pipeline","de":"📋 Pipeline","fr":"📋 Pipeline","en":"📋 Pipeline","ca":"📋 Pipeline"},
    "nav_agenda":     {"it":"📅 Agenda","de":"📅 Agenda","fr":"📅 Agenda","en":"📅 Agenda","ca":"📅 Agenda"},
    "nav_products":   {"it":"📦 Prodotti","de":"📦 Produkte","fr":"📦 Produits","en":"📦 Products","ca":"📦 Productes"},
    "nav_new":        {"it":"＋ Nuovo","de":"＋ Neu","fr":"＋ Nouveau","en":"＋ New","ca":"＋ Nou"},
    "nav_logout":     {"it":"⎋ Esci","de":"⎋ Abmelden","fr":"⎋ Déconn.","en":"⎋ Logout","ca":"⎋ Surt"},
    "dash_title":     {"it":"Panoramica CRM","de":"CRM Übersicht","fr":"Aperçu CRM","en":"CRM Overview","ca":"Resum CRM"},
    "dash_updated":   {"it":"Aggiornato","de":"Aktualisiert","fr":"Mis à jour","en":"Updated","ca":"Actualitzat"},
    "kpi_total":      {"it":"Clienti totali","de":"Kunden gesamt","fr":"Clients totaux","en":"Total clients","ca":"Clients totals"},
    "kpi_active":     {"it":"Attivi","de":"Aktiv","fr":"Actifs","en":"Active","ca":"Actius"},
    "kpi_closed":     {"it":"Chiusi ✅","de":"Abgeschl. ✅","fr":"Conclus ✅","en":"Closed ✅","ca":"Tancats ✅"},
    "kpi_lost":       {"it":"Persi","de":"Verloren","fr":"Perdus","en":"Lost","ca":"Perduts"},
    "kpi_followup":   {"it":"Follow-up oggi","de":"Follow-up heute","fr":"Follow-up auj.","en":"Follow-up today","ca":"Follow-up avui"},
    "kpi_pip_val":    {"it":"Valore pipeline","de":"Pipeline-Wert","fr":"Valeur pipeline","en":"Pipeline value","ca":"Valor pipeline"},
    "kpi_chi_val":    {"it":"Chiusi","de":"Abgeschl.","fr":"Conclus","en":"Closed","ca":"Tancats"},
    "dash_funnel":    {"it":"📊 Pipeline funnel","de":"📊 Pipeline-Trichter","fr":"📊 Entonnoir","en":"📊 Pipeline funnel","ca":"📊 Embut pipeline"},
    "dash_week_fu":   {"it":"📅 Follow-up settimana","de":"📅 Follow-up Woche","fr":"📅 Suivis semaine","en":"📅 Follow-ups week","ca":"📅 Seguiments setmana"},
    "dash_no_fu":     {"it":"Nessun follow-up in agenda.","de":"Kein Follow-up geplant.","fr":"Aucun suivi prévu.","en":"No follow-ups scheduled.","ca":"Cap seguiment programat."},
    "dash_recent":    {"it":"🕐 Clienti recenti","de":"🕐 Aktuelle Kunden","fr":"🕐 Clients récents","en":"🕐 Recent clients","ca":"🕐 Clients recents"},
    "th_name":        {"it":"Nome","de":"Name","fr":"Nom","en":"Name","ca":"Nom"},
    "th_stage":       {"it":"Fase","de":"Phase","fr":"Phase","en":"Stage","ca":"Fase"},
    "th_canton":      {"it":"Cantone","de":"Kanton","fr":"Canton","en":"Canton","ca":"Cantó"},
    "th_situ":        {"it":"Situazione","de":"Beruf","fr":"Situation","en":"Employment","ca":"Situació"},
    "th_income":      {"it":"Reddito/M","de":"Einkommen/M","fr":"Revenu/M","en":"Income/M","ca":"Ingressos/M"},
    "th_fu":          {"it":"Follow-up","de":"Follow-up","fr":"Suivi","en":"Follow-up","ca":"Seguiment"},
    "th_product":     {"it":"Prodotto","de":"Produkt","fr":"Produit","en":"Product","ca":"Producte"},
    "th_date":        {"it":"Data","de":"Datum","fr":"Date","en":"Date","ca":"Data"},
    "list_title":     {"it":"👥 Clienti","de":"👥 Kunden","fr":"👥 Clients","en":"👥 Clients","ca":"👥 Clients"},
    "list_in_crm":    {"it":"nel CRM","de":"im CRM","fr":"dans le CRM","en":"in CRM","ca":"al CRM"},
    "list_shown":     {"it":"mostrati","de":"angezeigt","fr":"affichés","en":"shown","ca":"mostrats"},
    "search_ph":      {"it":"🔍  Cerca nome, email, prodotto…","de":"🔍  Suche Name, E-Mail, Produkt…","fr":"🔍  Chercher nom, e-mail, produit…","en":"🔍  Search name, email, product…","ca":"🔍  Cerca nom, email, producte…"},
    "all_stages":     {"it":"Tutte le fasi","de":"Alle Phasen","fr":"Toutes phases","en":"All stages","ca":"Totes les fases"},
    "all_cantons":    {"it":"Tutti i cantoni","de":"Alle Kantone","fr":"Tous cantons","en":"All cantons","ca":"Tots els cantons"},
    "no_clients":     {"it":"Nessun cliente trovato.","de":"Keine Kunden gefunden.","fr":"Aucun client trouvé.","en":"No clients found.","ca":"Cap client trobat."},
    "pipeline_title": {"it":"📋 Pipeline","de":"📋 Pipeline","fr":"📋 Pipeline","en":"📋 Pipeline","ca":"📋 Pipeline"},
    "agenda_title":   {"it":"📅 Agenda Follow-up","de":"📅 Follow-up Agenda","fr":"📅 Agenda suivis","en":"📅 Follow-up Agenda","ca":"📅 Agenda seguiments"},
    "agenda_today":   {"it":"Oggi","de":"Heute","fr":"Aujourd'hui","en":"Today","ca":"Avui"},
    "ag_past":        {"it":"🔴 Scaduti","de":"🔴 Überfällig","fr":"🔴 En retard","en":"🔴 Overdue","ca":"🔴 Vençuts"},
    "ag_today":       {"it":"🟡 Oggi","de":"🟡 Heute","fr":"🟡 Aujourd'hui","en":"🟡 Today","ca":"🟡 Avui"},
    "ag_week":        {"it":"🔵 Questa settimana","de":"🔵 Diese Woche","fr":"🔵 Cette semaine","en":"🔵 This week","ca":"🔵 Aquesta setmana"},
    "ag_soon":        {"it":"⬜ Prossimamente","de":"⬜ Demnächst","fr":"⬜ Prochainement","en":"⬜ Soon","ca":"⬜ Properament"},
    "ag_no_fu":       {"it":"⚠️ Senza follow-up","de":"⚠️ Ohne Follow-up","fr":"⚠️ Sans suivi","en":"⚠️ No follow-up","ca":"⚠️ Sense seguiment"},
    "modal_new":      {"it":"➕ Nuovo cliente","de":"➕ Neuer Kunde","fr":"➕ Nouveau client","en":"➕ New client","ca":"➕ Nou client"},
    "modal_edit":     {"it":"✏️ Modifica","de":"✏️ Bearbeiten","fr":"✏️ Modifier","en":"✏️ Edit","ca":"✏️ Edita"},
    "btn_cancel":     {"it":"Annulla","de":"Abbrechen","fr":"Annuler","en":"Cancel","ca":"Cancel·la"},
    "btn_save":       {"it":"💾 Salva","de":"💾 Speichern","fr":"💾 Enregistrer","en":"💾 Save","ca":"💾 Desa"},
    "btn_delete":     {"it":"🗑️ Elimina","de":"🗑️ Löschen","fr":"🗑️ Supprimer","en":"🗑️ Delete","ca":"🗑️ Elimina"},
    "saved_ok":       {"it":"✅ Salvato!","de":"✅ Gespeichert!","fr":"✅ Enregistré!","en":"✅ Saved!","ca":"✅ Desat!"},
    "err_name":       {"it":"⚠️ Inserisci il nome.","de":"⚠️ Name erforderlich.","fr":"⚠️ Saisissez le nom.","en":"⚠️ Enter a name.","ca":"⚠️ Introduïu el nom."},
    "del_title":      {"it":"Conferma eliminazione","de":"Löschung bestätigen","fr":"Confirmer suppression","en":"Confirm deletion","ca":"Confirma l'eliminació"},
    "del_text":       {"it":"Eliminare «{n}»? Operazione irreversibile.",
                       "de":"«{n}» löschen? Nicht rückgängig machbar.",
                       "fr":"Supprimer «{n}»? Action irréversible.",
                       "en":"Delete «{n}»? This cannot be undone.",
                       "ca":"Eliminar «{n}»? Acció irreversible."},
    "sec_personal":   {"it":"Dati personali","de":"Persönliche Daten","fr":"Données personnelles","en":"Personal data","ca":"Dades personals"},
    "sec_pipeline":   {"it":"Pipeline CRM","de":"CRM Pipeline","fr":"Pipeline CRM","en":"CRM Pipeline","ca":"Pipeline CRM"},
    "sec_notes":      {"it":"Note","de":"Notizen","fr":"Notes","en":"Notes","ca":"Notes"},
    "f_nome":         {"it":"Nome e Cognome","de":"Vor- und Nachname","fr":"Nom et prénom","en":"Full name","ca":"Nom i cognoms"},
    "f_eta":          {"it":"Età","de":"Alter","fr":"Âge","en":"Age","ca":"Edat"},
    "f_sesso":        {"it":"Sesso","de":"Geschlecht","fr":"Sexe","en":"Gender","ca":"Sexe"},
    "f_sesso_m":      {"it":"Uomo","de":"Mann","fr":"Homme","en":"Male","ca":"Home"},
    "f_sesso_f":      {"it":"Donna","de":"Frau","fr":"Femme","en":"Female","ca":"Dona"},
    "f_tel":          {"it":"Telefono","de":"Telefon","fr":"Téléphone","en":"Phone","ca":"Telèfon"},
    "f_email":        {"it":"Email","de":"E-Mail","fr":"E-mail","en":"Email","ca":"Email"},
    "f_canton":       {"it":"Cantone","de":"Kanton","fr":"Canton","en":"Canton","ca":"Cantó"},
    "f_lang":         {"it":"Lingua","de":"Sprache","fr":"Langue","en":"Language","ca":"Idioma"},
    "f_reddito":      {"it":"Reddito /M CHF","de":"Einkommen /M CHF","fr":"Revenu /M CHF","en":"Income /M CHF","ca":"Ingressos /M CHF"},
    "f_situ":         {"it":"Situazione lav.","de":"Berufssituation","fr":"Situation prof.","en":"Employment","ca":"Situació lab."},
    "f_sc":           {"it":"Stato civile","de":"Zivilstand","fr":"État civil","en":"Marital status","ca":"Estat civil"},
    "f_figli":        {"it":"Figli","de":"Kinder","fr":"Enfants","en":"Children","ca":"Fills"},
    "f_nfigli":       {"it":"N° figli","de":"Anz. Kinder","fr":"Nb enfants","en":"No. children","ca":"N° fills"},
    "f_ipoteca":      {"it":"Ipoteca","de":"Hypothek","fr":"Hypothèque","en":"Mortgage","ca":"Hipoteca"},
    "f_stage":        {"it":"Fase pipeline","de":"Pipeline-Phase","fr":"Phase pipeline","en":"Pipeline stage","ca":"Fase pipeline"},
    "f_rischio":      {"it":"Tolleranza rischio","de":"Risikobereitschaft","fr":"Tolérance risque","en":"Risk tolerance","ca":"Tolerància risc"},
    "f_valore":       {"it":"Valore stimato CHF/anno","de":"Geschätzter Wert CHF/J","fr":"Valeur estimée CHF/an","en":"Est. value CHF/year","ca":"Valor estimat CHF/any"},
    "f_data1":        {"it":"Data primo contatto","de":"Datum Erstkontakt","fr":"Date 1er contact","en":"First contact date","ca":"Data primer contacte"},
    "f_followup":     {"it":"Prossimo follow-up","de":"Nächstes Follow-up","fr":"Prochain suivi","en":"Next follow-up","ca":"Proper seguiment"},
    "f_prodotto":     {"it":"Prodotto contrattato","de":"Vertragsprodukt","fr":"Produit contracté","en":"Contracted product","ca":"Producte contractat"},
    "f_note_ph":      {"it":"Osservazioni, prossimi passi…","de":"Beobachtungen, nächste Schritte…","fr":"Observations, prochaines étapes…","en":"Observations, next steps…","ca":"Observacions, pròxims passos…"},
    "yes":            {"it":"Sì","de":"Ja","fr":"Oui","en":"Yes","ca":"Sí"},
    "no":             {"it":"No","de":"Nein","fr":"Non","en":"No","ca":"No"},
    "s_lead":         {"it":"🔵 Lead","de":"🔵 Lead","fr":"🔵 Lead","en":"🔵 Lead","ca":"🔵 Lead"},
    "s_contattato":   {"it":"📞 Contattato","de":"📞 Kontaktiert","fr":"📞 Contacté","en":"📞 Contacted","ca":"📞 Contactat"},
    "s_riunione":     {"it":"🤝 Riunione","de":"🤝 Treffen","fr":"🤝 Réunion","en":"🤝 Meeting","ca":"🤝 Reunió"},
    "s_proposta":     {"it":"📄 Proposta","de":"📄 Angebot","fr":"📄 Proposition","en":"📄 Proposal","ca":"📄 Proposta"},
    "s_chiuso":       {"it":"✅ Chiuso","de":"✅ Abgeschlossen","fr":"✅ Conclu","en":"✅ Closed","ca":"✅ Tancat"},
    "s_perso":        {"it":"❌ Perso","de":"❌ Verloren","fr":"❌ Perdu","en":"❌ Lost","ca":"❌ Perdut"},
    "sit_dip":        {"it":"Dipendente","de":"Angestellt","fr":"Salarié","en":"Employee","ca":"Assalariat"},
    "sit_ind":        {"it":"Indipendente","de":"Selbstständig","fr":"Indépendant","en":"Self-employed","ca":"Autònom"},
    "sit_pen":        {"it":"Pensionato","de":"Rentner","fr":"Retraité","en":"Retired","ca":"Jubilat"},
    "sit_stu":        {"it":"Studente","de":"Student","fr":"Étudiant","en":"Student","ca":"Estudiant"},
    "sit_dis":        {"it":"Disoccupato","de":"Arbeitslos","fr":"Au chômage","en":"Unemployed","ca":"Aturat"},
    "sc_single":      {"it":"Single","de":"Ledig","fr":"Célibataire","en":"Single","ca":"Solter/a"},
    "sc_spos":        {"it":"Sposato/a","de":"Verheiratet","fr":"Marié(e)","en":"Married","ca":"Casat/ada"},
    "sc_div":         {"it":"Divorziato/a","de":"Geschieden","fr":"Divorcé(e)","en":"Divorced","ca":"Divorciat/ada"},
    "sc_ved":         {"it":"Vedovo/a","de":"Verwitwet","fr":"Veuf/veuve","en":"Widowed","ca":"Vidu/a"},
    "sc_uc":          {"it":"Unione civile","de":"Eingetr. Partnerschaft","fr":"Partenariat enr.","en":"Civil union","ca":"Unió civil"},
    "r_bassa":        {"it":"Bassa","de":"Niedrig","fr":"Faible","en":"Low","ca":"Baixa"},
    "r_media":        {"it":"Media","de":"Mittel","fr":"Moyenne","en":"Medium","ca":"Mitjana"},
    "r_alta":         {"it":"Alta","de":"Hoch","fr":"Élevée","en":"High","ca":"Alta"},
    # Notes log & alertes
    "nt_nota":        {"it":"📝 Nota","de":"📝 Notiz","fr":"📝 Note","en":"📝 Note","ca":"📝 Nota"},
    "nt_reunio":      {"it":"🤝 Riunione","de":"🤝 Treffen","fr":"🤝 Réunion","en":"🤝 Meeting","ca":"🤝 Reunió"},
    "nt_contracte":   {"it":"📄 Contratto","de":"📄 Vertrag","fr":"📄 Contrat","en":"📄 Contract","ca":"📄 Contracte"},
    "nt_trucada":     {"it":"📞 Chiamata","de":"📞 Anruf","fr":"📞 Appel","en":"📞 Call","ca":"📞 Trucada"},
    "note_new_ph":    {"it":"Cosa è successo? Prossimi passi…","de":"Was ist passiert?…","fr":"Que s'est-il passé?…","en":"What happened? Next steps…","ca":"Que ha passat? Pròxims passos…"},
    "sec_log":        {"it":"📋 Storico interazioni","de":"📋 Verlauf","fr":"📋 Historique","en":"📋 Interaction log","ca":"📋 Historial d'interaccions"},
    "sec_add_note":   {"it":"✏️ Aggiungi nota","de":"✏️ Notiz hinzufügen","fr":"✏️ Ajouter note","en":"✏️ Add note","ca":"✏️ Afegir nota"},
    "sec_alert":      {"it":"🔔 Prossimo contatto / Alerta","de":"🔔 Nächster Kontakt","fr":"🔔 Prochain contact","en":"🔔 Next contact / Alert","ca":"🔔 Proper contacte / Alerta"},
    "alert_motiu_ph": {"it":"Motivo del contatto…","de":"Kontaktgrund…","fr":"Raison du contact…","en":"Contact reason…","ca":"Motiu del contacte…"},
    "btn_save_note":  {"it":"💾 Salva nota + alerta","de":"💾 Notiz + Erinnerung","fr":"💾 Sauvegarder","en":"💾 Save note + alert","ca":"💾 Desa nota + alerta"},
    "note_saved":     {"it":"✅ Nota salvata","de":"✅ Notiz gespeichert","fr":"✅ Note sauvegardée","en":"✅ Note saved","ca":"✅ Nota desada"},
    "alert_saved":    {"it":"🔔 Alerta impostata","de":"🔔 Erinnerung gesetzt","fr":"🔔 Alerte définie","en":"🔔 Alert set","ca":"🔔 Alerta configurada"},
    "no_notes":       {"it":"Nessuna interazione registrata.","de":"Keine Interaktionen.","fr":"Aucune interaction.","en":"No interactions recorded.","ca":"Cap interacció registrada."},
    "no_change":      {"it":"⚠️ Niente da salvare.","de":"⚠️ Nichts zu speichern.","fr":"⚠️ Rien à enregistrer.","en":"⚠️ Nothing to save.","ca":"⚠️ Res a desar."},
    # Productes
    "prod_title":     {"it":"📦 Catalogo Prodotti","de":"📦 Produktkatalog","fr":"📦 Catalogue Produits","en":"📦 Product Catalogue","ca":"📦 Catàleg de Productes"},
    "prod_sub":       {"it":"Soluzioni finanziarie proposte da SVAG","de":"Finanzlösungen von SVAG","fr":"Solutions financières SVAG","en":"Financial solutions by SVAG","ca":"Solucions financeres de SVAG"},
    "prod_clients":   {"it":"clienti","de":"Kunden","fr":"clients","en":"clients","ca":"clients"},
    # Suggeriments
    "sugg_title":     {"it":"💡 Prodotti consigliati","de":"💡 Empfohlene Produkte","fr":"💡 Produits conseillés","en":"💡 Recommended products","ca":"💡 Productes recomanats"},
    "sugg_already":   {"it":"✅ Già contrattato","de":"✅ Bereits abgeschlossen","fr":"✅ Déjà contracté","en":"✅ Already contracted","ca":"✅ Ja contractat"},
    # Download
    "btn_download":   {"it":"📄 Scarica report","de":"📄 Bericht laden","fr":"📄 Télécharger","en":"📄 Download report","ca":"📄 Descarrega informe"},
    "dl_profile":     {"it":"PROFILO CLIENTE","de":"KUNDENPROFIL","fr":"PROFIL CLIENT","en":"CLIENT PROFILE","ca":"PERFIL CLIENT"},
    "dl_products":    {"it":"PRODOTTI RACCOMANDATI","de":"EMPFOHLENE PRODUKTE","fr":"PRODUITS RECOMMANDÉS","en":"RECOMMENDED PRODUCTS","ca":"PRODUCTES RECOMANATS"},
    "dl_notes":       {"it":"NOTE RIUNIONE","de":"BESPRECHUNGSNOTIZEN","fr":"NOTES DE RÉUNION","en":"MEETING NOTES","ca":"NOTES REUNIÓ"},
    "dl_next":        {"it":"PROSSIMO CONTATTO","de":"NÄCHSTER KONTAKT","fr":"PROCHAIN CONTACT","en":"NEXT CONTACT","ca":"PROPER CONTACTE"},
}

LANG_OPTS = [{"label":"🇮🇹 IT","value":"it"},{"label":"🇩🇪 DE","value":"de"},
             {"label":"🇫🇷 FR","value":"fr"},{"label":"🇬🇧 EN","value":"en"},
             {"label":"🟡 CA","value":"ca"}]

def ct(key, lc):
    row = _T.get(key, {})
    return row.get(lc) or row.get("it") or key

def slabel(stage, lc):
    s_key = f"s_{stage}"
    return ct(s_key, lc)

def stage_opts(lc):
    return [{"label": slabel(k, lc), "value": k} for k, _, _ in PIPELINE_STAGES]

def situ_opts(lc):
    return [{"label":ct(f"sit_{k}",lc),"value":v} for k,v in
            [("dip","Dipendente"),("ind","Indipendente"),("pen","Pensionato"),("stu","Studente"),("dis","Disoccupato")]]

def sc_opts(lc):
    return [{"label":ct(f"sc_{k}",lc),"value":v} for k,v in
            [("single","Single"),("spos","Sposato/a"),("div","Divorziato/a"),("ved","Vedovo/a"),("uc","Unione civile")]]

def risc_opts(lc):
    return [{"label":ct(f"r_{k}",lc),"value":v} for k,v in [("bassa","Bassa"),("media","Media"),("alta","Alta")]]

def yn_opts(lc):
    return [{"label":ct("no",lc),"value":"No"},{"label":ct("yes",lc),"value":"Si"}]

# ── DATA LAYER ───────────────────────────────────────────────────────────────
def _default(c):
    defs = {"telefono":"","email":"",
            "pipeline_stage": "chiuso" if c.get("stato")=="chiuso" else "lead",
            "data_primo_contatto": c.get("data_salvataggio",""),
            "data_prossimo_followup":"","valore_stimato":0,
            "prodotto_contrattato":"","note":"",
            "notes_log":[],"alerta_motiu":"",
            "data_salvataggio": date.today().isoformat(),"stato":"lead"}
    for k,v in defs.items(): c.setdefault(k,v)
    ps = c["pipeline_stage"]
    c["stato"] = "chiuso" if ps=="chiuso" else ("perso" if ps=="perso" else "da_chiudere")
    return c

def load_clients():
    if os.path.exists(CRM_FILE):
        try:
            with open(CRM_FILE,"r",encoding="utf-8") as f: return [_default(c) for c in json.load(f)]
        except Exception: pass
    return []

def save_clients(lst):
    with open(CRM_FILE,"w",encoding="utf-8") as f: json.dump(lst,f,ensure_ascii=False,indent=2)

def get_client(nome): return next((c for c in load_clients() if c.get("nome")==nome),None)
def upsert_client(e):
    cs=load_clients(); idx=next((i for i,c in enumerate(cs) if c.get("nome")==e["nome"]),None)
    if idx is not None: cs[idx]=e
    else: cs.append(e)
    save_clients(cs)
def delete_client(nome): save_clients([c for c in load_clients() if c.get("nome")!=nome])

# ── FLASK / AUTH ─────────────────────────────────────────────────────────────
server = Flask(__name__)
server.secret_key = os.environ.get("SECRET_KEY","alexfin-crm-secret")

_LOGIN_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AlexFin CRM · Login</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*,body{font-family:'Inter',sans-serif;box-sizing:border-box;margin:0;padding:0}
body{background:linear-gradient(135deg,#1e2235 0%,#151929 100%);min-height:100vh;display:flex;align-items:center;justify-content:center}
.card{background:#fff;border-radius:20px;padding:48px 44px;width:380px;box-shadow:0 20px 60px rgba(0,0,0,0.35)}
.logo-text{font-size:1.7rem;font-weight:800;color:#1e2235;margin-bottom:4px}
.logo-text span{color:#c0392b}
.logo-badge{background:#fde8e8;color:#c0392b;font-size:0.65rem;font-weight:700;padding:3px 9px;border-radius:20px;letter-spacing:0.08em}
.logo{margin-bottom:32px}
label{display:block;font-size:0.78rem;font-weight:600;color:#555;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px}
input{width:100%;padding:11px 14px;border:1px solid #e0e3ec;border-radius:10px;font-size:0.95rem;margin-bottom:18px;outline:none;color:#1e2235;transition:border .2s}
input:focus{border-color:#c0392b}
button{width:100%;padding:13px;background:#c0392b;color:#fff;border:none;border-radius:10px;font-size:1rem;font-weight:700;cursor:pointer;margin-top:4px}
button:hover{background:#a93226}
.error{background:#fde8e8;color:#c0392b;border-radius:8px;padding:10px 14px;font-size:0.84rem;margin-bottom:18px}
.footer{text-align:center;font-size:0.75rem;color:#aaa;margin-top:24px}
</style></head>
<body><div class="card">
  <div class="logo"><div class="logo-text"><span>Alex</span>Fin</div><span class="logo-badge">CRM</span></div>
  {% if error %}<div class="error">⚠️ {{ error }}</div>{% endif %}
  <form method="POST" action="/login">
    <label>Utente</label><input type="text" name="username" placeholder="nome utente" autocomplete="username" required>
    <label>Password</label><input type="password" name="password" placeholder="••••••••" autocomplete="current-password" required>
    <button type="submit">→ Accedi al CRM</button>
  </form>
  <div class="footer">Uso professionale riservato · © 2026 SVAG</div>
</div></body></html>"""

@server.route("/login",methods=["GET","POST"])
def login():
    error=None
    if request.method=="POST":
        if request.form.get("username","").strip()==AUTH_USER and request.form.get("password","")==AUTH_PASS:
            session["auth"]=True; return redirect(request.args.get("next","/"))
        error="Credenziali non valide."
    return render_template_string(_LOGIN_HTML,error=error)

@server.route("/logout")
def logout(): session.clear(); return redirect("/login")

@server.before_request
def require_login():
    if any(request.path.startswith(p) for p in ("/login","/crm_assets","/_favicon")): return
    if request.path.startswith("/_dash"): return ("Unauthorized",401) if not session.get("auth") else None
    if not session.get("auth"): return redirect(f"/login?next={request.path}")

# ── DASH APP ─────────────────────────────────────────────────────────────────
app = dash.Dash(__name__,server=server,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True,
                title="AlexFin CRM",assets_folder="crm_assets")

# ── UI HELPERS ───────────────────────────────────────────────────────────────
def _pill(stage, lc):
    lbl = slabel(stage, lc); color = STAGE_COLORS.get(stage,"#aaa")
    return html.Span(lbl,className="stage-pill",
                     style={"background":color+"22","color":color,"border":f"1px solid {color}55"})

def _kpi(label,value,cls="",delta=None):
    return dbc.Col(html.Div([html.Div(label,className="kpi-label"),
                              html.Div(value,className=f"kpi-value {cls}"),
                              html.Div(delta,className="kpi-delta") if delta else html.Div()
                             ],className="kpi-card"))

def _sec(title,children): return html.Div([html.Div(title,className="c-card-title"),*children],className="c-card")

def _lbl(t): return html.Div(t,className="crm-form-label")

def _fcol(lkey,child,lc,w=6):
    return dbc.Col([_lbl(ct(lkey,lc)),child],width=w,className="mb-3")

def _fu(c):
    fu=c.get("data_prossimo_followup","")
    try: return date.fromisoformat(fu) if fu else None
    except Exception: return None

# ── CLIENT FORM ──────────────────────────────────────────────────────────────
def _form(c=None, lc="it"):
    c=c or {}
    def v(k,d=""): return c.get(k,d)
    canton_opts=[{"label":x,"value":x} for x in CANTONS]
    lang_form=[{"label":"Italiano","value":"it"},{"label":"Deutsch","value":"de"},
               {"label":"Français","value":"fr"},{"label":"English","value":"en"},{"label":"Català","value":"ca"}]
    sec = lambda t: html.H6(t,className="text-muted mb-2 mt-2",
                             style={"fontSize":"0.72rem","textTransform":"uppercase","letterSpacing":"0.07em","fontWeight":"700"})
    return dbc.Form([
        sec(ct("sec_personal",lc)),
        dbc.Row([
            _fcol("f_nome",   dbc.Input(id="cf-nome",  value=v("nome"),    placeholder="Mario Rossi"),w=4,lc=lc),
            _fcol("f_eta",    dbc.Input(id="cf-eta",   type="number",value=v("eta",35),min=18,max=99),w=2,lc=lc),
            _fcol("f_sesso",  dbc.Select(id="cf-sesso",value=v("sesso","M"),
                              options=[{"label":ct("f_sesso_m",lc),"value":"M"},{"label":ct("f_sesso_f",lc),"value":"F"}]),w=2,lc=lc),
            _fcol("f_tel",    dbc.Input(id="cf-tel",   value=v("telefono"),placeholder="+41 79 000 00 00"),w=4,lc=lc),
        ],className="g-3"),
        dbc.Row([
            _fcol("f_email",  dbc.Input(id="cf-email", type="email",value=v("email"),placeholder="m@esempio.ch"),w=5,lc=lc),
            _fcol("f_canton", dbc.Select(id="cf-canton",value=v("canton","Zürich"),options=canton_opts),w=3,lc=lc),
            _fcol("f_lang",   dbc.Select(id="cf-lc",   value=v("lc","it"),options=lang_form),w=2,lc=lc),
            _fcol("f_reddito",dbc.Input(id="cf-reddito",type="number",value=v("reddito_mensile",5000),min=0,step=100),w=2,lc=lc),
        ],className="g-3"),
        dbc.Row([
            _fcol("f_situ",   dbc.Select(id="cf-situ", value=v("situazione","Dipendente"),options=situ_opts(lc)),w=3,lc=lc),
            _fcol("f_sc",     dbc.Select(id="cf-sc",   value=v("stato_civile","Single"),  options=sc_opts(lc)),  w=3,lc=lc),
            _fcol("f_figli",  dbc.Select(id="cf-figli",value="Si" if v("figli") else "No",options=yn_opts(lc)),  w=2,lc=lc),
            _fcol("f_nfigli", dbc.Input(id="cf-nfigli",type="number",value=v("n_figli",0),min=0,max=10),w=2,lc=lc),
            _fcol("f_ipoteca",dbc.Select(id="cf-ipot", value="Si" if v("ipoteca") else "No",options=yn_opts(lc)),w=2,lc=lc),
        ],className="g-3"),
        sec(ct("sec_pipeline",lc)),
        dbc.Row([
            _fcol("f_stage",  dbc.Select(id="cf-stage", value=v("pipeline_stage","lead"),options=stage_opts(lc)),w=3,lc=lc),
            _fcol("f_rischio",dbc.Select(id="cf-rischio",value=v("tolleranza_rischio","Media"),options=risc_opts(lc)),w=3,lc=lc),
            _fcol("f_valore", dbc.Input(id="cf-valore", type="number",value=v("valore_stimato",0),min=0,step=100),w=3,lc=lc),
            _fcol("f_data1",  dbc.Input(id="cf-data1",  type="date",value=v("data_primo_contatto",date.today().isoformat())),w=3,lc=lc),
        ],className="g-3"),
        dbc.Row([
            _fcol("f_followup",dbc.Input(id="cf-followup",type="date",value=v("data_prossimo_followup","")),w=3,lc=lc),
            _fcol("f_prodotto",dbc.Input(id="cf-prodotto",value=v("prodotto_contrattato",""),placeholder="Es: 3° Pilastro + KK"),w=9,lc=lc),
        ],className="g-3"),
        sec(ct("sec_notes",lc)),
        dbc.Textarea(id="cf-note",value=v("note",""),placeholder=ct("f_note_ph",lc),
                     style={"minHeight":"100px","borderRadius":"8px","border":"1px solid #e0e3ec","fontSize":"0.88rem","padding":"10px"}),
    ])

# ── LAYOUT ───────────────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Store(id="crm-reload",  data=0),
    dcc.Store(id="crm-lang",    data="it", storage_type="local"),
    dcc.Store(id="active-tab",  data="tab-dash"),
    dcc.Store(id="edit-nome",   data=None),
    dcc.Store(id="del-nome",    data=None),
    dcc.Store(id="info-nome",   data=None),
    dcc.Store(id="kanban-drop", data=None),
    dcc.Store(id="new-relay",   data=0),
    dcc.Store(id="dnd-setup",   data=0),
    dcc.Download(id="meet-dl"),
    dcc.Interval(id="crm-tick", interval=30_000, n_intervals=0),
    # Navbar
    html.Nav(id="crm-navbar", className="crm-navbar"),
    # Content
    html.Div(id="crm-content", className="crm-page"),
    # Edit modal
    dbc.Modal([
        dbc.ModalHeader(html.Span(id="modal-title"),close_button=True,className="modal-header"),
        dbc.ModalBody(html.Div(id="modal-body")),
        dbc.ModalFooter([
            dbc.Button(id="btn-cancel",color="secondary",outline=True,className="me-2"),
            dbc.Button(id="btn-save",  className="btn-crm-primary"),
            html.Div(id="modal-msg",style={"fontSize":"0.82rem","color":"#27ae60","marginLeft":"12px"}),
        ]),
    ], id="edit-modal", size="xl", scrollable=True, is_open=False),
    # Delete modal
    dbc.Modal([
        dbc.ModalHeader(id="del-modal-hdr",close_button=True),
        dbc.ModalBody(html.P(id="del-text")),
        dbc.ModalFooter([
            dbc.Button(id="btn-del-cancel",color="secondary",outline=True,className="me-2"),
            dbc.Button(id="btn-del-ok",    color="danger"),
        ]),
    ], id="del-modal", is_open=False),
    # Info / fitxa client modal
    dbc.Modal([
        dbc.ModalHeader(html.Span(id="info-title"),close_button=True,
                        style={"background":"#1e2235","color":"white","borderRadius":"12px 12px 0 0"}),
        dbc.ModalBody(html.Div(id="info-body")),
        dbc.ModalFooter([
            html.Div(id="info-note-msg",style={"fontSize":"0.85rem","color":"#27ae60","flex":"1","minHeight":"20px"}),
            dbc.Button(id="btn-download",color="secondary",outline=True,className="me-2"),
            dbc.Button(id="btn-save-note",className="btn-crm-primary"),
        ],style={"display":"flex","alignItems":"center","gap":"8px","background":"#f8f9fb",
                 "borderTop":"1px solid #eaecf2","borderRadius":"0 0 12px 12px"}),
    ], id="info-modal", size="xl", scrollable=True, is_open=False),
    # Product detail modal
    dbc.Modal([
        dbc.ModalHeader(html.Span(id="prod-title"), close_button=True,
                        style={"background":"#1e2235","color":"white","borderRadius":"12px 12px 0 0"}),
        dbc.ModalBody(html.Div(id="prod-body")),
    ], id="prod-modal", size="lg", scrollable=True, is_open=False),
])

# ── NAVBAR ───────────────────────────────────────────────────────────────────
@callback(Output("crm-navbar","children"), Input("crm-lang","data"))
def render_navbar(lc):
    lc=lc or "it"
    return [
        html.Div([html.Span("Alex",style={"color":"#c0392b"}),html.Span("Fin")],className="crm-logo"),
        html.Span("CRM",className="crm-badge"),
        html.Span("·",style={"color":"rgba(255,255,255,0.2)","margin":"0 6px"}),
        html.A(ct("nav_dash",lc),    id="nav-dashboard",className="crm-nav-link",href="#"),
        html.A(ct("nav_clients",lc), id="nav-clienti",  className="crm-nav-link",href="#"),
        html.A(ct("nav_pipeline",lc),id="nav-pipeline", className="crm-nav-link",href="#"),
        html.A(ct("nav_agenda",lc),    id="nav-agenda",    className="crm-nav-link",href="#"),
        html.A(ct("nav_products",lc),id="nav-products",  className="crm-nav-link",href="#"),
        html.A(ct("nav_new",lc),     id="btn-new",       className="crm-nav-link",href="#",
               style={"background":"rgba(192,57,43,0.22)"}),
        dcc.Dropdown(id="lang-sel",options=LANG_OPTS,value=lc,clearable=False,
                     style={"width":"80px","fontSize":"0.8rem","marginLeft":"auto","minWidth":"78px"}),
        html.A(ct("nav_logout",lc),href="/logout",className="crm-logout"),
    ]

@callback(Output("crm-lang","data"), Input("lang-sel","value"), prevent_initial_call=True)
def change_lang(v): return v or "it"

# FIX: Python callback per tab switching — sense race condition
@callback(Output("active-tab","data"),
          Input("nav-dashboard","n_clicks"), Input("nav-clienti","n_clicks"),
          Input("nav-pipeline","n_clicks"),  Input("nav-agenda","n_clicks"),
          Input("nav-products","n_clicks"),
          State("active-tab","data"), prevent_initial_call=True)
def switch_tab(a,b,c,d,e,cur):
    m={"nav-dashboard":"tab-dash","nav-clienti":"tab-list","nav-pipeline":"tab-kanban",
       "nav-agenda":"tab-agenda","nav-products":"tab-products"}
    return m.get(ctx.triggered_id, cur or "tab-dash")

# ── MAIN CONTENT ─────────────────────────────────────────────────────────────
@callback(Output("crm-content","children"),
          Input("active-tab","data"), Input("crm-reload","data"),
          Input("crm-lang","data"),   Input("crm-tick","n_intervals"))
def render_content(tab, _r, lc, _t):
    lc=lc or "it"; cs=load_clients()
    if tab=="tab-list":     return render_list(cs,lc)
    if tab=="tab-kanban":   return render_kanban(cs,lc)
    if tab=="tab-agenda":   return render_agenda(cs,lc)
    if tab=="tab-products": return render_products(lc)
    return render_dash(cs,lc)

# ── TAB 1: DASHBOARD ─────────────────────────────────────────────────────────
def render_dash(cs,lc):
    today=date.today()
    chiusi=sum(1 for c in cs if c.get("pipeline_stage")=="chiuso")
    attivi=sum(1 for c in cs if c.get("pipeline_stage") not in ("chiuso","perso"))
    persi =sum(1 for c in cs if c.get("pipeline_stage")=="perso")
    fu_oggi=[c for c in cs if _fu(c)==today]
    fu_sett=[c for c in cs if _fu(c) and today<=_fu(c)<=today+timedelta(days=7)]
    vp=sum(c.get("valore_stimato",0) for c in cs if c.get("pipeline_stage") not in ("chiuso","perso"))
    vc=sum(c.get("valore_stimato",0) for c in cs if c.get("pipeline_stage")=="chiuso")

    cnt={s:0 for s in STAGE_KEYS}
    for c in cs: cnt[c.get("pipeline_stage","lead")]+=1
    fs=[s for s in PIPELINE_STAGES if s[0]!="perso"]; mx=max((cnt[s[0]] for s in fs),default=1) or 1
    funnel=[html.Div([html.Div([
        html.Span(slabel(k,lc),style={"fontSize":"0.82rem","fontWeight":"600","minWidth":"110px"}),
        html.Div(style={"flex":"1","height":"10px","background":"#f0f2f7","borderRadius":"6px","overflow":"hidden","margin":"0 12px"},children=[
            html.Div(style={"width":f"{int(cnt[k]/mx*100)}%","height":"100%","background":color,"borderRadius":"6px"})]),
        html.Span(str(cnt[k]),style={"fontWeight":"700","color":color,"minWidth":"24px","textAlign":"right"}),
    ],style={"display":"flex","alignItems":"center","marginBottom":"10px"})]) for k,_,color in fs]

    urgenti=[]
    for c in sorted(fu_sett,key=lambda x:x.get("data_prossimo_followup","")):
        d=_fu(c);
        if not d: continue
        color="#e74c3c" if d<today else ("#f39c12" if d==today else "#3b82f6")
        lbl=ct("ag_past",lc).split()[-1] if d<today else (ct("ag_today",lc).split()[-1] if d==today else d.strftime("%d/%m"))
        urgenti.append(html.Div([
            html.Div(lbl,className="agenda-date",style={"color":color}),
            html.Div([html.Div(c.get("nome","—"),className="agenda-name"),
                      html.Div(f"{c.get('situazione','—')} · {c.get('canton','—')}",className="agenda-sub")]),
            html.Div(_pill(c.get("pipeline_stage","lead"),lc),style={"marginLeft":"auto"}),
        ],className="agenda-item",style={"borderLeftColor":color}))

    recents=sorted(cs,key=lambda c:c.get("data_salvataggio",""),reverse=True)[:5]
    rows=[html.Tr([html.Td(f"👤 {c.get('nome','—')}",style={"fontWeight":"600"}),
                   html.Td(_pill(c.get("pipeline_stage","lead"),lc)),
                   html.Td(c.get("canton","—"),style={"color":"#888","fontSize":"0.82rem"}),
                   html.Td(f"CHF {c.get('reddito_mensile',0):,}",style={"color":"#888","fontSize":"0.82rem"}),
                   html.Td(c.get("data_salvataggio","—"),style={"color":"#aaa","fontSize":"0.78rem"}),
                  ]) for c in recents]

    return html.Div([
        html.Div([html.Div(ct("dash_title",lc),style={"fontSize":"1.4rem","fontWeight":"800","color":"#1e2235"}),
                  html.Div(f"{ct('dash_updated',lc)}: {today.strftime('%d/%m/%Y')}",style={"color":"#aaa","fontSize":"0.8rem"})],
                 style={"marginBottom":"24px"}),
        dbc.Row([_kpi(ct("kpi_total",lc),len(cs),"blue"),_kpi(ct("kpi_active",lc),attivi,"orange"),
                 _kpi(ct("kpi_closed",lc),chiusi,"green"),_kpi(ct("kpi_lost",lc),persi,"red"),
                 _kpi(ct("kpi_followup",lc),len(fu_oggi),"red" if fu_oggi else ""),
                 _kpi(ct("kpi_pip_val",lc),f"CHF {vp:,}","orange",delta=f"{ct('kpi_chi_val',lc)}: CHF {vc:,}"),
                ],className="g-3 mb-4"),
        dbc.Row([
            dbc.Col(_sec(ct("dash_funnel",lc),funnel),width=5),
            dbc.Col(_sec(f"{ct('dash_week_fu',lc)} ({len(fu_sett)})",
                        urgenti or [html.Div(ct("dash_no_fu",lc),style={"color":"#aaa","fontSize":"0.85rem"})]),width=7),
        ],className="g-3"),
        _sec(ct("dash_recent",lc),[html.Table([
            html.Thead(html.Tr([html.Th(ct("th_name",lc)),html.Th(ct("th_stage",lc)),
                                html.Th(ct("th_canton",lc)),html.Th(ct("th_income",lc)),html.Th(ct("th_date",lc))])),
            html.Tbody(rows),
        ],className="crm-table w-100")]) if recents else html.Div(),
    ])

# ── TAB 2: LISTA CLIENTI ─────────────────────────────────────────────────────
def render_list(cs,lc):
    so=[{"label":ct("all_stages",lc),"value":""}]+stage_opts(lc)
    cl=sorted(set(c.get("canton","") for c in cs if c.get("canton")))
    co=[{"label":ct("all_cantons",lc),"value":""}]+[{"label":x,"value":x} for x in cl]
    return html.Div([
        html.Div([html.Div(ct("list_title",lc),style={"fontSize":"1.4rem","fontWeight":"800","color":"#1e2235"}),
                  html.Div(f"{len(cs)} {ct('list_in_crm',lc)}",style={"color":"#aaa","fontSize":"0.8rem"})],
                 style={"marginBottom":"20px"}),
        dbc.Row([
            dbc.Col(dbc.Input(id="filter-search",placeholder=ct("search_ph",lc),debounce=True,
                              style={"borderRadius":"10px","border":"1px solid #e0e3ec","fontSize":"0.88rem"}),width=5),
            dbc.Col(dbc.Select(id="filter-stage", value="",options=so),width=3),
            dbc.Col(dbc.Select(id="filter-canton",value="",options=co),width=3),
            dbc.Col(dbc.Button("＋",id="list-new-btn",className="btn-crm-primary w-100",
                               style={"fontSize":"1.2rem","lineHeight":"1.2"}),width=1),
        ],className="g-2 mb-4"),
        html.Div(id="client-table-body"),
    ])

@callback(Output("client-table-body","children"),
          Input("filter-search","value"), Input("filter-stage","value"),
          Input("filter-canton","value"), Input("crm-reload","data"), Input("crm-lang","data"),
          prevent_initial_call=False)
def update_table(search,stage,canton,_r,lc):
    lc=lc or "it"; cs=load_clients()
    q=(search or "").lower()
    if q: cs=[c for c in cs if q in c.get("nome","").lower() or q in c.get("email","").lower() or q in c.get("prodotto_contrattato","").lower()]
    if stage:  cs=[c for c in cs if c.get("pipeline_stage")==stage]
    if canton: cs=[c for c in cs if c.get("canton")==canton]
    if not cs: return html.Div(ct("no_clients",lc),style={"color":"#aaa","padding":"32px","textAlign":"center"})

    rows=[]
    for c in sorted(cs,key=lambda x:x.get("data_salvataggio",""),reverse=True):
        nome=c.get("nome","—"); fd=_fu(c)
        fu_str=fd.strftime("%d/%m/%Y") if fd else "—"
        is_past=bool(fd and fd<date.today())
        rows.append(html.Tr([
            html.Td(f"👤 {nome}",style={"fontWeight":"700"}),
            html.Td(_pill(c.get("pipeline_stage","lead"),lc)),
            html.Td(c.get("canton","—")),
            html.Td(c.get("situazione","—"),style={"color":"#888","fontSize":"0.82rem"}),
            html.Td(f"CHF {c.get('reddito_mensile',0):,}",style={"color":"#888"}),
            html.Td(html.Span(fu_str,style={"color":"#e74c3c","fontWeight":"700"} if is_past else {})),
            html.Td(c.get("prodotto_contrattato","") or "—",
                    style={"fontSize":"0.78rem","color":"#888","maxWidth":"160px","overflow":"hidden","textOverflow":"ellipsis","whiteSpace":"nowrap"}),
            html.Td([dbc.Button("ℹ️",id={"type":"btn-info",  "index":nome},size="sm",color="light",className="me-1 p-1"),
                     dbc.Button("✏️",id={"type":"btn-edit",  "index":nome},size="sm",color="light",className="me-1 p-1"),
                     dbc.Button("🗑️",id={"type":"btn-delete","index":nome},size="sm",color="light",className="p-1")],
                    style={"whiteSpace":"nowrap"}),
        ]))

    return html.Div([
        html.Table([
            html.Thead(html.Tr([html.Th(ct("th_name",lc)),html.Th(ct("th_stage",lc)),html.Th(ct("th_canton",lc)),
                                html.Th(ct("th_situ",lc)),html.Th(ct("th_income",lc)),
                                html.Th(ct("th_fu",lc)),html.Th(ct("th_product",lc)),html.Th("")])),
            html.Tbody(rows),
        ],className="crm-table w-100"),
        html.Div(f"{len(cs)} {ct('list_shown',lc)}",style={"color":"#aaa","fontSize":"0.75rem","marginTop":"10px","textAlign":"right","padding":"8px"}),
    ],className="c-card",style={"padding":"0","overflow":"hidden"})

# ── TAB 3: KANBAN (amb drag & drop) ──────────────────────────────────────────
def render_kanban(cs,lc):
    by={k:[] for k in STAGE_KEYS}
    for c in cs: by[c.get("pipeline_stage","lead")].append(c)
    cols=[]
    for key,_,color in PIPELINE_STAGES:
        cards=[html.Div([
            html.Div(c.get("nome","—"),className="kanban-card-name"),
            html.Div(f"{c.get('canton','—')} · CHF {c.get('reddito_mensile',0):,}/m",className="kanban-card-sub"),
            html.Div([html.Span(c.get("situazione",""),style={"fontSize":"0.72rem","color":"#aaa"}),
                      dbc.Button("ℹ️",id={"type":"btn-info","index":c.get("nome","")},size="sm",color="light",
                                 className="p-0 ms-1",style={"fontSize":"0.75rem"}),
                      dbc.Button("✏️",id={"type":"btn-edit","index":c.get("nome","")},size="sm",color="light",
                                 className="p-0 ms-1",style={"fontSize":"0.75rem"})],
                     style={"display":"flex","alignItems":"center","marginTop":"6px"}),
        ],className="kanban-card",
          # Atributs HTML5 drag & drop
          **{"data-drag": c.get("nome",""), "draggable":"true",
             "style":{"cursor":"grab"}}) for c in by[key]]
        tv=sum(c.get("valore_stimato",0) for c in by[key])
        cols.append(dbc.Col(html.Div([
            html.Div([html.Span(slabel(key,lc),className="kanban-col-title",
                                style={"borderBottomColor":color,"color":color}),
                      html.Span(f" {len(by[key])}",style={"color":color,"fontWeight":"800","fontSize":"0.9rem"}),
                      html.Span(f"  CHF {tv:,}" if tv else "",style={"fontSize":"0.72rem","color":"#aaa","marginLeft":"8px"})]),
            *cards,
            html.Div("— buit —",style={"color":"#ddd","textAlign":"center","marginTop":"20px","fontSize":"0.8rem"}) if not cards else html.Div(),
        ],className="kanban-col",
          # Columna accepta drops
          **{"data-drop": key}),width=2))

    return html.Div([
        html.Div([html.Div(ct("pipeline_title",lc),style={"fontSize":"1.4rem","fontWeight":"800","color":"#1e2235"}),
                  html.Div(f"{len(cs)} {ct('list_in_crm',lc)} · arrossega per canviar fase",
                           style={"color":"#aaa","fontSize":"0.8rem"})],
                 style={"marginBottom":"20px"}),
        dbc.Row(cols,className="g-2"),
    ])

# ── TAB 4: AGENDA ────────────────────────────────────────────────────────────
def render_agenda(cs,lc):
    today=date.today()
    wfu=[(c,_fu(c)) for c in cs if _fu(c)]; wfu.sort(key=lambda x:x[1])
    past  =[(c,d) for c,d in wfu if d<today]
    today_=[(c,d) for c,d in wfu if d==today]
    sett  =[(c,d) for c,d in wfu if today<d<=today+timedelta(days=7)]
    future=[(c,d) for c,d in wfu if d>today+timedelta(days=7)]
    no_fu =[c for c in cs if not _fu(c) and c.get("pipeline_stage") not in ("chiuso","perso")]

    def block(title,items,color):
        if not items: return html.Div()
        rows=[html.Div([
            html.Div(d.strftime("%d/%m"),className="agenda-date",style={"color":color}),
            html.Div([html.Div(c.get("nome","—"),className="agenda-name"),
                      html.Div(f"{c.get('situazione','—')} · {c.get('canton','—')} · CHF {c.get('reddito_mensile',0):,}/m",className="agenda-sub"),
                      html.Div(c.get("alerta_motiu","") or (c.get("note","")[:60]+"…" if len(c.get("note",""))>60 else c.get("note","")),
                               style={"fontSize":"0.72rem","color":"#888","marginTop":"2px","fontStyle":"italic"}) if (c.get("alerta_motiu") or c.get("note")) else html.Div()]),
            html.Div([_pill(c.get("pipeline_stage","lead"),lc),
                      dbc.Button("ℹ️",id={"type":"btn-info","index":c.get("nome","")},size="sm",color="light",className="ms-2 p-1"),
                      dbc.Button("✏️",id={"type":"btn-edit","index":c.get("nome","")},size="sm",color="light",className="ms-1 p-1")],
                     style={"marginLeft":"auto","display":"flex","alignItems":"center"}),
        ],className="agenda-item",style={"borderLeftColor":color}) for c,d in items]
        return _sec(f"{title} ({len(items)})",rows)

    no_fu_rows=[html.Div([
        html.Div("N/D",className="agenda-date",style={"color":"#ccc"}),
        html.Div([html.Div(c.get("nome","—"),className="agenda-name"),
                  html.Div(f"{c.get('situazione','—')} · {c.get('canton','—')}",className="agenda-sub")]),
        html.Div([_pill(c.get("pipeline_stage","lead"),lc),
                  dbc.Button("ℹ️",id={"type":"btn-info","index":c.get("nome","")},size="sm",color="light",className="ms-2 p-1"),
                  dbc.Button("✏️",id={"type":"btn-edit","index":c.get("nome","")},size="sm",color="light",className="ms-1 p-1")],
                 style={"marginLeft":"auto","display":"flex","alignItems":"center"}),
    ],className="agenda-item",style={"borderLeftColor":"#ddd"}) for c in no_fu]

    return html.Div([
        html.Div([html.Div(ct("agenda_title",lc),style={"fontSize":"1.4rem","fontWeight":"800","color":"#1e2235"}),
                  html.Div(f"{ct('agenda_today',lc)}: {today.strftime('%d/%m/%Y')}",style={"color":"#aaa","fontSize":"0.8rem"})],
                 style={"marginBottom":"20px"}),
        block(ct("ag_past", lc),past,  "#e74c3c"),
        block(ct("ag_today",lc),today_,"#f39c12"),
        block(ct("ag_week", lc),sett,  "#3b82f6"),
        block(ct("ag_soon", lc),future,"#888"),
        _sec(f"{ct('ag_no_fu',lc)} ({len(no_fu)})",no_fu_rows) if no_fu else html.Div(),
    ])

# ── MODAL LABELS reactius a idioma ───────────────────────────────────────────
@callback(Output("btn-cancel","children"), Output("btn-save","children"),
          Output("btn-del-cancel","children"), Output("btn-del-ok","children"),
          Output("del-modal-hdr","children"), Output("btn-save-note","children"),
          Output("btn-download","children"),
          Input("crm-lang","data"))
def modal_labels(lc):
    lc=lc or "it"
    return (ct("btn_cancel",lc),ct("btn_save",lc),ct("btn_cancel",lc),
            ct("btn_delete",lc),ct("del_title",lc),ct("btn_save_note",lc),ct("btn_download",lc))

# ── OPEN EDIT MODAL — btn-new sempre al DOM (navbar) ─────────────────────────
@callback(
    Output("edit-modal","is_open"),
    Output("modal-body","children"),
    Output("modal-title","children"),
    Output("edit-nome","data"),
    Input("btn-new",                       "n_clicks"),   # navbar — sempre DOM ✅
    Input("new-relay",                     "data"),       # relay de list-new-btn ✅
    Input({"type":"btn-edit","index":ALL}, "n_clicks"),   # pattern-matching ✅
    Input("btn-cancel",                    "n_clicks"),
    Input("btn-save",                      "n_clicks"),
    State("crm-lang","data"),
    prevent_initial_call=True,
)
def open_modal(n_new, n_relay, n_edit, n_cancel, n_save, lc):
    lc=lc or "it"; tid=ctx.triggered_id
    if tid in ("btn-cancel","btn-save") or tid is None:
        return False, dash.no_update, dash.no_update, None
    if tid in ("btn-new","new-relay"):
        if tid == "btn-new" and not (ctx.triggered or [{}])[0].get("value"):
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        return True, _form(None,lc), ct("modal_new",lc), None
    if isinstance(tid,dict) and tid.get("type")=="btn-edit":
        # FIX: ignora el render inicial (n_clicks=None) — evita modal auto-obert
        if not (ctx.triggered or [{}])[0].get("value"):
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        nome=tid["index"]; c=get_client(nome)
        return True, _form(c,lc), f"{ct('modal_edit',lc)} — {nome}", nome
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


# ── INFO FITXA CLIENT — helper ────────────────────────────────────────────────
_NOTE_TYPES = [("nota","#6b7280"),("reunio","#8b5cf6"),("contracte","#22c55e"),("trucada","#3b82f6")]
_NOTE_ICONS  = {"nota":"📝","reunio":"🤝","contracte":"📄","trucada":"📞"}

def _render_info_body(c, lc):
    lc = lc or "it"
    stage = c.get("pipeline_stage","lead"); color_s = STAGE_COLORS.get(stage,"#888")
    fd = _fu(c); today = date.today()
    fu_color = "#e74c3c" if (fd and fd<today) else ("#f39c12" if fd==today else "#1e2235")
    fu_str = fd.strftime("%d/%m/%Y") if fd else "—"

    try:
        d0 = date.fromisoformat(c.get("data_primo_contatto","") or c.get("data_salvataggio",""))
        delta = (today-d0).days; years=delta//365; months=(delta%365)//30
        durada_str = f"{years}a {months}m" if years else f"{months}m" if months else f"{delta}d"
    except Exception: durada_str = "—"

    def row(label,value,color=None):
        return html.Div([
            html.Span(label,style={"fontSize":"0.72rem","fontWeight":"700","color":"#999",
                                   "textTransform":"uppercase","letterSpacing":"0.06em",
                                   "minWidth":"160px","display":"inline-block"}),
            html.Span(str(value) if value else "—",style={"fontWeight":"600","color":color or "#1e2235"}),
        ],style={"padding":"7px 0","borderBottom":"1px solid #f5f5f5"})

    # ── Notes log
    notes_log = c.get("notes_log",[])
    def note_badge(t):
        col = dict(_NOTE_TYPES).get(t,"#6b7280"); ico = _NOTE_ICONS.get(t,"📝")
        return html.Span(f"{ico} {ct('nt_'+t,lc)}",
                         style={"background":col+"22","color":col,"border":f"1px solid {col}55",
                                "borderRadius":"12px","padding":"2px 8px","fontSize":"0.68rem","fontWeight":"700"})
    if notes_log:
        note_items=[html.Div([
            html.Div([note_badge(n.get("tipus","nota")),
                      html.Span(n.get("data",""),style={"fontSize":"0.72rem","color":"#aaa","marginLeft":"10px"})],
                     style={"marginBottom":"4px"}),
            html.Div(n.get("text",""),style={"fontSize":"0.87rem","color":"#333","lineHeight":"1.5"}),
        ],style={"padding":"10px 0","borderBottom":"1px solid #f0f2f7"}) for n in reversed(notes_log)]
    else:
        note_items=[html.Div(ct("no_notes",lc),style={"color":"#aaa","fontSize":"0.85rem","padding":"10px 0"})]

    # ── Old free-text note (backward compat)
    legacy_note = []
    if c.get("note") and not notes_log:
        legacy_note = [
            html.Div(ct("sec_notes",lc),style={"fontSize":"0.72rem","fontWeight":"700","color":"#999",
                                               "textTransform":"uppercase","letterSpacing":"0.06em","marginBottom":"6px"}),
            html.Div(c["note"],style={"background":"#f8f9fb","borderRadius":"10px","padding":"12px",
                                      "fontSize":"0.88rem","color":"#444","lineHeight":"1.6",
                                      "whiteSpace":"pre-wrap","border":"1px solid #eaecf2","marginBottom":"12px"}),
        ]

    # ── Alerta vigent
    alerta_motiu = c.get("alerta_motiu","")
    alert_banner = []
    if fd:
        alert_banner = [html.Div([
            html.Span("🔔 ",style={"fontSize":"1rem"}),
            html.Span(fd.strftime("%d/%m/%Y"),style={"fontWeight":"700","color":fu_color,"fontSize":"0.95rem"}),
            html.Span(f"  —  {alerta_motiu}" if alerta_motiu else "",
                      style={"color":"#666","fontSize":"0.85rem","marginLeft":"8px"}),
        ],style={"background":"#fff8e1","border":f"1px solid {fu_color}44","borderRadius":"10px",
                 "padding":"10px 16px","marginBottom":"12px"})]

    # ── Note type options
    note_type_opts=[{"label":f"{_NOTE_ICONS[k]} {ct('nt_'+k,lc)}","value":k} for k,_ in _NOTE_TYPES]

    return html.Div([
        # Header: fase + durada
        html.Div([
            html.Span(slabel(stage,lc),className="stage-pill",
                      style={"background":color_s+"22","color":color_s,"border":f"1px solid {color_s}55",
                             "fontSize":"0.85rem","padding":"5px 14px"}),
            html.Span(f"  ·  {ct('f_data1',lc)}: {c.get('data_primo_contatto','—')}",
                      style={"fontSize":"0.82rem","color":"#888","marginLeft":"12px"}),
            html.Span(f"  ·  {durada_str} al CRM",style={"fontSize":"0.82rem","color":"#888"}),
        ],style={"marginBottom":"20px"}),

        # Dades — 2 columnes
        dbc.Row([
            dbc.Col([
                html.H6("👤 Perfil",style={"fontWeight":"700","color":"#1e2235","marginBottom":"10px"}),
                row(ct("f_eta",lc),    f"{c.get('eta','—')} anys"),
                row(ct("f_sesso",lc),  ct("f_sesso_m",lc) if c.get("sesso")=="M" else ct("f_sesso_f",lc)),
                row(ct("f_canton",lc), c.get("canton","—")),
                row(ct("f_situ",lc),   c.get("situazione","—")),
                row(ct("f_sc",lc),     c.get("stato_civile","—")),
                row(ct("f_figli",lc),  f"{c.get('n_figli',0)} fills" if c.get("figli") else ct("no",lc)),
                row(ct("f_ipoteca",lc),ct("yes",lc) if c.get("ipoteca") else ct("no",lc)),
                row(ct("f_rischio",lc),c.get("tolleranza_rischio","—")),
            ],width=5),
            dbc.Col([
                html.H6("💼 CRM & Productes",style={"fontWeight":"700","color":"#1e2235","marginBottom":"10px"}),
                row(ct("f_reddito",lc), f"CHF {c.get('reddito_mensile',0):,}/mes"),
                row(ct("f_lang",lc),    c.get("lc","—").upper()),
                row(ct("f_tel",lc),     c.get("telefono","") or "—"),
                row("Email",            c.get("email","") or "—"),
                row(ct("f_valore",lc),  f"CHF {c.get('valore_stimato',0):,}/any" if c.get("valore_stimato") else "—"),
                row(ct("f_followup",lc),fu_str,color=fu_color),
                html.Div(style={"marginTop":"14px"}),
                html.Div(ct("f_prodotto",lc),
                         style={"fontSize":"0.72rem","fontWeight":"700","color":"#999",
                                "textTransform":"uppercase","letterSpacing":"0.06em","marginBottom":"6px"}),
                html.Div(c.get("prodotto_contrattato","") or "—",
                         style={"background":"#fde8e8","color":"#c0392b","padding":"8px 12px",
                                "borderRadius":"8px","fontSize":"0.88rem","fontWeight":"600",
                                "border":"1px solid #f5c6c0"} if c.get("prodotto_contrattato") else
                               {"color":"#aaa","fontSize":"0.88rem"}),
            ],width=7),
        ]),

        html.Hr(style={"margin":"20px 0"}),

        # ── Suggeriments de productes
        html.H6(ct("sugg_title",lc),style={"fontWeight":"700","color":"#1e2235","marginBottom":"10px"}),
        html.Div([html.Div([
            html.Div([
                html.Span(s["p"]["icon"]+" ",style={"fontSize":"1.05rem"}),
                html.Span(s["p"]["name"].get(lc,s["p"]["name"]["it"]),
                          style={"fontWeight":"700","color":"#27ae60" if s["already"] else "#1e2235","fontSize":"0.88rem"}),
                html.Span(f"  {ct('sugg_already',lc)}" if s["already"] else "",
                          style={"fontSize":"0.72rem","color":"#27ae60","marginLeft":"6px","fontStyle":"italic"}),
                # Botó "Veure detall" alineat a la dreta
                dbc.Button("📋 Detall",
                           id={"type":"btn-prod","index":s["p"]["id"]},
                           size="sm", color="light", outline=True,
                           style={"fontSize":"0.72rem","marginLeft":"auto","padding":"2px 8px",
                                  "float":"right","marginTop":"-2px"}),
            ],style={"display":"flex","alignItems":"center"}),
            html.Div(s["p"]["desc"].get(lc,s["p"]["desc"]["it"]),
                     style={"fontSize":"0.78rem","color":"#888","marginTop":"4px","lineHeight":"1.45"}),
        ],style={"padding":"8px 12px","borderRadius":"8px","marginBottom":"6px",
                 "background":"#f0fdf4" if s["already"] else "#f8f9fb",
                 "border":f"1px solid {'#bbf7d0' if s['already'] else '#eaecf2'}",
                 "opacity":"1" if s["fits"] else "0.45"})
        for s in _get_suggestions(c,lc)[:5]],style={"marginBottom":"4px"}),

        html.Hr(style={"margin":"20px 0"}),

        # ── Historial d'interaccions
        html.H6(ct("sec_log",lc),style={"fontWeight":"700","color":"#1e2235","marginBottom":"10px"}),
        *legacy_note,
        html.Div(note_items,style={"maxHeight":"220px","overflowY":"auto","paddingRight":"4px"}),

        html.Hr(style={"margin":"20px 0"}),

        # ── Afegir nota
        html.H6(ct("sec_add_note",lc),style={"fontWeight":"700","color":"#1e2235","marginBottom":"12px"}),
        dbc.Row([
            dbc.Col(dbc.Select(id="info-note-type",options=note_type_opts,value="nota",
                               style={"fontSize":"0.85rem"}),width=3),
            dbc.Col(dbc.Textarea(id="info-note-text",placeholder=ct("note_new_ph",lc),
                                 style={"fontSize":"0.87rem","borderRadius":"8px","border":"1px solid #e0e3ec",
                                        "padding":"8px","minHeight":"72px","resize":"vertical"}),width=9),
        ],className="mb-3"),

        # ── Alerta / pròxim contacte
        html.H6(ct("sec_alert",lc),style={"fontWeight":"700","color":"#1e2235","marginBottom":"8px"}),
        *alert_banner,
        dbc.Row([
            dbc.Col([
                html.Div(ct("f_followup",lc),className="crm-form-label"),
                dbc.Input(id="info-alert-date",type="date",value=fd.isoformat() if fd else "",
                          style={"fontSize":"0.87rem"}),
            ],width=3),
            dbc.Col([
                html.Div(ct("alert_motiu_ph",lc),className="crm-form-label"),
                dbc.Input(id="info-alert-motiu",value=alerta_motiu,
                          placeholder=ct("alert_motiu_ph",lc),style={"fontSize":"0.87rem"}),
            ],width=9),
        ]),
        html.Div(style={"height":"8px"}),  # spacing before footer
    ])


# ── INFO FITXA CLIENT — callback ──────────────────────────────────────────────
@callback(
    Output("info-modal","is_open"),
    Output("info-title","children"),
    Output("info-body","children"),
    Output("info-nome","data"),
    Input({"type":"btn-info","index":ALL},"n_clicks"),
    State("crm-lang","data"),
    prevent_initial_call=True,
)
def open_info(n_list, lc):
    lc=lc or "it"; tid=ctx.triggered_id
    # FIX: ignora el render inicial (n_clicks=None)
    if not isinstance(tid,dict) or not (ctx.triggered or [{}])[0].get("value"):
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    nome=tid["index"]; c=get_client(nome)
    if not c: return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    return True, f"👤 {nome}", _render_info_body(c,lc), nome


# ── SAVE NOTA + ALERTA ────────────────────────────────────────────────────────
@callback(
    Output("info-note-msg","children"),
    Output("crm-reload","data",allow_duplicate=True),
    Output("info-body","children",allow_duplicate=True),
    Input("btn-save-note","n_clicks"),
    State("info-nome","data"),
    State("info-note-type","value"),
    State("info-note-text","value"),
    State("info-alert-date","value"),
    State("info-alert-motiu","value"),
    State("crm-reload","data"),
    State("crm-lang","data"),
    prevent_initial_call=True,
)
def save_note(n, nome, tipus, text, alert_date, alert_motiu, rn, lc):
    lc = lc or "it"
    if not n or not nome: return dash.no_update, dash.no_update, dash.no_update
    c = get_client(nome)
    if not c: return dash.no_update, dash.no_update, dash.no_update

    msgs=[]; changed=False

    # Afegir entrada al log
    if text and text.strip():
        c.setdefault("notes_log",[]).append({
            "data": date.today().isoformat(),
            "tipus": tipus or "nota",
            "text": text.strip(),
        })
        msgs.append(ct("note_saved",lc)); changed=True

    # Actualitzar alerta
    old_date = c.get("data_prossimo_followup","")
    old_motiu= c.get("alerta_motiu","")
    new_date  = alert_date or ""
    new_motiu = alert_motiu or ""
    if new_date!=old_date or new_motiu!=old_motiu:
        c["data_prossimo_followup"] = new_date
        c["alerta_motiu"]           = new_motiu
        if new_date: msgs.append(ct("alert_saved",lc))
        changed=True

    if not changed:
        return ct("no_change",lc), dash.no_update, dash.no_update

    upsert_client(c)
    return "  ✦  ".join(msgs), (rn or 0)+1, _render_info_body(c,lc)

# ── SAVE — FIX: tanca modal automàticament ───────────────────────────────────
@callback(
    Output("modal-msg","children"),
    Output("crm-reload","data"),
    Output("edit-modal","is_open",allow_duplicate=True),
    Input("btn-save","n_clicks"),
    State("edit-nome","data"),
    State("cf-nome","value"),State("cf-eta","value"),State("cf-sesso","value"),
    State("cf-tel","value"),State("cf-email","value"),State("cf-canton","value"),
    State("cf-lc","value"),State("cf-reddito","value"),State("cf-situ","value"),
    State("cf-sc","value"),State("cf-figli","value"),State("cf-nfigli","value"),
    State("cf-ipot","value"),State("cf-stage","value"),State("cf-rischio","value"),
    State("cf-valore","value"),State("cf-data1","value"),State("cf-followup","value"),
    State("cf-prodotto","value"),State("cf-note","value"),
    State("crm-reload","data"),State("crm-lang","data"),
    prevent_initial_call=True,
)
def save(n,edit_nome,nome,eta,sesso,tel,email,canton,lc_c,reddito,situ,sc,figli,
         nfigli,ipot,stage,rischio,valore,data1,followup,prodotto,note,rn,lc):
    lc=lc or "it"
    if not n or not nome: return ct("err_name",lc), dash.no_update, dash.no_update
    e=_default({"nome":nome.strip(),"eta":int(eta or 30),"sesso":sesso or "M",
                "telefono":tel or "","email":email or "","canton":canton or "Zürich",
                "lc":lc_c or "it","reddito_mensile":int(reddito or 0),
                "situazione":situ or "Dipendente","stato_civile":sc or "Single",
                "figli":figli=="Si","n_figli":int(nfigli or 0),"ipoteca":ipot=="Si",
                "tolleranza_rischio":rischio or "Media","pipeline_stage":stage or "lead",
                "valore_stimato":int(valore or 0),"data_primo_contatto":data1 or date.today().isoformat(),
                "data_prossimo_followup":followup or "","prodotto_contrattato":prodotto or "",
                "note":note or "","data_salvataggio":date.today().isoformat()})
    upsert_client(e)
    return ct("saved_ok",lc), (rn or 0)+1, False  # ← tanca modal ✅

# ── DELETE ───────────────────────────────────────────────────────────────────
@callback(
    Output("del-modal","is_open"),
    Output("del-text","children"),
    Output("del-nome","data"),
    Output("crm-reload","data",allow_duplicate=True),
    Input({"type":"btn-delete","index":ALL},"n_clicks"),
    Input("btn-del-cancel","n_clicks"),
    Input("btn-del-ok","n_clicks"),
    State("del-nome","data"),State("crm-reload","data"),State("crm-lang","data"),
    prevent_initial_call=True,
)
def delete_flow(nd,nc,nok,nome_s,rn,lc):
    lc=lc or "it"; tid=ctx.triggered_id
    if tid=="btn-del-cancel": return False, dash.no_update, None, dash.no_update
    if tid=="btn-del-ok" and nome_s:
        delete_client(nome_s); return False, dash.no_update, None, (rn or 0)+1
    if isinstance(tid,dict) and tid.get("type")=="btn-delete":
        if not (ctx.triggered or [{}])[0].get("value"):
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        nome=tid["index"]
        return True, ct("del_text",lc).format(n=nome), nome, dash.no_update
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# ── PRODUCT DETAIL ───────────────────────────────────────────────────────────
def _thS():
    return {"fontSize":"0.68rem","color":"#999","fontWeight":"700","textTransform":"uppercase",
            "padding":"8px 10px","background":"#fafbfc","letterSpacing":"0.05em"}

def _rec_box(lines, color="#1e40af"):
    text = "\n".join(lines)
    return html.Div(style={
        "background":"#eff6ff","borderLeft":f"4px solid {color}",
        "borderRadius":"0 8px 8px 0","padding":"12px 16px","marginTop":"10px",
        "fontSize":"0.87rem","color":"#1e2235","lineHeight":"1.75","whiteSpace":"pre-line"},
        children=text)

def _mod_table(rows):
    # rows: (name, description, cost_label, highlight?)
    return html.Table([
        html.Thead(html.Tr([
            html.Th("Modalitat",      style=_thS()),
            html.Th("Característiques",style=_thS()),
            html.Th("Cost indicatiu", style={**_thS(),"whiteSpace":"nowrap"}),
        ])),
        html.Tbody([html.Tr([
            html.Td([html.Span("⭐ " if r[3] else "· ",
                               style={"color":"#f59e0b" if r[3] else "#ccc"}),
                     html.Span(r[0], style={"fontWeight":"700" if r[3] else "400"})],
                    style={"padding":"9px 10px","fontSize":"0.87rem",
                           "background":"#fffbeb" if r[3] else "","borderBottom":"1px solid #f0f2f7"}),
            html.Td(r[1], style={"padding":"9px 10px","fontSize":"0.83rem","color":"#444",
                                 "background":"#fffbeb" if r[3] else "","borderBottom":"1px solid #f0f2f7"}),
            html.Td(r[2], style={"padding":"9px 10px","fontSize":"0.82rem","color":"#888",
                                 "background":"#fffbeb" if r[3] else "","borderBottom":"1px solid #f0f2f7",
                                 "whiteSpace":"nowrap"}),
        ]) for r in rows]),
    ], style={"width":"100%","borderCollapse":"collapse","border":"1px solid #eaecf2",
              "borderRadius":"8px","overflow":"hidden"})

def _sec_pd(title, children):
    return html.Div([
        html.Div(title, style={"fontSize":"0.72rem","fontWeight":"700","color":"#999",
                               "textTransform":"uppercase","letterSpacing":"0.07em",
                               "marginBottom":"8px","marginTop":"18px"}),
        *children,
    ])

def _proj_table(rows_mese_cap, highlight_mese):
    return html.Table([
        html.Thead(html.Tr([html.Th("Import/mes",style=_thS()),html.Th("Capital estimat a 65a",style=_thS())])),
        html.Tbody([html.Tr([
            html.Td(f"CHF {m}/mes",style={"fontWeight":"700","color":"#c0392b","padding":"8px 10px"} if m==highlight_mese
                                    else {"padding":"8px 10px","fontSize":"0.87rem"}),
            html.Td(f"CHF {cap:,}",style={"fontWeight":"700","color":"#c0392b","padding":"8px 10px"} if m==highlight_mese
                                    else {"padding":"8px 10px","fontSize":"0.87rem"}),
        ]) for m,cap in rows_mese_cap],),
    ],style={"width":"100%","borderCollapse":"collapse","border":"1px solid #eaecf2","borderRadius":"8px","overflow":"hidden"})

def _prod_detail(prod_id, c, lc):
    lc = lc or "it"
    eta      = int(c.get("eta") or 40)
    reddito  = int(c.get("reddito_mensile") or 0)
    situ     = c.get("situazione","")
    rischio  = c.get("tolleranza_rischio","Media")
    has_fil  = bool(c.get("figli"))
    has_ipo  = bool(c.get("ipoteca"))
    n_figli  = int(c.get("n_figli") or 0)
    nome     = c.get("nome","—")

    def pv(m, anni, rate=0.015):
        if anni <= 0 or m <= 0: return 0
        return int(m * 12 * ((1+rate)**anni - 1) / rate)

    # ── 3° Pilastro ──────────────────────────────────────────────────────────
    if prod_id == "3p":
        anni     = max(65 - eta, 0)
        max_ann  = 35280 if situ=="Indipendente" else 7056
        max_mese = max_ann // 12
        sugg = (max_mese if reddito >= 8000 else
                400     if reddito >= 5000 else
                200     if reddito >= 3000 else 100)
        is_ass = has_fil or has_ipo
        rows_mod = [
            ("Conto bancario (3a)", "Versamenti flessibili, nessun vincolo vita. Rendimento tasso di mercato.",
             "CHF 0 spese base", not is_ass),
            ("Assicurazione (3a)", "Premio fisso, include copertura vita/invalidità integrata. Riscatto garantito.",
             f"da CHF {sugg}/mese", is_ass),
        ]
        proj = [(m, pv(m, anni)) for m in sorted({100,200,sugg,max_mese}) if m > 0]
        return html.Div([
            _sec_pd("Modalitats disponibles", [_mod_table(rows_mod)]),
            _sec_pd(f"Recomanació per {nome}", [_rec_box([
                f"📌 Import recomanat: CHF {sugg}/mes  (CHF {sugg*12:,}/any)",
                f"   → Màxim deduïble: CHF {max_mese}/mes  (CHF {max_ann:,}/any)",
                f"   → Anys restants fins 65: {anni}",
                f"   → Avantatge fiscal: deduccions directes de la base imposable",
                f"   → Modalitat: {'Assegurança (protecció vida inclosa)' if is_ass else 'Compte bancari (més flexible)'}",
            ])]),
            _sec_pd("Projecció capital a 65 anys (taxa 1.5%/any)", [_proj_table(proj, sugg)]),
        ])

    # ── Assicurazione Vita ───────────────────────────────────────────────────
    elif prod_id == "vita":
        cap     = max(200_000, reddito * 12 * 5)
        prem_p  = max(40,  int(cap / 1000 * 0.7))
        prem_m  = max(200, int(cap / 1000 * 2.5))
        rec_puro = eta < 45 or has_ipo
        return html.Div([
            _sec_pd("Modalitats", [_mod_table([
                ("Rischio puro (term life)", "Solo copertura decesso. Premio basso, nessun risparmio.",
                 f"da CHF {prem_p}/mes", rec_puro),
                ("Risparmio misto", "Copertura + componente risparmio. Riscatto garantito a scadenza.",
                 f"da CHF {prem_m}/mes", not rec_puro),
            ])]),
            _sec_pd(f"Recomanació per {nome}", [_rec_box([
                f"📌 Capital assegurat recomanat: CHF {cap:,}",
                f"   → Regla: 5× reddito annuo = CHF {reddito*12*5:,}",
                (f"   → Amb {n_figli} fill/s: mínim CHF 200.000" if has_fil else ""),
                (f"   → Amb hipoteca: cobrir almenys el deute pendent" if has_ipo else ""),
                f"   → Modalitat: {'Rischio puro — premi baixos, màxima cobertura' if rec_puro else 'Risparmio misto — també estalvi a llarg termini'}",
            ])]),
        ])

    # ── Assicurazione Invalidità ─────────────────────────────────────────────
    elif prod_id == "ai":
        ai_st = int(reddito * 0.60)
        gap   = max(0, reddito - ai_st)
        ind   = situ == "Indipendente"
        return html.Div([
            _sec_pd("Modalitats", [_mod_table([
                ("Complement AI (assalariats)", "Complementa l'AI estatal. Cobreix la llacuna fins al 80-90% del salari.",
                 f"da CHF {max(80, gap//10)}/mes", not ind),
                ("Cobertura autònoms", "Cobertura completa per a treballadors autònoms (sense AI automàtica).",
                 f"da CHF {max(150, gap//8)}/mes", ind),
            ])]),
            _sec_pd(f"Anàlisi llacuna per {nome}", [_rec_box([
                f"📌 Ingressos mensuals: CHF {reddito:,}",
                f"   → Cobertura AI estatal (~60%): CHF {ai_st:,}/mes",
                f"   → Llacuna a assegurar: CHF {gap:,}/mes",
                f"   → Cobertura recomanada: CHF {gap:,}/mes complement AI",
                ("   ⚠️  Autònom: cap AI automàtica → PRIORITAT ALTA" if ind else ""),
            ], color="#c0392b" if ind else "#1e40af")]),
        ])

    # ── Pianificazione Ipotecaria ────────────────────────────────────────────
    elif prod_id == "ipoteca":
        rec_mod = ("SARON" if rischio=="Alta" else
                   "Fisso 5 anni" if rischio=="Media" else "Fisso 10 anni")
        return html.Div([
            _sec_pd("Models de finançament", [_mod_table([
                ("Fisso 2 anni",   "Rata estable 2 anys. Renovació freqüent, bones condicions actuals.", "~1.8-2.2%/any", rischio=="Alta"),
                ("Fisso 5 anni",   "Equilibri estabilitat / flexibilitat. El més triat a Suïssa.",       "~2.0-2.5%/any", rischio=="Media"),
                ("Fisso 10 anys",  "Màxima estabilitat. Ideal si previsió de pujada de tipus.",          "~2.3-2.8%/any", rischio=="Bassa"),
                ("SARON (variable)","Tipus variable lligat al mercat. Ara convenient, però risc.",       "~1.3-1.6%/any", False),
                ("Mixt",           "50% fix + 50% SARON. Redueix volatilitat.",                         "tipus mitjà",   False),
            ])]),
            _sec_pd(f"Recomanació per {nome} (tolerància {rischio})", [_rec_box([
                f"📌 Model recomanat: {rec_mod}",
                f"   → Amortament INDIRECTE via 3° Pilar:",
                f"      En lloc d'amortitzar → versió capital al 3° Pilar",
                f"      Doble avantatge fiscal: deducció hipoteca + deducció 3° Pilar",
                f"      A 65 anys: capital disponible en comptes de deute cancel·lat",
                f"   → Comparar mínim 3 bancs / asseguradores",
            ])]),
        ])

    # ── Ottimizzazione LPP ───────────────────────────────────────────────────
    elif prod_id == "lpp":
        aliq    = (0.35 if reddito > 8000 else 0.28 if reddito > 5000 else 0.22)
        ex_comp = min(20000, reddito * 24)
        risp    = int(ex_comp * aliq)
        return html.Div([
            _sec_pd("Modalitats LPP", [_mod_table([
                ("Compres voluntàries (rescats)", "Versaments a la llacuna CP, deduïbles. Rendiment garantit CP.",
                 f"CHF 5.000-{ex_comp:,}/any", True),
                ("Retir anticipat per habitatge", "Retir parcial CP per a compra / renovació 1ª residència.",
                 "màx. 10% cada 5 anys", has_ipo),
                ("Planificació renda vs capital", "A jubilació: escollir entre renda mensual o capital únic.",
                 "depèn del pla CP", False),
            ])]),
            _sec_pd(f"Recomanació per {nome}", [_rec_box([
                f"📌 Compra voluntària exemple: CHF {ex_comp:,}/any",
                f"   → Alíquota fiscal estimada: {int(aliq*100)}%",
                f"   → Estalvi impostos immediat: CHF {risp:,}",
                f"   → Rendiment CP: ~2-3%/any (garantit)",
                f"   → Acció: sol·licitar extracte CP per calcular la llacuna exacta",
            ])]),
        ])

    # ── Hausrat + RC ─────────────────────────────────────────────────────────
    elif prod_id == "hausrat":
        val  = max(30000, reddito * 8)
        prem = 180 + min(100, reddito // 80)
        prem_pr = prem + 90
        rec_pr  = reddito >= 6000
        return html.Div([
            _sec_pd("Modalitats", [_mod_table([
                ("Standard", "Robatori, incendi, aigues. RC privada CHF 3M. Bici inclosa.",
                 f"~CHF {prem}/any", not rec_pr),
                ("Premium",  "Cobertura estesa: danys elèctrics, RC CHF 5M, assistència 24h.",
                 f"~CHF {prem_pr}/any", rec_pr),
            ])]),
            _sec_pd(f"Recomanació per {nome}", [_rec_box([
                f"📌 Valor contingut estimat: CHF {val:,}",
                f"   → Model recomanat: {'Premium' if rec_pr else 'Standard'}",
                f"   → Prima estimada: CHF {prem_pr if rec_pr else prem}/any",
                f"   → RC privada: indispensable (cobreix danys a tercers involuntaris)",
                f"   → Sovint inclòs en pack amb assegurança de malaltia → descomptes",
            ])]),
        ])

    # ── Cassa Malati ─────────────────────────────────────────────────────────
    elif prod_id == "malattia":
        franc_rec = (2500 if reddito >= 7000 else 1500 if reddito >= 5000
                     else 1000 if reddito >= 3000 else 500)
        mod_rec = ("HMO" if reddito >= 5000 else "Telmed" if reddito >= 3000 else "Standard")
        risp_franc = max(0, (franc_rec - 300) // 300 * 60)
        return html.Div([
            _sec_pd("Models LAMal", [_mod_table([
                ("HMO",      "Metge de referència HMO. Primes -15/20% vs estàndard. Limitació llibertat elecció.",
                 "-15-20% prima", reddito >= 5000),
                ("Telmed",   "Primera consulta per telèfon. Bon equilibri cost/flexibilitat.",
                 "-10-15% prima", 3000 <= reddito < 5000),
                ("Estàndard","Llibertat total d'elecció metge. Prima màxima.",
                 "prima base 100%", reddito < 3000),
            ])]),
            _sec_pd("Franquícia recomanada", [
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Franquícia",        style=_thS()),
                        html.Th("Estalvi primes/any", style=_thS()),
                        html.Th("Recomanat si…",      style=_thS()),
                    ])),
                    html.Tbody([html.Tr([
                        html.Td(f"CHF {f}",
                                style={"fontWeight":"700","color":"#c0392b","padding":"8px 10px",
                                       "background":"#fde8e8"} if f==franc_rec
                                       else {"padding":"8px 10px","fontSize":"0.87rem"}),
                        html.Td(f"CHF {max(0,(f-300)//300*60)}/any",
                                style={"padding":"8px 10px","fontSize":"0.87rem"}),
                        html.Td("Pocs visites/any" if f >= 1500 else "Ús mèdic habitual",
                                style={"padding":"8px 10px","fontSize":"0.82rem","color":"#888"}),
                    ]) for f in [300,500,1000,1500,2000,2500]]),
                ],style={"width":"100%","borderCollapse":"collapse","border":"1px solid #eaecf2","borderRadius":"8px","overflow":"hidden","marginBottom":"8px"}),
                _rec_box([
                    f"📌 Franquícia recomanada: CHF {franc_rec}",
                    f"   → Model: {mod_rec}",
                    f"   → Estalvi estimat vs CHF 300: CHF {risp_franc}/any",
                    f"   → Comparar anualment (canvi lliure a l'octubre)",
                ]),
            ]),
        ])

    return html.Div("—")


@callback(
    Output("prod-modal","is_open"),
    Output("prod-title","children"),
    Output("prod-body","children"),
    Input({"type":"btn-prod","index":ALL},"n_clicks"),
    State("info-nome","data"),
    State("crm-lang","data"),
    prevent_initial_call=True,
)
def open_prod_detail(n_list, nome, lc):
    lc = lc or "it"; tid = ctx.triggered_id
    if not isinstance(tid,dict) or not (ctx.triggered or [{}])[0].get("value"):
        return dash.no_update, dash.no_update, dash.no_update
    prod_id = tid["index"]
    p = next((x for x in PRODUCTS if x["id"]==prod_id), None)
    if not p: return dash.no_update, dash.no_update, dash.no_update
    c = get_client(nome) if nome else {}
    name = p["name"].get(lc, p["name"]["it"])
    return True, f"{p['icon']} {name}", _prod_detail(prod_id, c or {}, lc)

# ── RELAY list-new-btn → open_modal ──────────────────────────────────────────
@callback(Output("new-relay","data"),
          Input("list-new-btn","n_clicks"),
          State("new-relay","data"), prevent_initial_call=True)
def relay_new(n, cur):
    return (cur or 0)+1 if n else dash.no_update

# ── KANBAN DRAG & DROP — setup event listeners ────────────────────────────────
app.clientside_callback(
    """
    function(children) {
        document.removeEventListener('dragstart', window._crmDs);
        document.removeEventListener('dragend',   window._crmDe);
        document.removeEventListener('dragover',  window._crmDo);
        document.removeEventListener('dragleave', window._crmDl);
        document.removeEventListener('drop',      window._crmDr);

        window._crmDs = function(e) {
            var card = e.target.closest('[data-drag]');
            if (!card) return;
            e.dataTransfer.setData('text/plain', card.getAttribute('data-drag'));
            card.style.opacity = '0.45';
        };
        window._crmDe = function(e) {
            var card = e.target.closest('[data-drag]');
            if (card) card.style.opacity = '1';
        };
        window._crmDo = function(e) {
            var col = e.target.closest('[data-drop]');
            if (!col) return;
            e.preventDefault();
            col.style.outline = '2px dashed #c0392b';
            col.style.background = '#fff5f5';
        };
        window._crmDl = function(e) {
            var col = e.target.closest('[data-drop]');
            if (col && !col.contains(e.relatedTarget)) {
                col.style.outline = ''; col.style.background = '';
            }
        };
        window._crmDr = function(e) {
            var col = e.target.closest('[data-drop]');
            if (!col) return;
            e.preventDefault();
            col.style.outline = ''; col.style.background = '';
            var nome  = e.dataTransfer.getData('text/plain');
            var stage = col.getAttribute('data-drop');
            if (nome && stage) {
                window.dash_clientside.set_props('kanban-drop',
                    {data: {nome: nome, stage: stage, ts: Date.now()}});
            }
        };
        document.addEventListener('dragstart', window._crmDs);
        document.addEventListener('dragend',   window._crmDe);
        document.addEventListener('dragover',  window._crmDo);
        document.addEventListener('dragleave', window._crmDl);
        document.addEventListener('drop',      window._crmDr);
        return window.dash_clientside.no_update;
    }
    """,
    Output("dnd-setup","data"),
    Input("crm-content","children"),
    prevent_initial_call=True,
)

# ── KANBAN DROP — actualitza pipeline stage ───────────────────────────────────
@callback(Output("crm-reload","data",allow_duplicate=True),
          Input("kanban-drop","data"),
          State("crm-reload","data"), prevent_initial_call=True)
def kanban_drop(drop, rn):
    if not drop or not drop.get("nome") or not drop.get("stage"): return dash.no_update
    nome=drop["nome"]; stage=drop["stage"]
    if stage not in STAGE_KEYS: return dash.no_update
    c=get_client(nome)
    if not c: return dash.no_update
    c["pipeline_stage"]=stage
    c=_default(c); upsert_client(c)
    return (rn or 0)+1

# ── TAB 5: PRODUCTES ─────────────────────────────────────────────────────────
def render_products(lc):
    lc=lc or "it"; cs=load_clients()
    cards=[]
    for p in PRODUCTS:
        # Quants clients encaixen + quants ja el tenen
        n_fit=sum(1 for c in cs if _safe_fit(p,c))
        prodotto_set={(c.get("prodotto_contrattato","") or "").lower() for c in cs}
        n_has=sum(1 for c in cs if p["id"] in (c.get("prodotto_contrattato","") or "").lower())
        name=p["name"].get(lc,p["name"]["it"])
        desc=p["desc"].get(lc,p["desc"]["it"])
        cards.append(dbc.Col(html.Div([
            html.Div([html.Span(p["icon"],style={"fontSize":"2rem","marginRight":"12px"}),
                      html.Div([html.Div(name,style={"fontWeight":"800","fontSize":"1.05rem","color":"#1e2235"}),
                                html.Div(f"{n_fit} {ct('prod_clients',lc)} encaixen · {n_has} actuals",
                                         style={"fontSize":"0.75rem","color":"#888","marginTop":"2px"})]),
                     ],style={"display":"flex","alignItems":"center","marginBottom":"14px"}),
            html.Div(desc,style={"fontSize":"0.87rem","color":"#444","lineHeight":"1.65"}),
        ],className="c-card",style={"height":"100%"}),width=6,className="mb-3"))

    return html.Div([
        html.Div([html.Div(ct("prod_title",lc),style={"fontSize":"1.4rem","fontWeight":"800","color":"#1e2235"}),
                  html.Div(ct("prod_sub",lc),  style={"color":"#aaa","fontSize":"0.8rem"})],
                 style={"marginBottom":"24px"}),
        dbc.Row(cards),
    ])

def _safe_fit(p,c):
    try: return p["fit"](c)
    except Exception: return True

# ── SUGGERIMENTS de productes per perfil ─────────────────────────────────────
def _get_suggestions(c, lc):
    lc=lc or "it"
    prodotto=(c.get("prodotto_contrattato","") or "").lower()
    result=[]
    for p in PRODUCTS:
        fits=_safe_fit(p,c)
        already=p["id"] in prodotto
        result.append({"p":p,"fits":fits,"already":already})
    result.sort(key=lambda x:(not x["fits"],x["already"]))
    return result

# ── DOWNLOAD — report post-riunione ──────────────────────────────────────────
@callback(Output("meet-dl","data"),
          Input("btn-download","n_clicks"),
          State("info-nome","data"), State("crm-lang","data"),
          prevent_initial_call=True)
def download_report(n, nome, lc):
    if not n or not nome: return dash.no_update
    c=get_client(nome)
    if not c: return dash.no_update
    lc=lc or "it"; today=date.today()
    lines=[
        "="*56,
        f"  SVAG · Consulenza Finanziaria Svizzera",
        f"  {ct('dl_profile',lc)}: {nome}",
        f"  Data: {today.strftime('%d/%m/%Y')}",
        "="*56,"",
        f"─── {ct('dl_profile',lc)} ───",
        f"Età:       {c.get('eta','—')}  |  Sesso: {'M' if c.get('sesso')=='M' else 'F'}",
        f"Cantone:   {c.get('canton','—')}",
        f"Situazione:{c.get('situazione','—')}  |  Reddito: CHF {c.get('reddito_mensile',0):,}/m",
        f"Figli:     {'Sì' if c.get('figli') else 'No'}  |  Ipoteca: {'Sì' if c.get('ipoteca') else 'No'}",
        f"Rischio:   {c.get('tolleranza_rischio','—')}",
        f"Tel:       {c.get('telefono','—')}  |  Email: {c.get('email','—')}","",
        f"─── {ct('dl_notes',lc)} ───",
    ]
    # Notes log — solo ultime 3 riunioni
    notes_log=c.get("notes_log",[])
    meet_notes=[n for n in notes_log if n.get("tipus")=="reunio"][-3:] or notes_log[-3:]
    if meet_notes:
        for n2 in reversed(meet_notes):
            lines.append(f"[{n2.get('data','')}] {n2.get('text','')}")
    elif c.get("note"):
        lines.append(c["note"][:400])
    else:
        lines.append("—")
    lines+=["",f"─── {ct('dl_products',lc)} ───"]
    if c.get("prodotto_contrattato"):
        lines.append(f"✅ Contrattato: {c['prodotto_contrattato']}")
    sugg=[s for s in _get_suggestions(c,lc) if s["fits"] and not s["already"]][:4]
    for s in sugg:
        lines.append(f"⭐ {s['p']['name'].get(lc,s['p']['name']['it'])}")
    lines+=["",f"─── {ct('dl_next',lc)} ───"]
    fd=_fu(c)
    if fd:
        lines.append(f"Data:   {fd.strftime('%d/%m/%Y')}")
        if c.get("alerta_motiu"): lines.append(f"Motivo: {c['alerta_motiu']}")
    else:
        lines.append("—")
    lines+=["","─"*56,
            "  Alex Bevilacqua · SVAG · www.svag.ch",
            "─"*56]
    content="\n".join(lines)
    fname=f"SVAG_{nome.replace(' ','_')}_{today.isoformat()}.txt"
    return dict(content=content, filename=fname)

# ── MAIN ─────────────────────────────────────────────────────────────────────
if __name__=="__main__":
    debug=os.environ.get("DASH_DEBUG","true").lower()=="true"
    print(f"\n✅  AlexFin CRM  →  http://localhost:{PORT}")
    print(f"   Login: {AUTH_USER} / {AUTH_PASS}")
    print(f"   Idiomes: IT · DE · FR · EN · CA\n")
    app.run(debug=debug,port=PORT,host="0.0.0.0")
