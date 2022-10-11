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

bbb_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/bbb_articles.csv')
bbb_articles['doi_suffix'] = bbb_articles['doi'].apply(lambda x: get_doi_suffix(x))

bbb_article_paths = [path for path in txt_file_paths if path.stem in bbb_articles['doi_suffix'].to_list()]

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

text = text_df.loc[text_df['doi_suffix'] == 'japplphysiol.00498.2015',:]['text'].values[0]

def find_outlier_text(text):
    cough_re = re.compile(r'\s(cough(ing)?)', re.IGNORECASE) # cough is always included
    # at least one other term is required to accompany 'cough' in order to reference outliers
    weird_breath_re = re.compile(r'\s(swallow|sigh|talk|(throat.{0,2}clear|clear(ing)?.{0,2}throat))', re.DOTALL| re.IGNORECASE)

    error_synosyms_re = re.compile(r'\serrant|\saberrant', re.IGNORECASE) # these almost always refer to breaths
    # outlying, outlier, deviating, erroneous. These options sometimes appear but aren't reliable
    local_mean_re = re.compile(r'\slocal.{0,2}mean', re.DOTALL | re.IGNORECASE) # 'local mean' always refers to outliers
    # (three|four|3|4).{0,2}(sd|standard deviation).{0,50}(local|midpoint)
    if all([cough_re.search(text), weird_breath_re.search(text)]) or any([error_synosyms_re.search(text), local_mean_re.search(text)]):
        mo_list = [cough_re.search(text), weird_breath_re.search(text), error_synosyms_re.search(text), local_mean_re.search(text)]
        out = [mo.group() for mo in mo_list if mo]
        return out
    else:
        return False
find_outlier_text(text)

text_df['outlier'] = text_df['text'].progress_apply(lambda x: find_outlier_text(x))
text_df['outlier'].value_counts()

# now merge this with existing manual analysis data frame