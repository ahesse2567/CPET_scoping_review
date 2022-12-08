# combining overlapping strings

# https://stackoverflow.com/questions/52528744/how-to-merge-strings-with-overlapping-characters-in-python

def overlap(s1, s2, full_text=None, min_overlap=1):
    # Find the maximum overlap in s2 with the end of s1
    max_forward = max([i for i in range(len(s2)+1) if s1.endswith(s2[:i])])

    # Find the maximum overlap in s1 with the end of s2
    max_backwards = max([i for i in range(len(s1)+1) if s2.endswith(s1[:i])])

    # Use the maximum overlap to merge the two strings together
    if any([max_forward >= max_backwards, max_forward > 0]) and max_forward >= min_overlap:
        out = s1.replace(s2[:max_forward], "") + s2
    elif max_backwards > max_forward and max_backwards >= min_overlap:
        out = s2.replace(s1[:max_backwards], "") + s1
    elif any([s1.find(s2) >= 0, s2.find(s1) >= 0]) and max(max_forward, max_backwards) >= min_overlap:
        return s1 if len(s1) >= len(s2) else s2
    else:
        return None

    # Check if the merged string is in the full text (if provided)
    if full_text is not None:
        return out if full_text.find(out) >= 0 else None

    return out

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



"""
This is the ChatGPT rewrite of string_list_overlap to make this code faster:
def string_list_overlap(str_list, full_text=None):
    if not isinstance(str_list, list):
        return None
    if len(str_list) < 2: # return list if there's only one element
        return str_list

    out = []
    for i, longest_string in enumerate(str_list):
        other_strings = []
        for n, x in enumerate(str_list):
            if n != i:
                other_strings.append(x)

        for string in other_strings:
            temp_str = overlap(longest_string, string, full_text=full_text)
            if temp_str is not None:
                if longest_string in temp_str or temp_str in longest_string:
                    if len(temp_str) > len(longest_string):
                        longest_string = temp_str

        # if the longest string contains all others, be done with it
        contains_all = True
        for x in other_strings:
            if x not in longest_string:
                contains_all = False
                break
        if contains_all:
            return [longest_string]
        else:
            out.append(longest_string)

    out = list(set(out)) # remove duplicates

    any_substrings = any([o in other_o for i, o in enumerate(out) for other_o in out[:i] + out[i+1:]])

    while any_substrings and len(out) != len(str_list): # comparing string lengths prevents corner case infinite loops
        new_out = []
        for i, longest_string in enumerate(out):
            other_strings = []
            for n, x in enumerate(out):
                if n != i:
                    other_strings.append(x)

            for string in other_strings:
                temp_str = overlap(longest_string, string, full_text=full_text)
                if temp_str is not None:
                    if longest_string in temp_str or temp_str in longest_string:
                        if len(temp_str) > len(longest_string):
                            longest_string = temp_str

            # if the longest string contains all others, be done with it
            contains_all = True
            for x in other_strings:
                if x not in longest_string:
                    contains_all = False
                    break
            if contains_all:
                new_out.append(longest_string)
            else:
                new_out.append(longest_string)
        out = new_out
        any_substrings = any([o in other_o for i, o in enumerate(out) for other_o in out[:i] + out[i+1:]])

    if full_text:
        # remove combinations of text just in case they aren't in the reference text
        out = [o for o in out if o in full_text]
    return out

"""