# CLAUDE.md — Job-ही-Shauk Project Rules

> Machine-readable guide for Claude Code. Read this file **before** touching any other file.
> These rules override general defaults. Follow them line-by-line.

---

## 1. Project Identity

| Field | Value |
|---|---|
| Project name | Job-ही-Shauk |
| Sprint | Module 4 — Sprint 3 (Applied Data Science Foundations) |
| Team | Team 06 |
| Question | Which skills are trending, and which skill combinations correlate most strongly with successful job placement? |
| Primary language | Python 3.10+ |
| Package manager | `pip` (no `poetry`, `pnpm`, `npm`) |
| Dependency file | `requirements.txt` |
| Style | PEP 8 + `black` + `ruff` |

---

## 2. Role & Ownership Map

Every assignment has **exactly one owner**. Do not author work for a role you don't own.

| Member | Role | Owns assignments |
|---|---|---|
| Harshita Soni ★ | Data Analyst (Leader) | _On leave — assignments reassigned to Bhargav as of 2026-04-28_ |
| Harsh Singh | Backend | 4.5–4.19 |
| **Bhargav Kalambhe** | **Frontend & ML + Analyst (covering)** | **4.1–4.4, 4.20–4.28, 4.29–4.38, 4.39–4.43, 4.44** |

**Current user:** Bhargav Kalambhe.
When asked to "do my next work", pick the **lowest-numbered unchecked assignment in Bhargav's range** from `audit.md` (which now spans 4.1–4.4, 4.20–4.28, 4.29–4.38, 4.39–4.43, 4.44).

---

## 3. Repository Layout (source of truth)

```
./
├── CLAUDE.md                 # this file
├── README.md                 # user-facing documentation (no tracker/status tables)
├── audit.md                  # checklist, update log, tracker (internal)
├── requirements.txt          # pip dependencies
├── .gitignore
├── data/
│   ├── raw/                  # immutable source data (read-only)
│   └── processed/            # derived, regeneratable
├── notebooks/                # stage-based Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_analysis.ipynb
│   └── 04_visualisation.ipynb
├── outputs/
│   └── figures/              # generated plots (.png)
└── src/                      # reusable Python modules (created per assignment)
```

Rules:
- **Never** write to `data/raw/`. Treat it as read-only.
- **Never** hand-edit files in `outputs/`. They are regenerated.
- New `.py` files for assignments go in `src/` (create the folder on first use).

---

## 4. Coding Standards (Bhargav's assignment 4.20)

- PEP 8 compliant (enforced by `ruff`, formatted by `black`)
- Variable names: `snake_case`, descriptive, no single-letter names except loop counters
- Constants: `UPPER_SNAKE_CASE`
- Functions: `snake_case`, verb-first (e.g. `compute_average`, `load_postings`)
- Classes: `PascalCase`
- Line length: 100 characters max
- Indentation: 4 spaces (no tabs)
- Imports: grouped — stdlib → third-party → local, blank line between groups
- Docstrings: triple-quoted, one-line summary minimum for public functions
- Comments: explain **why**, not **what**. Skip comments the code already makes obvious.

---

## 5. Workflow Rules (BLOCKING)

### 5.1 Before starting any assignment
1. Open `audit.md` and locate the assignment row.
2. Confirm it is owned by the current user.
3. Mark its status as `In Progress` with today's date.

### 5.2 While working
- One assignment → one `.py` file (or one notebook section).
- Put the file under `src/` unless the assignment explicitly calls for a notebook.
- Add a **new H2 section** to `README.md` under the correct assignment number.
- Run `python3 -m black <file>` and `python3 -m ruff check <file>` before committing.

### 5.3 After finishing
1. Update `audit.md`:
   - Flip status to `Done` with today's date.
   - Add a row to the **Update Log** section.
2. Update README's Table of Contents.
3. Commit with message format: `feat(<scope>): <description> (assignment <N.M>)`
   Scopes: `backend` (Harsh), `analyst` (Harshita), `frontend`, `ml` (Bhargav).

### 5.4 Never do
- ❌ Put status tables / update logs / progress trackers in `README.md` — those belong in `audit.md`.
- ❌ Create files outside the layout in section 3 without asking.
- ❌ Modify another member's assignment content.
- ❌ Commit generated data (`data/processed/*.csv`, `outputs/figures/*.png`).
- ❌ Use emojis in code or README unless explicitly requested.
- ❌ Skip the audit.md update.

---

## 6. File-Path Conventions

| Artefact | Path pattern | Example |
|---|---|---|
| Assignment script | `src/<short_name>.py` | `src/pep8_basics.py` |
| Raw data | `data/raw/<entity>_<period>_raw.<ext>` | `data/raw/sample_job_postings.csv` |
| Processed data | `data/processed/<entity>_<period>_cleaned.<ext>` | `data/processed/postings_cleaned.csv` |
| Figure | `outputs/figures/<subject>_<chart_type>.png` | `outputs/figures/skills_distribution_hist.png` |
| Notebook | `notebooks/<NN>_<topic>.ipynb` | `notebooks/04_visualisation.ipynb` |

---

## 7. Commands Cheat-Sheet

```bash
# Install deps
python3 -m pip install -r requirements.txt

# Format + lint a file
python3 -m black src/<file>.py
python3 -m ruff check src/<file>.py

# Run a script
python3 src/<file>.py

# Launch notebooks
python3 -m jupyter notebook notebooks/
```

---

## 8. Current Context Pointers

- **User:** Bhargav Kalambhe (Frontend & ML)
- **Bhargav's next assignment:** lowest-numbered unchecked row across the merged ranges 4.1–4.4, 4.20–4.28, 4.29–4.38, 4.39–4.43, 4.44 in `audit.md`
- **Harsh's status:** assignments 4.5, 4.6, 4.7, 4.8, 4.9, 4.12–4.19 marked `Done` (see `audit.md`); 4.10, 4.11 still open
- **Harshita's status:** on leave from 2026-04-28; her 15 tasks are now Bhargav's (see §2)

---

## 9. When in doubt

1. Re-read this file top to bottom.
2. Check `audit.md` for the latest state.
3. If still unclear, ask the user — do **not** guess.
