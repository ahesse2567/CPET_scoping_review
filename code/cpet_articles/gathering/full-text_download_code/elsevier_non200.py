import pandas as pd
import requests
import json
import random
from tqdm import tqdm

### TRY CHANGING THE DOWNLOAD FORMAT TO SOMETHING BESIDES XML
# https://dev.elsevier.com/tecdoc_article_access.html

articles = pd.read_csv('data/cpet_articles/unpaywall/elsevier_non_oa_articles_status_codes.csv')
articles['publisher_status_code'].value_counts()

non200 = articles[articles['publisher_status_code'] != 200].reset_index(drop=True)
non200

with open("code/cpet_articles/gathering/pdf_download_code/elsevier_config.json") as config_file:
    api_key = json.load(config_file)['apikey']

elsevier_params = {
    'apiKey': api_key,
    'httpAccept': 'text/plain',
    # 'view': 'FULL'
}
elsevier_headers ={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0'}
folder = 'data/cpet_articles/full_texts/xmls/eslevier_non_oa_xmls'

status_codes = []
for idx, row in tqdm(non200.iterrows(), total=len(non200)):
    doi = row['doi']    
    doi_url = 'https://api.elsevier.com/content/article/doi/' + doi
    temp_dict = {'doi': doi}

    try:
        r = requests.get(url=doi_url, params=elsevier_params, headers=elsevier_headers,
        allow_redirects=True, verify=True)
        temp_dict.update({'publisher_status_code': r.status_code})

        # if r.status_code == 200:
        #     doi_suffix = str(doi.split('/')[1:]).strip("[']")
        #     filename = f'{folder}/{doi_suffix}.xml'
            
        #     with open(filename, mode='wb') as f:
        #         f.write(r.content)
        # if r.status_code != 200:
        #     print(r.status_code)

    except Exception as e:
        print(f'Exception at DOI {doi}')
        print(e)
        temp_dict.update({'error': e})
    
    status_codes.append(temp_dict)

status_code_df = pd.DataFrame(status_codes)
status_code_df['publisher_status_code'].value_counts()
non200['publisher_status_code'].value_counts()


# Test code

n = random.randint(0, len(non200))
doi = non200.loc[n, 'doi']
doi_url = 'https://api.elsevier.com/content/article/doi/' + doi

non200.loc[n, 'publisher_status_code']

r = requests.get(url=doi_url, params=elsevier_params, headers=elsevier_headers,
        allow_redirects=True, verify=True)
r.status_code

folder = 'data/cpet_articles/full_texts/xmls/eslevier_non_oa_xmls'
doi_suffix = str(doi.split('/')[1:]).strip("[']")
filename = f'{folder}/{doi_suffix}.xml'

with open(filename, mode='wb') as f:
    f.write(r.content)