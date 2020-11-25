import numpy as np
import scipy.stats


def map_range(value, from_min, from_max, to_min, to_max):
    # Figure out how 'wide' each range is
    from_range = from_max - from_min
    to_range = to_max - to_min

    # Convert the left range into a 0-1 range (float)
    value_scaled = (value - from_min) / from_range

    # Convert the 0-1 range into a value in the right range.
    return to_min + (value_scaled * to_range)


def ranksum_test(xn, xtotal, yn, ytotal):
    if xn == 0 and yn == 0:
        return 1.0
    x = np.zeros(xtotal)
    x[:xn] = 1
    y = np.zeros(ytotal)
    y[:yn] = 1
    statistic, pval = scipy.stats.mannwhitneyu(x, y)
    return pval


def mannwhitneyu(x, y):
    try:
        _, pval = scipy.stats.mannwhitneyu(x, y)
    except ValueError:
        pval = 1.0
    return pval


def latex_float(f):
    float_str = f"{f:2e}"
    if "e" in float_str:
        base, exponent = float_str.split("e")
        return fr"{float(base):.1f} \times 10^{{{int(exponent)}}}"
    else:
        return float_str
