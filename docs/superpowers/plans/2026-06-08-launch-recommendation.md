# Launch Recommendation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `pages/7_Launch_Recommendation.py` — a read-only executive synthesis page that ranks all video game genres by a composite Opportunity Score and Risk Score, displayed as a dual-view dashboard (all-time benchmark + current generation).

**Architecture:** Core computation is isolated in `utils/launch_recommendation.py` (two pure functions: `compute_genre_scores` and `get_current_gen_df`) so it can be unit-tested without importing Streamlit. The page file imports those functions and wires them into four rendering functions. Dual view runs `compute_genre_scores` twice — once on the full dataset, once on the current-generation slice.

**Tech Stack:** Python 3.10+, Streamlit 1.56, Plotly (`go.Bar`, `go.Scatter`, `go.Table`), pandas, numpy, pytest

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `utils/launch_recommendation.py` | `compute_genre_scores(df)` + `get_current_gen_df(df)` |
| Create | `tests/__init__.py` | makes tests/ a package |
| Create | `tests/test_launch_recommendation.py` | unit tests for the two utility functions |
| Create | `pages/7_Launch_Recommendation.py` | page config, rendering functions, main layout |
| Modify | `requirements.txt` | add `pytest` |
| Modify | `README.md` | add page 7 entry in Estratégias section + Conclusão update |

---

## Task 1: Add pytest to requirements and create test scaffold

**Files:**
- Modify: `requirements.txt`
- Create: `tests/__init__.py`
- Create: `tests/test_launch_recommendation.py`

- [ ] **Step 1: Add pytest to requirements.txt**

Append one line to `requirements.txt`:
```
pytest==8.3.5
```

- [ ] **Step 2: Create `tests/__init__.py`** (empty file)

- [ ] **Step 3: Create the test file with fixture and stubs**

Create `tests/test_launch_recommendation.py`:
```python
import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_df():
    """Minimal DataFrame mimicking dataset_clean() output — 2 genres, 60 titles each."""
    n = 60
    return pd.DataFrame({
        'genre':        ['Shooter'] * n + ['RPG'] * n,
        'total_sales':  [1.5] * n + [0.8] * n,
        'na_sales':     [0.8] * n + [0.1] * n,
        'jp_sales':     [0.1] * n + [0.6] * n,
        'pal_sales':    [0.4] * n + [0.1] * n,
        'other_sales':  [0.2] * n + [0.0] * n,
        'critic_score': [8.5] * (n // 2) + [6.5] * (n // 2) + [8.0] * (n // 2) + [6.0] * (n // 2),
        'console':      ['PS3'] * n + ['DS'] * n,
        'start_year':   [2006] * n + [2004] * n,
        'release_date': ['2008-01-01'] * n + ['2006-01-01'] * n,
        'generation':   ['7th Gen'] * n + ['6th Gen'] * n,
    })


def test_placeholder():
    assert True
```

- [ ] **Step 4: Install pytest and verify scaffold runs**

```bash
pip install pytest==8.3.5
pytest tests/ -v
```

Expected output: `1 passed` (the placeholder test).

- [ ] **Step 5: Commit**

```bash
git add requirements.txt tests/__init__.py tests/test_launch_recommendation.py
git commit -m "test: scaffold test suite for launch recommendation"
```

---

## Task 2: Implement `utils/launch_recommendation.py`

**Files:**
- Create: `utils/launch_recommendation.py`

- [ ] **Step 1: Write the failing tests (replace placeholder in test file)**

Replace the entire content of `tests/test_launch_recommendation.py`:

```python
import pytest
import pandas as pd
import numpy as np
from utils.launch_recommendation import compute_genre_scores, get_current_gen_df


@pytest.fixture
def sample_df():
    """Minimal DataFrame mimicking dataset_clean() output — 2 genres, 60 titles each."""
    n = 60
    return pd.DataFrame({
        'genre':        ['Shooter'] * n + ['RPG'] * n,
        'total_sales':  [1.5] * n + [0.8] * n,
        'na_sales':     [0.8] * n + [0.1] * n,
        'jp_sales':     [0.1] * n + [0.6] * n,
        'pal_sales':    [0.4] * n + [0.1] * n,
        'other_sales':  [0.2] * n + [0.0] * n,
        'critic_score': [8.5] * (n // 2) + [6.5] * (n // 2) + [8.0] * (n // 2) + [6.0] * (n // 2),
        'console':      ['PS3'] * n + ['DS'] * n,
        'start_year':   [2006] * n + [2004] * n,
        'release_date': ['2008-01-01'] * n + ['2006-01-01'] * n,
        'generation':   ['7th Gen'] * n + ['6th Gen'] * n,
    })


def test_returns_one_row_per_genre(sample_df):
    result = compute_genre_scores(sample_df)
    assert len(result) == 2
    assert set(result['genre']) == {'Shooter', 'RPG'}


def test_scores_in_valid_range(sample_df):
    result = compute_genre_scores(sample_df)
    assert result['opportunity_score'].between(0, 100).all(), "opportunity_score out of 0-100 range"
    assert result['risk_score'].between(0, 100).all(), "risk_score out of 0-100 range"


def test_required_columns_present(sample_df):
    result = compute_genre_scores(sample_df)
    required = {'genre', 'opportunity_score', 'risk_score', 'best_platform', 'best_timing', 'min_score'}
    assert required.issubset(set(result.columns))


def test_sorted_by_opportunity_descending(sample_df):
    result = compute_genre_scores(sample_df)
    scores = result['opportunity_score'].tolist()
    assert scores == sorted(scores, reverse=True), "Result not sorted by opportunity_score descending"


def test_shooter_higher_opportunity_than_rpg(sample_df):
    """Shooter: higher mean sales (1.5 vs 0.8) + better regional reach — must outscore RPG."""
    result = compute_genre_scores(sample_df).set_index('genre')
    assert result.loc['Shooter', 'opportunity_score'] > result.loc['RPG', 'opportunity_score']


def test_rpg_higher_risk_due_to_jp_concentration(sample_df):
    """RPG: 75% JP concentration (0.6/0.8) vs Shooter 53% NA — RPG must have higher risk."""
    result = compute_genre_scores(sample_df).set_index('genre')
    assert result.loc['RPG', 'risk_score'] > result.loc['Shooter', 'risk_score']


def test_get_current_gen_selects_latest_by_start_year():
    df = pd.DataFrame({
        'generation': ['5th Gen', '6th Gen', '7th Gen', '7th Gen'],
        'start_year': [1994, 2000, 2005, 2005],
        'total_sales': [1.0, 1.0, 1.0, 1.0],
    })
    result = get_current_gen_df(df)
    assert (result['generation'] == '7th Gen').all()
    assert len(result) == 2
```

- [ ] **Step 2: Run tests to confirm they fail (import error expected)**

```bash
pytest tests/test_launch_recommendation.py -v
```

Expected: `ImportError: cannot import name 'compute_genre_scores' from 'utils.launch_recommendation'`

- [ ] **Step 3: Create `utils/launch_recommendation.py`**

```python
import pandas as pd
import numpy as np

SCORE_THRESHOLD = 8.0


def compute_genre_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- Regional sums per genre ---
    g_sum = df.groupby('genre')[['total_sales', 'na_sales', 'jp_sales', 'pal_sales', 'other_sales']].sum()
    regional_shares = pd.DataFrame({
        'na':    g_sum['na_sales']    / g_sum['total_sales'],
        'jp':    g_sum['jp_sales']    / g_sum['total_sales'],
        'pal':   g_sum['pal_sales']   / g_sum['total_sales'],
        'other': g_sum['other_sales'] / g_sum['total_sales'],
    })
    regional_max = regional_shares.max(axis=1)

    # --- Opportunity sub-scores ---
    mean_sales = df.groupby('genre')['total_sales'].mean()
    sales_score = mean_sales / mean_sales.max() * 100

    reach_score = (1 - regional_max) * 100

    def _score_multiplier(sub):
        above = sub.loc[sub['critic_score'] >= SCORE_THRESHOLD, 'total_sales'].mean()
        below = sub.loc[sub['critic_score'] < SCORE_THRESHOLD, 'total_sales'].mean()
        if pd.isna(below) or below == 0:
            return 1.0
        if pd.isna(above):
            return 0.0
        return above / below

    raw_mult = df.groupby('genre').apply(_score_multiplier)
    score_multiplier = raw_mult.clip(0, 5) / 5 * 100

    # --- Risk sub-scores ---
    regional_concentration = regional_max * 100

    cv = df.groupby('genre')['total_sales'].std() / mean_sales
    cv_clipped = cv.clip(0, 2.0)
    cv_min, cv_max = cv_clipped.min(), cv_clipped.max()
    if cv_max > cv_min:
        score_sensitivity = (cv_clipped - cv_min) / (cv_max - cv_min) * 100
    else:
        score_sensitivity = pd.Series(50.0, index=cv.index)

    title_count = df.groupby('genre')['total_sales'].count()
    saturation_raw = title_count / mean_sales
    s_min, s_max = saturation_raw.min(), saturation_raw.max()
    if s_max > s_min:
        market_saturation = (saturation_raw - s_min) / (s_max - s_min) * 100
    else:
        market_saturation = pd.Series(50.0, index=saturation_raw.index)

    # --- Composite scores ---
    opportunity_score = (
        0.40 * sales_score +
        0.30 * reach_score +
        0.30 * score_multiplier
    ).round(0).astype(int).clip(0, 100)

    risk_score = (
        0.40 * regional_concentration +
        0.30 * score_sensitivity +
        0.30 * market_saturation
    ).round(0).astype(int).clip(0, 100)

    # --- Detail sub-metrics ---
    best_platform = (
        df.groupby(['genre', 'console'])['total_sales'].mean()
        .reset_index()
        .sort_values('total_sales', ascending=False)
        .groupby('genre')['console'].first()
    )

    df['_release_year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year
    df['_cycle_offset'] = (df['_release_year'] - df['start_year']).clip(lower=0)
    best_timing_raw = (
        df.groupby(['genre', '_cycle_offset'])['total_sales'].mean()
        .reset_index()
        .sort_values('total_sales', ascending=False)
        .groupby('genre')['_cycle_offset'].first()
    )
    best_timing = best_timing_raw.apply(lambda x: f"Ano {int(x)} do ciclo")

    def _min_score(sub):
        median_s = sub['total_sales'].median()
        scores = sub.loc[sub['total_sales'] > median_s, 'critic_score'].dropna()
        return round(float(np.percentile(scores, 70)), 1) if len(scores) > 0 else float('nan')

    min_score = df.groupby('genre').apply(_min_score)

    idx = opportunity_score.index
    result = pd.DataFrame({
        'genre':             idx,
        'opportunity_score': opportunity_score.values,
        'risk_score':        risk_score.reindex(idx).values,
        'best_platform':     best_platform.reindex(idx).values,
        'best_timing':       best_timing.reindex(idx).values,
        'min_score':         min_score.reindex(idx).values,
        'title_count':       title_count.reindex(idx).values,
    }).sort_values('opportunity_score', ascending=False).reset_index(drop=True)

    return result


def get_current_gen_df(df: pd.DataFrame) -> pd.DataFrame:
    current_gen = df.groupby('generation')['start_year'].median().idxmax()
    return df[df['generation'] == current_gen].copy()
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
pytest tests/test_launch_recommendation.py -v
```

Expected: `7 passed`

- [ ] **Step 5: Commit**

```bash
git add utils/launch_recommendation.py tests/test_launch_recommendation.py requirements.txt
git commit -m "feat: add compute_genre_scores and get_current_gen_df with tests"
```

---

## Task 3: Scaffold page and render KPI cards

**Files:**
- Create: `pages/7_Launch_Recommendation.py`

- [ ] **Step 1: Create the page file with config, imports, and `render_kpi_cards`**

Create `pages/7_Launch_Recommendation.py`:

```python
import streamlit as st
import plotly.graph_objects as go
from utils.data_loader import dataset_clean
from utils.sidebar import render_sidebar_rodape
from utils.launch_recommendation import compute_genre_scores, get_current_gen_df

st.set_page_config(
    page_title='Launch Recommendation',
    page_icon='🏆',
    layout='wide',
)

render_sidebar_rodape()


def render_kpi_cards(df_scores):
    best = df_scores.loc[df_scores['opportunity_score'].idxmax()]
    riskiest = df_scores.loc[df_scores['risk_score'].idxmax()]

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label='🟢 Melhor Aposta',
            value=best['genre'],
            delta=f"Oportunidade {best['opportunity_score']}/100",
        )
    with col2:
        st.metric(
            label='🔴 Maior Risco',
            value=riskiest['genre'],
            delta=f"Risco {riskiest['risk_score']}/100",
            delta_color='inverse',
        )


def render_ranking_chart(df_scores, title):
    pass  # implemented in Task 4


def render_detail_table(df_scores):
    pass  # implemented in Task 5


# ── Main layout ───────────────────────────────────────────────────────────────
st.title('🏆 Launch Recommendation')
st.markdown('Síntese executiva: score de oportunidade e risco por gênero de jogo, derivado das 6 dimensões de análise do dashboard.')

df = dataset_clean().copy()
df_hist = compute_genre_scores(df)

render_kpi_cards(df_hist)
```

- [ ] **Step 2: Run the Streamlit app locally and verify the page loads with KPI cards**

```bash
streamlit run app.py
```

Navigate to page "Launch Recommendation" in the sidebar. Expected: title + subtitle + 2 KPI metric cards (best genre and riskiest genre). No errors in terminal.

- [ ] **Step 3: Commit**

```bash
git add pages/7_Launch_Recommendation.py
git commit -m "feat: add page 7 scaffold with KPI cards"
```

---

## Task 4: Implement `render_ranking_chart`

**Files:**
- Modify: `pages/7_Launch_Recommendation.py`

- [ ] **Step 1: Replace the `render_ranking_chart` stub with full implementation**

Replace:
```python
def render_ranking_chart(df_scores, title):
    pass  # implemented in Task 4
```

With:
```python
def render_ranking_chart(df_scores, title):
    df_sorted = df_scores.sort_values('opportunity_score', ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sorted['opportunity_score'],
        y=df_sorted['genre'],
        orientation='h',
        name='Oportunidade',
        marker_color='#2ecc71',
        opacity=0.85,
    ))
    fig.add_trace(go.Scatter(
        x=df_sorted['risk_score'],
        y=df_sorted['genre'],
        mode='markers',
        name='Risco',
        marker=dict(symbol='diamond', color='#e74c3c', size=12),
    ))
    fig.update_layout(
        title=title,
        xaxis=dict(title='Score (0–100)', range=[0, 100]),
        height=420,
        template='plotly_dark',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
```

- [ ] **Step 2: Wire chart into the main layout**

Append after `render_kpi_cards(df_hist)` at the bottom of the file:

```python
st.divider()
st.subheader('📊 Benchmark Histórico — Todas as Gerações')
render_ranking_chart(df_hist, 'Ranking por Oportunidade vs Risco — Histórico Completo')
```

- [ ] **Step 3: Reload the app and verify the horizontal bar + diamond scatter chart renders**

Reload the page. Expected: green horizontal bars for all genres sorted by Oportunidade, red diamond markers at each genre's Risco score, both on a 0–100 x-axis.

- [ ] **Step 4: Commit**

```bash
git add pages/7_Launch_Recommendation.py
git commit -m "feat: add ranking chart with opportunity bars and risk scatter"
```

---

## Task 5: Implement `render_detail_table`

**Files:**
- Modify: `pages/7_Launch_Recommendation.py`

- [ ] **Step 1: Replace the `render_detail_table` stub**

Replace:
```python
def render_detail_table(df_scores):
    pass  # implemented in Task 5
```

With:
```python
def render_detail_table(df_scores):
    n = len(df_scores)
    row_colors = ['#1a1a2e' if i % 2 == 0 else '#16213e' for i in range(n)]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Gênero</b>', '<b>Oportunidade</b>', '<b>Risco</b>',
                    '<b>Melhor Plataforma</b>', '<b>Melhor Timing</b>', '<b>Nota Mínima</b>'],
            fill_color='#2c3e50',
            font=dict(color='white', size=13),
            align='left',
            height=32,
        ),
        cells=dict(
            values=[
                df_scores['genre'],
                df_scores['opportunity_score'],
                df_scores['risk_score'],
                df_scores['best_platform'].fillna('—'),
                df_scores['best_timing'].fillna('—'),
                df_scores['min_score'].fillna('—'),
            ],
            fill_color=[row_colors] * 6,
            font=dict(color='white', size=12),
            align='left',
            height=28,
        ),
    )])
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=min(60 + n * 30, 420))
    st.plotly_chart(fig, use_container_width=True)
```

- [ ] **Step 2: Wire table into the main layout**

Append after `render_ranking_chart(df_hist, ...)`:

```python
render_detail_table(df_hist)
```

- [ ] **Step 3: Reload the app and verify the table renders with alternating row colors**

Expected: table with 6 columns, alternating dark rows, `—` for any missing values.

- [ ] **Step 4: Commit**

```bash
git add pages/7_Launch_Recommendation.py
git commit -m "feat: add detail table with sub-metrics per genre"
```

---

## Task 6: Complete dual-view main layout

**Files:**
- Modify: `pages/7_Launch_Recommendation.py`

- [ ] **Step 1: Replace the entire bottom section of the file**

The current bottom of the file (after function definitions) is:

```python
# ── Main layout ───────────────────────────────────────────────────────────────
st.title('🏆 Launch Recommendation')
st.markdown('Síntese executiva: score de oportunidade e risco por gênero de jogo, derivado das 6 dimensões de análise do dashboard.')

df = dataset_clean().copy()
df_hist = compute_genre_scores(df)

render_kpi_cards(df_hist)

st.divider()
st.subheader('📊 Benchmark Histórico — Todas as Gerações')
render_ranking_chart(df_hist, 'Ranking por Oportunidade vs Risco — Histórico Completo')
render_detail_table(df_hist)
```

Replace it with:

```python
# ── Main layout ───────────────────────────────────────────────────────────────
st.title('🏆 Launch Recommendation')
st.markdown('Síntese executiva: score de oportunidade e risco por gênero de jogo, derivado das 6 dimensões de análise do dashboard.')

df = dataset_clean().copy()
df_hist = compute_genre_scores(df)

render_kpi_cards(df_hist)

st.divider()
st.subheader('📊 Benchmark Histórico — Todas as Gerações')
render_ranking_chart(df_hist, 'Ranking por Oportunidade vs Risco — Histórico Completo')
render_detail_table(df_hist)

st.divider()
st.subheader('🎯 Implicação — Geração Atual')

MIN_TITLES = 50
df_curr_raw = get_current_gen_df(df)
eligible = df_curr_raw.groupby('genre')['total_sales'].count()
df_curr_raw = df_curr_raw[df_curr_raw['genre'].isin(eligible[eligible >= MIN_TITLES].index)]

if df_curr_raw.empty:
    st.warning('Dados insuficientes para a geração atual (menos de 50 títulos por gênero). Exibindo apenas o benchmark histórico.')
else:
    df_curr = compute_genre_scores(df_curr_raw)
    render_ranking_chart(df_curr, 'Ranking por Oportunidade vs Risco — Geração Atual')
    render_detail_table(df_curr)
```

- [ ] **Step 2: Reload the app and verify full dual-view layout**

Expected:
- KPI cards at top
- "Benchmark Histórico" section: bar+scatter chart + table for all genres
- Divider
- "Implicação — Geração Atual" section: same structure filtered to latest generation, or warning if insufficient data
- No errors in terminal

- [ ] **Step 3: Commit**

```bash
git add pages/7_Launch_Recommendation.py
git commit -m "feat: complete dual-view layout — historical benchmark + current gen"
```

---

## Task 7: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add page 7 entry in the Estratégias section**

In `README.md`, after the existing entry for page 6 (`6. **Predictive Validity**` block), add:

```markdown
7. **Launch Recommendation**
- Síntese executiva que combina as 6 dimensões de análise em um score composto por gênero.
- Métricas Chave: Score de Oportunidade (0–100), Score de Risco (0–100), Melhor Plataforma por Gênero e Nota Mínima Sugerida.
- Gráficos: Ranking Horizontal de Oportunidade vs Risco (barras + marcadores) e Tabela de Sub-métricas por Gênero.
```

- [ ] **Step 2: Update the Conclusão section**

In `README.md`, find the closing sentence of the `## 👩‍💻 Conclusão` section and append:

```
 A página de síntese (Launch Recommendation) consolida todas as dimensões em um score de oportunidade e risco por gênero, permitindo decisões de lançamento baseadas em evidências históricas.
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add page 7 description to README"
```

---

## Task 8: Final smoke test

- [ ] **Step 1: Run the full test suite**

```bash
pytest tests/ -v
```

Expected: `7 passed`

- [ ] **Step 2: Run the app and navigate through all 7 pages**

```bash
streamlit run app.py
```

Navigate to each page from the sidebar. Verify no errors on any page, especially page 7 with both sections loaded.

- [ ] **Step 3: Confirm no regressions on pages 1–6**

Click through pages 1–6 and verify they still render with sidebar filters working.
