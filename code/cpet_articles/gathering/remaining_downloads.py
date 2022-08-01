from pathlib import Path
import pandas as pd
import re

pdf_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs').glob('*.pdf'))
pdfs = [path.stem for path in pdf_file_paths]

txt_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts').glob('*.txt'))
txts = [path.stem for path in txt_file_paths]

epub_file_paths = list(Path('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/epubs').glob('*.epub'))
epubs = [path.stem for path in epub_file_paths]

full_texts = list(set(pdfs + txts + epubs)) # use set() to remove duplicates

articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')

re_doi_suffix = re.compile(r'(?<=\d/).*')
articles['doi_suffix'] = articles['doi'].apply(lambda x: re_doi_suffix.search(x).group())
full_texts_to_download = [x for x in articles['doi_suffix'].tolist() if x not in full_texts]
len(full_texts_to_download)

remaining_articles = pd.merge(pd.DataFrame({'doi_suffix': full_texts_to_download}), articles, how='inner', on='doi_suffix')
print(remaining_articles['publisher'].value_counts()[0:40])
print('\n')
print(f'Total remaining articles to download: {remaining_articles.shape[0]}')

manual_download_publishers = remaining_articles['publisher'].value_counts()[remaining_articles['publisher'].value_counts() < 100].index.to_list()
manual_download_df = remaining_articles[remaining_articles['publisher'].isin(manual_download_publishers)].drop_duplicates().reset_index(drop=True)
manual_download_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/manual_downloads.csv',
index=False)