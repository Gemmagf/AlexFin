# AlexFin — Project Log & Documentació Tècnica
> Última actualització: 2026-04-20 (sessió 6b)  
> Mantenidora: Gemma Gardela  
> Client: Alex Bevilacqua, Assessor Financer SVAG (Canton Ticino, Suïssa)

---

## 📋 Changelog — Sessió 6b (2026-04-20) — Deploy Render.com

### `render.yaml` — Configuració automàtica de deploy
**Fitxer nou:** `render.yaml`  
Afegida configuració de Render.com per poder fer deploy amb un sol clic des del dashboard.

**Contingut:**
- Servei tipus `web`, runtime Python
- Build: `pip install -r requirements.txt`
- Start: `gunicorn dash_app:server --workers 1 --timeout 120`
- Pla: `free`
- Branca: `upgrade-streamlit-app`
- Variables d'entorn preconfigurades:
  - `SECRET_KEY` → generada automàticament per Render
  - `AUTH_USER` → `alex` (valor per defecte, canviable al dashboard)
  - `AUTH_PASS` → marcada com `sync: false` (cal posar-la manualment al dashboard per seguretat)

**Com fer el deploy:**
1. Ves a [render.com](https://render.com) → **New → Web Service**
2. Connecta el repo GitHub `AlexFin`
3. Render detecta el `render.yaml` automàticament
4. A la secció **Environment Variables**, posa el valor de `AUTH_PASS`
5. Fes clic a **Deploy** — l'app quedarà pública amb login protegit

**Fitxers canviats:** `render.yaml` (nou)

---

## 📋 Changelog — Sessió 6 (2026-04-20)

### i18n complet — totes les pàgines 100% traduïdes
**Problema:** Després de les correccions anteriors, quedaven centenars de strings hardcoded en italià a totes les pàgines: etiquetes CRM, temes de la checklist, boto PDF, gràfics, formularis SMTP, taules de pressupost, categories de prospecting, missatges d'alerta, etc.

**Solució sistemàtica — `i18n.py` _EXTRA (+60 claus noves per IT/DE/FR/EN/CA):**
- `pdf_btn`, `adv_anni`, `lacuna_obj` — botó PDF i subtítol advisor
- `rie_titolo/profilo/prio/temi/passi/note/urgenza` — capçaleres resum colloqui
- `crm_eta/reddito/situazione/appunti` — etiquetes CRM
- `smtp_porta/smtp_mittente`, `email_err_dest/smtp_cfg` — formularis SMTP
- `rac_fonte`, `adv_chf_anno`, `sim_scenario_lbl` — eixos gràfics Advisor
- `vita_sem_ok/warn/err` — semàfor budget mensual
- `vita_default_nomi` — noms objectius per defecte (llista localitzada)
- `vita_reddito_suff/deficit`, `vita_obj_raggiungibili/insufficiente` — alertes
- `vita_chf_mese_stimato/nec`, `vita_categoria`, `vita_anni_da_oggi` — taules i gràfics
- `vita_proiez_acc`, `vita_capacita_residua`, `vita_totale_risp` (ja existia)
- `prev_scen_ora/tardi/fis` — escenaris simulador 3r pilar
- `kk_ottimale`, `kk_risp_ok` — alertes Krankenkasse
- `prev_obiettivo_pct` — anotació línia objectiu gràfic de pensions
- `prosp_filter_cat`, `prosp_all_cat`, `prosp_no_results`, `prosp_spot_come_entrare`

**`dash_pages/advisor.py`:**
- `TEMI_LISTA` → `TEMI_LISTA_KEYS` amb claus i18n; labels traduïdes, value = text traduït
- CRM: labels Età/Reddito/Situazione → `t("crm_eta/reddito/situazione", lc)`
- Placeholder textarea CRM → `t("crm_appunti", lc)`
- Botó PDF → `t("pdf_btn", lc)`
- Subtítol → `{eta} {t('adv_anni', lc)}`
- Gràfic lacuna: eix Y → `t("adv_chf_anno", lc)`, labels Fonte → `t("rac_fonte", lc)`
- Simulador: columnes DataFrame → `_eta_lbl`, `_scen_lbl` dinàmics
- Formulari SMTP: Porta/Email mittente → `t("smtp_porta/mittente", lc)`
- Resum colloqui (`update_riepilogo`): tots els títols de secció → `t("rie_*", lc)`
- Email HTML (`send_email`): `lc` extret del store, tot el body traduït

**`dash_pages/vida_budget.py`:**
- Semàfor (ok/warn/err) → `t("vita_sem_*", lc, saldo=..., pct=...)` 
- Taula 50/30/20: columnes `_cat`, `_att`, `_tar` dinàmiques
- Fasi: noms categories → `t("vita_affitto/cibo/tras/...", lc)` com a claus dict
- Objectius: `default_nomi = t("vita_default_nomi", lc)`, tots els headers de DataFrame
- KPIs `vita_totale_risp`, `vita_capacita_residua` via `t()`
- Alertes objectius → `t("vita_obj_raggiungibili/insufficiente", lc, ...)`
- Gràfic gantt: `xaxis_title=t("vita_anni_da_oggi", lc)`, `title=t("vita_timeline", lc)`
- Gràfic acumulació → `t("vita_proiez_acc", lc)`, eix Y unificat

**`dash_pages/prospecting.py`:**
- `render_spots(lc)` ara accepta lc; afegit `prosp-spots-lc-store`
- Categoria dropdown → `t("prosp_filter_cat/all_cat", lc)`
- "Nessun risultato" → `t("prosp_no_results", lc)`
- SMTP labels Porta/Email mittente → `t("smtp_porta/mittente", lc)`

**`dash_pages/assegurances.py`:**
- Alert KK → `t("kk_risp_ok/kk_ottimale", lc)`
- Escenaris 3r pilar → `t("prev_scen_ora/tardi/fis", lc)` (variables per `color_discrete_map`)
- Anotació gràfic → `t("prev_obiettivo_pct", lc, pct=pct_obiettivo)`

**Fitxers canviats:** `i18n.py`, `dash_pages/advisor.py`, `dash_pages/vida_budget.py`, `dash_pages/prospecting.py`, `dash_pages/assegurances.py`

---

## 📋 Changelog — Sessió 5 (2026-04-20)

### i18n Home page — textos hardcoded eliminats
**Problema:** La pàgina Home tenia tots els textos en italià independent de l'idioma seleccionat: títols i descripcions de les 4 targetes de mòdul, les 4 estadístiques, el botó "→ Apri" i el títol de secció "Moduli".

**Solució:**
- `i18n.py` — afegides 14 noves claus `home_*` al bloc `_EXTRA` per a **IT, DE, FR, EN i CA**. Les altres 6 llengua fan fallback a italià via el mecanisme existent.
  - `home_open`, `home_moduli`
  - `home_mod_advisor/ass/budget/prosp_title` i `_desc` (amb params `{n_ev}`, `{n_sp}`, `{n_em}`)
  - `home_stat_lingue/eventi/pilastri/crm`
- `dash_pages/home.py` — refactoritzat: tots els strings literals substituïts per `t(key, lc)`. Nova funció `stat_box()` per DRY. La descripció de Prospecting usa `.format(n_ev=n_ev, n_sp=n_sp, n_em=n_em)`.

### Dropdowns sidebar — text unificat a gris fosc
**Problema:** Dins el sidebar, els camps de text (`dcc.Input`) mostraven text gris fosc sobre fons blanc, però els desplegables (`dcc.Dropdown`) mostraven text clar sobre fons quasi-transparent (fosc). Aparença inconsistent.

**Solució:** `assets/style.css` i `CUSTOM_CSS` a `dash_app.py` — els selectors `.Select-control` del sidebar ara reben el mateix tractament que els `.form-control`:
- `background: rgba(255,255,255,0.93)` — fons blanc
- `color: #1e2235` — text gris fosc
- `.Select-value-label`, `.Select-placeholder`, `.Select-single-value`, `.Select-input input` → tots `color: #1e2235`
- Menú desplegable: fons blanc amb ombra, opcions en fosc; hover en vermell AlexFin

**Fitxers canviats:** `assets/style.css`, `dash_app.py`, `i18n.py`, `dash_pages/home.py`

---

## 📋 Changelog — Sessió 4 (2026-04-19)

### PDF exportable de la reunió
**Fitxer nou:** `pdf_report.py`  
Genera un informe PDF complet de cada reunió amb el client. El botó **"Scarica PDF riunione"** apareix al tab *Note* de la pàgina Advisor, just sota el resum del col·loqui.

**Contingut del PDF (1 pàgina A4):**
1. **Header en vermell AlexFin** — Nom del client, data, cantó
2. **Perfil del client** — Taula 3 columnes: edat, situació, cantó, reddito, estat civil, fills, hipoteca, risc, anys fins jubilació
3. **KPI row** — 5 caixes: reddito anual, pensió estimada, AVS, LPP, lacuna (vermell/verd)
4. **Gràfic de barres horitzontals** — AVS / LPP / Lacuna previdenziale, dibuixat amb primitives `fpdf2` (sense imatges externes, sense kaleido)
5. **Recomanacions** — Llista priorizada (ALTA / RACCOMANDATA / OPZIONALE) amb raonament
6. **Notes del col·loqui** — Temes discutits, pròxims passos, notes lliures, urgència
7. **Disclaimer legal** al peu de pàgina

**Arquitectura:**
- `fpdf2 >= 2.7.9` (pure Python, sense dependències de sistema → compatible Render.com)
- Funció `_s(text)`: sanititzador latin-1 → substitueix en-dash, em-dash, cometes tipogràfiques, bullets, caràcters fora de rang. Helvetica de fpdf2 és codificació latin-1.
- `AlexFinPDF(FPDF)`: subclasse amb footer autònom (número de pàgina + data)
- `genera_pdf(store, note_libere, prossimi_passi, temi_discussi, urgenza_label) → bytes`

**Integració Dash:**
- `dcc.Download(id="pdf-download")` al `layout()` de `advisor.py` (fora dels tabs perquè sempre existeixi al DOM)
- Botó `dbc.Button(id="pdf-btn")` al tab Note, sota el riepilogo-box
- Callback `download_pdf`: rep tots els States de nota + store → crida `genera_pdf()` → retorna `dcc.send_bytes(pdf_bytes, filename)`
- Nom del fitxer: `AlexFin_<NomeCognome>_<YYYYMMDD>.pdf`

**Contingut final del PDF** (les notes del col·loqui NO s'inclouen — queden privades al tab Note):
1. Header branded AlexFin (vermell)
2. Perfil del client (taula 3 columnes)
3. KPI row (5 caixes: reddito, pensió, AVS, LPP, Lacuna)
4. Gràfic barres previdenziali + target 70%
5. Recomanacions prioritzades
6. Disclaimer legal

**Fitxers canviats:** `pdf_report.py` (nou), `dash_pages/advisor.py`, `requirements.txt`

### CRM: clients demo afegits
**Fitxer nou:** `clienti.json`  
6 clients demo precarregats:
- 5 **chiusi** (tancats) amb dates reals nov 2025 – mar 2026: Marco Ferretti, Petra Müller, Luca Bernasconi, Ana Popescu, Stefan Brunner
- 1 **da_chiudere** (per tancar): Yuki Tanaka, expat japonesa, follow-up 28 abril, proposta 3a assicurativo + complementare dental/vista

---

## 📋 Changelog — Sessió 3 (2026-04-19)

### i18n complet — canvi d'idioma en temps real
**Problema:** El canvi d'idioma al selector del sidebar només actualitzava alguns títols de pàgina. Les labels del formulari lateral, les opcions dels dropdowns, els marks del slider i les etiquetes dels tabs de totes les pàgines quedaven sempre en italià.

**Causa:** `make_sidebar()` crea el layout una sola vegada com a HTML estàtic. `layout()` de cada pàgina fa el mateix amb `dbc.Tabs`. Cap d'ells tenia un callback que els re-renderitzés quan canviava `lc`.

**Solució:**
- `dash_app.py`: nou callback `update_sidebar_i18n` amb 18 Outputs → tradueix en temps real totes les labels, placeholders, opcions de dropdowns (situazione, stato_civile, figli, ipoteca) i marks del slider (rischio). Els **valors interns** dels dropdowns resten en italià per mantenir compatibilitat amb `calcola_raccomandazioni()`.
- `advisor.py`, `assegurances.py`, `vida_budget.py`: els `dbc.Tabs` s'han mogut del `layout()` estàtic a un callback (`render_header`) que rep `app-store` → les etiquetes es tradueixen quan canvia l'idioma.

### Inputs sidebar: text visible
**Problema:** Les lletres no es veien quan l'usuari escrivia el nom, edat, etc. al formulari del sidebar.  
**Causa:** `color: #ffffff` (text blanc) sobre un fons quasi-transparent molt fosc → invisible.  
**Solució:** `color: #1e2235` (gris fosc) + `background: rgba(255,255,255,0.93)` (fons blanc translúcid). Placeholders en `#999`. Canvi aplicat a `assets/style.css` i al `CUSTOM_CSS` de `dash_app.py`.

### Cantó per defecte: Zürich
El sidebar i el store inicial ara parteixen de **Zürich** en lloc de Ticino, que és el mercat principal de l'assessor.

### Budget mensile: text de les cel·les
**Problema:** Les etiquetes dels camps del formulari (Affitto, Alimentazione, etc.) eren massa grans i es veien tallades.  
**Solució:** Helper intern `_budget_row(label, input_id, ...)` → font `0.72rem`, `text-overflow: ellipsis`, `white-space: nowrap`, inputs `form-control-sm` (font `0.82rem`, padding reduït).

### Fonts oficials suïsses
**Fitxer nou:** `sources.py`  
Conté 20 links a pàgines oficials de la Confederació Helvètica i organismes reconeguts, agrupats per secció:

| Secció | Fonts |
|---|---|
| Assicurazioni | FINMA, SVV, Ombudsman assegurances |
| Krankenkasse | UFSP/BAG, priminfo.admin.ch, Ombudsman casses malats |
| Previdenza | AHV-IV.ch, UFAS (LPP), UFAS (3a), Compenswiss |
| Budget | ch.ch, Budgetberatung Schweiz, SECO |
| Advisor | ch.ch, FINMA, AFC (fiscalitat) |
| Prospecting | SCICC, economiesuisse, SECO, Swiss Global Enterprise |

La funció `sources_footer(section)` retorna un component Dash amb els links com a peu de pàgina. S'ha afegit a totes les pàgines (advisor, assegurances, krankenkasse, previdenza, budget, fasi di vita, obiettivi, events, spots).

### Deploy preparat
- `Procfile`, `runtime.txt`, `gunicorn` a `requirements.txt`
- `AUTH_USER`, `AUTH_PASS`, `SECRET_KEY` via variables d'entorn
- Pàgina de login branded (disseny AlexFin, HTML/CSS inline)
- Botó "⎋ Esci" al navbar
- `main` branch sincronitzat i llest per Render.com

---

## 📌 Propòsit de l'aplicació

**AlexFin** és una eina B2B professional per a l'assessor financer **Alex Bevilacqua** (SVAG).  
**No és una app d'autoservei per a clients finals.** L'assessor l'usa en dues situacions:

1. **Durant reunions amb clients**: mostra productes SVAG, fa simulacions patrimonials i recomanacions personalitzades en temps real.
2. **Per trobar clients nous (prospecting)**: llista d'events de networking a Suïssa, associacions professionals, i sistema d'enviament de correus personalitzats.

**Context geogràfic:** Canton Ticino + Zürich, Luzern, Winterthur, St.Gallen, Bern, Basel.  
**Públic objectiu de l'assessor:** Expatriats, professionals, empresaris, treballadors per compte propi a Suïssa.

---

## 🗺️ Historial de versions

### v0.1 — Streamlit MVP (febrer–març 2026)
**Stack:** Streamlit (MPA), Altair, pandas  
**Fitxers principals:** `app.py`, `app2.py`, `pages/`, `idiomes.py`

Funcionalitats inicials:
- 5 pestanyes: About Me, Temes Financers, Planificador, Krankenkasse, Simulador fiscal
- Traduccions inline (diccionari `idiomes.py`)
- Formulari de perfil al sidebar
- Gràfic de projecció patrimonial (Altair)
- Simulador fiscal simplificat per cantó

**Problemes coneguts que van motivar la migració:**
- Bug de sidebar en MPA: el selector d'idioma desapareixia en navegar entre pàgines (`key=` + `index=` combinats a `st.selectbox` causaven conflicte a `session_state`)
- UI rígida, poc professional per a reunions amb clients
- Difícil d'escalar i organitzar amb múltiples pàgines
- Altair menys flexible que Plotly per a gràfics financers interactius

---

### v1.0 — Migració a Dash (abril 2026)
**Stack:** Dash 4.1.0 + Dash Bootstrap Components 2.0.4 + Plotly 6.3.1  
**Entry point:** `dash_app.py`

#### Decisió de migració: per què Dash?

Es van avaluar quatre alternatives:

| Framework | Avantatge | Problema |
|---|---|---|
| **Dash** ✅ | Python natiu, Plotly integrat, MPA estable, ideal per dashboards financers | Callbacks explícits (verbós) |
| Reflex | React sota el capó, modern | Massa nou, poca documentació financera |
| NiceGUI | Molt simple | Poc control de layout |
| Panel | Flexible | Menys polit visualment |

**Decisió: Dash** per la seva maduresa en dashboards B2B, integració nativa amb Plotly (ja instal·lat) i capacitat de MPA sense bugs de session_state.

#### Arquitectura Dash

```
dash_app.py                  ← Entry point, layout global, sidebar, navbar, auth
├── dash_pages/
│   ├── home.py              ← Landing amb 4 mòduls + stats
│   ├── advisor.py           ← Raccomandazioni + Simulatore + Note + CRM
│   ├── assegurances.py      ← Assicurazioni + Krankenkasse + Previdenza
│   ├── vida_budget.py       ← Budget + Fasi di vita + Obiettivi
│   └── prospecting.py       ← Events + Spots + Email Marketing + Log
├── assets/
│   └── style.css            ← Design system complet
├── i18n.py                  ← Sistema de traduccions (11 idiomes)
├── products.py              ← Productes SVAG, KK, Pilastres, recomanacions
├── prospect_data.py         ← Dades events, spots, plantilles email
├── clienti.json             ← CRM local (generat automàticament)
├── email_sent.json          ← Log d'emails enviats (generat automàticament)
├── Procfile                 ← gunicorn per deploy (Render.com)
├── runtime.txt              ← python-3.11.9
└── requirements.txt         ← dependències pinades
```

#### Estat global — dcc.Store

Tot el perfil del client es guarda a un `dcc.Store(id="app-store", storage_type="session")` i es comparteix entre totes les pàgines:

```python
{
  "lc": "it",               # codi d'idioma actiu
  "nome": "Marco Rossi",
  "eta": 42,
  "sesso": "M",
  "situazione": "Dipendente",
  "canton": "Ticino",
  "reddito_mensile": 5500,
  "stato_civile": "Sposato/a",
  "figli": True,
  "n_figli": 2,
  "ipoteca": False,
  "tolleranza_rischio": "Media"
}
```

El sidebar escriu a l'store amb cada canvi. Cada pàgina llegeix l'store com a `Input`.

---

## 🧩 Funcionalitats per pàgina

### `home.py` — Pàgina d'inici
- Hero amb títol AlexFin + subtítol i18n
- Píndola del client actiu (si hi ha nom al perfil)
- Fila de stats dinàmics: idiomes (11), events networking (count real de `prospect_data`), pilastres (3), CRM (∞)
- 4 cards de mòdul amb hover effect i link directe a cada secció

---

### `advisor.py` — Dashboard de l'assessor
**4 sub-tabs:**

#### 🎯 Raccomandazioni
- Motor de recomanació basat en regles (`calcola_raccomandazioni()` a `products.py`)
- Inputs: edat, situació laboral, cantó, ingressos, figli, ipoteca, tollerança al risc, anys fins a la pensió
- Output: llista de productes SVAG prioritzats (Alta / Raccomandata / Opzionale)
- KPIs: edat, reddito annuo, anys al pensionament, pensió estimada (1°+2° pilar), lacuna previdenziale
- Filtres per prioritat
- Indicador semàfor si hi ha lacuna pensionística

#### 📈 Simulatore Patrimoniale
- Inputs: risparmi attuali, risparmio mensile, rendimento %, edat de pensionament
- Gràfic Plotly interactiu: projecció del patrimoni fins al pensionament
- 3 escenaris what-if opcionals:
  - Shock de mercat (−2% rendiment)
  - Reducció d'ingressos al 50%
  - Despesa extraordinaria CHF 50.000
- KPIs de resultat: patrimoni final, total aportat, rendita mensile (regla 4%), cobertura % vs. reddito

#### 📝 Note del Col·loqui + Email
- Editor de notes de reunió: apunts lliures, temes discutits, pròxims passos
- Urgència del client (3 nivells: exploratiu / interessat / llest per decidir)
- Resum automàtic del perfil generat
- Descàrrega de resum en `.txt`
- Enviament per SMTP (HTML formatat) directament al client

#### 👥 CRM Clienti
- Guardar perfil complet del client a `clienti.json`
- Llista de clients guardats amb càrrega i eliminació
- KPIs del dashboard: total clients, reunions del mes, pròxima cita
- Objectiu mensual de clients (slider) amb barra de progrés

---

### `assegurances.py` — Productes SVAG
**3 sub-tabs:**

#### 🛡️ Assicurazioni Private
- Catàleg de productes SVAG (definits a `products.py`)
- Selector de producte amb descripció, categoria, cost indicatiu
- Gràfic Plotly: evolució del premi per edat
- Detall: cobertures, exclusions, cas real comparatiu (amb vs. sense assegurança)
- Estimació de cost per l'edat actual del client

#### 💊 Krankenkasse (LAMal/KVG)
- Sub-tab 1: Franquícies (300, 500, 1000, 1500, 2000, 2500 CHF) i models (Standard, Telmed, HMO, Médecin de famille) amb descripció i estalvi estimat
- Sub-tab 2: Assegurances complementàries (LCA)
- Sub-tab 3: Calculadora d'estalvi — comparació franquícia/model actual vs. proposta, amb estalvi anual i a 5 anys
- Taula de primes 2026 per cantó (Adult, Jove, Nen)

#### 🏛️ Previdenza (3 Pilastres)
- Sub-tab 1: Esquema visual dels 3 pilastres suïssos (AVS/AI, LPP, 3a)
- Sub-tab 2: Simulador 3r Pilar — versament anual, anys inversió, rendiment, alíquota fiscal → capital a venciment, estalvi fiscal, cost del retard (5 anys), tributació al rescat; comparació 3a bancari vs. 3a asseguratiu
- Sub-tab 3: Lacuna previdenziale — objectiu reddito en pensió (% del reddito attuale), lacuna residual calculada

---

### `vida_budget.py` — Vida & Budget
**3 sub-tabs:**

#### 🏠 Budget Mensile
- 3 fonts d'ingressos configurables (salari principal, segon reddito, altri)
- 7 categories de despeses (affitto, alimentació, transport, salut, lleure, asilo, altro)
- Regla 50/30/20 adaptada a Suïssa: Necessitats (50%) / Discrecional (30%) / Estalvi (20%)
- Indicadors semàfor (verd/groc/vermell) per cada categoria
- Gràfic donut Plotly: distribució de despeses
- Objectiu d'estalvi mensual personalitzable

#### 👨‍👩‍👧 Fasi di Vita
- Selector de fase vital: Jove sense fills → Parella → Família amb nens → Adolescents → Fills a la uni → Niu buit → Pre-pensió
- Per cada fase: descripció, riscos principals, productes recomanats, costos típics

#### 🎯 Obiettivi Finanziari
- Fins a 5 objectius configurables (nom, import CHF, anys per assolir-lo)
- Càlcul d'estalvi mensual necessari per objectiu
- Gràfic Gantt Plotly: timeline visual dels objectius
- KPIs: estalvi mensual total necessari, objectius assolibles amb el saldo actual, escart mensual

---

### `prospecting.py` — Prospecting & Networking
**4 sub-tabs:**

#### 📅 Events & Networking
- 30+ events de networking a: Zürich, Luzern, Winterthur, St.Gallen, Bern, Basel, Lugano, Bellinzona
- Tipus d'events: BNI, Rotary, Lions, IHK, Startup&Tech, Finance, Alumni, Expat, PMI, Università, Industria
- Freqüències: Settimanale, Mensile, Bimestrale, Trimestrale, Annuale
- Filtres: per Città, Tipus, Freqüència
- Cards per cada event: nom, tipus (badge de color), freqüència, descripció, target, link al site
- Agrupació per ciutat amb comptador

#### 🏛️ Luoghi & Associazioni (Networking Spots)
- 12 spots/associacions: BNI, Rotary, Lions, IHK, Alumni universitaris, clubs expat, PMI
- Categories: Rotary & Lions / Referral Networking / Camere di Commercio / Alumni / Professional Clubs / Expat & International / PMI & Imprenditori
- Per cada spot: descripció, target, com entrar, link

#### 📧 Email Marketing
- 5 plantilles email professionals:
  - `fredda_presentazione` — primer contacte fred
  - `follow_up_evento` — follow-up post event de networking
  - `risparmio_krankenkasse` — proposta d'estalvi KK
  - `terzo_pilastro` — proposta 3r pilar
  - `check_up_gratuito` — oferta de check-up financer gratuït
- Personalització dinàmica: nom destinatari, email, on es van conèixer, telèfon
- Configuració SMTP (Gmail, port 587, TLS) en acordió col·lapsable
- Preview de l'email (cos + mini-report HTML adjunt)
- Enviament SMTP real amb cos en text + HTML (template amb capçalera SVAG)
- Missatges d'èxit/error localitzats

#### 📊 Storico Invii
- Log persistent a `email_sent.json`
- Taula amb els últims 50 enviaments: data, destinatari, email, template, cantó
- KPI: total emails enviats

---

## 🌍 Sistema d'internacionalització (i18n)

**Fitxer:** `i18n.py`  
**11 idiomes:** IT, DE, FR, EN, ES, PT, SQ (albanès), SR (serbi), TR (turc), RM (romànx), CA (català)

**Arquitectura:**
- Diccionari `TRANSLATIONS`: claus per idioma, amb traduccions completes per IT, DE, FR, EN, ES, PT, SQ, SR, TR, RM, CA
- Diccionari `_EXTRA`: claus afegides posteriorment per IT, DE, FR, EN → s'incorporen a TRANSLATIONS via merge amb fallback a IT
- Funció `t(key, lang_code, **kwargs)`: retorna la traducció, amb fallback a IT i finalment a la clau
- L'idioma s'emmagatzema a `app-store["lc"]` i es canvia des del selector del sidebar

**Categories de claus:**
- `app_*`: títol, subtítol, footer
- `sidebar_*`: tots els camps del formulari lateral
- `tab_*`: etiquetes de les pestanyes principals
- `rac_*`, `ass_*`, `kk_*`, `prev_*`: seccions específiques
- `vita_*`, `sim_*`, `note_*`, `email_*`: seccions de vida i notes
- `adv_*`: dashboard advisor (CRM, mètriques)
- `prosp_*`: tota la pàgina de prospecting (títol, tabs, filtres, botons, missatges)

---

## 🔐 Sistema d'autenticació

**Implementació:** Flask session-based login (integrat dins el servidor Flask de Dash)

**Flux:**
1. Qualsevol petició sense sessió activa → redirect 302 a `/login`
2. `/login` (GET): pàgina HTML estilitzada amb el disseny AlexFin (blanc, vermell #c0392b, Inter)
3. `/login` (POST): valida `AUTH_USER` + `AUTH_PASS` → si correcte, `session["auth"] = True` → redirect a l'app
4. `/logout`: esborra la sessió → redirect a `/login`
5. Rutes `/_dash-*` (AJAX interns de Dash): retornen 401 sense redirect (per no trencar el JS del client)
6. `/assets/*` i `/_favicon`: sempre públiques

**Variables d'entorn necessàries:**
| Variable | Descripció | Valor per defecte (dev) |
|---|---|---|
| `AUTH_USER` | Nom d'usuari | `alex` |
| `AUTH_PASS` | Contrasenya | `svag2026` |
| `SECRET_KEY` | Clau de sessió Flask | `alexfin-dev-secret-change-in-prod` |
| `DASH_DEBUG` | Mode debug | `true` (dev) / `false` (prod) |
| `PORT` | Port del servidor | `8050` |

**Navbar:** botó "⎋ Esci" top-right que fa logout

---

## 🎨 Design System

**Fitxer:** `assets/style.css`  
**Font:** Inter (Google Fonts)  
**Paleta:**
- Primari: `#c0392b` (vermell SVAG)
- Dark navy: `#1e2235` (navbar, sidebar)
- Dark bg sidebar: `#151929`
- Background pàgina: `#f0f2f7`
- Text: `#1e2235` (fosc), `#888` (subtítol), `#555` (cos)
- Verd èxit: `#27ae60` / Taronja avís: `#f39c12` / Vermell error: `#e74c3c`

**Components CSS principals:**
- `.app-shell`: flex container (sidebar fix + content flex:1) amb padding-top 56px (navbar)
- `#sidebar`: 240px fix, sticky, scroll intern, gradient fosc
- Inputs sidebar: fons translúcid, border blanc 18%, focus vermell
- `.content-card`, `.metric-card`, `.rec-card`: cards blanques amb ombra i border-radius
- `.badge-alta/racc/opz`: pills de prioritat (vermell/taronja/gris)
- `.budget-ok/warn/err`: indicadors semàfor
- `dcc.Dropdown` sidebar: `.Select-*` selectors (React Select v1)
- `dcc.Dropdown` contingut: `#page-content .Select-*` selectors amb hover vermell
- `.mod-card`: cards de la home amb hover (border vermell + shadow)
- `dbc.Accordion`: colors vermell per ítem actiu

---

## 🚀 Deploy

**Plataforma:** Render.com (Free tier)  
**Servidor:** Gunicorn  
**Comanda d'inici:** `gunicorn dash_app:server`

**Fitxers de deploy:**
- `Procfile`: `web: gunicorn dash_app:server`
- `runtime.txt`: `python-3.11.9`
- `requirements.txt`: dependències pinades (dash==4.1.0, dbc==2.0.4, plotly==6.3.1, gunicorn>=21.2.0)
- `.env.example`: template de variables d'entorn

**Notes de producció:**
- `DASH_DEBUG=false` obligatori en producció
- `SECRET_KEY` ha de ser un string aleatori de 32+ bytes (`secrets.token_hex(32)`)
- Free tier de Render: cold start ~30 seg si porta 15 min sense visites
- SMTP sortint pot requerir SendGrid/Mailgun si Gmail bloqueja des del servidor

---

## 🗃️ Fitxers de dades

| Fitxer | Contingut | Generat per |
|---|---|---|
| `clienti.json` | Array de perfils de clients guardats | advisor.py (CRM) |
| `email_sent.json` | Array de log d'emails enviats | prospecting.py |
| `prospect_data.py` | EVENTS, NETWORKING_SPOTS, EMAIL_TEMPLATES, CITIES, EVENT_TYPES, SPOT_CATEGORIES | Dades estàtiques, mantingudes manualment |
| `products.py` | PRODUCTS (SVAG), KK_PREMI_CANTON, KK_FRANCHIGIE, KK_MODELLI, PILLAR_1/2/3, `calcola_raccomandazioni()` | Dades estàtiques, mantingudes manualment |

---

## 📦 Dependències

```
dash==4.1.0
dash-bootstrap-components==2.0.4
plotly==6.3.1
pandas>=2.0.0
numpy>=1.26.0
Pillow>=10.0.0
gunicorn>=21.2.0
```

---

## 📁 Legacy (mantingut per referència)

| Fitxer | Descripció |
|---|---|
| `app.py` | Versió Streamlit original (landing) |
| `pages/1_Advisor.py` | Pàgina Streamlit Advisor |
| `pages/2_Assegurances.py` | Pàgina Streamlit Assegurances |
| `pages/3_Vida_Budget.py` | Pàgina Streamlit Vida & Budget |
| `utils.py` | Sidebar compartit Streamlit (fix MPA key conflict) |
| `legacy/` | Fitxers originals: app2.py, idiomes.py, functions.py, financial_projection.py, etc. |

---

## 🏃 Com executar en local

```bash
cd ~/Documents/git_projects/AlexFin
python3 dash_app.py
# → http://localhost:8050
# Login: alex / svag2026 (defecte dev)
```

---

## 🔮 Possibles millores futures

- **Informe PDF de reunió** — exportar gràfics Plotly + recomanacions + notes en PDF professional (sol·licitat, pendent d'implementació)
- Integració amb Google Calendar per a les cites
- Enviament d'emails via SendGrid (evita restriccions SMTP en producció)
- Mapa interactiu dels events de networking (Plotly Mapbox)
- Autenticació multi-usuari (per si SVAG vol que altres assessors usin l'eina)
- Mode offline / PWA per usar sense connexió durant les reunions
