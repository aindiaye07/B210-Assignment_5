"""
Utilities for analyzing tip amounts.

Provides a function `compare_avg_tip_by_smoker` which computes average tip
for smoker and non-smoker groups and optionally runs a Welch t-test if
scipy is installed.

The function accepts either a pandas DataFrame with columns 'tip' and
'smoker' (values like 'Yes'/'No' or True/False), or an iterable of
dict-like records with the same keys.

Example usage is available in the `__main__` guard.
"""

from typing import Iterable, Dict, Tuple, Optional
import statistics

try:
    import pandas as pd  # type: ignore
except Exception:
    pd = None  # type: ignore


def _to_bool_smoker(val) -> Optional[bool]:
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    if s in ("yes", "y", "true", "t", "1"):
        return True
    if s in ("no", "n", "false", "f", "0"):
        return False
    return None


def compare_avg_tip_by_smoker(records: Iterable[Dict], do_ttest: bool = False) -> Dict:
    """Compare average tip amount between smokers and non-smokers.

    Args:
        records: An iterable of records. Each record must have a 'tip'
            key (numeric) and a 'smoker' key (bool-like or 'Yes'/'No').
        do_ttest: If True and scipy is available, perform Welch's t-test
            between the two groups and include p-value in the result.

    Returns:
        A dictionary with keys: 'n_smoker', 'n_non_smoker', 'avg_tip_smoker',
        'avg_tip_non_smoker', 'difference' (smoker - non-smoker), and
        optionally 'ttest_pvalue'.
    """

    tips_smoker = []
    tips_non = []

    # If a pandas DataFrame is passed, handle it directly for convenience
    if pd is not None and isinstance(records, pd.DataFrame):
        df = records
        if 'tip' not in df.columns or 'smoker' not in df.columns:
            raise ValueError("DataFrame must contain 'tip' and 'smoker' columns")
        for _, row in df[['tip', 'smoker']].iterrows():
            s = _to_bool_smoker(row['smoker'])
            try:
                tip = float(row['tip'])
            except Exception:
                continue
            if s is True:
                tips_smoker.append(tip)
            elif s is False:
                tips_non.append(tip)
        # proceed to summary
    else:
        for rec in records:
            if not isinstance(rec, dict) and not hasattr(rec, '__getitem__'):
                # try to convert to dict-like using vars()
                try:
                    rec = dict(rec)
                except Exception:
                    continue
            smoker_val = None
            try:
                smoker_val = rec.get('smoker', rec.get('Smoker'))
            except Exception:
                # fallback for mappings that raise
                try:
                    smoker_val = rec['smoker']
                except Exception:
                    smoker_val = None

            s = _to_bool_smoker(smoker_val)
            try:
                tip = float(rec.get('tip', rec.get('Tip')))
            except Exception:
                continue
            if s is True:
                tips_smoker.append(tip)
            elif s is False:
                tips_non.append(tip)

    def safe_mean(lst):
        return statistics.mean(lst) if lst else None

    avg_smoker = safe_mean(tips_smoker)
    avg_non = safe_mean(tips_non)
    result = {
        'n_smoker': len(tips_smoker),
        'n_non_smoker': len(tips_non),
        'avg_tip_smoker': avg_smoker,
        'avg_tip_non_smoker': avg_non,
        'difference': (avg_smoker - avg_non) if (avg_smoker is not None and avg_non is not None) else None,
    }

    if do_ttest:
        try:
            from scipy import stats  # type: ignore
            if tips_smoker and tips_non:
                tstat, pval = stats.ttest_ind(tips_smoker, tips_non, equal_var=False, nan_policy='omit')
                result['ttest_pvalue'] = float(pval)
            else:
                result['ttest_pvalue'] = None
        except Exception:
            # scipy not available or other error; omit p-value
            result['ttest_pvalue'] = None

    return result


if __name__ == '__main__':
    # Minimal example dataset
    sample = [
        {'tip': 3.0, 'smoker': 'No'},
        {'tip': 5.0, 'smoker': 'Yes'},
        {'tip': 2.5, 'smoker': 'No'},
        {'tip': 4.0, 'smoker': 'Yes'},
        {'tip': 3.5, 'smoker': 'No'},
    ]

    out = compare_avg_tip_by_smoker(sample, do_ttest=False)
    print('Summary:')
    for k, v in out.items():
        print(f"{k}: {v}")
