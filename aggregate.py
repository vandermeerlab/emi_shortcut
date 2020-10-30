def combine_with_append(values_bygroup):
    bygroup = {}
    for group in values_bygroup[0]:
        bygroup[group] = []
        for value in values_bygroup:
            bygroup[group].append(value[group])
    return bygroup


def combine_with_sum(values_bygroup):
    bygroup = {}
    for group in values_bygroup[0]:
        bygroup[group] = 0
        for value in values_bygroup:
            bygroup[group] += value[group]
    return bygroup
