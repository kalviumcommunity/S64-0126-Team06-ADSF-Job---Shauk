# Audit Log — Job-ही-Shauk (Team 06, Sprint 3)

> Internal tracker. **Not** user-facing. Moved out of `README.md` on 2026-04-20.
> Status vocabulary: `Not Started` · `In Progress` · `Under Review` · `Done`

---

## 1. Master Checklist (4.1 – 4.44)

### Harshita Soni ★ — Data Analyst (15 tasks, on leave from 2026-04-28; covered by Bhargav)

| # | Task | Status | Last Updated | Notes |
|---|---|---|---|---|
| 4.1 | Technology Orientation: What Is Data Science & How Data Projects Work | `Done` | 2026-04-28 | Bhargav — README section: what DS is (vs BI/analytics/ML), 5-stage data-project loop with ASCII diagram, role map, and Job-ही-Shauk stage→folder→owner mapping |
| 4.2 | [LM] Understanding the Data Science Lifecycle: Question → Data → Insight | `Not Started` | — | |
| 4.3 | [LM] Reading & Interpreting a Sample Data Science Project Repository | `Not Started` | — | |
| 4.4 | Building the Project Plan & MVP Definition for the Data Science Sprint | `Not Started` | — | |
| 4.29 | Loading CSV Data into Pandas DataFrames | `Done` | 2026-04-28 | Bhargav — `src/load_csv_data.py`: 6 load patterns (plain, `parse_dates`, explicit `dtype`+`na_values`, `usecols`+`index_col`, `StringIO` with `sep=';'`, safe `try/except FileNotFoundError`); dtype-before/after contrast on `date_posted` (object → datetime64[ns]); black + ruff clean |
| 4.30 | Inspecting DataFrames Using head(), info(), and describe() | `Done` | 2026-04-28 | Bhargav — `src/inspect_dataframe.py`: runs the inspection routine on **two** frames — the 3-row bundled CSV and a `generate_realistic_postings(120)` synthetic frame with lognormal salary and ~12% NaN injected — so `info()` actually shows non-null gaps (103/120, 114/120) and `describe()` actually shows real spread + skew (salary mean 11.63 vs median 10.90, std 4.69, range 4.2–32.2); includes `head` / `tail`, `info()` captured via `io.StringIO`, `isna().sum()` cross-check, `describe(include='all')` for categoricals, and an `explain_skewness()` helper that prints the mean-vs-median gap as a one-line read; black + ruff clean |
| 4.31 | Understanding Data Shapes and Column Data Types | `Not Started` | — | |
| 4.32 | Selecting Rows and Columns Using Indexing and Slicing | `Not Started` | — | |
| 4.33 | Detecting Missing Values in DataFrames | `Not Started` | — | |
| 4.34 | Handling Missing Values Using Drop and Fill Strategies | `Not Started` | — | |
| 4.35 | Identifying and Removing Duplicate Records | `Not Started` | — | |
| 4.36 | Standardizing Column Names and Data Formats | `Not Started` | — | |
| 4.37 | Computing Basic Summary Statistics for Individual Columns | `Not Started` | — | |
| 4.38 | Comparing Distributions Across Multiple Columns | `Not Started` | — | |
| 4.44 | Writing Final Project Insights, Assumptions, and Limitations in README | `Not Started` | — | |

### Harsh Singh — Backend (15 tasks)

| # | Task | Status | Last Updated | Notes |
|---|---|---|---|---|
| 4.5 | Installing Python and Anaconda on the Local Machine | `Done` | 2026-04-17 | Installed via Anaconda distribution; `(base)` env confirmed |
| 4.6 | Verifying Python, Conda, and Jupyter Installation | `Done` | 2026-04-17 | Verified via `--version` and `conda info` |
| 4.7 | Launching Jupyter Notebook and Understanding the Home Interface | `Done` | 2026-04-17 | Launched via `jupyter notebook`; Files / Running / Clusters tabs understood |
| 4.8 | Understanding Notebook Cells: Code vs Markdown | `Done` | 2026-04-17 | Code, Markdown, LaTeX rendering, shortcuts covered |
| 4.9 | Running, Restarting, and Interrupting Jupyter Kernels | `Done` | 2026-04-17 | Interrupt, Restart, Restart & Run All documented |
| 4.10 | Writing Markdown for Headings, Lists, and Code Blocks in Notebooks | `Not Started` | — | |
| 4.11 | Creating a Project Folder Structure for Data Science Work | `Not Started` | — | |
| 4.12 | Organizing Raw Data, Processed Data, and Output Artifacts | `Done` | 2026-04-17 | Folder structure, naming conventions, best practices documented |
| 4.13 | Creating and Running a First Python Script for Data Analysis | `Done` | 2026-04-18 | `student_marks_analysis.py` — variables, lists, loops, conditionals |
| 4.14 | Understanding Python Numeric and String Data Types | `Done` | 2026-04-18 | `numeric_and_string_types.py` — int/float/str, f-strings, conversions |
| 4.15 | Working with Python Lists, Tuples, and Dictionaries | `Done` | 2026-04-18 | `collections_demo.py` — list/tuple/dict operations |
| 4.16 | Writing Conditional Statements in Python | `Done` | 2026-04-18 | `conditional_statements.py` — if/elif/else, and/or/not |
| 4.17 | Using for and while Loops for Iterative Processing | `Done` | 2026-04-18 | `loops_demo.py` — for, while, break, continue, while…else |
| 4.18 | Defining and Calling Python Functions | `Done` | 2026-04-18 | `functions_demo.py` — 4 reusable functions, default + keyword args |
| 4.19 | Passing Data into Functions and Returning Results | `Done` | 2026-04-18 | `data_flow_functions.py` — parameters, returns, chaining |

### Bhargav Kalambhe — Frontend & ML (14 tasks)

| # | Task | Status | Last Updated | Notes |
|---|---|---|---|---|
| 4.20 | Writing Readable Variable Names and Comments (PEP8 Basics) | `Done` | 2026-04-20 | `src/pep8_basics.py` — BEFORE/AFTER contrast, constants, docstrings, type hints; black + ruff clean |
| 4.21 | Structuring Python Code for Readability and Reuse | `Done` | 2026-04-20 | `src/code_structure.py` — 5-section layout (imports, constants, pure helpers, reporting, orchestration); `main()` + entry-point guard; black + ruff clean |
| 4.22 | Creating NumPy Arrays from Python Lists | `Done` | 2026-04-20 | `src/numpy_arrays_from_lists.py` — 1D + 2D `np.array()`, `shape`/`ndim`/`size`/`dtype` inspection, list-vs-array arithmetic contrast; black + ruff clean |
| 4.23 | Understanding Array Shape, Dimensions, and Index Positions | `Done` | 2026-04-20 | `src/array_shape_indexing.py` — 1D/2D layout walk-through, complete index maps, zero-based access, `:`-slicing, `safe_get` out-of-range check; black + ruff clean |
| 4.24 | Performing Basic Mathematical Operations on NumPy Arrays | `Done` | 2026-04-20 | `src/array_math.py` — element-wise +/-/*/÷ on matched arrays, scalar ops, int/float promotion, supply/demand ratio domain example; black + ruff clean |
| 4.25 | Applying Vectorized Operations Instead of Python Loops | `Done` | 2026-04-20 | `src/vectorization.py` — 4 loop-vs-vector pairs (scale, add, filter, np.where), `np.array_equal` correctness check, `time.perf_counter` bench on 100k elements (~20–35× speed-ups); black + ruff clean |
| 4.26 | Understanding NumPy Broadcasting with Simple Examples | `Done` | 2026-04-20 | `src/broadcasting.py` — 4 working cases (scalar+1D, scalar+2D, matrix+row, matrix+column) plus caught `ValueError` for incompatible `(3,)`+`(4,)`; black + ruff clean |
| 4.27 | Creating Pandas Series from Lists and Arrays | `Done` | 2026-04-20 | `src/pandas_series.py` — 4 construction patterns (list, array, explicit labels, dict), `iloc` vs `loc`, label-aware addition producing NaN for unmatched labels; black + ruff clean |
| 4.28 | Creating Pandas DataFrames from Dictionaries and Files | `Done` | 2026-04-20 | `src/pandas_dataframes.py` — 4 construction patterns (dict-of-lists, list-of-dicts, dict-of-Series, `read_csv`), shape/columns/dtypes inspection, column/row selection, `.values` → `ndarray`; black + ruff clean |
| 4.39 | Visualizing Data Distributions Using Histograms | `Not Started` | — | |
| 4.40 | Visualizing Data Distributions Using Boxplots | `Not Started` | — | |
| 4.41 | Identifying Trends Over Time Using Line Plots | `Not Started` | — | |
| 4.42 | Exploring Relationships Between Variables Using Scatter Plots | `Not Started` | — | |
| 4.43 | Detecting Outliers Using Visual Inspection and Simple Rules | `Not Started` | — | |

---

## 2. Summary Counters

| Member | Done | In Progress | Not Started | Total |
|---|---:|---:|---:|---:|
| Harshita Soni ★ (on leave) | 0 | 0 | 0 | 0 |
| Harsh Singh | 10 | 0 | 5 | 15 |
| Bhargav Kalambhe (incl. analyst cover) | 12 | 0 | 17 | 29 |
| **Overall** | **22** | **0** | **22** | **44** |

Done: **22 / 44** (~50%)

---

## 3. What's Done

- Harsh: environment setup, Jupyter orientation, folder structure, Python fundamentals (data types, collections, control flow, functions, data flow).
- Repo scaffolding: `data/raw`, `data/processed`, `outputs/figures`, `notebooks/`, `.gitignore`.
- Project docs: `CLAUDE.md`, `audit.md`, `requirements.txt` added 2026-04-20.

## 4. What's Remaining (priority order)

### Blocking path for Bhargav (next-up first)
1. First tranche of 4.20–4.28 **COMPLETE** — all 9 foundation assignments done.
2. 4.39 – 4.43 — Visualisation suite (the final 5 Bhargav tasks; needs Harshita's cleaned DataFrames — coordinate before starting)

### Other members
- Harsh: 4.10, 4.11 (plus verify 4.5–4.9 matches current README)
- Harshita: all 15 tasks — highest priority are 4.1–4.4 (planning) so everyone else has context

---

## 5. Update Log

| Date | Author | Update |
|---|---|---|
| 2026-04-17 | Harsh Singh | Completed 4.5 – 4.9: Anaconda install, tool verification, Jupyter launch, cell types, kernel management |
| 2026-04-17 | Harsh Singh | Completed 4.12: Data organization strategy — raw/processed/outputs structure, naming, best practices |
| 2026-04-18 | Harsh Singh | Completed 4.13: `student_marks_analysis.py` — first Python script with variables, lists, loop, conditional, arithmetic |
| 2026-04-18 | Harsh Singh | Completed 4.14: `numeric_and_string_types.py` — int/float/str, arithmetic, f-strings, type conversion |
| 2026-04-18 | Harsh Singh | Completed 4.15: `collections_demo.py` — list/tuple/dict with safe lookups |
| 2026-04-18 | Harsh Singh | Completed 4.16: `conditional_statements.py` — if/elif/else ladders, logical operators, combined conditions |
| 2026-04-18 | Harsh Singh | Completed 4.17: `loops_demo.py` — for/while loops, break/continue, while…else |
| 2026-04-18 | Harsh Singh | Completed 4.18: `functions_demo.py` — 4 functions with single/multiple/default/keyword parameters |
| 2026-04-18 | Harsh Singh | Completed 4.19: `data_flow_functions.py` — parameters in, returns out, reuse and chaining |
| 2026-04-20 | Bhargav Kalambhe | Repo hygiene: added `CLAUDE.md`, `audit.md`, `requirements.txt`; moved tracker + update log out of `README.md` |
| 2026-04-20 | Bhargav Kalambhe | Completed 4.20: `src/pep8_basics.py` — PEP 8 BEFORE/AFTER contrast, `UPPER_SNAKE_CASE` constant, type hints, docstrings, intent-only comments; black + ruff clean; full README section added |
| 2026-04-20 | Bhargav Kalambhe | Completed 4.21: `src/code_structure.py` — 5-section layout (imports, constants, pure helpers, reporting functions, orchestration); `main()` + entry-point guard; pure vs side-effecting helpers split; black + ruff clean; full README section added |
| 2026-04-20 | Bhargav Kalambhe | Completed 4.22: `src/numpy_arrays_from_lists.py` — 1D array from flat list, 2D array from nested list (3×4 sector×skill), inspection of `shape`/`ndim`/`size`/`dtype`, and list-vs-array arithmetic contrast (concatenation vs element-wise); black + ruff clean; full README section added |
| 2026-04-20 | Bhargav Kalambhe | Completed 4.23: `src/array_shape_indexing.py` — complete 1D and 2D index maps, zero-based access, negative indices, row/column `:`-slicing, and `safe_get` defensive out-of-range check that names the offending axis and length; black + ruff clean; full README section added |
| 2026-04-20 | Bhargav Kalambhe | Completed 4.24: `src/array_math.py` — element-wise +/-/*/÷ on two shape-matched arrays, scalar ops (including `**`), int+float dtype promotion, and a domain mini-example computing a supply/demand ratio across five skills; black + ruff clean; full README section added |
| 2026-04-20 | Bhargav Kalambhe | Completed 4.25: `src/vectorization.py` — 4 loop-vs-vector rewrites (scale, pairwise add, boolean-mask filter, `np.where` conditional), `np.array_equal` correctness asserts, `time.perf_counter` benchmarks on 100k elements showing ~20–35× speed-ups; black + ruff clean; full README section added |
| 2026-04-20 | Bhargav Kalambhe | Completed 4.26: `src/broadcasting.py` — four broadcasting cases (scalar+1D, scalar+2D, matrix+row-vector, matrix+column-vector) plus a caught `ValueError` for incompatible `(3,)`+`(4,)`; ASCII layout walk-through and right-aligned shape table in the README; black + ruff clean |
| 2026-04-20 | Bhargav Kalambhe | Completed 4.27: `src/pandas_series.py` — 4 construction patterns (list → default index, NumPy array → dtype preserved, list + explicit labels, dict → keys as index), `iloc` vs `loc` access, boolean-mask filtering, and label-aware addition demonstrating that unmatched labels become `NaN` (dtype promoted to `float64`); black + ruff clean |
| 2026-04-20 | Bhargav Kalambhe | Completed 4.28: `src/pandas_dataframes.py` — four DataFrame construction patterns (dict-of-lists → columns, list-of-dicts → rows with `NaN` for missing keys, dict-of-Series → typed columns with index alignment, `pd.read_csv` on `data/raw/sample_job_postings.csv`), shape/columns/index/dtypes inspection, column and row selection, and confirmation that `frame.values` is an `np.ndarray` closing the 4.22 → 4.28 arc; black + ruff clean |
| 2026-04-28 | Bhargav Kalambhe | Ownership update: Harshita on leave from 2026-04-28; her 15 tasks (4.1–4.4, 4.29–4.38, 4.44) reassigned to Bhargav. `CLAUDE.md` §2 updated; audit counters recalculated |
| 2026-04-28 | Bhargav Kalambhe | Completed 4.1: Technology Orientation README section — defines data science vs BI/analytics/ML, walks the 5-stage data-project loop (question → data → cleaning → analysis → communication) with an ASCII diagram, maps the six standard roles to Team 06 members, and ties each stage to a concrete folder/owner in this repo |
| 2026-04-28 | Bhargav Kalambhe | Completed 4.29: `src/load_csv_data.py` — six `pd.read_csv` patterns (plain, `parse_dates`, explicit `dtype`+`na_values`, `usecols`+`index_col`, in-memory `StringIO` with `sep=';'`, safe `try/except FileNotFoundError`) with dtype before/after contrast on the date column (object → datetime64[ns]); README adds a six-row pattern table, full code listing, per-pattern explanations, and "common mistakes" matrix; black + ruff clean. New branching model: branched off `data-dev`; will PR `data4.29` → `data-dev`. |
| 2026-04-28 | Bhargav Kalambhe | Completed 4.30: `src/inspect_dataframe.py` — three-method inspection routine (`head` / `info` / `describe`) demonstrated on **two** frames: the 3-row bundled CSV (the form a learner first meets) AND a 120-row synthetic frame from `generate_realistic_postings()` with a lognormal salary distribution and ~12% NaN injected, so `info()` actually shows non-null gaps and `describe()` actually shows real spread, real quartiles, and real skew (salary mean 11.63 vs median 10.90 → +0.73 right-skew). Adds `info()` capture via `io.StringIO`, `isna().sum()` cross-check, `describe(include='all')` for categoricals, and an `explain_skewness()` helper. README expanded to cover both-frame demo, realistic `info()` output, realistic `describe()` table, and a "common mistakes" row specifically for "demoing on a 3-row toy CSV only". Branch `data4.30` off latest `data-dev`. |

---

## 6. Team Coordination Notes (unchanged from project brief)

- Harsh's backend Python functions (4.18–4.19) are consumed by Harshita's data-cleaning pipeline → coordinate interfaces early.
- Bhargav's NumPy work (4.22–4.26) underpins the ML-ready numerical layer → document array shapes for Harshita's stat modules.
- Bhargav's visualisations (4.39–4.43) depend on Harshita's cleaned DataFrames → agree on processed-file naming in week 1.
- All code must follow PEP 8 (Bhargav's 4.20) and be pushed to the shared repo with descriptive commit messages.
- Final README (4.44, Harshita) requires input summaries from all three members before submission.
