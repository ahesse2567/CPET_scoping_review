import pandas as pd
import requests
import json
from tqdm import tqdm
import random

# see instructions from getting started guide
# https://dev.elsevier.com/tecdoc_text_mining.html
# Article retreival API guide: https://dev.elsevier.com/documentation/ArticleRetrievalAPI.wadl#d1e52

articles = pd.read_csv('data/cpet_articles/unpaywall/unpaywall_info.csv')
elsevier_non_oa_articles = articles[(articles['is_oa'] == False) & \
    (articles['publisher'] == 'Elsevier BV')].reset_index(drop=True)
# elsevier_non_oa_articles

# Load api key
with open("code/cpet_articles/gathering/pdf_download_code/elsevier_config.json") as config_file:
    api_key = json.load(config_file)['apikey']

elsevier_params = {
    'apiKey': api_key,
    'httpAccept': 'application/pdf',
    'view': 'FULL'
}
elsevier_headers ={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0'}
folder = 'data/cpet_articles/full_texts/pdfs/elsevier_non_oa_pdfs'
file_ext = '.pdf'

n = random.randint(0, len(elsevier_non_oa_articles))
doi = elsevier_non_oa_articles.loc[0,'doi']
doi_url = 'https://api.elsevier.com/content/article/doi/' + doi

r = requests.get(url=doi_url, params=elsevier_params, headers=elsevier_headers,
allow_redirects=True, verify=True)
r.status_code
r.iter_content
r.raw

doi_suffix = str(doi.split('/')[1:]).strip("[']")
filename = f'{folder}/{doi_suffix}{file_ext}'

with open(filename, mode='wb') as f:
    f.write(r.content)


# status_codes = []
# for idx, row in tqdm(elsevier_non_oa_articles.iterrows(), total=len(elsevier_non_oa_articles)):
#     doi = row['doi']    
#     doi_url = 'https://api.elsevier.com/content/article/doi/' + doi
#     temp_dict = {'doi': doi}

#     try:
#         r = requests.get(url=doi_url, params=elsevier_params, headers=elsevier_headers,
#         allow_redirects=True, verify=True)
#         temp_dict.update({'publisher_status_code': r.status_code})

#         if r.status_code == 200:
#             doi_suffix = str(doi.split('/')[1:]).strip("[']")
#             filename = f'{folder}/{doi_suffix}{file_ext}'
            
#             with open(filename, mode='wb') as f:
#                 f.write(r.content)

#     except Exception as e:
#         print(f'Exception at DOI {doi}')
#         print(e)
#         temp_dict.update({'error': e})
    
#     status_codes.append(temp_dict)

# status_code_df = pd.DataFrame(status_codes)
# status_code_df
# elsevier_non_oa_articles

# merge = pd.merge(elsevier_non_oa_articles, status_code_df, how='outer', on='doi')
# merge.to_csv('data/cpet_articles/unpaywall/elsevier_non_oa_articles_status_codes.csv',
#     index=False)