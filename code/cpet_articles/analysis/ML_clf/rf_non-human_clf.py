from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
# from nltk.probability import FreqDist
from pathlib import Path
import random
import pandas as pd
import re
from tqdm import tqdm
from sklearn.model_selection import StratifiedKFold, cross_val_score, RepeatedStratifiedKFold, train_test_split, GridSearchCV
# from statistics import mean, stdev
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from sklearn.ensemble import RandomForestClassifier
import numpy as np
# import time
import sys
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/analysis/')
from helper_funcs.text_analysis import tokenize_file
import shutil
tqdm.pandas()

txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').glob('*.txt'))
txt_file_stems = [path.stem for path in txt_file_paths]

manual_analysis_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - Data.csv')
manual_analysis_df = manual_analysis_df[~manual_analysis_df['Gas data'].isna()].reset_index(drop=True)

eligibility_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - eligibility.csv')
# eligibility_df = eligibility_df[~eligibility_df['Eligible'].isna()].reset_index(drop=True) # delete this?

comb_df = pd.concat([manual_analysis_df, eligibility_df[['doi_suffix', 'Eligible', 'Eligibility note']]])
comb_df = comb_df[(comb_df['Eligibility note'] == 'Non-human') | (comb_df['Eligibility note'].isna())]
comb_df['non-human'] = comb_df['Eligibility note'].apply(lambda x: False if pd.isna(x) else True)

remaining_article_paths = [path for path in txt_file_paths if path.stem not in comb_df['doi_suffix'].to_list()]

file_paths_to_analyze = [path for path in txt_file_paths if path.stem in comb_df['doi_suffix'].to_list()]
file_stems_to_analyze = [path.stem for path in file_paths_to_analyze]

files_df = pd.DataFrame(
    {'doi_suffix': file_stems_to_analyze,
    'file_path': file_paths_to_analyze}
)

# remove files that may have been moved to parsing error, non-english, etc.
merge_df = pd.merge(files_df, comb_df, how='inner', on='doi_suffix')
# manual_analysis_df
merge_df['tokens'] = merge_df['file_path'].progress_apply(lambda x: tokenize_file(x, mode='lemm'))
merge_df = merge_df[~merge_df['tokens'].isna()] # remove files with None for tokens
merge_df['joined_tokens'] = merge_df['tokens'].progress_apply(lambda x: ' '.join(x))

# should we rerun language and average world length code here just in case?
# my hunch is yes

vectorizer = TfidfVectorizer(stop_words='english')
rf_clf = RandomForestClassifier()

X = vectorizer.fit_transform(merge_df['joined_tokens'].to_list())
rf_clf.fit(X.toarray(), merge_df['non-human'].to_list())
# rskf_cv = RepeatedStratifiedKFold(n_splits = 5, n_repeats = 2)
# scores = cross_val_score(rf_clf, X.toarray(), merge_df['non-human'].to_list(), cv = rskf_cv)
# mean_score = round(np.mean(scores),3)*100
# print(f'Current Accuracy: {mean_score}%')

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
    
X_test = vectorizer.transform(test_df['tokens'].to_list())
preds = rf_clf.predict_proba(X_test)
# preds
# rf_clf.classes_
test_df = test_df.drop('tokens', axis=1)

test_df['pred_human'] = preds[:,0]
test_df['pred_non-human'] = preds[:,1]
test_df['pred_0.5'] = abs(preds[:,0]-0.5)
test_df['pred'] = test_df.apply(lambda x: 'human' if x['pred_human'] > 0.5 else 'non-human', axis=1)
# test_df['article'] = test_df['article'].apply(lambda x: x.replace('.txt', ''))
test_df['pred'].value_counts()
pred_non_human_df = test_df[test_df['pred'] == 'non-human'].reset_index(drop=True)
pred_non_human_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/non-human_pred.csv',
index=False)


"""
I'm not sure we need to copy files into the prediction folder because we only need to document if they have gas data or not.
Only if we're doing a full analysis do we need to copy them into Google Drive.

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
"""