import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.probability import FreqDist
from pathlib import Path
import glob
import random
import pandas as pd
import re
import requests
from tqdm import tqdm
from sklearn.model_selection import StratifiedKFold, cross_val_score, RepeatedStratifiedKFold
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB,BernoulliNB,GaussianNB,ComplementNB
from statistics import mean
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
from sklearn import metrics
from sklearn.model_selection import train_test_split


def process_file(file_name, file_list):
    txt_re = re.compile(file_name)
    fname = list(filter(txt_re.search, file_list))[0]
    
    # check file size to make sure the txt file actually has text
    file_size = 0
    while file_size == 0:
        file_size = Path(fname).stat().st_size
        if file_size != 0: # check if conversion to txt didn't work
            with open(fname, 'r') as f:
                text = f.read()
        else:
            print('Empty file, returning None')
            return None
    text_lower = text.lower()
    tokens = word_tokenize(text_lower)
    stop_words = set(stopwords.words('english'))

    filtered_tokens = [t for t in tokens if t not in stop_words]
    
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(t) for t in filtered_tokens]
    
    return lemmatized_words

def get_raw_text(file_name, file_list):
    txt_re = re.compile(file_name)
    fname = list(filter(txt_re.search, file_list))[0]
    
    # check file size to make sure the txt file actually has text
    file_size = 0
    while file_size == 0:
        file_size = Path(fname).stat().st_size
        if file_size != 0: # check if conversion to txt didn't work
            with open(fname, 'r') as f:
                text = f.read()
        else:
            print('Empty file, returning None')
            return None
    text_lower = text.lower()

txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').glob('*.txt'))
txt_files = [path.stem for path in txt_file_paths]
txt_files_df = pd.DataFrame({'doi_suffix': txt_files})

manual_text_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/Manual text analysis - Data.csv')
# manual_text_df['txt_file_name'] = manual_text_df.apply(lambda x: str(x['doi_suffix'] + '.txt'), axis=1) # not sure I need this
manual_text_df = manual_text_df[manual_text_df['Eligible'] == 'e'] # remove non-original research, animal studies, etc.

merge_df = pd.merge(txt_files_df, manual_text_df, how='inner', on='doi_suffix') # only analyze files for which we have the txt files

# analyzed_txt_files = manual_text_df['txt_file_name'].to_list()
# files_to_analyze = [file for file in analyzed_txt_files if file in txt_files] # only analyze files for which we have the txt files


words = [process_file(f, list(map(str, txt_file_paths))) for f in tqdm(merge_df['doi_suffix'].to_list())]
joined_words = [' '.join(text) for text in words]

gas_data = merge_df['Gas data'].to_list()

features_train, features_test, labels_train, labels_test = train_test_split(joined_words, gas_data, test_size=0.25, random_state=10)

vectorizer = TfidfVectorizer(stop_words='english')

vectorized_features_train = vectorizer.fit_transform(features_train)
vectorized_features_test = vectorizer.transform(features_test)

def show_most_informative_features(vectorizer, clf, n=20): # I think this works with classifiers besides naive bayes
    feature_names = vectorizer.get_feature_names()
    coefs_with_fns = sorted(zip(clf.coef_, feature_names))
    top = zip(coefs_with_fns[:n], coefs_with_fns[:-(n + 1):-1])
    for (coef_1, fn_1), (coef_2, fn_2) in top:
        print("\t%.4f\t%-15s\t\t%.4f\t%-15s" % (coef_1, fn_1, coef_2, fn_2))

show_most_informative_features(vectorizer, MultinomialNB, n=20)

