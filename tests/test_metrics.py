import numpy as np
import pandas as pd

from quantlab import annualized_sharpe, max_drawdown


def test_sharpe_matches_closed_form():
    r = pd.Series([0.01, -0.005, 0.02, 0.0, 0.003])
    expected = r.mean() / r.std(ddof=1) * np.sqrt(252)
    assert np.isclose(annualized_sharpe(r), expected)


def test_sharpe_is_nan_for_constant_returns():
    assert np.isnan(annualized_sharpe(pd.Series([0.01, 0.01, 0.01])))


def test_max_drawdown():
    # equity: 1.1 -> 0.88 -> 0.968; peak 1.1, trough 0.88 => -20%
    r = pd.Series([0.10, -0.20, 0.10])
    assert np.isclose(max_drawdown(r), -0.20)
