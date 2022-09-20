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


def time_bin_average(text):
    mo_list = [
        re.search(r'(\s\d{1,2}[\s-]s)', text)
    ]

    
    out = any(mo is not None for mo in mo_list)

    return out

# \d{1,2}[\s-]?s(ec(ond(s)?)?)?\s
# regular expression for time-bin averages below
# (((average(d)?|mean|interval|period|sample[(ds)]?|every|over|into|each|last)+.{0,5})+\s\d{1,2}[\s-]{0,2}(s(ec(ond(s)?)?)?[\s-]?|(min(ute)?)))|(\s\d{1,2}[\s-]{0,2}(s(ec(ond(s)?)?)?[\s-]?|(min(ute)?))((average(d)?|mean|interval|period|sample(d)?|every|over|into|each|last)+.{0,5})+)

text_df['time_bin_average'] = text_df['text'].progress_apply(lambda x: time_bin_average(x))
text_df['time_bin_average'].value_counts()
text_df[text_df['time_bin_average']]

time_bin_re = re.compile(r'\s\d{1,2}[\s-]s')
text_df['time_bin_average'] = text_df['text'].progress_apply(lambda x: time_bin_re.findall(x))
text_df[~text_df['time_bin_average'].isna()]