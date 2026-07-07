"""Package init runs before any submodule import, which is why the numpy
compat guard for pandas-ta-classic lives here rather than in indicators.py:
Python guarantees this executes first, so the ordering doesn't depend on
import order elsewhere in the app.

pandas-ta-classic declares numpy>=2.0 natively and, as of 0.6.52, does not
reference the removed `numpy.NaN` alias in its core indicator modules — this
guard is defensive insurance (a no-op on a clean install), not a known-needed
fix, since only a subset of its indicator modules were inspected.
"""

import numpy as np

if not hasattr(np, "NaN"):
    np.NaN = np.nan  # type: ignore[attr-defined]
