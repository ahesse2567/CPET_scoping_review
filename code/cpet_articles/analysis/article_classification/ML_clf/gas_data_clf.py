from pathlib import Path
import random
import pandas as pd
import re
from tqdm import tqdm
from sklearn.model_selection import StratifiedKFold, cross_val_score, RepeatedStratifiedKFold, train_test_split, GridSearchCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import time
import sys
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/analysis/')
from helper_funcs.text_analysis import tokenize_file
import shutil
import functools as ft
tqdm.pandas()

def get_doi_suffix(doi):
    doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
    doi_suffix = re.sub(r"""([()\\*,"': /?;<>])""", '_._', doi_suffix) # remove bad chars
    doi_suffix = re.sub(r'(_._){2,}', '_._', doi_suffix) # remove multiple sequences of _._
    return doi_suffix

# load existing file paths
txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').glob('*.txt'))
txt_file_stems = [path.stem for path in txt_file_paths]

# load fully analyzed files
manual_analysis_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - Data.csv')
manual_analysis_df = manual_analysis_df[~manual_analysis_df['gas_data'].isna()].reset_index(drop=True)

# load files where eligibility was the only thing determined
eligibility_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - eligibility.csv')
eligibility_df = eligibility_df[~eligibility_df['eligible'].isna()].reset_index(drop=True)
# find ineligible articles
ineligible_articles = eligibility_df[eligibility_df['eligible'] == False]['doi_suffix'].to_list()

# load bbb articles
bbb_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/bbb_articles.csv')
bbb_articles['doi_suffix'] = bbb_articles['doi'].apply(lambda x: get_doi_suffix(x))
# remove ineligible articles
eligible_bbb_df = bbb_articles[~bbb_articles['doi_suffix'].isin(ineligible_articles)]

pd.merge(manual_analysis_df, eligible_bbb_df, how='inner', on='doi_suffix')['gas_data'].value_counts()

dfs = [manual_analysis_df, eligibility_df, bbb_articles]
merge_df = ft.reduce(lambda left, right: pd.merge(left, right, on='doi_suffix'), dfs)
merge_df

pd.merge(manual_analysis_df, bbb_articles)['doi_suffix'].to_clipboard(index=False)
# ok, not enough articles to train a model to screen for actually collecting gas data
# the text of BBB usually always means they collected gas data