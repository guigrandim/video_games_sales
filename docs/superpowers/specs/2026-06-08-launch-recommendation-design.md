# Design: Page 7 — Launch Recommendation

**Date:** 2026-06-08  
**Author:** Guilherme Grandim  
**Status:** Approved

---

## Overview

A synthesis page that ranks video game genres by a composite Opportunity Score and Risk Score, derived from the analytical dimensions built across pages 1–6. Serves as the executive conclusion of the BrasCo dashboard — one screen that answers "where should we launch next, and what are the risks?"

No user inputs. The page computes and displays results automatically on load.

---

## Architecture

### Data Source

Calls `dataset_clean()` directly (no `render_sidebar()`). Uses `render_sidebar_rodape()` in the sidebar for visual consistency with other pages.

The computation runs twice:
1. **Historical benchmark** — full dataset, all generations
2. **Current generation** — filtered to the generation whose consoles have the highest median `start_year`. Computed as: `df.groupby('generation')['start_year'].median().idxmax()`. This is robust to string sorting of generation labels ("1st Gen", "10th Gen", etc.).

### File

`pages/7_Launch_Recommendation.py`

### Functions

| Function | Purpose |
|---|---|
| `compute_genre_scores(df)` | Returns a DataFrame with one row per genre and all score columns |
| `render_kpi_cards(df_scores)` | Renders the two highlight KPI cards at the top |
| `render_ranking_chart(df_scores, title)` | Renders the horizontal bar + scatter Plotly figure |
| `render_detail_table(df_scores)` | Renders the Plotly Table with sub-metric columns |

---

## Score Formula

### Sub-metrics (computed per genre from the input df)

| Sub-metric | Derivation | Range |
|---|---|---|
| `sales_score` | Mean total_sales per genre, normalized 0–100 vs max genre | 0–100 |
| `reach_score` | 100 minus regional concentration index: `max(na%, jp%, pal%, other%) × 100` | 0–100 |
| `score_multiplier` | Ratio of mean sales above vs below critic_score threshold (8.0), normalized 0–100 | 0–100 |
| `regional_concentration` | `max(na%, jp%, pal%, other%) × 100` (high = risky) | 0–100 |
| `score_sensitivity` | Coefficient of variation (std/mean) of total_sales within genre, clipped at 2.0 then min-max normalized across genres to 0–100 (high variance = risky) | 0–100 |
| `market_saturation` | Title count per unit of total_sales, normalized 0–100 (high count/low sales = saturated) | 0–100 |

### Composite Scores

```
opportunity_score = 0.40 × sales_score
                  + 0.30 × reach_score
                  + 0.30 × score_multiplier

risk_score        = 0.40 × regional_concentration
                  + 0.30 × score_sensitivity
                  + 0.30 × market_saturation
```

Both scores are rounded to integers. Genres with fewer than 50 titles in the filtered dataset are excluded from the current-generation view (insufficient data).

### Detail Sub-metrics (displayed in table, not used in score)

| Column | Derivation |
|---|---|
| `best_platform` | Console with highest mean total_sales for that genre |
| `best_timing` | Offset year within the console generation cycle (computed as `release_year − console start_year`) with the highest mean total_sales for that genre. Displayed as "Ano N do ciclo". |
| `min_score` | 70th percentile of critic_score among titles above the genre's median total_sales |

---

## Page Layout

```
page_config: title="Launch Recommendation", icon="🏆", layout="wide"

[Page title + subtitle]

[KPI row: 2 columns]
  Left:  Melhor Aposta — genre with highest opportunity_score (green)
  Right: Maior Risco   — genre with highest risk_score (red)

──────────────────────────────────────────
## Benchmark Histórico — Todas as Gerações
[render_ranking_chart(df_hist, "Benchmark Histórico")]
[render_detail_table(df_hist)]

──────────────────────────────────────────
## Implicação — Geração Atual
[render_ranking_chart(df_curr, "Geração Atual")]
[render_detail_table(df_curr)]
```

---

## Plotly Chart Spec

**Figure:** single `go.Figure` with two traces on shared axes

- `go.Bar`: horizontal, x = opportunity_score, y = genre (sorted descending), color `#2ecc71`, opacity 0.85, name "Oportunidade"
- `go.Scatter`: x = risk_score, y = genre (same order), mode = "markers", marker symbol `diamond`, color `#e74c3c`, size 12, name "Risco"

Both traces share the same x-axis (0–100). Layout: `barmode='overlay'`, `xaxis_title="Score (0–100)"`, `height=420`, `template="plotly_dark"` (consistent with other pages).

**Table:** `go.Table` with columns: Gênero, Oportunidade, Risco, Melhor Plataforma, Melhor Timing, Nota Mínima. Header color `#2c3e50`, alternating row colors `#1a1a2e` / `#16213e`.

---

## Constraints

- Genres with `<50` titles excluded from current-gen view
- critic_score threshold fixed at `8.0` (consistent with Page 6 finding)
- `@st.cache_data` on `dataset_clean()` (inherited from data_loader)
- No sidebar filters — page is intentionally read-only/conclusive
- Page must load without errors when no generation filter returns data (fallback: show historical view only with a warning)
