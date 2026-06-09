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
    required = {'genre', 'opportunity_score', 'risk_score', 'best_platform', 'best_timing', 'min_score', 'title_count'}
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
