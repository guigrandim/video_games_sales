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

    raw_mult = df.groupby('genre').apply(_score_multiplier, include_groups=False)
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

    min_score = df.groupby('genre').apply(_min_score, include_groups=False)

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
