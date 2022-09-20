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

bbb_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/bbb_articles.csv')
bbb_df['doi_suffix'] = bbb_df['doi'].apply(lambda x: get_doi_suffix(x))

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

text='''Expired air was analyzed every 30 second using an automatic
gas analyzer (AE300S, Minato Medical Science, Osaka,
Japan).'''
text=text.lower()

# \d{1,2}[\s-]?s(ec(ond(s)?)?)?\s
time_bin_avg_re = re.compile(r'')
# regular expression for time-bin averages below
# older
# (((average(d)?|mean|interval|period|sample[(ds)]?|every|over|into|each|last)+.{0,5})+\s\d{1,2}[\s-]{0,2}(s(ec(ond(s)?)?)?[\s-]?|(min(ute)?)))|(\s\d{1,2}[\s-]{0,2}(s(ec(ond(s)?)?)?[\s-]?|(min(ute)?))((average(d)?|mean|interval|period|sample(d)?|every|over|into|each|last)+.{0,5})+)
# most recent
# (((average[ds]{0,1}|mean|interval|period|sample[ds]{0,1}|every|over|into|each|last|during|highest|frequency)+.{0,5})+[\s\(\)]\d{1,2}[\s-]{0,2}((s(ec)?(econd)?(econds)?)+|(m(in)?(inute)?(inutes)?)+)[\(\)\s.,;?-])|([\s\(\)]\d{1,2}[\s-]{0,2}((s(ec)?(econd)?(econds)?)+|(m(in)?(inute)?(inutes)?)+)[\(\)\s.,;?-].{0,5}((average[ds]{0,1}|mean|interval|periods{0,1}|sample[ds]{0,1}|every|over|into|each|last)+)+)
time_bin_avg_re = re.compile(r'''(
    (((average[ds]{0,1}|mean|interval|period|sample[ds]{0,1}|every|over|into|each|last|during|highest|frequency)+.{0,5})+[\s\(\)]\d{1,2}[\s-]{0,2}((s(ec)?(econd)?(econds)?)+|(m(in)?(inute)?(inutes)?)+)[\(\)\s.,;?-])|([\s\(\)]\d{1,2}[\s-]{0,2}((s(ec)?(econd)?(econds)?)+|(m(in)?(inute)?(inutes)?)+)[\(\)\s.,;?-].{0,5}((average[ds]{0,1}|mean|interval|periods{0,1}|sample[ds]{0,1}|every|over|into|each|last)+)+)
    )''', re.IGNORECASE | re.DOTALL | re.VERBOSE)

# I think I might first search by units in seconds, and later in units that include minutes

time_bin_avg_re.findall(text)

text_df['time_bin_avg'] = text_df['text'].progress_apply(lambda x: time_bin_avg_re.findall(x) if time_bin_avg_re.findall(x) is not None else False)

time_bin_avg_phrase = text_df.loc[5,'time_bin_avg']
time_bin_avg_phrase
doi_suffix = text_df.loc[1,'doi_suffix']
doi_suffix
# find groups that contain DIGITS.
# if all digits are the same, record what the digits are

text_df['time_bin_avg_phrase'] = 
# rolling breath average
# if breath number appears BEFORE "smoothing, rolling, etc."
# (\d{1,2}|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}breathe{0,1}[\s-]{0,2}(smooth(ing)?|roll(ing)?|sliding|running)+

breath_roll_re = re.compile(r'''(
    (\d{1,2}|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}(breathe{0,1}|points{0,1})[\s-]{0,2}(smooth(ing)?(ed)?|roll(ing)?|sliding|running)+|(smooth(ing)?(ed)?|roll(ing)?|sliding|running|filter(ed)?)+\s{0,2}(each)?\s{0,2}(\d{1,2}|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)[\s-]{0,2}(breathe{0,1}|points{0,1})
    )''', re.VERBOSE)

# how do we deal with a MOS as a median?

# digital filters will be tough because they almost ALWAYS refer to EMG data

text_df['time_bin_average'] = text_df['text'].progress_apply(lambda x: time_bin_average(x))
text_df['time_bin_average'].value_counts()
text_df[text_df['time_bin_average']]

time_bin_re = re.compile(r'\s\d{1,2}[\s-]s')
text_df['time_bin_average'] = text_df['text'].progress_apply(lambda x: time_bin_re.findall(x))
text_df[~text_df['time_bin_average'].isna()]





# (((average[ds]{0,1}|mean|interval|period|sample[ds]{0,1}|every|over|into|each|last)+.{0,5})+\s\d{1,2}[\s-]{0,2}

# ((s(ec)?(econd)?(econds)?)+|(m(in)?(inute)?(inutes)?)+)\s
