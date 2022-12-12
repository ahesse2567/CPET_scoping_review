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

# load fully analyzed files
manual_analysis_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - Data.csv')
manual_analysis_df = manual_analysis_df[~manual_analysis_df['gas_data'].isna()].reset_index(drop=True)

# load files where eligibility was the only thing determined
eligibility_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - eligibility.csv')
ineligible_articles = eligibility_df[eligibility_df['eligible']==False]['doi_suffix'].to_list()
# drop ineligible articles
manual_analysis_df = manual_analysis_df[~manual_analysis_df['eligible'].isin(ineligible_articles)]
# eligibility_df = eligibility_df[~eligibility_df['eligible'].isna()].reset_index(drop=True)


# read in files from manual_analysis_df to train model
file_paths_to_analyze = [path for path in txt_file_paths if path.stem in manual_analysis_df['doi_suffix'].to_list()]
file_stems_to_analyze = [path.stem for path in file_paths_to_analyze if path.stem]

files_df = pd.DataFrame(
    {'doi_suffix': file_stems_to_analyze,
    'file_path': file_paths_to_analyze}
)

merge_df = pd.merge(files_df, manual_analysis_df, how='inner', on='doi_suffix')
merge_df = merge_df[~merge_df['processing_details'].isna()]

merge_df['tokens'] = merge_df['file_path'].progress_apply(lambda x: tokenize_file(x, mode='lemm'))
merge_df['joined_tokens'] = merge_df['tokens'].progress_apply(lambda x: ' '.join(x))

vectorizer = TfidfVectorizer(stop_words='english')
rf_clf = RandomForestClassifier(verbose=1)

X = vectorizer.fit_transform(merge_df['joined_tokens'].to_list())
rf_clf.fit(X.toarray(), merge_df['processing_details'].to_list())
rskf_cv = RepeatedStratifiedKFold(n_splits = 5, n_repeats = 2)
scores = cross_val_score(rf_clf, X.toarray(), merge_df['processing_details'].to_list(), cv = rskf_cv)
mean_score = round(np.mean(scores),3)*100
print(f'Current Accuracy: {mean_score}%')

# read in bbb articles
bbb_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/bbb_articles.csv')
bbb_articles['doi_suffix'] = bbb_articles['doi'].apply(lambda x: get_doi_suffix(x))

bbb_article_paths = [path for path in txt_file_paths if path.stem in bbb_articles['doi_suffix'].to_list()]
remaining_article_paths = [path for path in bbb_article_paths if path.stem not in file_stems_to_analyze]

n = 500
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
test_df['pred_processing_details'] = test_df.apply(lambda x: False if x['pred_false'] > 0.5 else True, axis=1)

test_df = test_df.reindex(columns=['doi_suffix', 'file_path', 'pred_processing_details', 'pred_0.5'])

test_df.sort_values(['pred_processing_details', 'pred_0.5'], ascending=False).to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/processing_details_pred.csv',
index=False)