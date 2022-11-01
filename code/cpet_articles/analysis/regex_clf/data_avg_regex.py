from pathlib import Path
import pandas as pd
import re
from tqdm import tqdm
tqdm.pandas()
from code.cpet_articles.analysis.helper_funcs.text_analysis import read_raw_text, get_surrounding_text
# from code.cpet_articles.utils.article_names import get_doi_suffix
from code.cpet_articles.analysis.helper_funcs.comb_overlapping_str import *

def reorder_columns(dataframe, col_name, position):
    temp_col = dataframe[col_name] # store col to move
    dataframe = dataframe.drop(columns=[col_name]) # drop old position
    dataframe.insert(loc=position, column=col_name, value=temp_col) # insert at new position
    print(dataframe.columns)
    return dataframe

txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').rglob('*.txt'))

bbb_df_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/bbb_articles.csv')
bbb_df = pd.read_csv(bbb_df_path, dtype='str')
# bbb_df['doi_suffix'] = bbb_df['doi'].apply(lambda x: get_doi_suffix(x))

bbb_article_paths = [path for path in txt_file_paths if path.stem in bbb_df['doi_suffix'].to_list()]

raw_text = []
for path in tqdm(bbb_article_paths):
    try:
        rt = read_raw_text(path)
        raw_text.append(rt)
    except FileNotFoundError as e:
        print(e)

txt_files = [path.stem for path in bbb_article_paths]
text_df = pd.DataFrame({
    'doi_suffix': txt_files,
    'path': bbb_article_paths,
    'text': raw_text})

# [str(path) for path in txt_file_paths if path.stem == 'mss.0000000000001353'][0]

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

def find_avg_text(text):
    # time-bin average with NUMBERS
    time_bin_avg_sec_re = re.compile(r'''(
    # avg keywords
    (?:(?:(?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|during|highest|frequency|record)+.{0,5})+
    # numbers and seconds
    [\s\(\)]\d{1,2}[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)[\(\)\s.,;?-])
    # numbers and seconds, if they come first
    |(?:[\s\(\)]\d{1,2}[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)[\(\)\s.,;?-]
    # averaging keywords. There doesn't seem to be as many keywords that come after the numbers
    .{0,5}(?:(?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last)+)+)
    )''', re.DOTALL | re.VERBOSE)

    time_bin_avg_min_re = re.compile(r'''(
        # order is avg-time
        (?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|during|highest|frequency|record|per)+
        .{0,10}
        (?:\d{0,1}|one)(?:[\W\s]){0,2}
        min(?:ute|utes)?
        | # order is time_avg
        (?:\d{0,1}|one)(?:[\W\s]){0,2}
        min(?:ute|utes)?
        .{0,10}
        (?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|during|highest|frequency|record|per)+
        )''', re.DOTALL | re.VERBOSE)

    time_bin_avg_words_re = re.compile(r'''(
        (?:
        (?:(?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|during|highest|frequency|record)+.{0,5})+
        (?:one|two|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|fifteen|twenty|thirty|sixty)
        (?:(?:[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)[\(\)\s.,;?-])|(?:[\s-]{0,2}min(?:ute)?s?))
        )
        |
        (?:
        (?:one|two|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|fifteen|twenty|thirty|sixty)
        (?:(?:[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)[\(\)\s.,;?-])|(?:[\s-]{0,2}min(?:ute)?s?))
        (?:(?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|during|highest|frequency|record)+.{0,5})+
        )
        )''', re.DOTALL | re.VERBOSE)
    
    # time rolling will be split into the order in which the phrasing can appear. That is roll-time-avg, time-roll-avg, etc.
    roll_time_avg_re = re.compile(r'''(
        (?:roll(?:ing)?|smooth(?:ed|ing)|running|moving|sliding|roll(?:ing|ed))
        .{0,15}
        (?:(?:[\s\(\)]\d{1,2}[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)\b)|(?:one|two|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|fifteen|twenty|thirty|sixty))+
        .{0,15}
        (?:(?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|points?)+)+
        )''', re.DOTALL | re.VERBOSE)

    time_roll_avg_re = re.compile(r'''(
        (?:(?:[\s\(\)]\d{1,2}[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)\b)|(?:one|two|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|fifteen|twenty|thirty|sixty))+
        .{0,15}
        (?:roll(?:ing)?|smooth(?:ed|ing)|running|moving|sliding|roll(?:ing|ed))+
        .{0,15}(?:(?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|points?)+)+
        )''', re.DOTALL | re.VERBOSE)

    roll_avg_time_re = re.compile(r'''(
        (?:roll(?:ing)?|smooth(?:ed|ing)|running|moving|sliding|roll(?:ing|ed))+
        .{0,15}
        (?:(?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|points?)+)+
        .{0,15}
        (?:(?:[\s\(\)]\d{1,2}[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)\b)|(?:one|two|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|fifteen|twenty|thirty|sixty))+
        )''')

    # rolling breath average
    # if breath number appears BEFORE "smoothing, rolling, etc."
    # (?:(?:\d{1,2}|three|four|[(?:fi)|ﬁ]ve|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}?:breath[es]?|points{0,1})[\s-]{0,2}(?:smooth(?:ing)?(?:ed)?|roll(?:ing)?|sliding|running|moving)+)+|(?:(?:smooth(?:ing)?(?:ed)?|roll(?:ing)?|sliding|running|moving|filter(?:ed)?)+\s{0,2}(?:each)?\s{0,2}(?:\d{1,2}|three|four|[(?:fi)|ﬁ]ve|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}(?:breath[es]?|points?))+
    breath_roll_re = re.compile(r'''( # TODO make these noncapturing groups for speed
        (?:(?:\d{1,2}|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}(?:breath[es]?|points{0,1})[\s-]{0,2}(?:smooth(?:ing)?(?:ed)?|roll(?:ing)?|sliding|running|moving)+)+
        |(?:(?:smooth(?:ing)?(?:ed)?|roll(?:ing)?|sliding|running|moving|filter(?:ed)?)+\s{0,2}(?:each)?\s{0,2}(?:\d{1,2}|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}(?:breath[es]?|points?))+
        )''', re.IGNORECASE | re.VERBOSE)

    digital_filter_re = re.compile(r'''(
        butterworth|savitzky[\s\W]{0,2}golay|(?:fast\W{0,2}fourier\W{0,2}transform|fft)
        )''', re.DOTALL | re.VERBOSE)

    re_list = [
        time_bin_avg_sec_re,
        time_bin_avg_min_re,
        time_bin_avg_words_re,
        roll_time_avg_re,
        time_roll_avg_re,
        roll_avg_time_re,
        breath_roll_re,
        digital_filter_re
    ]

    out = [rl.findall(text) for rl in re_list if rl.search(text)]
    out = flatten_list(out)

    if out:
        return out
    else:
        return False

find_avg_text('The breath-by-breathV̇ O2 data collected by the gas analysis system was averaged per minute for further analysis')


    


# full regex below for easy copy and paste
# (((average[ds]?|mean|interval|periods?|sample[ds]?|every|over|into|each|last|during|highest|frequency|record)+.{0,5})+[\s\(\)]\d{1,2}[\s-]{0,2}((s(ec)?(econd)?(econds)?)+)[\(\)\s.,;?-])|([\s\(\)]\d{1,2}[\s-]{0,2}((s(ec)?(econd)?(econds)?)+)[\(\)\s.,;?-].{0,5}((average[ds]?|mean|interval|periods?|sample[ds]?|every|over|into|each|last)+)+)

time_bin_avg_sec_re = re.compile(r'''(
    # avg keywords
    (?:(?:(?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|during|highest|frequency|record)+.{0,5})+
    # numbers and seconds.
    [\s\(\)]\d{1,2}[\s-]{0,2}((?:s(?:ec)?(?:econd)?(?:econds)?)+)[\(\)\s.,;?-])
    # numbers and seconds, if they come first
    |(?:[\s\(\)]\d{1,2}[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)[\(\)\s.,;?-]
    # averaging keywords. There doesn't seem to be as many keywords that come after the numbers
    .{0,5}(?:(?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last)+)+)
    )''', re.DOTALL | re.VERBOSE)



# I think I might first search by units in seconds, and later in units that include minutes
# text = text_df.loc[text_df['doi_suffix'] == 'mss.mss.0000000000001353']
# text = text.lower()
# time_bin_avg_sec_re.findall(text)

text_df['time_bin_avg_sec'] = text_df['text'].progress_apply(lambda x: time_bin_avg_sec_re.findall(x) if time_bin_avg_sec_re.search(x) else False)
text_df[text_df['time_bin_avg_sec'] != False]
# text_df['time_bin_avg_sec'][0:10]
text_df.loc[text_df['doi_suffix'] == 'mss.0000000000001353']['time_bin_avg_sec']
n = 102
time_bin_avg_phrase = text_df.loc[n,'time_bin_avg_sec']
time_bin_avg_phrase
len(time_bin_avg_phrase)

doi_suffix = text_df.loc[n,'doi_suffix']
doi_suffix

text_list = time_bin_avg_phrase
def extract_avgs(text_list):
    # function returns matches from averaging method regex that contains numbers
    if not isinstance(text_list, list):
        return False
    # this needs updating to capture values like "five", not just numbers
    num_phrase_re = re.compile(r'(?:\d+.?[a-zA-Z]+)|(?:[a-zA-Z]+.?\d+)', re.DOTALL)
    phrases_with_nums = []
    for l in text_list:
        for t in l:
            if num_phrase_re.search(t):
                phrases_with_nums.append(t)
                
    unique_phrases = list(set(phrases_with_nums))
    # find exactly what numbers there are
    just_nums_re = re.compile(r'\d+')
    nums = []
    for phrase in unique_phrases:
        num = just_nums_re.search(phrase).group()
        nums.append(num)
    res = list(zip(unique_phrases, nums))
    return res

extract_avgs(text_list)

# do we need to get the text near the averaging phrase so we can tellif it's about
# gas exchange or not?

text_df['time_bin_avg_nums'] = text_df['time_bin_avg_sec'].apply(lambda x: extract_avgs(x))
text_df['time_bin_avg_nums'][0]


    # # reference to gas exchange before avg phrase
    # (v.{0,2}o2|respirat|gas|air|ventilat|pulmonary|(oxygen|o2).{0,2}(consumption|uptake)|metabolic.{0,2}cart)
    # .{{0,{chars}}}{phrase}
    # | # also check in case the gas exchange words came after the avg phrase
    # {phrase}.{{0,{chars}}}
    # (v.{0,2}o2|respirat|gas|air|ventilat|pulmonary|(oxygen|o2).{0,2}(consumption|uptake)|metabolic.{0,2}cart)
    # )
    # example regex to find if avg phrases are actually referring to VO2
    # this does not have as many {} as the f string would
    # (v.{0,2}o2|respirat|gas|air|ventilat|pulmonary|(oxygen|o2).{0,2}(consumption|uptake)|metabolic.{0,2}cart).{0,100} 30 seconds into| 30 seconds into.{0,100}(v.{0,2}o2|respirat|gas|air|ventilat|pulmonary|(oxygen|o2).{0,2}(consumption|uptake)|metabolic.{0,2}cart)


import random
n = random.randint(0, text_df.shape[0])
row = text_df.loc[0,:]
row

surrounding_text = []
for idx, row in tqdm(text_df.iterrows(), total=text_df.shape[0]):
    temp_list = []
    if isinstance(row['time_bin_avg_nums'], list):
        for ph, num in row['time_bin_avg_nums']:
            temp = get_surrounding_text(phrase=ph, text=row['text'], chars=200)
            temp_list.append(temp)
        temp_list = [item for item in temp_list if item is not None]
        temp_list = [item for sublist in temp_list for item in sublist]
        comb_text_list = string_list_overlap(temp_list, row['text']) # combine text together to eliminate some later reading
        if comb_text_list:
            surrounding_text.append(comb_text_list)
        else:
            surrounding_text.append(False)
    else:
        surrounding_text.append(False)



for i in range(20):
    print(surrounding_text[i])

text_df['time_bin_surrounding_text'] = surrounding_text

manual_text_analysis_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - Data.csv')
manual_text_analysis_df = pd.read_csv(manual_text_analysis_path, dtype='str')

# copy this into the Google Sheet
merge_df = pd.merge(
    manual_text_analysis_df.drop(['time_bin_avg_nums', 'time_bin_surrounding_text'], axis=1),\
    text_df[['doi_suffix', 'time_bin_avg_nums', 'time_bin_surrounding_text']],\
    how='outer', on='doi_suffix').drop_duplicates(subset='doi_suffix')
merge_df['doi_suffix'] = merge_df['doi_suffix'].astype('str')
merge_df = reorder_columns(merge_df, 'time_bin_avg_nums', position=10)
merge_df = reorder_columns(merge_df, 'time_bin_surrounding_text', position=11)
# merge_df.to_clipboard(index=False)

merge_df[['time_bin_avg_nums','time_bin_surrounding_text']].to_clipboard(index=False)
merge_df.columns

avg_df = merge_df[['doi_suffix', 'time_bin_avg_nums', 'time_bin_surrounding_text', 'Avg type', 'Avg subtype', 'Avg amount',
       'Avg MOS', 'Avg mean type', 'avg_details']]

import pyperclip
pyperclip.copy(text_df.loc[text_df['doi_suffix'] == 's00421-005-1350-3',:].reset_index().loc[0,'text'])

text_df['breath_roll_avg'] = text_df['text'].progress_apply(lambda x: breath_roll_re.findall(x) if len(breath_roll_re.findall(x)) > 0 else False)
text_df['breath_roll_avg']
text_df['breath_roll_avg_nums'] = text_df['breath_roll_avg'].apply(lambda x: extract_avgs(x))
text_df['breath_roll_avg_nums']
text_df[text_df['breath_roll_avg_nums'] != False]
# how do we deal with a MOS as a median?

# digital filters will be tough because they almost ALWAYS refer to EMG data



