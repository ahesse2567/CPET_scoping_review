# import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
# from nltk.probability import FreqDist
from pathlib import Path
import random
import pandas as pd
import re
# import requests
from tqdm import tqdm
from sklearn.model_selection import StratifiedKFold, cross_val_score, RepeatedStratifiedKFold, train_test_split, GridSearchCV
from statistics import mean, stdev
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import numpy as np
import pickle
import time
import sys
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/analysis/')
from helper_funcs.text_analysis import tokenize_file, read_raw_text
import shutil

tqdm.pandas()

txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').glob('*.txt'))
txt_file_stems = [path.stem for path in txt_file_paths]
manual_analysis_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/Manual text analysis - Data.csv')
remaining_article_paths = [path for path in txt_file_paths if path.stem not in manual_analysis_df['doi_suffix'].to_list()]

# should removing ineligible articles be it's own classification system?
# should removing articles whose methods refer to an external refernce be their own classification system?
manual_analysis_df = manual_analysis_df[(manual_analysis_df['Eligible'] == 'e') & (manual_analysis_df['External ref'] == 'n')].reset_index(drop=True)
manual_analysis_df.shape

manual_analysis_df[manual_analysis_df['Gas data'].isna()]
file_paths_to_analyze = [path for path in txt_file_paths if path.stem in manual_analysis_df['doi_suffix'].to_list()]
file_stems_to_analyze = [path.stem for path in file_paths_to_analyze]

files_df = pd.DataFrame(
    {'doi_suffix': file_stems_to_analyze,
    'file_path': file_paths_to_analyze}
)

# remove files that may have been moved to parsing error, non-english, etc.
manual_analysis_df = pd.merge(files_df, manual_analysis_df, how='inner', on='doi_suffix')
# manual_analysis_df
manual_analysis_df['tokens'] = manual_analysis_df['file_path'].progress_apply(lambda x: tokenize_file(x, mode='lemm'))
manual_analysis_df['joined_tokens'] = manual_analysis_df['tokens'].progress_apply(lambda x: ' '.join(x))


# should we rerun language and average world length code here just in case?
# my hunch is yes

vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(manual_analysis_df['joined_tokens'].to_list())

rskf_cv = RepeatedStratifiedKFold(n_splits = 5, n_repeats = 2)

rf_clf = RandomForestClassifier()
rf_clf.fit(X.toarray(), manual_analysis_df['Gas data'].to_list())
scores = cross_val_score(rf_clf, X.toarray(), manual_analysis_df['Gas data'].to_list(), cv = rskf_cv)
scores

n = len(remaining_article_paths)
random_n = random.sample(remaining_article_paths, n)
test_texts = [' '.join(tokenize_file(path, mode='lemm')) for path in tqdm(random_n)]

X_test = vectorizer.transform(test_texts)
preds = rf_clf.predict_proba(X_test)
# preds
# rf_clf.classes_

test_dict = {
    'doi_suffix': [path.stem for path in random_n],
    'file_path': [path for path in random_n],
    'pred_n': preds[:,0],
    'pred_y': preds[:,1],
    'pred_0.5': abs(preds[:,0]-0.5)
}
test_df = pd.DataFrame.from_dict(test_dict)
test_df['pred'] = test_df.apply(lambda x: 'y' if x['pred_n'] < 0.5 else 'n', axis=1)
# test_df['article'] = test_df['article'].apply(lambda x: x.replace('.txt', ''))

pred_n_df = test_df[test_df['pred'] == 'n'].reset_index(drop=True)
pred_n_df.to_clipboard(index=False)

dest_folder = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/manual_analysis/prediction_articles')
pdf_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs').glob('*.pdf'))
epub_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/epubs').glob('*.epub'))
txt_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').glob('*.txt'))


for idx, row in pred_n_df.iterrows():
    # try to copy the file in the order of pdf, epub, then finally txt
    article_re = re.compile(re.escape(row['file_path'].stem))
    if list(filter(article_re.search, list(map(str, pdf_paths)))):
        source = Path(list(filter(article_re.search, list(map(str, pdf_paths))))[0])
        dest = dest_folder / str(row['doi_suffix'] + source.suffix)
        shutil.copy(source, dest)
    elif list(filter(article_re.search, list(map(str, epub_paths)))):
        source = Path(list(filter(article_re.search, list(map(str, epub_paths))))[0])
        dest = dest_folder / str(row['doi_suffix'] + source.suffix)
        shutil.copy(source, dest)
    elif list(filter(article_re.search, list(map(str, txt_paths)))):
        source = Path(list(filter(article_re.search, list(map(str, txt_paths))))[0])
        dest = dest_folder / str(row['doi_suffix'] + source.suffix)
        shutil.copy(source, dest)