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
