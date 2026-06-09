import pandas as pd
import numpy as np

SCORE_THRESHOLD = 8.0


def compute_genre_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula os scores compostos de oportunidade e risco por gênero de jogo,
    derivados das seis dimensões de análise do dashboard BrasCo.

    Scores compostos
    ----------------
    - opportunity_score : 0.40 × sales_score + 0.30 × reach_score + 0.30 × score_multiplier
    - risk_score        : 0.40 × regional_concentration + 0.30 × score_sensitivity + 0.30 × market_saturation

    Sub-scores de oportunidade
    --------------------------
    - sales_score             : média de total_sales do gênero normalizada 0–100 em relação ao gênero de maior venda
    - reach_score             : 100 − concentração regional máxima (quanto menor a dependência de uma única região, maior o score)
    - score_multiplier        : razão entre a média de vendas de títulos acima vs abaixo do threshold de critic_score (8.0),
                                normalizada 0–100 com clip em 5×

    Sub-scores de risco
    -------------------
    - regional_concentration  : participação máxima de uma única região nas vendas totais do gênero × 100
    - score_sensitivity       : coeficiente de variação (std/mean) das vendas do gênero, clipado em 2.0 e
                                normalizado 0–100 entre gêneros (alta variância = alto risco)
    - market_saturation       : razão entre contagem de títulos e média de vendas, normalizada 0–100
                                (muitos títulos com poucas vendas = mercado saturado)

    Sub-métricas de detalhe (não entram nos scores)
    ------------------------------------------------
    - best_platform           : console com maior média de total_sales para o gênero
    - min_score               : 70º percentil do critic_score entre títulos acima da mediana de vendas do gênero
    - title_count             : número de títulos do gênero no DataFrame de entrada

    Parâmetros
    ----------
    df : pd.DataFrame
        Dataset limpo (saída de dataset_clean()). Deve conter 'genre', 'total_sales',
        'na_sales', 'jp_sales', 'pal_sales', 'other_sales', 'critic_score' e 'console'.

    Retorna
    -------
    result : pd.DataFrame
        Uma linha por gênero, ordenada por opportunity_score decrescente.
        Colunas: genre, opportunity_score, risk_score, best_platform, min_score, title_count.
        Ambos os scores são inteiros no intervalo 0–100.
    """
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
        0.40 * sales_score.fillna(0) +
        0.30 * reach_score.fillna(0) +
        0.30 * score_multiplier.fillna(0)
    ).round(0).clip(0, 100).astype(int)

    risk_score = (
        0.40 * regional_concentration.fillna(0) +
        0.30 * score_sensitivity.fillna(0) +
        0.30 * market_saturation.fillna(0)
    ).round(0).clip(0, 100).astype(int)

    # --- Detail sub-metrics ---
    best_platform = (
        df.groupby(['genre', 'console'])['total_sales'].mean()
        .reset_index()
        .sort_values('total_sales', ascending=False)
        .groupby('genre')['console'].first()
    )


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
        'min_score':         min_score.reindex(idx).values,
        'title_count':       title_count.reindex(idx).values,
    }).sort_values('opportunity_score', ascending=False).reset_index(drop=True)

    return result


def get_current_gen_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra o DataFrame para a geração de consoles mais recente.

    A geração atual é identificada como aquela com a maior mediana de start_year
    entre seus consoles, tornando o critério robusto a labels textuais como
    "1st Gen", "10th Gen" (que não ordenam corretamente como strings).

    Parâmetros
    ----------
    df : pd.DataFrame
        Dataset limpo (saída de dataset_clean()). Deve conter 'generation' e 'start_year'.

    Retorna
    -------
    pd.DataFrame
        Subconjunto do DataFrame original contendo apenas as linhas da geração mais recente.
    """
    current_gen = df.groupby('generation')['start_year'].median().idxmax()
    return df[df['generation'] == current_gen].copy()
