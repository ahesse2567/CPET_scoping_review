import pandas as pd
from pathlib import Path
import sys
helper_func_folder_path = Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/gathering/full-text_download_code/')

sys.path.append(str(helper_func_folder_path))
from helper_funcs.articles import get_doi_suffix, get_current_full_texts

current_full_texts = get_current_full_texts()
current_full_texts_df = pd.DataFrame({'doi_suffix': current_full_texts})

all_articles = pd.read_csv(str(Path('data/cpet_articles/unpaywall/unpaywall_info.csv')))
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))

merge = pd.merge(current_full_texts_df, all_articles, how='inner', on='doi_suffix').drop_duplicates()
merge.to_csv(str(Path('data/cpet_articles/full_texts/unpaywall/downloaded_articles.csv')), index=False)