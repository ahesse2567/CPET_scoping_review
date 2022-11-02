# combining overlapping strings

# https://stackoverflow.com/questions/52528744/how-to-merge-strings-with-overlapping-characters-in-python

def overlap(s1, s2, full_text=None): # add param for minimum required overlap?
    # what is the index in string two with the max overlap in string one?
    max_forward = max(i for i in range(len(s2)+1) if s1.endswith(s2[:i]))
    max_backwards = max(i for i in range(len(s1)+1) if s2.endswith(s1[:i]))
    # using that overlap, merge the two strings together
    # there's a problem when the overlap is by exactly one character. This joins strings
    # together that should NOT go together
    # compare against full_text?
    if (max_forward >= max_backwards) & (max_forward > 0):
        out = s1[:-max_forward] + s2
    elif max_backwards > max_forward:
        out = s2[:-max_backwards] + s1
    elif s1 in s2 or s2 in s1:
        if len(s1) >= len(s2):
            return s1
        elif len(s2) > len(s1):
            return s2
    else:
        return None
    if full_text:
        if out in full_text:
            return out
        else:
            return None
    return out # in case you don't want to reference against the full text

def string_list_overlap(str_list, full_text=None):
    if not isinstance(str_list, list):
        return None
    if len(str_list) < 2: # return list if there's only one element
        return str_list
    out = []
    for i, longest_string in enumerate(str_list):
        other_strings = [x for n, x in enumerate(str_list) if n != i]
        for string in other_strings:
            temp_str = overlap(longest_string, string, full_text=full_text)
            if temp_str is not None:
                if longest_string in temp_str or temp_str in longest_string:
                    if len(temp_str) > len(longest_string):
                        longest_string = temp_str
            # if overlap(longest_string, string, full_text=full_text):
                # longest_string = overlap(longest_string, string)
        # if the longest string contains all others, be done with it
        if all([x in longest_string for x in other_strings]):
            return [longest_string]
        else:
            out.append(longest_string)
    out = list(set(out)) # remove duplicates

    any_substrings = any([o in other_o for i, o in enumerate(out) for other_o in out[:i] + out[i+1:]])

    if any_substrings and len(out) != len(str_list): # comparing string lengths prevents corner case infinite loops
        out = string_list_overlap(out, full_text=full_text)

    if full_text:
        # remove combinations of text just in case they aren't in the reference text
        out = [o for o in out if o in full_text]
    return out
