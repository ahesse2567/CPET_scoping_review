from pathlib import Path
import pandas as pd
import re
import sys
from tqdm import tqdm
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/gathering/full-text_download_code/')
from helper_funcs.articles import *

all_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))

p = Path('/Users/antonhesse/Downloads/Manual PDF Analysis').glob('**/*')
files = [x for x in p if x.is_file()]

full_texts = [f.stem for f in files]
full_texts_df = pd.DataFrame({'doi_suffix': full_texts})
full_texts_df.to_clipboard(index=False)

manual_text_analysis_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/Manual text analysis - Data.csv')

merge = pd.merge(manual_text_analysis_df, full_texts_df, how='inner', on='doi_suffix')
merge.to_csv('/Users/antonhesse/Desktop/manual_text_analysis_merge.csv', index=False)

to_be_analyzed = [article for article in full_texts if article not in merge['doi_suffix'].to_list()]
pd.DataFrame(to_be_analyzed).to_clipboard(index=False)