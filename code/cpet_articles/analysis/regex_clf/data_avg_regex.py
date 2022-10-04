from pathlib import Path
import pandas as pd
import re
from tqdm import tqdm
import sys
helper_funcs_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/analysis/')
sys.path.append(str(helper_funcs_path))
from helper_funcs.text_analysis import read_raw_text
tqdm.pandas()

def get_doi_suffix(doi):
    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
    doi_suffix = re.sub(r"""([()\\*,"': /?;<>])""", '_._', doi_suffix) # remove bad chars
    doi_suffix = re.sub(r'(_._){2,}', '_._', doi_suffix) # remove multiple sequences of _._
    return doi_suffix

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

# full regex below for easy copy and paste
# (((average[ds]?|mean|interval|periods?|sample[ds]?|every|over|into|each|last|during|highest|frequency)+.{0,5})+[\s\(\)]\d{1,2}[\s-]{0,2}((s(ec)?(econd)?(econds)?)+)[\(\)\s.,;?-])|([\s\(\)]\d{1,2}[\s-]{0,2}((s(ec)?(econd)?(econds)?)+)[\(\)\s.,;?-].{0,5}((average[ds]?|mean|interval|periods?|sample[ds]?|every|over|into|each|last)+)+)

time_bin_avg_sec_re = re.compile(r'''(
    # avg keywords
    (((average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last|during|highest|frequency)+.{0,5})+
    # numbers and seconds.
    [\s\(\)]\d{1,2}[\s-]{0,2}((s(ec)?(econd)?(econds)?)+)[\(\)\s.,;?-])
    # numbers and seconds, if they come first
    |([\s\(\)]\d{1,2}[\s-]{0,2}((s(ec)?(econd)?(econds)?)+)[\(\)\s.,;?-]
    # averaging keywords. There doesn't seem to be as many keywords that come after the numbers
    .{0,5}((average[ds]?|mean|intervals?|periods?|sample[ds]?|every|over|into|each|last)+)+)
    )''', re.IGNORECASE | re.DOTALL | re.VERBOSE)

# I think I might first search by units in seconds, and later in units that include minutes
text = text_df.loc[text_df['doi_suffix'] == 'mss.0000000000001429']
text = text.lower()
time_bin_avg_sec_re.findall(text)

text_df['time_bin_avg_sec'] = text_df['text'].progress_apply(lambda x: time_bin_avg_sec_re.findall(x) if len(time_bin_avg_sec_re.findall(x)) > 0 else False)
text_df['time_bin_avg_sec'][0:10]
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
    num_phrase_re = re.compile(r'(\d+.?[a-zA-Z]+)|([a-zA-Z]+.?\d+)', re.DOTALL)
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

manual_text_analysis_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - Data.csv')
manual_text_analysis_df = pd.read_csv(manual_text_analysis_path, dtype='str')

# copy this into the Google Sheet
merge_df = pd.merge(manual_text_analysis_df, text_df[['doi_suffix', 'time_bin_avg_nums']], how='outer', on='doi_suffix').drop_duplicates(subset='doi_suffix')
merge_df['doi_suffix'] = merge_df['doi_suffix'].astype('str')
merge_df.to_clipboard(index=False)
# rolling breath average
# if breath number appears BEFORE "smoothing, rolling, etc."
# ((\d{1,2}|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}(breath[es]?|points{0,1})[\s-]{0,2}(smooth(ing)?(ed)?|roll(ing)?|sliding|running|moving)+)+|((smooth(ing)?(ed)?|roll(ing)?|sliding|running|moving|filter(ed)?)+\s{0,2}(each)?\s{0,2}(\d{1,2}|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}(breath[es]?|points?))+

breath_roll_re = re.compile(r'''(
    ((\d{1,2}|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}(breath[es]?|points{0,1})[\s-]{0,2}(smooth(ing)?(ed)?|roll(ing)?|sliding|running|moving)+)+
    |((smooth(ing)?(ed)?|roll(ing)?|sliding|running|moving|filter(ed)?)+\s{0,2}(each)?\s{0,2}(\d{1,2}|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}(breath[es]?|points?))+
    )''', re.IGNORECASE | re.VERBOSE)

text_df['breath_roll_avg'] = text_df['text'].progress_apply(lambda x: breath_roll_re.findall(x) if len(breath_roll_re.findall(x)) > 0 else False)
text_df['breath_roll_avg']
text_df['breath_roll_avg_nums'] = text_df['breath_roll_avg'].apply(lambda x: extract_avgs(x))
text_df['breath_roll_avg_nums']
text_df[text_df['breath_roll_avg_nums'] != False]
# how do we deal with a MOS as a median?

# digital filters will be tough because they almost ALWAYS refer to EMG data



