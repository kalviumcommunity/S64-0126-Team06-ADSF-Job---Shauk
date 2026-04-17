# Job-ही-Shauk

**Labour Market Intelligence for Smarter Career Decisions**

*"Shauk" (शौक) means passion or interest in Hindi — Job is my passion*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: ruff](https://img.shields.io/badge/linting-ruff-red.svg)](https://github.com/astral-sh/ruff)

---

## Table of Contents

- [Assignment & Task Updates](#assignment--task-updates)
- [Overview](#overview)
- [Question Data Insight Lifecycle Assignment](#question-data-insight-lifecycle-assignment)
- [Repository Understanding Milestone](#repository-understanding-milestone)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Pipeline Stages](#pipeline-stages)
- [Data Models](#data-models)
- [Visualizations](#visualizations)
- [Configuration](#configuration)
- [Testing](#testing)
- [CI/CD](#cicd)
- [Project Structure](#project-structure)
- [Key Insights](#key-insights)
- [Contributing](#contributing)
- [License](#license)

---

<!-- TEMP SECTION: Remove before final project submission -->
## Assignment & Task Updates

> **Note:** This section is temporary. It tracks ongoing assignment progress and task status for Sprint 3. Remove this section before final project submission.

### Sprint 3 — Assignment Tracker

| # | Assignment / Task | Owner | Status | Last Updated | Notes |
|---|---|---|---|---|---|
| 4.1 | | | | | |
| 4.2 | | | | | |
| 4.3 | | | | | |
| 4.4 | | | | | |
| 4.5 | Installing Python and Anaconda on the Local Machine | Harsh Singh | `Done` | 2026-04-17 | Installed via Anaconda distribution; `(base)` env confirmed |
| 4.6 | Verifying Python, Conda, and Jupyter Installation | Harsh Singh | `Done` | 2026-04-17 | All three verified via `--version` and `conda info` commands |
| 4.7 | Launching Jupyter Notebook and Understanding the Home Interface | Harsh Singh | `Done` | 2026-04-17 | Launched via `jupyter notebook`; Files / Running / Clusters tabs understood |
| 4.8 | Understanding Notebook Cells: Code vs Markdown | Harsh Singh | `Done` | 2026-04-17 | Code cells, Markdown cells, LaTeX rendering, and keyboard shortcuts covered |
| 4.9 | Running, Restarting, and Interrupting Jupyter Kernels | Harsh Singh | `Done` | 2026-04-17 | Interrupt, Restart, Restart & Run All — use cases and behaviour documented |

**Status options:** `Not Started` · `In Progress` · `Under Review` · `Done`

---

### Update Log

Use this log to record significant progress, blockers, or decisions. Add a new row each time something noteworthy happens.

| Date | Author | Update |
|---|---|---|
| 2026-04-17 | Harsh Singh | Completed assignments 4.5 – 4.9: Anaconda install, tool verification, Jupyter launch, cell types, and kernel management |

---
<!-- END TEMP SECTION -->

## Overview

Job-ही-Shauk is a production-grade, reproducible data science pipeline that analyzes labour market datasets to surface trending skills and identify correlations between specific skill sets and successful job placements. The system ingests publicly available job-posting and placement-outcome data, processes it through a structured 6-stage Python pipeline, and delivers actionable insights via statistical summaries and interactive visualizations.

### Core Research Question

> **"Which skills are trending, and which skill combinations correlate most strongly with successful job placement?"**

Every pipeline stage is oriented toward answering this question with statistical rigor, not just producing charts.

### What Makes This Different

- **Statistical Rigor**: Uses Wilson confidence intervals and placement lift calculations instead of naive rates
- **Skill Canonicalization**: Fuzzy matching eliminates spelling variants (e.g., "Python3" → "python")
- **Demand-Supply Analysis**: Joins job postings with candidate outcomes to compute market dynamics
- **Reproducibility**: Run manifests track git SHA, config hashes, and data hashes for bit-level reproducibility
- **Production-Ready**: CI/CD pipeline, property-based testing, structured logging, and modular architecture

---

## Question Data Insight Lifecycle Assignment

### 1) Explaining the Lifecycle: Question -> Data -> Insight

Data science starts with a **question**, not with a dashboard or a model.
A clear question defines the decision we want to support, the scope of the work, and what success looks like. Without this step, teams can produce technically correct analysis that answers the wrong problem.

In this project, a focused question is:
**"Which skills show strong market demand, and which skill combinations are linked with higher placement outcomes?"**

That question determines:
- what data we should collect,
- how we clean and structure it,
- which metrics are meaningful,
- and how we interpret the results.

The next stage is **data as evidence**. Data is not automatically useful just because we have it.
Before analysis, we need to understand:
- what each field actually means,
- how and when the data was collected,
- where values are missing or biased,
- and whether sources can be fairly compared.

For example, if job postings list skills in free text but outcome data uses different naming styles, we cannot compare demand and placement reliably until skills are standardized. So understanding data quality and context is part of the core reasoning, not a side task.

Finally, **insight** emerges from exploration plus interpretation.
Insight is not only "Python appears many times." Insight is "Python demand is high, supply is lower in some sectors, and its placement lift stays above baseline even after controlling for experience." That type of insight is decision-ready because it explains what action to take and why.

How the lifecycle connects:
- A precise question tells us what evidence matters.
- Data understanding makes that evidence trustworthy.
- Exploration turns trustworthy evidence into useful decisions.

### 2) Applying the Lifecycle to a Project Context

#### Project Context
An employability training institute wants to redesign its next 6-month analytics bootcamp to improve student placement outcomes.

#### Question to Answer
**"Which 8-10 skills should be prioritized so graduates are more likely to be placed within 90 days?"**

#### Data Needed
- **Job demand data** from job boards and company postings:
  - required skills,
  - role titles,
  - sector,
  - experience expectations,
  - posting date.
- **Candidate outcome data** from institute records:
  - student skill profiles,
  - project background,
  - placement status,
  - time-to-placement,
  - offered salary.
- **Optional validation data** from recruiter feedback:
  - whether trained skills match real hiring needs.

This data represents both sides of the same labor market:
- employer demand (what companies ask for),
- learner outcomes (what leads to placement success).

#### Useful Decision-Making Insight
A useful insight would be:
**"Learners with Python + SQL + dashboarding skills have consistently higher placement probability across sectors, while some high-frequency skills add little marginal placement value."**

This supports concrete decisions:
- prioritize high-impact skill bundles,
- reduce low-impact content,
- align curriculum with measurable hiring demand.

---

## Repository Understanding Milestone

### 1) Project Intent and High-Level Flow

This repository is trying to answer a labor-market decision problem:  
**Which skills are in demand, and which skill patterns are associated with stronger placement outcomes?**

The intent is not only to "analyze data," but to connect two practical views of employability:
- employer-side demand from job postings,
- candidate-side outcomes from placement records.

The high-level workflow follows a typical data science lifecycle:
- **Problem framing**: define a concrete employability question.
- **Data understanding and preparation**: ingest, validate, clean, and standardize raw sources.
- **Feature harmonization**: canonicalize skill names so cross-source comparison is reliable.
- **Integration and analysis**: join demand and outcome signals, compute rates/lift/confidence intervals.
- **Communication**: produce figures and insight artifacts for interpretation and decisions.

The structure reflects these lifecycle stages by separating raw/interim/processed data, stage-wise notebooks, reusable utilities, and final outputs. This makes it easier to trace how a result was produced and where each transformation happened.

### 2) Repository Structure and File Roles

#### What work happens in major folders
- `data/`: staged datasets (`raw`, `interim`, `processed`, `output`) showing the progression from source files to analysis-ready tables.
- `notebooks/`: stage-based workflow execution and investigation; these are the primary pipeline touchpoints.
- `src/`: reusable logic (IO, cleaning, canonicalization, join, stats, visualization) and orchestration in `pipeline.py`.
- `configs/`: schemas and parameters (e.g., thresholds, vocabulary rules) that control behavior without hard-coding.
- `outputs/`: generated artifacts (charts, narrative insights) intended for consumption, not manual editing.
- `tests/`: unit/property/integration checks that protect expected behavior.

#### Exploratory work vs finalized analysis in this repository
Exploratory work appears in notebooks where intermediate checks, profiling, and step-level validation are visible. Finalized analysis is represented by reusable functions in `src/`, codified configs in `configs/`, tested behavior in `tests/`, and reproducible output artifacts in `outputs/`.

#### Where a new contributor should be cautious
- Treat `data/raw/` as immutable source-of-truth input.
- Avoid editing generated files in `outputs/` directly.
- Be careful when changing schema expectations and canonical vocabulary rules, because those can affect downstream joins and metrics.
- Prefer adding/changing logic in `src/` with tests, then re-running notebooks/pipeline rather than patching notebook outputs by hand.

### 3) Assumptions, Gaps, and Open Questions

#### Assumptions visible in the project
- Skill mentions are assumed to be meaningful proxies for market demand and candidate capability.
- Placement outcomes are treated as comparable across sectors/time after cleaning and standardization.
- Canonicalization and fuzzy matching thresholds are assumed to preserve semantic meaning without introducing major mapping errors.
- Available datasets are assumed sufficient to estimate practical relationships (e.g., lift), even though they may not capture all external factors.

#### Missing documentation or unclear points
- The expected provenance and refresh cadence of source datasets could be clearer.
- It is not fully explicit which outputs are considered authoritative for decision-making when notebook and script runs differ.
- Re-run order is documented, but contributor guidance for "safe extension" patterns (where to add a new analysis end-to-end) can be more explicit.

#### One improvement to make extension easier
Add a short **"Contributor Decision Guide"** section that answers:
- where to place a new analysis notebook/module,
- how to register new configs/schemas,
- which tests are mandatory before PR,
- and which artifacts should or should not be committed.

This would reduce onboarding time and lower risk of accidental breakage for first-time contributors.

---

## Key Features

### 🎯 Core Capabilities

- **6-Stage ETL Pipeline**: Ingestion → Cleaning → Canonicalization → Join → Analysis → Visualization
- **Skill Vocabulary Management**: External YAML-based canonical skill mapping with fuzzy matching (rapidfuzz)
- **Statistical Analysis**: Placement lift, Wilson confidence intervals, stratified analysis by experience
- **Interactive Visualizations**: 7 static PNG charts + optional Plotly HTML exports
- **Adaptive Temporal Granularity**: Auto-selects daily/weekly/monthly/quarterly based on date range
- **Group-wise Null Filling**: Sector-level medians with global fallback

### 🔬 Advanced Features

- **Property-Based Testing**: 18 correctness properties validated via Hypothesis
- **Run Manifests**: JSON artifacts tracking git SHA, config hash, input/output hashes, stage durations
- **Structured Logging**: Rich-formatted logs with daily rotation and 30-day retention
- **Colorblind-Safe Palettes**: Okabe-Ito and other accessible color schemes
- **Modular Architecture**: `src/utils/` split into io, validate, clean, canonicalize, join, stats, viz modules

---

## Architecture

### System Architecture Overview

```mermaid
graph TD
    A[Raw CSV Files<br/>job_postings.csv<br/>placement_outcomes.csv] --> B[Stage 1: Ingestion<br/>01_ingestion.ipynb]
    CFG[configs/<br/>skills_canonical.yaml<br/>pipeline.yaml] --> B
    B --> C[Stage 2: Cleaning<br/>02_cleaning.ipynb]
    C --> D[Stage 3: Canonicalization<br/>03_canonicalize.ipynb<br/>C6]
    CFG --> D
    D --> E[Stage 4: Join<br/>04_join.ipynb]
    E --> F[Stage 5: Analysis<br/>05_analysis.ipynb<br/>C7]
    F --> G[Stage 6: Visualization<br/>06_visualisation.ipynb]
    G --> H[Outputs<br/>charts .png + .html<br/>clean CSVs<br/>insights.md]

    subgraph "C2: Python Core Layer"
        B
        C
        D
        E
        F
        G
    end

    subgraph "C1: Project Scaffolding"
        I[src/utils/<br/>Modular helpers]
        J[src/pipeline.py<br/>Orchestrator]
    end

    I --> B
    I --> C
    I --> D
    I --> E
    I --> F
    I --> G
    J --> B
```

### Component Legend

| Component | Description |
|---|---|
| **C1** | Project Scaffolding — folder structure, environment, configs |
| **C2** | Python Core Layer — shared utility modules with type hints |
| **C3** | Numerical Engine — NumPy vectorised operations |
| **C4** | Data Pipeline — ingestion and cleaning notebooks |
| **C5** | Insight & Reporting — analysis and visualisation notebooks |
| **C6** | Canonicalization Layer — skill vocabulary mapping and fuzzy matching |
| **C7** | Statistical Engine — lift, Wilson CI, stratified analysis |

### Data Flow Diagram

```mermaid
graph LR
    E1([Job Postings CSV]) --> P[Job-ही-Shauk<br/>Pipeline]
    E2([Placement Outcomes CSV]) --> P
    E3([configs/]) --> P
    P --> O1([Charts .png + .html])
    P --> O2([Clean CSVs])
    P --> O3([insights.md])
    P --> O4([Aggregated Tables])
    P --> O5([Run Manifest JSON])
```

### Pipeline Execution Flow

```mermaid
sequenceDiagram
    participant Raw as Raw Data (CSV)
    participant Cfg as configs/
    participant Ingest as 01_ingestion.ipynb
    participant Clean as 02_cleaning.ipynb
    participant Canon as 03_canonicalize.ipynb
    participant Join as 04_join.ipynb
    participant Analyse as 05_analysis.ipynb
    participant Viz as 06_visualisation.ipynb
    participant Out as outputs/

    Raw->>Ingest: load_csv() + validate_schema()
    Ingest->>Ingest: inspect_dataframe() + check_nulls() + check_duplicates()
    Ingest->>Ingest: assert_dtypes()
    Ingest->>Clean: validated raw DataFrames
    Clean->>Clean: drop_null_rows() + fill_nulls_grouped() + remove_duplicates()
    Clean->>Clean: standardise_columns() + parse_skill_list() + standardise_dates()
    Clean->>Canon: data/interim/*.csv
    Cfg->>Canon: load_skill_vocabulary()
    Canon->>Canon: canonicalize_skill_list()
    Canon->>Join: canonicalized DataFrames + report
    Join->>Join: build_skill_demand_supply_table()
    Join->>Join: build_sector_skill_matrix()
    Join->>Analyse: data/processed/*.csv
    Analyse->>Analyse: compute_placement_lift() + wilson_confidence_interval()
    Analyse->>Analyse: stratified_placement_analysis() + select_temporal_granularity()
    Analyse->>Viz: aggregated result DataFrames
    Viz->>Out: top_skills.png, skill_trend.png, placement_rate.png
    Viz->>Out: salary_dist.png, salary_exp_scatter.png, skill_boxplot.png, corr_heatmap.png
    Viz->>Out: interactive HTML charts (optional)
```

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Runtime** | Python | 3.10+ | Core language |
| **Environment** | Anaconda / Conda | Latest | Dependency isolation |
| **Notebook** | Jupyter Notebook | 6.x / 7.x | Interactive pipeline execution |
| **Data Manipulation** | Pandas | 2.x | DataFrame operations, ETL |
| **Numerical Compute** | NumPy | 1.24+ | Vectorised array operations |
| **Statistical Compute** | SciPy | ≥ 1.11 | Wilson confidence intervals |
| **Fuzzy Matching** | rapidfuzz | ≥ 3.0 | C-optimized skill matching |
| **Config Management** | PyYAML | ≥ 6.0 | External config parsing |
| **Visualisation** | Matplotlib | 3.7+ | Base plotting engine |
| **Visualisation** | Seaborn | 0.12+ | Statistical chart styling |
| **Visualisation** | Plotly | ≥ 5.18 | Interactive HTML exports |
| **Code Quality** | ruff | ≥ 0.1 | Fast Python linting |
| **Code Formatting** | black | ≥ 24.0 | Opinionated formatting |
| **Logging** | rich | ≥ 13.0 | Colorized structured logging |
| **Testing** | pytest | ≥ 7.0 | Unit test runner |
| **Testing** | hypothesis | ≥ 6.0 | Property-based testing |

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Anaconda or Miniconda
- Git

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-org/job-hi-shauk.git
cd job-hi-shauk
```

2. **Create conda environment**

```bash
conda env create -f environment.yml
conda activate job-hi-shauk
```

3. **Verify installation**

```bash
python -c "import pandas, numpy, scipy, rapidfuzz; print('All dependencies installed!')"
```

### Quick Start

1. **Place raw data files** in `data/raw/`:
   - `job_postings.csv`
   - `placement_outcomes.csv`

2. **Run the pipeline** (execute notebooks in order):

```bash
# Option 1: Run all notebooks sequentially
jupyter nbconvert --to notebook --execute notebooks/01_ingestion.ipynb
jupyter nbconvert --to notebook --execute notebooks/02_cleaning.ipynb
jupyter nbconvert --to notebook --execute notebooks/03_canonicalize.ipynb
jupyter nbconvert --to notebook --execute notebooks/04_join.ipynb
jupyter nbconvert --to notebook --execute notebooks/05_analysis.ipynb
jupyter nbconvert --to notebook --execute notebooks/06_visualisation.ipynb

# Option 2: Use the orchestrator script (v2)
python src/pipeline.py
```

3. **View outputs**:
   - Charts: `outputs/figures/*.png`
   - Interactive charts: `outputs/interactive/*.html`
   - Insights: `outputs/insights.md`
   - Run manifest: `configs/run_manifest_*.json`

---

## Pipeline Stages

### Stage 1: Ingestion

**Purpose**: Load and validate raw CSV files against expected schemas.

**Key Functions**:
- `load_csv()` — Parse CSVs with date column handling
- `validate_schema()` — Assert all required columns present
- `assert_dtypes()` — Verify column data types
- `inspect_dataframe()` — Display shape, dtypes, null counts

**Outputs**: Validated DataFrames ready for cleaning

---

### Stage 2: Cleaning

**Purpose**: Clean, deduplicate, and standardize raw data.

**Key Functions**:
- `standardise_columns()` — Lowercase column names, replace spaces with underscores
- `drop_null_rows()` — Remove rows exceeding null threshold
- `fill_nulls_grouped()` — Fill nulls with sector-level medians (v2)
- `remove_duplicates()` — Deduplicate on primary keys
- `parse_skill_list()` — Split comma-separated skills into lists
- `standardise_dates()` — Parse date columns with coercion

**Outputs**: `data/interim/jobs_cleaned.csv`, `data/interim/placements_cleaned.csv`

---

### Stage 3: Canonicalization (v2)

**Purpose**: Map raw skill strings to canonical vocabulary using fuzzy matching.

**Three-Tier Resolution**:
1. **Exact Match** (O(1)): Direct dictionary lookup
2. **Fuzzy Match**: rapidfuzz with configurable threshold (default 88%)
3. **Unmatched**: Flagged for vocabulary expansion

**Key Functions**:
- `load_skill_vocabulary()` — Load YAML vocabulary with version validation
- `canonicalize_skill()` — Map single skill to canonical form
- `canonicalize_skill_list()` — Process entire skill lists

**Outputs**: 
- `data/interim/jobs_canonicalized.csv`
- `data/interim/placements_canonicalized.csv`
- `data/interim/canonicalization_report.csv` (audit trail)

**Example**:
```
"pythn" → "python" (fuzzy match, score 92)
"machine learning" → "machine_learning" (exact match)
"xyz123" → null (unmatched)
```

---

### Stage 4: Join (v2)

**Purpose**: Outer join job postings and placement outcomes to compute demand-supply dynamics.

**Key Functions**:
- `build_skill_demand_supply_table()` — Compute demand count, supply count, placement rates, lift
- `build_sector_skill_matrix()` — Pivot table of skills by sector

**Outputs**: `data/processed/skill_demand_supply.csv`, `data/processed/sector_skill_matrix.csv`

**Schema**: SKILL_DEMAND_SUPPLY
- `canonical_skill` (primary key)
- `demand_count` — # job postings requiring this skill
- `supply_count` — # candidates listing this skill
- `placed_with_skill`, `unplaced_with_skill`
- `demand_supply_ratio`
- `base_placement_rate`, `skill_placement_rate`, `lift`
- `wilson_ci_low`, `wilson_ci_high`

---

### Stage 5: Analysis (v2)

**Purpose**: Compute statistically grounded insights with confidence intervals.

**Key Functions**:
- `compute_placement_lift()` — P(placed|skill) / P(placed)
- `wilson_confidence_interval()` — Binomial CI via scipy.stats
- `stratified_placement_analysis()` — Control for experience confounding
- `select_temporal_granularity()` — Auto-select D/W/M/Q based on date range
- `skill_trend_over_time()` — Temporal trend analysis
- `correlation_matrix()` — Pearson correlations
- `detect_outliers_iqr()` — IQR-based outlier detection

**Outputs**: `data/output/placement_lift.csv`, `data/output/stratified_rates.csv`, `data/output/skill_trends.csv`

---

### Stage 6: Visualization

**Purpose**: Generate 7 static PNG charts + optional interactive HTML exports.

**Charts**:
1. **Top-20 Skills by Frequency** (Horizontal Bar, Okabe-Ito palette)
2. **Skill Trend Over Time** (Line Plot, tab10 palette)
3. **Placement Lift by Skill** (Bar Chart, RdBu_r diverging)
4. **Salary Distribution** (Histogram, viridis)
5. **Salary vs Experience** (Scatter Plot, plasma)
6. **Skill Count Boxplot** (Boxplot by Sector, Set2)
7. **Correlation Heatmap** (Seaborn Heatmap, coolwarm)

**Export Contract**:
```python
plt.tight_layout()
plt.savefig(output_path, dpi=150, bbox_inches='tight')
plt.show()
assert os.path.exists(output_path)
df_hash = hashlib.sha256(pd.util.hash_pandas_object(underlying_df).values).hexdigest()
assert df_hash == expected_hash or is_first_run
plt.close()
```

**Outputs**: `outputs/figures/*.png`, `outputs/interactive/*.html`

---

## Data Models

### Input Schema: job_postings.csv

| Column | Type | Nullable | Description |
|---|---|---|---|
| `job_id` | int64 | No | Unique identifier (primary key) |
| `job_title` | object | No | Role title |
| `company` | object | Yes | Hiring company |
| `sector` | object | Yes | Industry sector |
| `location` | object | Yes | City/State |
| `skills_required` | object | No | Comma-separated skill tags |
| `date_posted` | datetime | No | Posting date |
| `experience_min_yrs` | float64 | Yes | Minimum years required |
| `salary_lpa` | float64 | Yes | Annual salary (Lakhs INR) |

### Input Schema: placement_outcomes.csv

| Column | Type | Nullable | Description |
|---|---|---|---|
| `candidate_id` | int64 | No | Unique identifier (primary key) |
| `skills` | object | No | Comma-separated skills |
| `education` | object | Yes | Highest qualification |
| `years_of_experience` | float64 | Yes | Total experience |
| `placed` | int64 (0/1) | No | Binary placement status |
| `placement_date` | datetime | Yes | Date of placement |
| `offered_salary_lpa` | float64 | Yes | Offered salary |
| `sector_placed_in` | object | Yes | Placement sector |

### Output Schema: SKILL_DEMAND_SUPPLY (Stage 4)

| Column | Type | Description |
|---|---|---|
| `canonical_skill` | object | Primary key |
| `demand_count` | int64 | # job postings requiring skill |
| `supply_count` | int64 | # candidates with skill |
| `placed_with_skill` | int64 | # placed candidates with skill |
| `unplaced_with_skill` | int64 | # unplaced candidates with skill |
| `demand_supply_ratio` | float64 | demand / supply |
| `base_placement_rate` | float64 | Overall P(placed) |
| `skill_placement_rate` | float64 | P(placed \| skill) |
| `lift` | float64 | skill_rate / base_rate |
| `wilson_ci_low` | float64 | 95% CI lower bound |
| `wilson_ci_high` | float64 | 95% CI upper bound |

---

## Visualizations

### Sample Outputs

#### Top-20 Skills by Frequency
![Top Skills](outputs/figures/top_skills.png)

#### Skill Trend Over Time
![Skill Trend](outputs/figures/skill_trend.png)

#### Placement Lift by Skill
![Placement Lift](outputs/figures/placement_lift.png)

#### Salary Distribution
![Salary Distribution](outputs/figures/salary_dist.png)

#### Salary vs Experience
![Salary vs Experience](outputs/figures/salary_exp_scatter.png)

#### Skill Count Boxplot by Sector
![Skill Boxplot](outputs/figures/skill_boxplot.png)

#### Correlation Heatmap
![Correlation Heatmap](outputs/figures/corr_heatmap.png)

---

## Configuration

### configs/skills_canonical.yaml

External vocabulary management with semantic versioning:

```yaml
version: "2.1.0"
last_updated: "2026-04-15"
changelog:
  - version: "2.1.0"
    date: "2026-04-15"
    changes: "Merged 'machine learning' and 'ml' into canonical 'machine_learning'"

fuzzy_match_threshold: 0.88

canonical_skills:
  python:
    aliases: ["python3", "python 3", "py", "python programming"]
    category: "programming_language"
  
  machine_learning:
    aliases: ["ml", "machine learning", "machinelearning"]
    category: "data_science"
  
  sql:
    aliases: ["structured query language", "mysql", "postgresql", "tsql"]
    category: "database"
```

### configs/pipeline.yaml

Pipeline parameters and thresholds:

```yaml
random_seed: 42
null_thresholds:
  drop_column: 0.80
  drop_row: 0.50
min_support: 5
temporal_granularity_rules:
  - max_days: 14
    rule: "D"
  - max_days: 90
    rule: "W"
  - max_days: 730
    rule: "M"
  - max_days: 9999
    rule: "Q"
logging:
  level: "INFO"
  rotation: "daily"
  retention_days: 30
```

---

## Testing

### Unit Tests

25 test cases covering all utility functions:

```bash
pytest tests/test_utils.py -v
```

**Coverage**:
- TC-01 to TC-12: Original v1 functions
- TC-13 to TC-25: v2 functions (canonicalization, join, stats)

### Property-Based Tests

18 correctness properties validated via Hypothesis:

```bash
pytest tests/test_utils.py -v -k "property"
```

**Key Properties**:
- Property 1: `parse_skill_list` round-trip idempotence
- Property 13: `canonicalize_skill` output always canonical or None
- Property 15: Wilson CI bounds contain sample proportion
- Property 18: Structural determinism (data-hash equality)

### Integration Tests

End-to-end pipeline on synthetic fixtures:

```bash
pytest tests/test_integration.py -v
```

**Assertions**:
- All 7 PNG files created
- Run manifest JSON with non-empty git SHA
- Input/output hash matching

---

## CI/CD

### GitHub Actions Workflow

`.github/workflows/ci.yml` runs on every push:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Conda
        uses: conda-incubator/setup-miniconda@v2
        with:
          environment-file: environment.yml
      - name: Lint with ruff
        run: ruff check src/ tests/
      - name: Format check with black
        run: black --check src/ tests/
      - name: Run tests with coverage
        run: pytest tests/ --cov=src --cov-report=term-missing
      - name: Run integration tests
        run: pytest tests/test_integration.py -v
```

**Failure gates the PR** — no merge until all checks pass.

---

## Project Structure

```
job-hi-shauk/
├── configs/                    # External configuration (v2)
│   ├── skills_canonical.yaml  # Canonical skill vocabulary
│   ├── pipeline.yaml           # Pipeline parameters
│   └── schemas.py              # Schema definitions
├── data/
│   ├── raw/                    # Original CSVs (read-only)
│   ├── interim/                # Between-stage checkpoints (v2)
│   ├── processed/              # Cleaned DataFrames
│   └── output/                 # Aggregated tables
├── notebooks/
│   ├── 01_ingestion.ipynb      # Load & validate
│   ├── 02_cleaning.ipynb       # Clean & standardize
│   ├── 03_canonicalize.ipynb   # Skill vocabulary mapping (v2)
│   ├── 04_join.ipynb           # Demand-supply join (v2)
│   ├── 05_analysis.ipynb       # Statistical analysis (v2)
│   └── 06_visualisation.ipynb  # Chart generation
├── outputs/
│   ├── figures/                # PNG exports
│   ├── interactive/            # Plotly HTML (v2)
│   └── insights.md             # Auto-generated narrative (v2)
├── src/
│   ├── utils/                  # Modular package (v2)
│   │   ├── io.py               # CSV loading
│   │   ├── validate.py         # Schema validation
│   │   ├── clean.py            # Cleaning functions
│   │   ├── canonicalize.py     # Skill mapping (v2)
│   │   ├── join.py             # Demand-supply join (v2)
│   │   ├── stats.py            # Statistical engine (v2)
│   │   ├── viz.py              # Chart helpers
│   │   └── logging_config.py   # Structured logging (v2)
│   └── pipeline.py             # Orchestrator (v2)
├── tests/
│   ├── fixtures/               # Synthetic test data
│   ├── test_utils.py           # Unit tests
│   ├── test_canonicalize.py    # Canonicalization tests (v2)
│   ├── test_join.py            # Join tests (v2)
│   ├── test_stats.py           # Stats tests (v2)
│   └── test_integration.py     # End-to-end tests
├── .github/workflows/ci.yml    # CI/CD pipeline (v2)
├── .gitignore
├── environment.yml
├── pyproject.toml              # ruff + black config (v2)
└── README.md
```

---

## Key Insights

### Top-5 Trending Skills (Example)

Based on pipeline analysis of 10,000 job postings and 5,000 placement outcomes:

1. **Python** — 62% of postings, placement lift 1.35 (35% above baseline)
2. **SQL** — 58% of postings, placement lift 1.28
3. **Machine Learning** — 45% of postings, placement lift 1.42
4. **Data Visualization** — 38% of postings, placement lift 1.18
5. **Cloud Computing** — 32% of postings, placement lift 1.25

### Placement Lift Analysis

**Lift** = P(placed | skill) / P(placed)

- Lift > 1.0: Skill improves placement probability
- Lift = 1.0: Skill has no effect
- Lift < 1.0: Skill correlates with lower placement (rare)

**Example**: If base placement rate is 60% and Python skill holders have 81% placement rate, then lift = 81% / 60% = 1.35.

### Stratified Analysis

Placement rates by experience level (controlling for confounding):

| Experience | Placement Rate | 95% CI | Sample Size |
|---|---|---|---|
| 0-2 years | 52% | [48%, 56%] | 1,200 |
| 2-5 years | 68% | [64%, 72%] | 1,800 |
| 5+ years | 79% | [75%, 83%] | 2,000 |

### Demand-Supply Dynamics

| Skill | Demand Count | Supply Count | D/S Ratio | Interpretation |
|---|---|---|---|---|
| Python | 6,200 | 3,800 | 1.63 | High demand, moderate supply |
| SQL | 5,800 | 4,200 | 1.38 | Balanced market |
| Machine Learning | 4,500 | 2,100 | 2.14 | **Undersupplied** — opportunity |
| Excel | 3,200 | 4,800 | 0.67 | Oversupplied |

---

## Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Install dev dependencies: `conda env create -f environment.yml`
4. Make changes and add tests
5. Run linting: `ruff check src/ tests/`
6. Run formatting: `black src/ tests/`
7. Run tests: `pytest tests/ --cov=src`
8. Commit with descriptive message
9. Push and create a Pull Request

### Code Standards

- Follow PEP 8 (enforced by ruff + black)
- Add type hints to all functions
- Write docstrings (Google style)
- Maintain test coverage > 80%
- Update README for new features

### Vocabulary Expansion

To add new canonical skills:

1. Edit `configs/skills_canonical.yaml`
2. Bump version (semantic versioning)
3. Add changelog entry
4. Run canonicalization stage
5. Review `data/interim/canonicalization_report.csv`
6. Commit with message: `vocab: add [skill_name] v[version]`

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Team 06**: Harshita Soni (Leader), Harsh Singh, Harsh Singh
- **Sprint**: Module 4 – Sprint #3: Applied Data Science Foundations
- **Version**: v2.0 (April 2026)

---

## Version History

### v2.0 (Current) — April 2026

- Added Stage 3 (Canonicalization) and Stage 4 (Join)
- Added Statistical Engine (lift, Wilson CI, stratification)
- Externalized configs to YAML
- Restructured `src/utils` into modular package
- Added run manifests for reproducibility
- Replaced byte-level determinism with structural determinism
- Added group-wise null filling
- Added adaptive temporal granularity
- Added CI/CD pipeline (GitHub Actions)
- Added 6 new correctness properties (Properties 13-18)
- Added 13 new unit test cases (TC-13 through TC-25)

### v1.0 — January 2026

- Initial 4-stage linear ETL pipeline
- 12 correctness properties
- PNG-only visualization
- Monolithic `src/utils.py`

---

## Contact

For questions or support, please open an issue on GitHub or contact the team at [team06@example.com](mailto:team06@example.com).

---

**Built with ❤️ by Team 06 | Empowering Career Decisions Through Data**
