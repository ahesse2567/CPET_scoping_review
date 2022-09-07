from pathlib import Path
import pandas as pd
import re
from tqdm import tqdm
import sys
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/gathering/full-text_download_code/helper_funcs/')
from helper_funcs.articles import get_doi_suffix

# tqdm.pandas()

all_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))
eligibility_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/text_analysis/Manual text analysis - eligibility.csv')

