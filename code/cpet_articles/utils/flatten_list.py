# turn a list of lists into one list without any sublists
# e.g. [[item1, item2], [item3]] becomes [item1, item2, item3]
def flatten_list(lst):
    out = []
    for l in lst:
        if isinstance(l, list):
            for item in l:
                out.append(item)
        else:
            out.append(l)
    if any([isinstance(o, list) for o in out]):
        out = flatten_list(out)
    return out