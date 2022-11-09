import sys
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/gathering/full-text_download_code/')
from helper_funcs.articles import get_current_full_texts, get_doi_suffix
import pandas as pd
import requests
import json
from tqdm import tqdm
import random
import re
from pathlib import Path
import numpy as np

# see instructions from getting started guide
# https://dev.elsevier.com/tecdoc_text_mining.html
# Article retreival API guide: https://dev.elsevier.com/documentation/ArticleRetrievalAPI.wadl#d1e52
# see code at bottom to download a single file at a time for testing

current_full_texts = get_current_full_texts()

all_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))
full_texts_to_download = [x for x in tqdm(all_articles['doi_suffix'].tolist()) if x not in current_full_texts]

remaining_articles = pd.merge(pd.DataFrame({'doi_suffix': full_texts_to_download}), all_articles, how='inner', on='doi_suffix')
articles = remaining_articles[remaining_articles['publisher'] == 'Elsevier BV'].drop_duplicates().reset_index(drop=True)
articles.shape

# Load api key
with open("/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/gathering/full-text_download_code/elsevier/elsevier_config.json") as config_file:
    config = json.load(config_file)
api_key = config['apikey']
insttoken = config['insttoken']

elsevier_params = {
    'apiKey': api_key,
    'insttoken': insttoken,
    'httpAccept': 'text/plain',
    'view': 'FULL'
}
elsevier_headers ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0'}
folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/txts'
file_ext = 'txt'

"""
n = random.randint(0, len(articles))
row = articles.loc[n,:]
"""

log = []
for idx, row in tqdm(articles.iterrows(), total=len(articles)):
    doi = row['doi']
    doi_url = 'https://api.elsevier.com/content/article/doi/' + doi
    out = {'doi': doi}

    try:
        r = requests.get(url=doi_url, params=elsevier_params, headers=elsevier_headers,
            allow_redirects=True, verify=True)
        out.update({'publisher_status_code': r.status_code})

        if r.status_code == 200:
            doi_suffix = str(doi.split('/', 1)[1:]).strip("[']")
            filename = f'{folder}/{doi_suffix}.{file_ext}'
            
            with open(filename, mode='wb') as f:
                f.write(r.content)

    except Exception as e:
        print(f'Exception at DOI {doi}')
        print(e)
        out.update({'error': e})
    
    log.append(out)

log_df = pd.DataFrame(log)
# log_df['publisher_status_code'].value_counts()
if 'error' not in log_df.columns:
    log_df['error'] = np.nan

error_df = log_df[(log_df['publisher_status_code'] != 200) | (~log_df['error'].isna())]

merge = pd.merge(error_df, articles, how='inner', on='doi')
merge.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/elsevier_status_codes.csv',
    index=False)

"""
n = random.randint(0, len(articles))
doi = articles.loc[n,'doi']
# doi = '10.1378/chest.97.1.12'
doi_url = 'https://api.elsevier.com/content/article/doi/' + doi

r = requests.get(url=doi_url, params=elsevier_params,headers=elsevier_headers,
    allow_redirects=True,verify=True)
r.status_code

doi_suffix = get_doi_suffix(doi)
filename = f'{folder}/{doi_suffix}.{file_ext}'

with open(filename, mode='wb') as f:
    f.write(r.content)
"""
