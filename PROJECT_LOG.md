# AlexFin — Project Log & Documentació Tècnica
> Última actualització: 2026-04-19  
> Mantenidora: Gemma Gardela  
> Client: Alex Bevilacqua, Assessor Financer SVAG (Canton Ticino, Suïssa)

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

- Exportació de l'informe del client en PDF
- Integració amb Google Calendar per a les cites
- Enviament d'emails via SendGrid (evita restriccions SMTP en producció)
- Mapa interactiu dels events de networking (Plotly Mapbox)
- Autenticació multi-usuari (per si SVAG vol que altres assessors usin l'eina)
- Mode offline / PWA per usar sense connexió durant les reunions
