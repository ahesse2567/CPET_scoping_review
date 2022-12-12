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
from helper_funcs.text_analysis import tokenize_file, read_raw_text
from helper_funcs.regex import *

txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').rglob('*.txt'))
txt_file_stems = [path.stem for path in txt_file_paths]

# load manually analyzed articles
manual_analysis_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/Manual text analysis - Data.csv')
remaining_article_paths = [path for path in txt_file_paths if path.stem not in manual_analysis_df['doi_suffix'].to_list()]
# remove ineligible articles and those that point to an external reference
manual_analysis_df = manual_analysis_df[(manual_analysis_df['Eligible'] == 'e') & (manual_analysis_df['External ref'] == 'n')].reset_index(drop=True)
manual_analysis_df.shape

file_paths_to_analyze = [path for path in txt_file_paths if path.stem in manual_analysis_df['doi_suffix'].to_list()]
file_stems_to_analyze = [path.stem for path in file_paths_to_analyze]

files_df = pd.DataFrame(
    {'doi_suffix': file_stems_to_analyze,
    'file_path': file_paths_to_analyze}
)
# add file_paths to df
manual_analysis_df = pd.merge(files_df, manual_analysis_df, how='inner', on='doi_suffix')
manual_analysis_df['tokens'] = manual_analysis_df['file_path'].progress_apply(lambda x: tokenize_file(x, mode='lemm'))
manual_analysis_df['joined_tokens'] = manual_analysis_df['tokens'].progress_apply(lambda x: ' '.join(x))

# Screen out parsing errors by checking for average word length > 1.5 characters
manual_analysis_df['avg_word_len'] = manual_analysis_df.apply(lambda x: np.mean(list(map(len, x['tokens']))), axis=1)
manual_analysis_df = manual_analysis_df[manual_analysis_df['avg_word_len'] > 1.5].reset_index(drop=True)

PRETRAINED_MODEL_PATH = '/Users/antonhesse/opt/anaconda3/bin/lid.176.bin'
model = fasttext.load_model(PRETRAINED_MODEL_PATH)

# TODO screen for language
# there was kind of an issue where it thinks that some articles are 'de', rather than 'en'. Fix later
# manual_analysis_df['language'] = manual_analysis_df['joined_tokens'].progress_apply(lambda x: model.predict(x) if x != None else np.nan)
# manual_analysis_df['lang_code'] = manual_analysis_df.progress_apply(lambda x: x['language'][0][0], axis=1)
# manual_analysis_df['lang_code'].value_counts()

manual_analysis_df['o2_uptake'] = manual_analysis_df.apply(lambda x: oxygen_uptake_re(x['joined_tokens']), axis=1)
manual_analysis_df['vo2_units'] = manual_analysis_df.apply(lambda x: vo2_units_re(x['joined_tokens']), axis=1)
manual_analysis_df['gas_collection_methods'] = manual_analysis_df.apply(lambda x: gas_collection_methods_re(x['joined_tokens']), axis=1)
# manual_analysis_df['estimated_vo2'] = manual_analysis_df.apply(lambda x: estimated_vo2_re(x['joined_tokens']), axis=1)

manual_analysis_df[manual_analysis_df['o2_uptake'] == False] # these articles are VERY likely to NOT include gas data
manual_analysis_df[manual_analysis_df['gas_collection_methods'] == True].shape  # these articles are VERY likely to INCLUDE gas data
manual_analysis_df[manual_analysis_df['gas_collection_methods'] == True]['Gas data'].value_counts()
manual_analysis_df[(manual_analysis_df['gas_collection_methods'] == True) & (manual_analysis_df['Gas data'] == 'n')]


# repeat analysis on unread articles

n = len(remaining_article_paths)
random_n = random.sample(remaining_article_paths, n)
test_tokens = [tokenize_file(path, mode='lemm') for path in tqdm(random_n)]
test_joined_tokens = [' '.join(tokens) for tokens in tqdm(test_tokens)]

test_df = pd.DataFrame(
    {'doi_suffix': [path.stem for path in random_n],
    'file_path': [path for path in random_n],
    'tokens': test_tokens,
    'joined_tokens': test_joined_tokens}
    )

test_df['o2_uptake'] = test_df['joined_tokens'].progress_apply(lambda x: oxygen_uptake_re(x))
test_df['vo2_units'] = test_df['joined_tokens'].progress_apply(lambda x: vo2_units_re(x))
test_df['gas_collection_methods'] = test_df['joined_tokens'].progress_apply(lambda x: gas_collection_methods_re(x))

test_df['o2_uptake'].value_counts()

test_df[test_df['o2_uptake'] == False].reset_index(drop=True)[['doi_suffix', 'file_path']].to_clipboard(index=False)