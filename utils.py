import numpy as np
from scipy import stats

import meta


def map_range(value, from_min, from_max, to_min, to_max):
    # Figure out how 'wide' each range is
    from_range = from_max - from_min
    to_range = to_max - to_min

    # Convert the left range into a 0-1 range (float)
    value_scaled = (value - from_min) / from_range

    # Convert the 0-1 range into a value in the right range.
    return to_min + (value_scaled * to_range)


def save_lmer_model(model, savepath):
    with open(savepath, "w") as fp:
        print(f"Formula: {model.formula}\n", file=fp)
        print(f"Family: {model.family}\t Inference: {model.sig_type}", file=fp)
        print(
            f"Number of observations: {model.data.shape[0]}\t Groups: {model.grps}",
            file=fp,
        )
        print(f"Log-likelihood: {model.logLike} \t AIC: {model.logLike}", file=fp)
        print(f"Random effects: {model.ranef_var}", file=fp)
        if model.ranef_corr is not None:
            print(f"{model.ranef_corr}", file=fp)
        else:
            print("No random effect correlations specified", file=fp)
        if model.coefs is not None:
            print("Fixed effects:", file=fp)
            print(f"{model.coefs}", file=fp)
        else:
            print("No fixed effects estimated", file=fp)


def save_ttest_results(df, variable, savepath):
    output = {
        trajectory: df[df["trajectory"] == trajectory][variable]
        for trajectory in meta.behavioral_trajectories
    }

    with open(savepath, "w") as fp:
        print(f"% Trial {variable} ttest results\n", file=fp)
        for trajectory in meta.behavioral_trajectories:
            print(f"% {trajectory}:", file=fp)
            # print(f"% {output[trajectory].describe()}\n", file=fp)
            print(f"% count: {output[trajectory].count()}", file=fp)
            print(f"% mean: {output[trajectory].mean():.3f}", file=fp)
            print(f"% std: {output[trajectory].std():.3f}", file=fp)
            print(f"% min: {output[trajectory].min():.3f}", file=fp)
            print(f"% max: {output[trajectory].max():.3f}\n", file=fp)

        for grouping in meta.stats_trajectory_groupings:
            t_check = stats.ttest_ind(
                output[grouping[0]].values.tolist(),
                output[grouping[1]].values.tolist(),
            )
            print(f"% {grouping[0]} & {grouping[1]}: \n% {t_check}", file=fp)
            if t_check[1] < meta.alpha:
                print(
                    f"% {grouping[0]} different from {grouping[1]} with "
                    f"alpha = {meta.alpha}",
                    file=fp,
                )
            print("% ---------\n", file=fp)


def ranksum_test(xn, xtotal, yn, ytotal):
    if xn == 0 and yn == 0:
        return 1.0
    x = np.zeros(xtotal)
    x[:xn] = 1
    y = np.zeros(ytotal)
    y[:yn] = 1
    statistic, pval = stats.mannwhitneyu(x, y)
    return pval
