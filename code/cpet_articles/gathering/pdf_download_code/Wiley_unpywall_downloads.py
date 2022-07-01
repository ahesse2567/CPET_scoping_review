from math import comb
import requests
import pandas as pd
import json
from tqdm import tqdm

with open('code/cpet_articles/gathering/pdf_download_code/crossref_config.json') as config_file:
    wiley_token = json.load(config_file)['api_key']

articles = pd.read_csv('/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/unpaywall/unpaywall_info.csv')
wiley_articles = articles[(articles['is_oa'] == False) & \
    (articles['publisher'] == 'Wiley')].reset_index(drop=True) # & \ # 
    #     (articles['status_code'] == '503')].reset_index(drop=True)
wiley_articles.shape

user_agent = 'application/vnd.citationstyles.csl+json, application/vnd.crossref.unixref+xml'
crossref_headers = {
    'Accept': 'application/vnd.citationstyles.csl+json, application/vnd.crossref.unixref+xml',
    'User-Agent': user_agent
}
with open('code/cpet_articles/gathering/pdf_download_code/crossref_config.json') as config_file:
    wiley_token = json.load(config_file)['api_key']
folder = '/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/pdfs/wiley_non_oa_pdfs'

crossref_status_codes = {}
wiley_status_codes = {}
error_dict = {}

for i, row in tqdm(wiley_articles.iterrows(), total = wiley_articles.shape[0]):
    doi = row['doi']
    doi_url = row['doi_url']

    try:
        crossref_response = requests.get(
            url = doi_url,
            headers=crossref_headers,
            allow_redirects=True,
            verify=True)
        crossref_status_codes.update({doi: crossref_response.status_code})

        if crossref_response.status_code != 200:
            print(f'Crossref status code {crossref_response.status_code} for DOI {doi}')
            continue
        
        pdf_url = crossref_response.json()['link'][0]['URL']
        
        wiley_headers = {
            'User-Agent': user_agent,
            'Wiley-TDM-Client-Token': wiley_token,
            # 'CR-TDM-Rate-Limit': '5' ,
            # 'CR-TDM-Rate-Limit-Remaining': '4',
            # 'CR-TDM-Rate-Limit-Reset': '1375427514'
        }

        wiley_response = requests.get(pdf_url, headers = wiley_headers, allow_redirects=True, verify=True)
        wiley_status_codes.update({doi: wiley_response.status_code})

        if wiley_response.status_code != 200:
            print(f'Wiley status code {wiley_response.status_code} for DOI {doi}')
            continue

        doi = row['doi']
        doi_suffix = str(doi.split('/')[1:]).strip("[']")

        filename = f'{folder}/{doi_suffix}.pdf'

        with open(filename, mode='wb') as f:
            f.write(wiley_response.content)
    
    except Exception as e:
        print(f'Exception occured at DOI {doi}: {e}')
        error_dict.update({doi: e})


wiley_status_codes.values()
# manually try and download articles with non 200 status codes

##### got stuck at i = 1056
remaining_articles = wiley_articles.iloc[1056:,:]

for i, row in tqdm(remaining_articles.iterrows(), total = remaining_articles.shape[0]):
    doi = row['doi']
    doi_url = row['doi_url']

    try:
        crossref_response = requests.get(
            url = doi_url,
            headers=crossref_headers,
            allow_redirects=True,
            verify=True)
        crossref_status_codes.update({doi: crossref_response.status_code})

        if crossref_response.status_code != 200:
            print(f'Crossref status code {crossref_response.status_code} for DOI {doi}')
            continue
        
        pdf_url = crossref_response.json()['link'][0]['URL']
        
        wiley_headers = {
            'User-Agent': user_agent,
            'Wiley-TDM-Client-Token': wiley_token,
            # 'CR-TDM-Rate-Limit': '5' ,
            # 'CR-TDM-Rate-Limit-Remaining': '4',
            # 'CR-TDM-Rate-Limit-Reset': '1375427514'
        }

        wiley_response = requests.get(pdf_url, headers = wiley_headers, allow_redirects=True, verify=True)
        wiley_status_codes.update({doi: wiley_response.status_code})

        if wiley_response.status_code != 200:
            print(f'Wiley status code {wiley_response.status_code} for DOI {doi}')
            continue

        doi = row['doi']
        doi_suffix = str(doi.split('/')[1:]).strip("[']")

        filename = f'{folder}/{doi_suffix}.pdf'

        with open(filename, mode='wb') as f:
            f.write(wiley_response.content)
    
    except Exception as e:
        print(f'Exception occured at DOI {doi}: {e}')
        error_dict.update({doi: e})

crossref_status_codes
wiley_status_codes
error_dict

cr_df = pd.DataFrame.from_dict(crossref_status_codes, orient='index').assign(type='crossref_status_code')
cr_df.index.name = 'doi'
cr_df.reset_index(inplace=True)
w_df = pd.DataFrame.from_dict(wiley_status_codes, orient='index').assign(type='wiley_status_code')
w_df.index.name = 'doi'
w_df.reset_index(inplace=True)
err_df = pd.DataFrame.from_dict(error_dict, orient='index').assign(type='exception')
err_df.index.name = 'doi'
err_df.reset_index(inplace=True)

comb_df = pd.concat([cr_df, w_df, err_df]).rename(columns={0: 'value'})
comb_df = comb_df.pivot(index='doi', columns='type', values='value')
comb_df.index.name = 'doi'
comb_df.reset_index(inplace=True)
comb_df['wiley_status_code'].value_counts()

merge = pd.merge(comb_df, wiley_articles, how='outer', on='doi')
# merge.to_csv('data/cpet_articles/unpaywall/wiley_non_oa_status_codes.csv',index=False)
# I'm able to manually download articles with status code 500, 503, 404, 403, and 400