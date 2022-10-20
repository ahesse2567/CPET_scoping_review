# combining overlapping strings

# https://stackoverflow.com/questions/52528744/how-to-merge-strings-with-overlapping-characters-in-python

def overlap(s1, s2):
    # what is the index in string two with the max overlap in string one?
    max_forward = max(i for i in range(len(s2)+1) if s1.endswith(s2[:i]))
    max_backwards = max(i for i in range(len(s1)+1) if s2.endswith(s1[:i]))
    # using that overlap, merge the two strings together
    if (max_forward >= max_backwards) & (max_forward > 0):
        out = s1[:-max_forward] + s2
        return out
    elif max_backwards > max_forward:
        out = s2[:-max_backwards] + s1
        return out
    elif s1 in s2 or s2 in s1:
        if len(s1) >= len(s2):
            return s1
        elif len(s2) > len(s1):
            return s2

def string_list_overlap(str_list, full_text=None):
    if not isinstance(str_list, list):
        return None
    if len(str_list) < 2: # return list if there's only one element
        return str_list
    out = []
    for i, longest_string in enumerate(str_list):
        other_strings = [x for n, x in enumerate(str_list) if n != i]
        for string in other_strings: 
            if overlap(longest_string, string):
                longest_string = overlap(longest_string, string)
        # if the longest string contains all others, be done with it
        if all([x in longest_string for x in other_strings]):
            return [longest_string]
        else:
            out.append(longest_string)
    out = list(set(out)) # remove duplicates
    # check if any strings are substrings of any other strings. If so, enter function again
    # test = []
    # for i, o in enumerate(out):
    #     sublist = out[:i] + out[i+1:]
    #     for s in sublist:
    #         res = o in s
    #         test.append(res)
    # if any(test):
    if any([o in other_o for i, o in enumerate(out) for other_o in out[:i] + out[i+1:]]):
        out = string_list_overlap(out)

    if full_text:
        # remove combinations of text just in case they aren't in the reference text
        out = [o for o in out if o in full_text]
    return out

s1 = 'ne flowmeter was calibrated using a 3l syringe. breath-by-breath gas-exchange data were filtered for aberrant data points (data point out of the range mean ± 4sd). earlobe capillary blood samples (25 µl) were '
s2 = 'diody- namic component (0–360 seconds) with td constrained at zero in the fitting window. occasional errant breath values were deleted from the data set if they fell more than four standard deviations outsid'
s3 = 'he manufacturer’s instructions, while the k4b2 turbine flowmeter was calibrated using a 3l syringe. breath-by-breath gas-exchange data were filtered for aberrant data points (data point out of the range mean ± 4sd). earlobe capillary blood samples (25 µl) were collected and analyzed for lactate concen- tration us'
s4 = 'amic component (0–360 seconds) with td constrained at zero in the fitting window. occasional errant breath values were deleted from the data set if they fell more than four standard deviations outside the mean 30- second periods (ozyener et al. 2001). in order to in- crease the confidence of '

str_list = [s1, s2, s3, s4]

comb_lists = string_list_overlap(str_list)
comb_lists
len(comb_lists)
# s1 = '''

# Data points outside of the computed 99% prediction bands
# were deemed to be aberrant breaths (e.g., sighing, coughing)
# and were removed from the analysis. After the regression was
# recomputed, no additiona'''

# s2 = '''ints outside of the computed 99% prediction bands
# were deemed to be aberrant breaths (e.g., sighing, coughing)
# and were removed from the analysis. After the regression was
# recomputed, no additional data points'''

# s3 = '''e

#  ðt   TDpÞ=τpÞÞ:

# ð1Þ

# Data points outside of the computed 99% prediction bands
# were deemed to be aberrant breaths (e.g., sighing, coughing)
# and were removed from the analysis. After the regression was
# reco'''

# s4 = ''' were computed by taking the observed data and sub-
# tracting it from the best ﬁt regression line obtained from Eq. 1.'''

# str_list = [s1, s2, s3, s4]

# overlapping_strings = string_list_overlap(str_list)
# overlapping_strings
# len(overlapping_strings)