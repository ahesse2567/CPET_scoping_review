# combining overlapping strings

# https://stackoverflow.com/questions/52528744/how-to-merge-strings-with-overlapping-characters-in-python

# combining overlapping strings
def overlap(s1, s2, full_text=None, min_overlap=2):
    # Find the maximum overlap in s2 with the end of s1
    max_forward = max([i for i in range(len(s2)+1) if s1.endswith(s2[:i])], default=0)

    # Find the maximum overlap in s1 with the end of s2
    max_backwards = max([i for i in range(len(s1)+1) if s2.endswith(s1[:i])], default=0)

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

# My original implementation of string_list_overlap
def string_list_overlap(str_list, full_text=None):
    if not isinstance(str_list, list):
        return None

    str_list = list(set(str_list))
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

# s1 = "Hello, my name is Anton"
# s2 = "is Anton"
# s3 = "I like to rollerblade"
# s4 = "I hope I can finish my PhD by the spring semester."
# s5 = "rollerblade. I also like to fish"
# s6 = "I can"
# s7 = "I like"
# s8 = "to fish"
# overlap(s1, s2)
# overlap(s2, s1)

# full_text = "Hello, my name is Anton, and I like to rollerblade. I also like to fish. I hope I can finish my PhD by the spring semester."
# string_list = [s1, s2, s3, s4, s5, s6, s7, s8]

# string_list_overlap(str_list=string_list, full_text=full_text)

"""
Some suggestions from CHATgpt

def string_list_overlap(str_list, full_text=None):
    # Check if the input is a valid list of strings
    if not isinstance(str_list, list):
        return None

    # Create an empty list to store the overlapping strings
    out = []

    # Create a dictionary to store the strings in the list
    # This is used to avoid adding duplicate strings to the list
    str_dict = {}
    for s in str_list:
        str_dict[s] = True

    # Iterate over the strings in the list
    for i, longest_string in enumerate(str_list):
        # Create a list of strings to compare with the current string
        other_strings = [x for n, x in enumerate(str_list) if n != i]

        # Iterate over the other strings in the list
        for string in other_strings:
            # Find the maximum overlap in s2 with the end of s1
            max_forward = max([j for j in range(len(s2)+1) if s1.endswith(s2[:j])], default=0)

            # Find the maximum overlap in s1 with the end of s2
            max_backwards = max([j for j in range(len(s1)+1) if s2.endswith(s1[:j])], default=0)

            # Use the maximum overlap to merge the two strings together
            if any([max_forward >= max_backwards, max_forward > 0]) and max_forward >= min_overlap:
                temp_str = s1[:len(s1) - max_forward] + s2
            elif max_backwards > max_forward and max_backwards >= min_overlap:
                temp_str = s2[:len(s2) - max_backwards] + s1
            elif any([s1.find(s2) >= 0, s2.find(s1) >= 0]) and max(max_forward, max_backwards) >= min_overlap:
                temp_str = s1 if len(s1) >= len(s2) else s2
            else:
                temp_str = None

            # If the merged string is not None and it is not a duplicate,
            # add it to the list of overlapping strings
            if temp_str is not None and temp_str not in str_dict:
                str_dict[temp_str] = True
                out.append(temp_str)

    # Check if the full_text parameter is provided
    if full_text is not None:
        # If the full_text parameter is provided,
        # remove any strings that are not in the full text
        out = [o for o in out if o in full_text]

    return out

"""