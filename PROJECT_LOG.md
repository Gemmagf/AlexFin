# AlexFin – Project Log
> Last updated: 2026-04-12

---

## Overview

Streamlit web app for **Alex Bevilacqua**, a Swiss financial advisor. The app helps users understand Swiss finance topics (3rd pillar, Krankenkasse, taxes, ETFs) and includes a personal financial projection simulator with what-if scenarios.

**Active branch:** `upgrade-streamlit-app`

---

## File Structure

| File | Purpose |
|---|---|
| `app2.py` | Main Streamlit app — 5 tabs (About Me, Topics, Planner, Health, Tax) |
| `idiomes.py` | Inline translation dictionary (EN, DE, FR, IT, CA...) used by `app2.py` |
| `translations.py` | New `Translator` class loading JSON files per language — not yet integrated |
| `financial_projection.py` | `run_projection()` function + standalone Streamlit prototype code |
| `functions.py` | `make_circle()` utility for circular profile image rendering |
| `idees` | Business plan for a future AI accounting SaaS product (separate project idea) |
| `ideas.txt` | Marketing material: Instagram carousel texts and website copy for Alex |

---

## App Tabs

1. **About Me** — Alex's bio, services offered, and booking link
2. **Financial Topics** — 10 expandable topics (3a pillar, Krankenkasse, ETFs, taxes, expat guide...)
3. **Planner & Simulator** — User form + net worth projection chart with what-if scenarios
4. **Health Insurance** — Krankenkasse overview with a cost-layer bar chart
5. **Tax Simulator** — Tax estimate by canton and permit type

---

## Known Bugs

### 1. `financial_projection.py` — Top-level Streamlit code executes on import
**File:** `financial_projection.py`, lines 23–96  
**Problem:** The file contains `st.sidebar.checkbox(...)` and `st.write(...)` calls at module level (outside any function). When `app2.py` does `from financial_projection import run_projection`, these lines execute immediately, causing unexpected Streamlit widget rendering and potential runtime errors if Streamlit context is not ready.  
**Fix needed:** Move all top-level Streamlit code into a `if __name__ == "__main__":` block or delete it entirely (it's a prototype leftover).

### 2. `financial_projection.py` — `pandas` imported twice
**File:** `financial_projection.py`, lines 30–31  
**Problem:** `import pandas as pd` appears twice.  
**Fix needed:** Remove the duplicate import.

### 3. `app2.py` — Duplicate imports mid-file
**File:** `app2.py`, lines 64–66  
**Problem:** `import pandas as pd`, `import altair as alt`, and `import streamlit as st` are repeated inside the `with tabs[1]:` block, even though they are already imported at the top of the file.  
**Fix needed:** Remove the duplicate imports inside the tab block.

### 4. Missing image assets
**Files:** `alex_doll.png`, `photo.png`  
**Problem:** Both images are referenced in `app2.py` but do not exist in the repository. The app handles this gracefully with `try/except` fallbacks, but the visual output is degraded.  
**Fix needed:** Add the image assets to the repo or document where to obtain them.

---

## Unfinished / Incomplete Features

### 1. Two translation systems coexist without integration
**Files:** `idiomes.py`, `translations.py`  
**Status:** `idiomes.py` (large inline dict) is the system currently used by `app2.py`. `translations.py` is a newer, cleaner `Translator` class that loads from JSON files per language (`translations/<lang>.json`) — but these JSON files do not exist yet and the class is never called anywhere.  
**Next step:** Decide on one system. Recommended: migrate to `translations.py` + JSON files to keep `app2.py` clean, then delete `idiomes.py`.

### 2. Hardcoded Catalan labels in `app2.py`
**File:** `app2.py`, lines 155–157  
**Problem:** What-if scenario checkboxes use hardcoded Catalan strings:
```python
sim_part_time = st.checkbox("Pare treballa 50%", key="sim_part_time")
sim_market_shock = st.checkbox("Mercat estancat (-2%)", key="sim_market_shock")
sim_private_school = st.checkbox("Universitat Estrangera", key="sim_private_school")
```
These bypass the translation system entirely.  
**Next step:** Add these keys to `idiomes.py` (and future JSON files) and use `lang["..."]` references.

### 3. Planner simulator values partially hardcoded
**File:** `app2.py`, lines 150–151 and `form_data` dict  
**Problem:** `forecast_years = 25` and `investment_return = 4.5` are defined as local variables but `investment_return` is also inside `form_data` as `"investmentReturn": 4.5`. The local variable is unused — `run_projection()` reads from `form_data`. There is no user-facing input for investment return rate.  
**Next step:** Either expose `investment_return` as a user input (slider) or remove the redundant local variable.

### 4. `form_data` uses placeholder values
**File:** `app2.py`, lines 168–169  
**Problem:** `annualGrossSalary2` and `monthlyContribution` use placeholder values (`current_salary` and `3000` respectively) instead of dedicated user inputs.  
**Next step:** Add input fields for second salary and monthly savings contribution.

### 5. Health Insurance tab is not interactive
**File:** `app2.py`, lines 203–219  
**Status:** Shows a static bar chart with hardcoded data. No user inputs, no personalisation.  
**Next step:** Add inputs for canton, age, model type, and deductible to generate a personalised estimate.

### 6. Tax Simulator uses a simplified rate
**File:** `app2.py`, lines 221–235  
**Problem:** Tax rate is hardcoded as `0.11` for Zurich and `0.13` for all other cantons — a very rough approximation. Other cantons are not differentiated.  
**Next step:** Implement a proper progressive tax table per canton or integrate an external API.

### 7. Recommendations section is hardcoded in Catalan
**File:** `app2.py`, lines 196–201  
**Problem:** The success/warning messages after simulation use hardcoded Catalan strings instead of the translation system.

### 8. `early_retirement_age` logic is trivial
**File:** `financial_projection.py`, lines 80–82  
**Problem:** `early_retirement_age` is simply `currentAge + forecast_years` (always 25 years out), which makes the label misleading. It does not actually detect the earliest year when wealth exceeds a target.  
**Next step:** Implement real early retirement detection by scanning the projection for when `totalWealth` crosses a configurable threshold.

---

## Notes

- The `idees` file and `ideas.txt` are planning/marketing documents and are not part of the app code.
- The project is in early development / MVP stage. Core architecture works but several features are stubs or prototypes.
