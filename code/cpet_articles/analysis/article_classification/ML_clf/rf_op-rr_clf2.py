from pathlib import Path
import random
import pandas as pd
import re
# import requests
from tqdm import tqdm
from sklearn.model_selection import StratifiedKFold, cross_val_score, RepeatedStratifiedKFold, train_test_split, GridSearchCV
# from statistics import mean, stdev
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.ensemble import RandomForestClassifier
import numpy as np
# import pickle
import time
import sys
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/analysis/')
from helper_funcs.text_analysis import tokenize_file
import shutil
tqdm.pandas()

# load existing file paths
txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').glob('*.txt'))
txt_file_stems = [path.stem for path in txt_file_paths]

# load fully analyzed files
manual_analysis_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - Data.csv')
manual_analysis_df = manual_analysis_df[~manual_analysis_df['gas_data'].isna()].reset_index(drop=True)

# load files where eligibility was the only thing determined
eligibility_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - eligibility.csv')
eligibility_df = eligibility_df[~eligibility_df['eligible'].isna()].reset_index(drop=True)

comb_df = pd.concat([manual_analysis_df, eligibility_df]) # make one big eligibility data frame
comb_df = comb_df[~comb_df['eligible'].isna()] # remove na vals in eligible column

remaining_article_paths = [path for path in txt_file_paths if path.stem not in comb_df['doi_suffix'].to_list()]

file_paths_to_analyze = [path for path in txt_file_paths if path.stem in comb_df['doi_suffix'].to_list()]
file_stems_to_analyze = [path.stem for path in file_paths_to_analyze if path.stem]

files_df = pd.DataFrame(
    {'doi_suffix': file_stems_to_analyze,
    'file_path': file_paths_to_analyze}
)
# get non-human file stems
human_stems = comb_df[comb_df['human'] == True]['doi_suffix'].to_list()
# remove non-human file stems from files_df
files_df = files_df[files_df['doi_suffix'].isin(human_stems)]

merge_df = pd.merge(files_df, comb_df, how='inner', on='doi_suffix')
merge_df['file_path'] = merge_df['file_path_x']
merge_df = merge_df.drop(['file_path_x', 'file_path_y'], axis=1)
merge_df = merge_df[merge_df['op-rr'].notna()] # remove random na values
merge_df['tokens'] = merge_df['file_path'].progress_apply(lambda x: tokenize_file(x, mode='lemm'))
merge_df['joined_tokens'] = merge_df['tokens'].progress_apply(lambda x: ' '.join(x))


vectorizer = TfidfVectorizer(stop_words='english')
rf_clf = RandomForestClassifier(verbose=1)

X = vectorizer.fit_transform(merge_df['joined_tokens'].to_list())
rf_clf.fit(X.toarray(), merge_df['op-rr'].to_list())
rskf_cv = RepeatedStratifiedKFold(n_splits = 5, n_repeats = 2)
scores = cross_val_score(rf_clf, X.toarray(), merge_df['op-rr'].to_list(), cv = rskf_cv)
mean_score = round(np.mean(scores),3)*100
print(f'Current Accuracy: {mean_score}%')

bbb_articles = pd.read_csv(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/bbb_articles.csv'))

remaining_article_paths = [path for path in remaining_article_paths if path.stem in bbb_articles['doi_suffix'].to_list()]

n = len(remaining_article_paths)
random_n = random.sample(remaining_article_paths, n)
test_texts = []
for idx, path in tqdm(enumerate(random_n), total=len(random_n)):
    try:
        tokens = tokenize_file(path, mode='lemm')
        if tokens is not None:
            tokens = ' '.join(tokens)
        test_texts.append(tokens)
    except FileNotFoundError as e:
        print(e)
        test_texts.append(None)

test_df = pd.DataFrame({
    'doi_suffix': [path.stem for path in random_n],
    'file_path': [path for path in random_n],
    'tokens': test_texts
})
test_df = test_df[~test_df['tokens'].isna()].reset_index(drop=True)

X_test = vectorizer.transform(test_texts)
preds = rf_clf.predict_proba(X_test)
# preds
# rf_clf.classes_

test_df = test_df.drop('tokens', axis=1)

test_df['pred_false'] = preds[:,0]
test_df['pred_true'] = preds[:,1]
test_df['pred_0.5'] = abs(preds[:,0]-0.5)
test_df['pred_op-rr'] = test_df.apply(lambda x: False if x['pred_false'] > 0.5 else True, axis=1)

test_df = test_df.reindex(columns=['doi_suffix', 'file_path', 'pred_op-rr', 'pred_0.5'])

test_df.sort_values(['pred_op-rr', 'pred_0.5'], ascending=False).to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/op-rr_pred.csv',
index=False)