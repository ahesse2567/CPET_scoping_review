from pathlib import Path
import pandas as pd
import re
from tqdm import tqdm
tqdm.pandas()
from code.cpet_articles.analysis.helper_funcs.text_analysis import read_raw_text, get_surrounding_text
# from code.cpet_articles.utils.article_names import get_doi_suffix
from code.cpet_articles.analysis.helper_funcs.comb_overlapping_str import *
from code.cpet_articles.analysis.helper_funcs.reorder_columns import reorder_columns

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

def find_avg_terms(text):
    # time-bin average with NUMBERS
    time_bin_avg_sec_re = re.compile(r'''(
    # avg keywords
    (?:(?:(?:average[ds]?|mean|intervals?|value|segment|periods?|sample[ds]?|every|over|into|each|last|during|highest|frequency|record)+.{0,5})+
    # numbers and seconds
    [\s\(\)]\d{1,2}[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)[\(\)\s.,;?-])
    # numbers and seconds, if they come first
    |(?:[\s\(\)]\d{1,2}[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)[\(\)\s.,;?-]
    # averaging keywords. There doesn't seem to be as many keywords that come after the numbers
    .{0,5}(?:(?:average[ds]?|mean|intervals?|periods?|value|segment|sample[ds]?|every|over|into|each|last)+)+)
    )''', re.DOTALL | re.VERBOSE)

    time_bin_avg_min_re = re.compile(r'''(
        # order is avg-time
        (?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|during|highest|frequency|record)+
        .{0,10}
        (?:1|one)(?:[\W\s]){0,2} # I think we only need 1-minute averages
        min(?:ute|utes)?
        | # order is time_avg
        (?:1|one)(?:[\W\s]){0,2}
        min(?:ute|utes)?
        .{0,10}
        (?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|during|highest|frequency|record)+
        )''', re.DOTALL | re.VERBOSE)

    time_bin_avg_words_re = re.compile(r'''(
        (?:
        (?:(?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|during|highest|frequency|record)+.{0,5})+
        \b(?:one|two|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|fifteen|twenty|thirty|sixty)\b # tried adding word boundary to prevent his like "inTENsity"
        (?:(?:[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)[\(\)\s.,;?-])|(?:[\s-]{0,2}min(?:ute)?s?))
        )
        |
        (?:
        (?:one|two|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|fifteen|twenty|thirty|sixty)
        (?:(?:[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)[\(\)\s.,;?-])|(?:[\s-]{0,2}min(?:ute)?s?)).{0,5}
        (?:(?:average[ds]?|mean|intervals?|periods?|value|segment|sample[ds]?|every|over|into|each|last|during|highest|frequency|record)+)+
        )
        )''', re.DOTALL | re.VERBOSE)

    # This regex is for phrases like "The breath-by-breathV̇ O2 data collected by the gas analysis system was averaged per minute"
    avg_per_min_re = re.compile(r'''(
        (?:average[ds]?|mean|display(?:ed)?)
        .{0,50}
        (?:last|once|each|per|every)
        .{0,5}
        min(?:ute)?s?
        )''', re.DOTALL | re.VERBOSE)
    
    # time rolling will be split into the order in which the phrasing can appear. That is roll-time-avg, time-roll-avg, etc.
    roll_time_avg_re = re.compile(r'''(
        (?:roll(?:ing)?|smooth(?:ed|ing)|running|moving|sliding|roll(?:ing|ed))
        .{0,15}
        (?:(?:[\s\(\)]\d{1,2}[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)\b)|(?:one|two|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|fifteen|twenty|thirty|sixty))+
        .{0,15}
        (?:(?:average[ds]?|mean|intervals?|periods?|value|segment|sample[ds]?|every|over|into|each|last|points?)+)+
        )''', re.DOTALL | re.VERBOSE)

    time_roll_avg_re = re.compile(r'''(
        (?:(?:[\s\(\)]\d{1,2}[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)\b)|(?:one|two|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|fifteen|twenty|thirty|sixty))+
        .{0,15}
        (?:roll(?:ing)?|smooth(?:ed|ing)|running|moving|sliding|roll(?:ing|ed))+
        .{0,15}(?:(?:average[ds]?|mean|intervals?|value|segment|periods?|sample[ds]?|every|over|into|each|last|points?)+)+
        )''', re.DOTALL | re.VERBOSE)

    roll_avg_time_re = re.compile(r'''(
        (?:roll(?:ing)?|smooth(?:ed|ing)|running|moving|sliding|roll(?:ing|ed))+
        .{0,15}
        (?:(?:average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|points?)+)+
        .{0,15}
        (?:(?:[\s\(\)]\d{1,2}[\s-]{0,2}(?:(?:s(?:ec)?(?:econd)?(?:econds)?)+)\b)|(?:one|two|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|fifteen|twenty|thirty|sixty))+
        )''', re.DOTALL | re.VERBOSE)

    # rolling breath average
    # if breath number appears BEFORE "smoothing, rolling, etc."
    # (?:(?:\d{1,2}|three|four|[(?:fi)|ﬁ]ve|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}?:breath[es]?|points{0,1})[\s-]{0,2}(?:smooth(?:ing)?(?:ed)?|roll(?:ing)?|sliding|running|moving)+)+|(?:(?:smooth(?:ing)?(?:ed)?|roll(?:ing)?|sliding|running|moving|filter(?:ed)?)+\s{0,2}(?:each)?\s{0,2}(?:\d{1,2}|three|four|[(?:fi)|ﬁ]ve|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}(?:breath[es]?|points?))+
    breath_roll_re = re.compile(r'''( 
        (?:(?:\d{1,2}|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}(?:breath[es]?|points{0,1})[\s-]{0,2}(?:smooth(?:ing)?(?:ed)?|roll(?:ing)?|sliding|running|moving)+)+
        |(?:(?:smooth(?:ing)?(?:ed)?|roll(?:ing)?|sliding|running|moving|filter(?:ed)?)+\s{0,2}(?:each)?\s{0,2}(?:\d{1,2}|three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}(?:breath[es]?|points?))+
        )''', re.DOTALL | re.VERBOSE)

    breath_bin_re = re.compile(r'''(
        (?:every|each)[\s-]{0,2}
        (?:three|four|(?:fi|ﬁ)ve|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|twenty|thirty)[\s-]{0,2}
        (?:breath[es]?|points{0,1})
        )''', re.DOTALL | re.VERBOSE)

    digital_filter_re = re.compile(r'''(
        butterworth|savitzky[\s\W]{0,2}golay|(?:fast\W{0,2}fourier\W{0,2}transform|fft)
        )''', re.DOTALL | re.VERBOSE)

    re_list = [
        time_bin_avg_sec_re,
        time_bin_avg_min_re,
        time_bin_avg_words_re,
        avg_per_min_re,
        roll_time_avg_re,
        time_roll_avg_re,
        roll_avg_time_re,
        breath_roll_re,
        breath_bin_re,
        digital_filter_re
    ]

    out = [rl.findall(text) for rl in re_list if rl.search(text)]
    out = flatten_list(out)
    out = list(set(out)) # remove duplicates

    if out:
        return out
    else:
        return False

text = """
Minute  ventilation  (VE),  oxy­ gen uptake (VO,), and carbon dioxide output (VCO:) were  calculated  for  each  four  breaths  according  to previously described and validated methods [9]
"""
find_avg_terms(text)
# find_avg_terms('The breath-by-breathV̇ O2 data collected by the gas analysis system was averaged per minute for further analysis')

text_df['avg_terms'] = text_df['text'].progress_apply(lambda x: find_avg_terms(x))
text_df[text_df['avg_terms'] != False]

# row = text_df[text_df['doi_suffix'] == 'srep44590']
# row = row.loc[row.index[0],:]
# text = row['text']
# find_avg_terms(row['text'])
# this found the word "performin" somehow...

surrounding_text = []
for idx, row in tqdm(text_df.iterrows(), total=text_df.shape[0]):
    temp_list = []
    if isinstance(row['avg_terms'], list):
        for avg_term in row['avg_terms']:
            temp = get_surrounding_text(phrase=avg_term, text=row['text'], chars=200)
            temp_list.append(temp)
        temp_list = [item for item in temp_list if item is not None]
        flat_list = flatten_list(temp_list)
        unique_list = list(set(flat_list))
        comb_text_list = string_list_overlap(unique_list, row['text']) # combine text together to eliminate some later reading
        if comb_text_list:
            surrounding_text.append(comb_text_list)
        else:
            surrounding_text.append(False)
    else:
        surrounding_text.append(False)

text_df['avg_text'] = surrounding_text

# there's an issue where it's not getting the correct strings anymore

def capitalize_substring(main_string, sub_string):
    out = main_string.replace(sub_string, sub_string.upper())
    return out

# this will help with reading later
surrounding_text_cap = []
for idx, row in tqdm(text_df.iterrows(), total=text_df.shape[0]):
    temp = []
    if row['avg_text']:
        for text in row['avg_text']:
            for term in row['avg_terms']:
                if term in text:
                    text = capitalize_substring(text, term)
            temp.append(text)
        surrounding_text_cap.append(temp)
    else:
        surrounding_text_cap.append(row['avg_text'])

text_df['avg_text'] = surrounding_text_cap

# res = text_df[text_df['doi_suffix'] == 'srep44590'].loc[text_df[text_df['doi_suffix'] == 'srep44590'].index[0], 'avg_text']
# for r in res:
#     print(r)
#     print('\n\n******')

# import random
# n = random.randint(0, text_df.shape[0])
# row = text_df.loc[0,:]
# row

manual_text_analysis_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - Data.csv')
manual_text_analysis_df = pd.read_csv(manual_text_analysis_path, dtype='str')

# copy this into the Google Sheet
merge_df = pd.merge(
    manual_text_analysis_df.drop(['avg_terms', 'avg_text'], axis=1),\
    text_df[['doi_suffix', 'avg_terms', 'avg_text']],\
    how='outer', on='doi_suffix').drop_duplicates(subset='doi_suffix')
merge_df['doi_suffix'] = merge_df['doi_suffix'].astype('str')
merge_df = reorder_columns(merge_df, 'avg_terms', position=10)
merge_df = reorder_columns(merge_df, 'avg_text', position=11)
# merge_df.to_clipboard(index=False)

merge_df[['avg_terms','avg_text']].to_clipboard(index=False)
merge_df.columns
merge_df