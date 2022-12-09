# https://stackoverflow.com/questions/52528744/how-to-merge-strings-with-overlapping-characters-in-python

# combining overlapping strings
def overlap(s1, s2, full_text=None, min_overlap=2):
    # check if s1 or s2 are a substring of the other string
    if s1 in s2:
        out = s2
        if full_text is not None:
            return out if full_text.find(out) >= 0 else None
        else:
            return out

    if s2 in s1:
        out = s1
        if full_text is not None:
            return out if full_text.find(out) >= 0 else None
        else:
            return out

    # Find the maximum overlap in s2 with the end of s1
    max_forwards = max([i for i in range(len(s2)+1) if s1.endswith(s2[:i])], default=0)

    # Find the maximum overlap in s1 with the end of s2
    max_backwards = max([i for i in range(len(s1)+1) if s2.endswith(s1[:i])], default=0)

    # Use the maximum overlap to merge the two strings together
    if any([max_forwards >= max_backwards, max_forwards > 0]) and max_forwards >= min_overlap:
        out = s1.replace(s2[:max_forwards], "") + s2
    elif max_backwards > max_forwards and max_backwards >= min_overlap:
        out = s2.replace(s1[:max_backwards], "") + s1
    elif any([s2 in s1, s1 in s2]) and max(max_forwards, max_backwards) >= min_overlap:
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
    if len(str_list) < 2:
        return str_list
    str_list = list(set(str_list)) # remove potential duplicates before starting
    out = []
    for longest_string in str_list:
        other_strings = set(str_list) - {longest_string}
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


# Test cases
"""
s1 = "Hello, my name is Anton"
s2 = "is Anton"
s3 = "I like to rollerblade"
s4 = "I hope I can finish my PhD by the spring semester."
s5 = "rollerblade. I also like to fish"
s6 = "I can"
s7 = "I like"
s8 = "to fish"
overlap(s1, s2)
overlap(s2, s1)

full_text = "Hello, my name is Anton, and I like to rollerblade. I also like to fish. I hope I can finish my PhD by the spring semester."
string_list = [s1, s2, s3, s4, s5, s6, s7, s8]

string_list_overlap(str_list=string_list, full_text=full_text)
list3 = [
    'Hello, my name is Anton',
    'I can',
    'I hope I can finish my PhD by the spring semester.']

string_list_overlap(list3)

string_list_overlap(['I can', 'I hope I can finish my PhD by the spring semester.'], full_text=full_text)
"""