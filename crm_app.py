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

# ── I18N ────────────────────────────────────────────────────────────────────
_T = {
    "nav_dash":       {"it":"📊 Dashboard","de":"📊 Übersicht","fr":"📊 Tableau","en":"📊 Dashboard","ca":"📊 Tauler"},
    "nav_clients":    {"it":"👥 Clienti","de":"👥 Kunden","fr":"👥 Clients","en":"👥 Clients","ca":"👥 Clients"},
    "nav_pipeline":   {"it":"📋 Pipeline","de":"📋 Pipeline","fr":"📋 Pipeline","en":"📋 Pipeline","ca":"📋 Pipeline"},
    "nav_agenda":     {"it":"📅 Agenda","de":"📅 Agenda","fr":"📅 Agenda","en":"📅 Agenda","ca":"📅 Agenda"},
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
    ], id="info-modal", size="lg", scrollable=True, is_open=False),
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
        html.A(ct("nav_agenda",lc),  id="nav-agenda",   className="crm-nav-link",href="#"),
        html.A(ct("nav_new",lc),     id="btn-new",      className="crm-nav-link",href="#",
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
          State("active-tab","data"), prevent_initial_call=True)
def switch_tab(a,b,c,d,cur):
    m={"nav-dashboard":"tab-dash","nav-clienti":"tab-list","nav-pipeline":"tab-kanban","nav-agenda":"tab-agenda"}
    return m.get(ctx.triggered_id, cur or "tab-dash")

# ── MAIN CONTENT ─────────────────────────────────────────────────────────────
@callback(Output("crm-content","children"),
          Input("active-tab","data"), Input("crm-reload","data"),
          Input("crm-lang","data"),   Input("crm-tick","n_intervals"))
def render_content(tab, _r, lc, _t):
    lc=lc or "it"; cs=load_clients()
    if tab=="tab-list":   return render_list(cs,lc)
    if tab=="tab-kanban": return render_kanban(cs,lc)
    if tab=="tab-agenda": return render_agenda(cs,lc)
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

# ── TAB 3: KANBAN ────────────────────────────────────────────────────────────
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
        ],className="kanban-card") for c in by[key]]
        tv=sum(c.get("valore_stimato",0) for c in by[key])
        cols.append(dbc.Col(html.Div([
            html.Div([html.Span(slabel(key,lc),className="kanban-col-title",
                                style={"borderBottomColor":color,"color":color}),
                      html.Span(f" {len(by[key])}",style={"color":color,"fontWeight":"800","fontSize":"0.9rem"}),
                      html.Span(f"  CHF {tv:,}" if tv else "",style={"fontSize":"0.72rem","color":"#aaa","marginLeft":"8px"})]),
            *cards,
            html.Div("—",style={"color":"#ddd","textAlign":"center","marginTop":"20px","fontSize":"0.8rem"}) if not cards else html.Div(),
        ],className="kanban-col"),width=2))

    return html.Div([
        html.Div([html.Div(ct("pipeline_title",lc),style={"fontSize":"1.4rem","fontWeight":"800","color":"#1e2235"}),
                  html.Div(f"{len(cs)} {ct('list_in_crm',lc)}",style={"color":"#aaa","fontSize":"0.8rem"})],
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
                      html.Div(c.get("note","")[:80]+("…" if len(c.get("note",""))>80 else ""),
                               style={"fontSize":"0.72rem","color":"#bbb","marginTop":"2px"}) if c.get("note") else html.Div()]),
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
          Output("del-modal-hdr","children"),
          Input("crm-lang","data"))
def modal_labels(lc):
    lc=lc or "it"
    return ct("btn_cancel",lc),ct("btn_save",lc),ct("btn_cancel",lc),ct("btn_delete",lc),ct("del_title",lc)

# ── OPEN EDIT MODAL — btn-new sempre al DOM (navbar) ─────────────────────────
@callback(
    Output("edit-modal","is_open"),
    Output("modal-body","children"),
    Output("modal-title","children"),
    Output("edit-nome","data"),
    Input("btn-new",                       "n_clicks"),   # navbar — sempre DOM ✅
    Input({"type":"btn-edit","index":ALL}, "n_clicks"),   # pattern-matching ✅
    Input("btn-cancel",                    "n_clicks"),
    Input("btn-save",                      "n_clicks"),
    State("crm-lang","data"),
    prevent_initial_call=True,
)
def open_modal(n_new, n_edit, n_cancel, n_save, lc):
    lc=lc or "it"; tid=ctx.triggered_id
    if tid in ("btn-cancel","btn-save") or tid is None:
        return False, dash.no_update, dash.no_update, None
    if tid == "btn-new":
        return True, _form(None,lc), ct("modal_new",lc), None
    if isinstance(tid,dict) and tid.get("type")=="btn-edit":
        nome=tid["index"]; c=get_client(nome)
        return True, _form(c,lc), f"{ct('modal_edit',lc)} — {nome}", nome
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update


# ── INFO FITXA CLIENT ─────────────────────────────────────────────────────────
@callback(
    Output("info-modal","is_open"),
    Output("info-title","children"),
    Output("info-body","children"),
    Input({"type":"btn-info","index":ALL},"n_clicks"),
    State("crm-lang","data"),
    prevent_initial_call=True,
)
def open_info(n_list, lc):
    lc=lc or "it"; tid=ctx.triggered_id
    if not isinstance(tid,dict) or not any(n for n in (n_list or []) if n):
        return dash.no_update, dash.no_update, dash.no_update
    nome=tid["index"]; c=get_client(nome)
    if not c: return dash.no_update, dash.no_update, dash.no_update

    # Dades
    def row(label,value,color=None):
        return html.Div([
            html.Span(label,style={"fontSize":"0.72rem","fontWeight":"700","color":"#999",
                                   "textTransform":"uppercase","letterSpacing":"0.06em","minWidth":"160px","display":"inline-block"}),
            html.Span(str(value) if value else "—",
                      style={"fontWeight":"600","color":color or "#1e2235"}),
        ], style={"padding":"7px 0","borderBottom":"1px solid #f5f5f5"})

    stage=c.get("pipeline_stage","lead")
    color_s=STAGE_COLORS.get(stage,"#888")
    fd=_fu(c); today=date.today()
    fu_color="#e74c3c" if (fd and fd<today) else ("#f39c12" if fd==today else "#1e2235")
    fu_str=fd.strftime("%d/%m/%Y") if fd else "—"

    # Anys com a client
    try:
        d0=date.fromisoformat(c.get("data_primo_contatto","") or c.get("data_salvataggio",""))
        delta=(today-d0).days
        years=delta//365; months=(delta%365)//30
        durada_str=f"{years}a {months}m" if years else f"{months}m" if months else f"{delta}d"
    except Exception:
        durada_str="—"

    body=html.Div([
        # Header colorat amb fase
        html.Div([
            html.Span(slabel(stage,lc),className="stage-pill",
                      style={"background":color_s+"22","color":color_s,"border":f"1px solid {color_s}55","fontSize":"0.85rem","padding":"5px 14px"}),
            html.Span(f"  ·  {ct('f_data1',lc)}: {c.get('data_primo_contatto','—')}",
                      style={"fontSize":"0.82rem","color":"#888","marginLeft":"12px"}),
            html.Span(f"  ·  {durada_str} nel CRM",style={"fontSize":"0.82rem","color":"#888"}),
        ], style={"marginBottom":"20px"}),

        dbc.Row([
            dbc.Col([
                html.H6("👤 Profilo", style={"fontWeight":"700","color":"#1e2235","marginBottom":"10px"}),
                row(ct("f_eta",lc),     f"{c.get('eta','—')} anni"),
                row(ct("f_sesso",lc),   ct("f_sesso_m",lc) if c.get("sesso")=="M" else ct("f_sesso_f",lc)),
                row(ct("f_canton",lc),  c.get("canton","—")),
                row(ct("f_situ",lc),    c.get("situazione","—")),
                row(ct("f_sc",lc),      c.get("stato_civile","—")),
                row(ct("f_figli",lc),   f"{c.get('n_figli',0)} {ct('f_nfigli',lc).lower()}" if c.get("figli") else ct("no",lc)),
                row(ct("f_ipoteca",lc), ct("yes",lc) if c.get("ipoteca") else ct("no",lc)),
                row(ct("f_rischio",lc), c.get("tolleranza_rischio","—")),
            ], width=5),
            dbc.Col([
                html.H6("💼 CRM & Prodotti", style={"fontWeight":"700","color":"#1e2235","marginBottom":"10px"}),
                row(ct("f_reddito",lc),  f"CHF {c.get('reddito_mensile',0):,}/mese"),
                row(ct("f_lang",lc),     c.get("lc","—").upper()),
                row(ct("f_tel",lc),      c.get("telefono","") or "—"),
                row("Email",             c.get("email","") or "—"),
                row(ct("f_valore",lc),   f"CHF {c.get('valore_stimato',0):,}/anno" if c.get("valore_stimato") else "—"),
                row(ct("f_followup",lc), fu_str, color=fu_color),
                html.Div(style={"marginTop":"14px"}),
                html.Div(ct("f_prodotto",lc),
                         style={"fontSize":"0.72rem","fontWeight":"700","color":"#999","textTransform":"uppercase","letterSpacing":"0.06em","marginBottom":"6px"}),
                html.Div(c.get("prodotto_contrattato","") or "—",
                         style={"background":"#fde8e8","color":"#c0392b","padding":"8px 12px",
                                "borderRadius":"8px","fontSize":"0.88rem","fontWeight":"600",
                                "border":"1px solid #f5c6c0"} if c.get("prodotto_contrattato") else
                               {"color":"#aaa","fontSize":"0.88rem"}),
            ], width=7),
        ]),

        html.Hr(style={"margin":"18px 0"}),
        html.H6(ct("sec_notes",lc),style={"fontWeight":"700","color":"#1e2235","marginBottom":"8px"}),
        html.Div(c.get("note","") or "—",
                 style={"background":"#f8f9fb","borderRadius":"10px","padding":"14px",
                        "fontSize":"0.88rem","color":"#444","lineHeight":"1.6",
                        "whiteSpace":"pre-wrap","border":"1px solid #eaecf2"}),
    ])

    return True, f"👤 {nome}", body

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
        nome=tid["index"]
        return True, ct("del_text",lc).format(n=nome), nome, dash.no_update
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# ── MAIN ─────────────────────────────────────────────────────────────────────
if __name__=="__main__":
    debug=os.environ.get("DASH_DEBUG","true").lower()=="true"
    print(f"\n✅  AlexFin CRM  →  http://localhost:{PORT}")
    print(f"   Login: {AUTH_USER} / {AUTH_PASS}")
    print(f"   Idiomes: IT · DE · FR · EN · CA\n")
    app.run(debug=debug,port=PORT,host="0.0.0.0")
