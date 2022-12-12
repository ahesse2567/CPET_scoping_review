import random
import pandas as pd
import re
from pathlib import Path
from tqdm import tqdm
tqdm.pandas()
import numpy as np
import fasttext
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import sys
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/analysis/')
from helper_funcs.text_analysis import read_raw_text
from helper_funcs.regex import non_human

txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').glob('*.txt'))
txt_file_stems = [path.stem for path in txt_file_paths]

manual_analysis_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - Data.csv')
manual_analysis_df = manual_analysis_df[(~manual_analysis_df['Gas data'].isna()) | \
    (~manual_analysis_df['Eligibility note'].isna())].reset_index(drop=True)
# manual_analysis_df['Eligibility note'].value_counts()

eligibility_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - Non-human pred.csv')
eligibility_df = eligibility_df[~eligibility_df['Eligible'].isna()].reset_index(drop=True)

comb_df = pd.concat([manual_analysis_df, eligibility_df[['doi_suffix', 'Eligible', 'Eligibility note']]])
comb_df = comb_df[(comb_df['Eligibility note'] == 'Non-human') | (comb_df['Eligibility note'].isna())]
comb_df['human'] = comb_df['Eligibility note'].apply(lambda x: True if pd.isna(x) else False)

remaining_article_paths = [path for path in txt_file_paths if path.stem not in comb_df['doi_suffix'].to_list()]

file_paths_to_analyze = [path for path in txt_file_paths if path.stem in comb_df['doi_suffix'].to_list()]
file_stems_to_analyze = [path.stem for path in file_paths_to_analyze]

files_df = pd.DataFrame({
    'doi_suffix': file_stems_to_analyze,
    'file_path': file_paths_to_analyze
    })

# remove files that may have been moved to parsing error, non-english, etc.
merge_df = pd.merge(files_df, comb_df, how='inner', on='doi_suffix')
merge_df['human'].value_counts()

n = len(remaining_article_paths)
random_n = random.sample(remaining_article_paths, n)
raw_texts = [read_raw_text(path) for path in tqdm(random_n)]

test_df = pd.DataFrame(
    {'doi_suffix': [path.stem for path in random_n],
    'file_path': [path for path in random_n],
    'text': raw_texts}
    )


def fish(text):
    fish_re = re.compile(r' fish ', re.DOTALL)
    mo_list = [fish_re.search(text)]
    res = any(mo is not None for mo in mo_list)
    return res

test_df = test_df[~test_df['text'].isna()].reset_index(drop=True) # remove potential None values
test_df['pred'] = test_df['text'].progress_apply(lambda x: 'i' if fish(x) else 'e')
test_df['pred'].value_counts()
pred_df = test_df.drop('text', axis=1)[test_df['pred'] == 'i'].drop_duplicates().reset_index(drop=True)
pred_df.to_clipboard(index=False, header=False)
pred_df