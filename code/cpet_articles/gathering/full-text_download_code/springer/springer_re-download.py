import requests
import pandas as pd
import requests
import json
from tqdm import tqdm
import sys
sys.path.append('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/gathering/full-text_download_code/')
from helper_funcs.articles import get_current_full_texts, get_doi_suffix, download_pdf
import random
import re

# I discovered that the file names didn't match the DOI suffix for many closed access, Springer articles, so I'm redownloading those PDFs
# DON'T FORGET TO USE THE VPN!!!

def find_springer_download_link(response):
    for record in response.json()['records']:
        if record['identifier'].split('doi:')[1].lower() == doi.lower():
            for l in record['url']:
                if l['format'] == 'pdf':
                    pdf_url = l['value']
                    return pdf_url

# current_full_texts = get_current_full_texts()

all_articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
all_articles['doi_suffix'] = all_articles['doi'].apply(lambda x: get_doi_suffix(x))
# full_texts_to_download = [x for x in tqdm(all_articles['doi_suffix'].tolist()) if x not in current_full_texts]

# remaining_articles = pd.merge(pd.DataFrame({'doi_suffix': full_texts_to_download}), all_articles, how='inner', on='doi_suffix')
springer_re = re.compile(r'springer', re.IGNORECASE)
all_articles['springer'] = all_articles['publisher'].apply(lambda x: springer_re.search(str(x)))

articles = all_articles[(all_articles['publisher'].str.contains('Springer') == True) & (all_articles['is_oa'] == False)].drop_duplicates().reset_index(drop=True)
articles.shape

with open('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/code/cpet_articles/gathering/full-text_download_code/springer/springer_config.json') as config_file:
    api_key = json.load(config_file)['api_key']
# api_key

springer_api_url = 'https://api.springernature.com/meta/v2/json?'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0'}
folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/full_texts/pdfs/'
# dest_folder = '/Users/antonhesse/Desktop/'

"""
n = random.randint(0, articles.shape[0])
row = articles.loc[n,:]
"""

# log = []

# got to i == 1210 before it quit
for i, row in tqdm(articles.iterrows(), total=articles.shape[0]):
    doi = row['doi']
    out = {'doi': doi}
    params = {'api_key': api_key, 'q': doi}
    try:
        response = requests.get(url = springer_api_url, params = params, headers=headers, allow_redirects=True)
        out.update({'query_status_code': response.status_code})
        if response.status_code == 200:
            pdf_url = find_springer_download_link(response)
            pdf_response = requests.get(pdf_url, allow_redirects=True) # do I need stream=True?
            out.update({'pdf_status_code': pdf_response.status_code})
            if pdf_response.status_code == 200:
                download_pdf(doi, dest_folder=folder, content=pdf_response.content)
    except Exception as e:
        print(f'{e} at index {i} for DOI {doi}')
        out.update({'error': e})

    log.append(out)

log_df = pd.DataFrame(log)
log_df['query_status_code'].value_counts()
log_df['pdf_status_code'].value_counts()
log_df[~log_df['error'].isna()]

log_df.to_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/springer_status_codes.csv',
    index=False)


"""
# for individual article testing
n = random.randint(0, invalid_url_df.shape[0])
row = invalid_url_df.loc[n,:]

# log = []
for i, row in tqdm(invalid_url_df.iterrows(), total=invalid_url_df.shape[0]):
    doi = row['doi']
    out = {'doi': doi}
    params = {'api_key': api_key, 'q': doi}
    try:
        response = requests.get(url = springer_api_url, params = params, headers=headers, allow_redirects=True)
        out.update({'query_status_code': response.status_code})
        if response.status_code == 200:
            pdf_url = find_springer_download_link(response)
            pdf_response = requests.get(pdf_url, stream=True, allow_redirects=True)
            out.update({'pdf_status_code': pdf_response.status_code})
            if pdf_response.status_code == 200:
                download_pdf(doi, dest_folder=folder, content=pdf_response.content)
    except Exception as e:
        print(f'{e} at index {i} for DOI {doi}')
        out.update({'error': e})

    log.append(out)
"""