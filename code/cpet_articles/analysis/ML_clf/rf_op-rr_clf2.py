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
manual_analysis_df = manual_analysis_df[~manual_analysis_df['Gas data'].isna()].reset_index(drop=True)

# load files where eligibility was the only thing determined
eligibility_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - eligibility.csv')
eligibility_df = eligibility_df[~eligibility_df['eligible'].isna()].reset_index(drop=True)

comb_df = pd.concat([manual_analysis_df, eligibility_df]) # make one big eligibility data frame
comb_df = comb_df[~comb_df['eligible'].isna()] # remove na vals in eligible column

remaining_article_paths = [path for path in txt_file_paths if path.stem not in comb_df['doi_suffix'].to_list()]
file_paths_to_analyze = [path for path in txt_file_paths if path.stem in comb_df['doi_suffix'].to_list()]
file_stems_to_analyze = [path.stem for path in file_paths_to_analyze]

# TODO predict on JUST op-rr and JUST human, but remove all ineligible articles PRIOR to running that code

