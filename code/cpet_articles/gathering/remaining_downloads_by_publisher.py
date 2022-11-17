# from pathlib import Path
import pandas as pd
# import re
from tqdm import tqdm
from code.cpet_articles.gathering.full_text_download_code.helper_funcs.articles import get_current_full_texts
from code.cpet_articles.utils.article_names import get_doi_suffix

current_full_texts = get_current_full_texts()
manual_downloads_df = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/Manual Downloads - Articles.csv')
# find which articles I tried to download, but could not b/c I didn't have a subscription
unsubscribed_articles_df = manual_downloads_df[(manual_downloads_df['subscribed'] == False) & (manual_downloads_df['done'] == True)]

all_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))
full_texts_to_download = [x for x in tqdm(all_articles['doi_suffix'].tolist()) if x not in current_full_texts and x not in unsubscribed_articles_df['doi_suffix'].to_list()]

remaining_articles = pd.merge(pd.DataFrame({'doi_suffix': full_texts_to_download}), all_articles, how='inner', on='doi_suffix')
remaining_articles.shape
print(remaining_articles['publisher'].value_counts()[0:40])
print()
print(f'Total remaining articles to download: {remaining_articles.shape[0]}')

remaining_articles_to_download_df = remaining_articles[[
    'doi_url', 'doi', 'doi_suffix', 'journal_name', 'publisher'
]]

remaining_articles_to_download_df.to_clipboard(index=False)

choice = input('Would you like to rerun articles to download manually? (y/n) ')
if choice == 'y':
    manual_download_publishers = remaining_articles['publisher'].value_counts()[remaining_articles['publisher'].value_counts() < 100].index.to_list()
    manual_download_df = remaining_articles[remaining_articles['publisher'].isin(manual_download_publishers)].drop_duplicates().reset_index(drop=True)
    manual_download_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/manual_downloads.csv',
    index=False)


# manual_download_publishers = remaining_articles['publisher'].value_counts()[remaining_articles['publisher'].value_counts() < 100].index.to_list()
# manual_download_df = remaining_articles[remaining_articles['publisher'].isin(manual_download_publishers)].drop_duplicates().reset_index(drop=True)
# manual_download_df.shape
# manual_download_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/manual_downloads.csv',
# index=False)


# manual_downloads_df = remaining_articles[~remaining_articles['publisher'].isin(['Informa UK Limited', 'Wiley', 'American Physiological Society'])].drop_duplicates().reset_index(drop=True)
# manual_downloads_df[['doi_url', 'doi', 'doi_suffix', 'journal_name', 'publisher']].to_clipboard(index=False)