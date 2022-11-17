import pandas as pd
from pathlib import Path
from code.cpet_articles.gathering.full_text_download_code.helper_funcs.articles import get_current_full_texts
from code.cpet_articles.utils.article_names import get_doi_suffix

current_full_texts = get_current_full_texts()
current_full_texts_df = pd.DataFrame({'doi_suffix': current_full_texts})

all_articles = pd.read_csv(str(Path('data/cpet_articles/unpaywall/unpaywall_info.csv')))
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))

merge_df = pd.merge(current_full_texts_df, all_articles, how='inner', on='doi_suffix').drop_duplicates()
merge_df.to_csv(str(Path('data/cpet_articles/unpaywall/downloaded_articles.csv')), index=False)